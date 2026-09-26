# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
DataFlow-specific CDP API client with support for 308 redirects
"""

import json
import time
from typing import Any, Dict, Optional, Union, List
from urllib.parse import urlparse, quote
from urllib.error import HTTPError
from email.utils import formatdate
from ansible.module_utils.urls import open_url

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
    CdpClient,
    CdpError,
    make_signature_header,
)


# ============================================================================
# HTTP request/response helpers for workload (Bearer-token) transport
#
# These hold the request-building and response-parsing logic used by
# WorkloadTransport below. They are kept local to this DataFlow-specific module
# rather than shared from cdp_client.py, which signs requests with Ed25519.
# ============================================================================


def build_query_string(url: str, params: Optional[Dict[str, Any]]) -> str:
    """
    Append query parameters to a URL.

    List values expand into repeated ``key=item`` pairs. Returns the URL
    unchanged when ``params`` is empty.
    """
    if not params:
        return url

    query_params: List[str] = []
    for key, value in params.items():
        if isinstance(value, list):
            query_params.extend(f"{key}={item}" for item in value)
        else:
            query_params.append(f"{key}={value}")
    return f"{url}?{'&'.join(query_params)}"


def serialize_request_body(
    data: Optional[Union[Dict[str, Any], List[Any]]] = None,
    json_data: Optional[Union[Dict[str, Any], List[Any]]] = None,
) -> Optional[str]:
    """
    Serialize a request body to a JSON string.

    ``json_data`` takes precedence over ``data``. Returns None when neither is
    provided.
    """
    if json_data is not None:
        return json.dumps(json_data)
    if data is not None:
        return json.dumps(data)
    return None


def parse_success_response(resp: Any, status_code: int) -> Any:
    """
    Parse a 2xx HTTP response.

    Returns None for 204, the decoded JSON object for a JSON body, a
    ``{"response": <text>}`` wrapper for a non-JSON body, or an empty dict when
    there is no body.
    """
    if status_code == 204:
        return None
    if resp:
        response_text = resp.read().decode("utf-8")
        if response_text:
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {"response": response_text}
        return {}
    return {}


def parse_error_message(info: Dict[str, Any], status_code: int) -> str:
    """
    Extract a human-readable error message from an HTTP error info dict.

    Looks in the response body for ``message`` / ``error`` / ``errorMessages``
    / ``errorMessage`` keys, falling back to ``info['msg']``.
    """
    error_message = f"HTTP {status_code} Error"
    try:
        error_body = info.get("body")
        if error_body:
            error_data = json.loads(error_body)
            if "message" in error_data:
                error_message = error_data["message"]
            elif "error" in error_data:
                error_message = error_data["error"]
            elif "errorMessages" in error_data:
                msgs = error_data["errorMessages"]
                error_message = " ".join(msgs) if isinstance(msgs, list) else str(msgs)
            else:
                error_message = error_data.get("errorMessage", "Unknown error")
        else:
            error_message = info.get("msg", "Unknown error")
    except Exception:
        error_message = info.get("msg", "Unknown error")
    return error_message


def is_retryable_status(status_code: int) -> bool:
    """Return True for status codes worth retrying (5xx, 408, 429)."""
    return status_code >= 500 or status_code in (408, 429)


def compute_backoff(attempt: int) -> float:
    """Exponential backoff with a 5s ceiling: 0.5s, 1s, 2s, 4s, 5s, ..."""
    return min(0.5 * (2**attempt), 5)


class CdpDfApiClient(AnsibleCdpClient):
    """
    DataFlow-specific CDP API client that extends AnsibleCdpClient.

    This client handles DataFlow-specific requirements such as:
    - 308 Permanent Redirect handling for flow import operations
    - DataFlow extension format transformation (metadata in headers, content in body)
    """

    def __init__(self, module, base_url, access_key, private_key, **kwargs):
        super().__init__(
            module=module,
            base_url=base_url,
            access_key=access_key,
            private_key=private_key,
            **kwargs,
        )
        self.endpoint_tls = module.params.get("endpoint_tls", True)

    def _transform_df_flow_payload(
        self,
        body: str,
        headers: Dict[str, str],
    ) -> tuple[str, Dict[str, str]]:
        """
        Transform DataFlow flow import payload to extension format.

        Moves metadata from JSON body to custom headers and extracts
        the raw flow definition content as the body.

        Args:
            body: Original JSON request body
            headers: Request headers dictionary (will be modified in-place)

        Returns:
            Tuple of (transformed_body, headers)

        Reference:
            cdpcli/extensions/df/__init__.py::_build_upload_flow_headers
        """
        try:
            request_data = json.loads(body)

            # Extract metadata and move to custom headers (URI-encoded)
            if "name" in request_data:
                headers["Flow-Definition-Name"] = quote(request_data["name"])
            if "description" in request_data:
                headers["Flow-Definition-Description"] = quote(
                    request_data["description"],
                )
            if "comments" in request_data:
                headers["Flow-Definition-Comments"] = quote(request_data["comments"])
            if "collectionCrn" in request_data:
                headers["Flow-Definition-Collection-Identifier"] = quote(
                    request_data["collectionCrn"],
                )
            if "tags" in request_data:
                tags_json = '{ "tags": ' + json.dumps(request_data["tags"]) + "}"
                headers["Flow-Definition-Tags"] = quote(tags_json)

            # Body becomes raw flow content (not wrapped in JSON)
            transformed_body = request_data.get("file", "")
            return transformed_body, headers

        except (json.JSONDecodeError, KeyError):
            # If transformation fails, return original body
            return body, headers

    def _is_df_flow_import_redirect(self, redirect_path: str) -> bool:
        """
        Check if a redirect is for a DataFlow flow import operation.

        Args:
            redirect_path: The redirect URL path

        Returns:
            True if this is a DataFlow flow import redirect
        """
        return "/catalog/flows" in redirect_path

    def _handle_special_status_code(
        self,
        status_code: int,
        info: Dict[str, Any],
        method: str,
        url: str,
        body: Optional[str],
        headers: Dict[str, str],
    ) -> Optional[tuple]:
        """
        Override to handle 308 Permanent Redirect for DataFlow operations.

        Args:
            status_code: HTTP status code received
            info: Response info dictionary from fetch_url
            method: HTTP method used
            url: Full request URL
            body: Request body (may be None)
            headers: Request headers

        Returns:
            None if status code not 308, or tuple of (resp, info) if handled
        """
        if status_code != 308:
            return None

        redirect_url = info.get("location")
        if not redirect_url:
            raise CdpError(
                f"308 redirect received but no location header for {url}",
            )

        # Extract path from redirect URL for signature calculation
        parsed_redirect = urlparse(redirect_url)
        redirect_path = parsed_redirect.path
        if parsed_redirect.query:
            redirect_path += "?" + parsed_redirect.query

        # Check if this needs DataFlow extension format transformation
        is_df_flow_import = self._is_df_flow_import_redirect(redirect_path)

        redirect_body = body
        redirect_headers = dict(headers)

        if is_df_flow_import and body:
            # Transform to DataFlow extension format
            redirect_body, redirect_headers = self._transform_df_flow_payload(
                body,
                redirect_headers,
            )

        # Re-sign for the redirect URL (signature uses path only)
        redirect_headers["x-altus-date"] = formatdate(usegmt=True)
        redirect_headers["x-altus-auth"] = make_signature_header(
            method,
            redirect_path,
            redirect_headers,
            self.access_key,
            self.private_key,
        )

        # Follow the redirect
        return fetch_url(
            self.module,
            redirect_url,
            method=method,
            headers=redirect_headers,
            data=redirect_body,
            timeout=self.timeout,
        )


class WorkloadTransport(CdpClient):
    """
    HTTP transport for CDP data-service workload APIs.

    Workload APIs (e.g. DataFlow ``/dfx/api/...``) authenticate with a JWT
    Bearer token plus an XSRF cookie, unlike the control plane which signs
    requests with Ed25519. This base owns the request/retry/parse machinery so
    concrete workload clients only declare their auth headers.

    Responsibilities:
        - XSRF/CSRF cookie capture and replay
        - Retry with exponential backoff on transient failures
        - Raises CdpError on failure (it does not call ``module.fail_json``)

    Subclasses must set ``self.validate_certs``, ``self.base_url``, ``self.timeout``,
    ``self.cookies`` and ``self.headers`` in their ``__init__``.
    """

    def _url(self, path: str) -> str:
        """Construct the full request URL from the base URL and a path."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request_headers(self) -> Dict[str, str]:
        """Return per-request headers: base headers plus any captured cookies."""
        headers = self.headers.copy()
        if self.cookies:
            headers["Cookie"] = "; ".join(
                [f"{k}={v}" for k, v in self.cookies.items()],
            )
            if "XSRF-TOKEN" in self.cookies:
                headers["X-XSRF-TOKEN"] = self.cookies["XSRF-TOKEN"]
        return headers

    def _capture_cookies(self, response) -> None:
        """
        Capture cookies from a response into ``self.cookies``.

        Workload APIs hand back an XSRF token via ``Set-Cookie`` on the first
        request; subsequent mutating requests must echo it back.
        """
        cookie_headers = response.info().get_all("set-cookie") or []
        for cookie_header in cookie_headers:
            if "=" in cookie_header:
                cookie_part = cookie_header.split(";")[0]
                name, value = cookie_part.split("=", 1)
                self.cookies[name.strip()] = value.strip()

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        max_retries: int = 3,
        squelch: Dict[int, Any] = {},
    ) -> Any:
        """
        Make a workload API request with cookie handling and retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path relative to the base URL
            params: Query parameters appended to the URL
            data: Request body serialized as JSON
            json_data: Request body serialized as JSON (takes precedence over data)
            max_retries: Maximum number of attempts before failing
            squelch: Map of status codes to values returned instead of raising

        Returns:
            Parsed JSON response, or None for 204 responses

        Raises:
            CdpError: On non-squelched HTTP errors or exhausted retries
        """
        url = build_query_string(self._url(path), params)
        headers = self._request_headers()
        body = serialize_request_body(data=data, json_data=json_data)

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = open_url(
                    url,
                    data=body,
                    headers=headers,
                    method=method,
                    timeout=self.timeout,
                    validate_certs=self.validate_certs,
                )

                self._capture_cookies(resp)
                status_code = resp.getcode()

                if status_code in squelch:
                    return squelch[status_code]

                return parse_success_response(resp, status_code)

            except HTTPError as e:
                status_code = e.code

                if status_code in squelch:
                    return squelch[status_code]

                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    error_body = ""

                info = {"body": error_body, "msg": str(e), "status": status_code}
                error_message = parse_error_message(info, status_code)

                if is_retryable_status(status_code) and attempt < max_retries - 1:
                    time.sleep(compute_backoff(attempt))
                    last_error = CdpError(
                        f"{error_message} for {url}",
                        status=status_code,
                    )
                    continue

                raise CdpError(f"{error_message} [{status_code}] for {url}")

            except CdpError:
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(compute_backoff(attempt))
                    last_error = CdpError(f"Connection error for {url}: {str(e)}")
                    continue
                raise CdpError(
                    f"Request failed after {max_retries} attempts for {url}: {str(e)}",
                )

        if last_error:
            raise last_error
        raise CdpError(f"Request failed for {url}")

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an HTTP GET request."""
        return self._make_request("GET", path, params=params)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        squelch: Dict[int, Any] = {},
    ) -> Dict[str, Any]:
        """Execute an HTTP POST request."""
        return self._make_request(
            "POST",
            path,
            data=data,
            json_data=json_data,
            squelch=squelch,
        )

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        squelch: Dict[int, Any] = {},
    ) -> Dict[str, Any]:
        """Execute an HTTP PUT request."""
        return self._make_request(
            "PUT",
            path,
            data=data,
            json_data=json_data,
            squelch=squelch,
        )

    def delete(self, path: str, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        """Execute an HTTP DELETE request."""
        return self._make_request("DELETE", path, squelch=squelch)


class CdpDfWorkloadClient(WorkloadTransport):
    """
    CDP DataFlow Workload Service client using Bearer token authentication.

    Communicates with the DataFlow Workload Service (``/dfx/api/rpc-v1/...``).
    The token and base URL are obtained from the control plane via IAM
    ``generateWorkloadAuthToken``. All transport behaviour comes from
    WorkloadTransport; this class only declares the Bearer auth headers.
    """

    def __init__(
        self,
        base_url: str,
        access_token: str,
        validate_certs: bool = True,
        timeout_seconds: int = 60,
        default_page_size: int = 100,
    ):
        """
        Initialize the DataFlow workload client.

        Args:
            base_url: Base URL of the DataFlow Workload Service
            access_token: JWT Bearer token from generateWorkloadAuthToken
            validate_certs: Whether to validate TLS certificates for the workload endpoint
            timeout_seconds: Per-request HTTP timeout in seconds
            default_page_size: Default page size for paginated requests
        """
        super().__init__(default_page_size=default_page_size)
        self.validate_certs = validate_certs
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout_seconds
        self.cookies: Dict[str, str] = {}
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
