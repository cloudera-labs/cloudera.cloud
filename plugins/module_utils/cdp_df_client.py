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
from email.utils import formatdate
from ansible.module_utils.urls import fetch_url

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
    CdpError,
    make_signature_header,
)


class CdpDfApiClient(AnsibleCdpClient):
    """
    DataFlow-specific CDP API client that extends AnsibleCdpClient.
    
    This client handles DataFlow-specific requirements such as:
    - 308 Permanent Redirect handling for flow import operations
    - DataFlow extension format transformation (metadata in headers, content in body)
    """

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
                    request_data["description"]
                )
            if "comments" in request_data:
                headers["Flow-Definition-Comments"] = quote(request_data["comments"])
            if "collectionCrn" in request_data:
                headers["Flow-Definition-Collection-Identifier"] = quote(
                    request_data["collectionCrn"]
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

    def _handle_308_redirect(
        self,
        redirect_url: str,
        method: str,
        body: Optional[str],
        headers: Dict[str, str],
    ) -> tuple:
        """
        Handle 308 Permanent Redirect for DataFlow operations.
        
        Args:
            redirect_url: Full redirect URL
            method: HTTP method
            body: Request body
            headers: Request headers
            
        Returns:
            Tuple of (resp, info) from fetch_url
        """
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
                body, redirect_headers
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
        Make HTTP request with DataFlow-specific 308 redirect handling.
        
        Extends the base _make_request to handle 308 redirects that are
        specific to DataFlow flow import operations.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Path on the API endpoint
            params: URL query parameters
            data: Form data
            json_data: JSON data
            max_retries: Maximum number of retry attempts
            squelch: Dictionary of HTTP status codes to squelch with default return values

        Returns:
            Response data as dictionary or None for 204 responses

        Raises:
            AnsibleModule.fail_json: On HTTP errors or connection failures
        """
        try:
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

            # Populate validate_certs from endpoint_tls
            self.module.params["validate_certs"] = self.module.params.get(
                "endpoint_tls",
                True,
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

                    # Handle 308 Permanent Redirect (DataFlow specific)
                    if status_code == 308:
                        redirect_url = info.get("location")
                        if not redirect_url:
                            raise CdpError(
                                f"308 redirect received but no location header for {url}"
                            )
                        
                        resp, info = self._handle_308_redirect(
                            redirect_url,
                            method,
                            body,
                            self.headers,
                        )
                        status_code = info["status"]

                    # Handle authentication errors
                    if status_code == 401:
                        raise CdpError(f"Unauthorized access to {path}", status=401)

                    if status_code == 403:
                        raise CdpError(f"Forbidden access to {path}", status=403)

                    if status_code in squelch:
                        self.module.warn(
                            f"Squelched error {status_code} for {url}",
                        )
                        return squelch[status_code]

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

                    try:
                        error_body = info.get("body")
                        if error_body:
                            error_data = json.loads(error_body)
                            error_message = error_data.get(
                                "message", error_data.get("error", error_message)
                            )
                        else:
                            error_message = info.get("msg", "Unknown error")
                    except:
                        error_message = info.get("msg", "Unknown error")

                    # Retry on server errors (5xx) or specific client errors
                    if status_code >= 500 or status_code in [408, 429]:
                        if attempt < max_retries - 1:
                            wait_time = min(0.5 * (2**attempt), 5)
                            time.sleep(wait_time)
                            last_error = CdpError(
                                f"{error_message} for {url} (attempt {attempt + 1}/{max_retries})"
                            )
                            continue

                    raise CdpError(f"{error_message} [{status_code}] for {url}")

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
        except Exception as e:
            self.module.fail_json(msg=str(e))
