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
CDP Data Service Workload Client

This module provides a universal client for CDP Data Service workload APIs
(DataFlow, Data Engineering, Data Warehouse, Machine Learning, etc.)

Data service workload APIs use JWT Bearer token authentication instead of
Ed25519 signature authentication used by the control plane APIs.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union

from ansible.module_utils.urls import fetch_url
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


class DataServiceClient(CdpClient):
    """
    Universal CDP Data Service Workload client using Bearer token authentication.
    
    This client is used for all CDP Data Service workload APIs including:
    - DataFlow (DF)
    - Data Engineering (DE)
    - Data Warehouse (DW)
    - Machine Learning (ML)
    - Operational Database (OpDB)
    
    These services require JWT Bearer token authentication instead of Ed25519 
    signatures used by the control plane. Each service has its own base URL 
    which is discovered through control plane APIs (e.g., initiateDeployment)
    or IAM generateWorkloadAuthToken API.
    
    Key Features:
    - Bearer token authentication
    - XSRF/CSRF token handling via cookies
    - Automatic cookie management
    - Retry logic for transient failures
    """

    def __init__(
        self,
        module,
        base_url: str,
        access_token: str,
        timeout_seconds: int = 60,
        default_page_size: int = 100,
    ):
        """
        Initialize CDP Data Service Workload client.

        Args:
            module: Ansible module instance
            base_url: Base URL for the workload API (from initiateDeployment or generateWorkloadAuthToken)
            access_token: JWT Bearer token (from generateWorkloadAuthToken)
            timeout_seconds: HTTP request timeout in seconds
            default_page_size: Default page size for paginated requests
        """
        super().__init__(default_page_size=default_page_size)
        self.module = module
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout_seconds = timeout_seconds
        
        # Cookie storage for XSRF tokens
        self.cookies = {}
        
        # Standard headers for workload APIs
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _url(self, path: str) -> str:
        """Construct full URL from base URL and path."""
        return f"{self.base_url}/{path.lstrip('/')}"

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
        Make HTTP request to workload API using Bearer token authentication.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            params: Query parameters
            data: Form data
            json_data: JSON data
            max_retries: Maximum number of retries
            squelch: Dict mapping status codes to return values

        Returns:
            Parsed JSON response

        Raises:
            CdpError: On request failure
        """
        url = self._url(path)
        headers = self.headers.copy()
        
        # Add cookies to request if we have any
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            headers["Cookie"] = cookie_str
            
            # Also add XSRF token as header if present (required for POST/PUT/DELETE)
            if "XSRF-TOKEN" in self.cookies:
                headers["X-XSRF-TOKEN"] = self.cookies["XSRF-TOKEN"]

        # Prepare request body
        body = None
        if json_data is not None:
            body = json.dumps(json_data)
        elif data is not None:
            body = json.dumps(data)

        # Set validate_certs in module.params (fetch_url reads from there)
        # Save original value to restore later
        original_validate_certs = self.module.params.get("validate_certs")
        self.module.params["validate_certs"] = self.module.params.get("endpoint_tls", True)

        last_error = None
        try:
            for attempt in range(max_retries):
                try:
                    resp, info = fetch_url(
                        self.module,
                        url,
                        data=body,
                        headers=headers,
                        method=method,
                        timeout=self.timeout_seconds,
                    )

                    status_code = info.get("status", -1)
                    
                    # Extract and store cookies from response
                    set_cookie = info.get("set-cookie")
                    if set_cookie:
                        # Parse Set-Cookie header(s) - can be string or list
                        cookie_headers = [set_cookie] if isinstance(set_cookie, str) else set_cookie
                        for cookie_header in cookie_headers:
                            # Extract cookie name and value (before first semicolon)
                            if "=" in cookie_header:
                                cookie_part = cookie_header.split(";")[0]
                                name, value = cookie_part.split("=", 1)
                                self.cookies[name.strip()] = value.strip()

                    # Check if we should squelch this status code
                    if status_code in squelch:
                        return squelch[status_code]

                    # Handle connection errors (status -1)
                    if status_code == -1:
                        error_msg = info.get("msg", "Connection error")
                        if attempt < max_retries - 1:
                            wait_time = min(0.5 * (2**attempt), 5)
                            time.sleep(wait_time)
                            last_error = CdpError(
                                f"{error_msg} for {url}",
                                status=status_code,
                            )
                            continue
                        raise CdpError(f"{error_msg} for {url}", status=status_code)
                    
                    # Handle success responses (200-299)
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

                    # Handle error responses (400+)
                    error_message = f"HTTP {status_code} Error"
                    
                    # Try to parse error from response body (in info['body'])
                    try:
                        error_body = info.get("body")
                        if error_body:
                            error_data = json.loads(error_body)
                            
                            if "message" in error_data:
                                error_message = error_data["message"]
                            elif "error" in error_data:
                                error_message = error_data["error"]
                            elif "errorMessages" in error_data:
                                error_messages = error_data["errorMessages"]
                                if isinstance(error_messages, list):
                                    error_message = " ".join(error_messages)
                                else:
                                    error_message = str(error_messages)
                            else:
                                error_message = error_data.get("errorMessage", "Unknown error")
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
                                f"{error_message} for {url}",
                                status=status_code,
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
        finally:
            # Always restore original validate_certs
            if original_validate_certs is not None:
                self.module.params["validate_certs"] = original_validate_certs

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP GET request."""
        return self._make_request("GET", path, params=params)

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        squelch: Dict[int, Any] = {},
    ) -> Dict[str, Any]:
        """Execute HTTP POST request."""
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
        """Execute HTTP PUT request."""
        return self._make_request(
            "PUT",
            path,
            data=data,
            json_data=json_data,
            squelch=squelch,
        )

    def delete(self, path: str, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        """Execute HTTP DELETE request."""
        return self._make_request("DELETE", path, squelch=squelch)

