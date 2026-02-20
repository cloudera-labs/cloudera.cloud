# -*- coding: utf-8 -*-
#
# Copyright 2025 Cloudera, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from email.utils import formatdate
from functools import wraps
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError
from http.client import HTTPResponse
from ansible.module_utils.urls import Request

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    make_signature_header,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    def __init__(self, kwargs):
        super(AnsibleFailJson, self).__init__(
            kwargs.get("msg", "General module failure"),
        )
        self.__dict__.update(kwargs)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    def __init__(self, kwargs):
        super(AnsibleExitJson, self).__init__(
            kwargs.get("msg", "General module success"),
        )
        self.__dict__.update(kwargs)

    def __getattr__(self, attr):
        return self.__dict__.get(attr, None)


def handle_response(func):
    """Decorator to handle HTTP response parsing and error squelching."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        squelch = kwargs.get("squelch", {})
        try:
            response: HTTPResponse = func(*args, **kwargs)
            if response:
                response_text = response.read().decode("utf-8")
                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"response": response_text}
                else:
                    return {}
            else:
                return {}
        except HTTPError as e:
            if e.code in squelch:
                return squelch[e.code]
            else:
                raise

    return wrapper


def build_flow_import_headers(request_data: Dict[str, Any]) -> Dict[str, str]:
    """Build headers for DataFlow flow import (following cdpcli extension pattern)."""
    from urllib.parse import quote

    headers = {}
    if "name" in request_data:
        headers["Flow-Definition-Name"] = quote(request_data["name"])
    if "description" in request_data:
        headers["Flow-Definition-Description"] = quote(request_data["description"])
    if "comments" in request_data:
        headers["Flow-Definition-Comments"] = quote(request_data["comments"])
    if "collectionCrn" in request_data:
        headers["Flow-Definition-Collection-Identifier"] = quote(
            request_data["collectionCrn"],
        )

    return headers


def set_credential_headers(
    method: str,
    url: str,
    access_key: str,
    private_key: str,
) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    headers["x-altus-date"] = formatdate(usegmt=True)
    headers["x-altus-auth"] = make_signature_header(
        method,
        url,
        headers,
        access_key,
        private_key,
    )

    return headers


def prepare_body(
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    if json_data is not None:
        return json.dumps(json_data)
    elif data is not None:
        return json.dumps(data)
    else:
        return None


class TestCdpClient(CdpClient):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        private_key: str,
        default_page_size: int = 100,
    ):
        super().__init__(default_page_size)
        self.request = Request(http_agent="TestCdpClient/1.0")
        self.endpoint = endpoint.rstrip("/")
        self.access_key = access_key
        self.private_key = private_key
        self.cookies = {}  # Cookie storage for XSRF tokens (needed for /dfx endpoints)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Prepare query parameters
        if params:
            path += "?" + urlencode(params)

        url = f"{self.endpoint}/{path.strip('/')}"

        return Request().get(
            url=url,
            headers=set_credential_headers(
                method="GET",
                url=url,
                access_key=self.access_key,
                private_key=self.private_key,
            ),
        )

    def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        squelch: Dict[int, Any] = {},
    ) -> Dict[str, Any]:
        url = f"{self.endpoint}/{path.strip('/')}"
        body = prepare_body(data, json_data)

        try:
            response = Request().post(
                url=url,
                headers=set_credential_headers(
                    method="POST",
                    url=url,
                    access_key=self.access_key,
                    private_key=self.private_key,
                ),
                data=body,
            )
            # Parse successful response
            response_text = response.read().decode("utf-8")
            return json.loads(response_text) if response_text else {}

        except HTTPError as e:
            # Handle 308 Permanent Redirect for DataFlow flow imports
            if e.code == 308:
                redirect_url = e.headers.get("Location") or e.headers.get("location")
                if not redirect_url:
                    raise

                # Parse redirect URL to get path for signature

                parsed = urlparse(redirect_url)
                redirect_path = parsed.path
                if parsed.query:
                    redirect_path += "?" + parsed.query

                # Check if this is a DataFlow flow import (needs header transformation)
                is_df_flow_import = "/catalog/flows" in redirect_path

                redirect_body = body
                redirect_headers = set_credential_headers(
                    method="POST",
                    url=redirect_path,
                    access_key=self.access_key,
                    private_key=self.private_key,
                )

                # Transform body to DataFlow format if needed
                if is_df_flow_import and body:
                    try:
                        request_data = json.loads(body)
                        # Build custom headers (following cdpcli extension pattern)
                        redirect_headers.update(build_flow_import_headers(request_data))
                        # Body becomes raw flow content
                        redirect_body = request_data.get("file", "")
                    except (json.JSONDecodeError, KeyError):
                        pass

                # Follow redirect
                redirect_response = Request().open(
                    method="POST",
                    url=redirect_url,
                    headers=redirect_headers,
                    data=redirect_body.encode("utf-8") if redirect_body else None,
                )

                # Parse redirect response
                response_text = redirect_response.read().decode("utf-8")
                return json.loads(response_text) if response_text else {}

            elif e.code in squelch:
                return squelch[e.code]
            else:
                raise

    def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        squelch: Dict[int, Any] = {},
    ) -> Dict[str, Any]:
        url = f"{self.endpoint}/{path.strip('/')}"

        return Request().put(
            url=url,
            headers=set_credential_headers(
                method="PUT",
                url=url,
                access_key=self.access_key,
                private_key=self.private_key,
            ),
            data=prepare_body(data, json_data),
        )

    def delete(self, path: str, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        url = f"{self.endpoint}/{path.strip('/')}"

        return Request().delete(
            url=url,
            headers=set_credential_headers(
                method="DELETE",
                url=url,
                access_key=self.access_key,
                private_key=self.private_key,
            ),
        )
