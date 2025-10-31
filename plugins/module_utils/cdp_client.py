# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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
A common Ansible-based REST client for the Cloudera on Cloud Platform (CDP)
"""

import abc
import configparser
import json
import os
import time

from base64 import b64decode, urlsafe_b64encode
from collections import OrderedDict
from cryptography.hazmat.primitives.asymmetric import ed25519
from email.utils import formatdate
from typing import Any, Dict, Optional, List, Tuple, Union
from urllib.parse import urlencode, urlparse

from ansible.module_utils.urls import fetch_url


def load_cdp_config(
    access_key,
    private_key,
    credentials_path,
    profile,
) -> Tuple[str, str]:
    """
    Load CDP credential configuration, by parsing credential file, by checking
    (access_key,private_key) are not (None,None)
    """
    if access_key is None or private_key is None:
        exists = os.path.exists(credentials_path)
        if not exists:
            msg = "Credentials file '{0}' does not exist"
            raise Exception(msg.format(credentials_path))

        config = configparser.ConfigParser()
        config.read(credentials_path)

        if not config.has_section(profile):
            raise Exception("CDP profile '{0}' not found".format(profile))

        if access_key is None:
            if config.has_option(profile, "cdp_access_key_id"):
                access_key = config.get(profile, "cdp_access_key_id")
            else:
                msg = "CDP profile '{0}' is missing 'cdp_access_key_id'"
                raise Exception(msg.format(profile))

        if private_key is None:
            if config.has_option(profile, "cdp_private_key"):
                private_key = config.get(profile, "cdp_private_key")
            else:
                msg = "CDP profile '{0}' is missing 'cdp_private_key'"
                raise Exception(msg.format(profile))

    return access_key, private_key


def create_canonical_request_string(
    method,
    uri,
    headers,
    auth_method,
):
    """
    Create a canonical request string from aspects of the request.
    """
    headers_of_interest = []
    for header_name in ["content-type", "x-altus-date"]:
        found = False
        for key in headers:
            key_lc = key.lower()
            if headers[key] is not None and key_lc == header_name:
                headers_of_interest.append(headers[key].strip())
                found = True
        if not found:
            headers_of_interest.append("")

    # Our signature verification with treat a query with no = as part of the
    # path, so we do as well. It appears to be a behavior left to the server
    # implementation, and python and our java servlet implementation disagree.
    uri_components = urlparse(uri)
    path = uri_components.path
    if not path:
        path = "/"
    if uri_components.query:
        path += "?" + uri_components.query

    canonical_string = method.upper() + "\n"
    canonical_string += "\n".join(headers_of_interest) + "\n"
    canonical_string += path + "\n"
    canonical_string += auth_method

    return canonical_string


def create_signature_string(
    canonical_string,
    private_key,
):
    """
    Create the string form of the digital signature of the canonical request
    string.
    """
    seed = b64decode(private_key)
    if len(seed) != 32:
        raise Exception("Not an Ed25519 private key!")
    parsed_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)

    signature = parsed_private_key.sign(
        canonical_string.encode("utf-8"),
    )
    return urlsafe_b64encode(signature).strip().decode("utf-8")


def create_encoded_authn_params_string(
    access_key,
    auth_method,
):
    """
    Create the base 64 encoded string of authentication parameters.
    """
    auth_params = OrderedDict()
    auth_params["access_key_id"] = access_key
    auth_params["auth_method"] = auth_method
    encoded_json = json.dumps(auth_params).encode("utf-8")
    return urlsafe_b64encode(encoded_json).strip()


def create_signature_header(
    encoded_authn_params,
    signature,
):
    """
    Combine the encoded authentication parameters string and signature string
    into the signature header value.
    """
    return "%s.%s" % (encoded_authn_params.decode("utf-8"), signature)


def make_signature_header(
    method: str,
    uri: str,
    headers: Dict[str, str],
    access_key: str,
    private_key: str,
):
    """
    Generates the value to be used for the x-altus-auth header in the service
    call.
    """
    if len(private_key) != 44:
        raise Exception("Only ed25519v1 keys are supported!")

    auth_method = "ed25519v1"

    canonical_string = create_canonical_request_string(
        method,
        uri,
        headers,
        auth_method,
    )
    signature = create_signature_string(canonical_string, private_key)
    encoded_authn_params = create_encoded_authn_params_string(
        access_key,
        auth_method,
    )
    signature_header = create_signature_header(encoded_authn_params, signature)
    return signature_header


class CdpError(Exception):
    """CDP Client Error Exception"""

    def __init__(self, msg: str, status: Optional[int] = None):
        """
        Initialize CDP error.

        Args:
            msg: Error message
            status: HTTP status code (if applicable)
        """
        super().__init__(msg)
        self.msg = msg
        self.status = status


class CdpClient:
    """Abstract base class for CDP API clients."""

    # Abstract HTTP methods that must be implemented by subclasses
    @abc.abstractmethod
    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP GET request."""
        pass

    @abc.abstractmethod
    def _post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP POST request."""
        pass

    @abc.abstractmethod
    def _put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP PUT request."""
        pass

    @abc.abstractmethod
    def _delete(self, path: str) -> Dict[str, Any]:
        """Execute HTTP DELETE request."""
        pass


class CdpConsumptionClient(CdpClient):
    """Abstract base class for CDP Consumption API clients."""

    # TODO Handle page size and pagination tokens (see cdpy library)

    def list_compute_usage_records(
        self,
        from_timestamp: str,
        to_timestamp: str,
    ) -> Dict[str, Any]:
        """List compute usage records within a time range."""
        return self._post(
            "/api/v1/consumption/listComputeUsageRecords",
            json_data={
                "fromTimestamp": from_timestamp,
                "toTimestamp": to_timestamp,
            },
        )


class AnsibleCdpClient(CdpConsumptionClient):
    """Ansible-based CDP client using native Ansible HTTP methods."""

    def __init__(
        self,
        module,
        base_url: str,
        access_key: str,
        private_key: str,
        timeout_seconds: int = 30,
        proxy_context_path: Optional[str] = None,
    ):
        """
        Initialize CDP client with Ansible module.

        Args:
            module: AnsibleModule instance
            base_url: Base URL for CDP API
            timeout_seconds: Request timeout in seconds
            proxy_context_path: Optional CDP proxy context path
        """
        self.module = module
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.proxy_context_path = proxy_context_path
        self.access_key = access_key
        self.private_key = private_key

        # Build headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Add CDP proxy headers if configured
        if self.proxy_context_path:
            self.headers["X-ProxyContextPath"] = self.proxy_context_path

        # Load credentials from module parameters or environment

    def _url(self, path: str) -> str:
        """Construct full URL from path."""
        return f"{self.base_url}/{path.strip('/')}"

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        max_retries: int = 3,
    ) -> Any:
        """
        Make HTTP request with retry logic using Ansible's fetch_url.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: URL parameters
            data: Form data
            json_data: JSON data
            max_retries: Maximum number of retry attempts

        Returns:
            Response data as dictionary or None for 204 responses

        Raises:
            AtlasError: On HTTP errors or connection failures
        """
        url = self._url(path)

        # Create the CDP signature headers
        self.headers["x-altus-date"] = formatdate(usegmt=True)
        self.headers["x-altus-auth"] = make_signature_header(
            method,
            url,
            self.headers,
            self.access_key,
            self.private_key,
        )

        # Add query parameters to URL if provided
        if params:
            # Handle list parameters (e.g., guid=[guid1, guid2])
            query_params = []
            for key, value in params.items():
                if isinstance(value, list):
                    for item in value:
                        query_params.append(f"{key}={item}")
                else:
                    query_params.append(f"{key}={value}")
            url = f"{url}?{'&'.join(query_params)}"

        # Prepare request body
        body = None
        if json_data is not None:
            body = json.dumps(json_data)
        elif data is not None:
            body = json.dumps(data)

        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                resp, info = fetch_url(
                    self.module,
                    url,
                    method=method,
                    headers=self.headers,
                    data=body,
                    timeout=self.timeout,
                )

                status_code = info["status"]

                # Handle authentication errors
                if status_code == 401:
                    raise CdpError(f"Unauthorized access to {path}", status=401)

                if status_code == 403:
                    raise CdpError(f"Forbidden access to {path}", status=403)

                # Handle success responses
                if 200 <= status_code < 300:
                    # 204 No Content - return None
                    if status_code == 204:
                        return None

                    if resp:
                        response_text = resp.read().decode("utf-8")
                        if response_text:
                            try:
                                return json.loads(response_text)
                            except json.JSONDecodeError:
                                return {"response": response_text}
                        else:
                            return {}
                    else:
                        return {}

                # Handle error responses
                error_message = f"HTTP {status_code} Error"
                if resp:
                    try:
                        error_data = json.loads(info.get("body"))
                        error_message = f"{error_data.get('errorMessage', 'Unknown error')} [{error_data.get('errorCode', 'Unknown code')}]"
                    except:
                        error_message = f"{info.get('msg', 'Unknown error')}"

                # Retry on server errors (5xx) or specific client errors
                if status_code >= 500 or status_code in [408, 429]:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 0.5s, 1s, 2s, 4s, 5s (max)
                        wait_time = min(0.5 * (2**attempt), 5)
                        time.sleep(wait_time)
                        last_error = CdpError(
                            f"{error_message} for {url}",
                            status=status_code,
                        )
                        continue

                raise CdpError(f"{error_message} for {url}", status=status_code)

            except CdpError:
                raise
            except Exception as e:
                # Retry on connection errors
                if attempt < max_retries - 1:
                    wait_time = min(0.5 * (2**attempt), 5)
                    time.sleep(wait_time)
                    last_error = CdpError(
                        f"Connection error for {url}: {str(e)}",
                    )
                    continue
                else:
                    raise CdpError(
                        f"Request failed after {max_retries} attempts for {url}: {str(e)}",
                    )

        # If we exhausted all retries
        if last_error:
            raise last_error
        raise CdpError(f"Request failed for {url}")

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP GET request."""
        return self._make_request("GET", path, params=params)

    def _post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP POST request."""
        return self._make_request("POST", path, data=data, json_data=json_data)

    def _put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP PUT request."""
        return self._make_request("PUT", path, data=data, json_data=json_data)

    def _delete(self, path: str) -> Dict[str, Any]:
        """Execute HTTP DELETE request."""
        return self._make_request("DELETE", path)
