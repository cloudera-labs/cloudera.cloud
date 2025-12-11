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
from typing import Any, Dict
from urllib.parse import urlencode
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
        return self.__dict__[attr]


def handle_response(func):
    """Decorator to handle HTTP response parsing and error squelching."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        squelch = kwargs.get('squelch', {})
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


class TestCdpClient(CdpClient):
    def __init__(self, endpoint: str, access_key:str, private_key:str, default_page_size: int = 100):
        super().__init__(default_page_size)
        self.request = Request(http_agent="TestCdpClient/1.0")
        self.endpoint = endpoint.rstrip("/")
        self.access_key = access_key
        self.private_key = private_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def set_credential_headers(self, method:str, url:str):
        self.headers["x-altus-date"] = formatdate(usegmt=True)
        self.headers["x-altus-auth"] = make_signature_header(
            method,
            url,
            self.headers,
            self.access_key,
            self.private_key,
        )

    @handle_response
    def get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Prepare query parameters
        if params:
            path += "?" + urlencode(params)

        url = f"{self.endpoint}/{path.strip('/')}"

        self.set_credential_headers(method="GET", url=url)

        return Request().get(
            url=url,
            headers=self.headers
        )
    
    @handle_response
    def post(self, path: str, data: Dict[str, Any] | None = None, json_data: Dict[str, Any] | None = None, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        # Prepare request body
        body = None
        if json_data is not None:
            body = json.dumps(json_data)
        elif data is not None:
            body = json.dumps(data)

        url = f"{self.endpoint}/{path.strip('/')}"

        self.set_credential_headers(method="POST", url=url)

        return Request().post(
            url=url,
            headers=self.headers,
            data=body,
        )
    
    def put(self, path: str, data: Dict[str, Any] | None = None, json_data: Dict[str, Any] | None = None, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        return {}
    
    def delete(self, path: str, squelch: Dict[int, Any] = {}) -> Dict[str, Any]:
        return {}
