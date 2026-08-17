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

import os

import json
import pytest
import time
import warnings

from email.utils import formatdate
from functools import wraps
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError, URLError
from http.client import HTTPResponse
from ansible.module_utils.urls import Request

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    make_signature_header,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


def required_or_skip(var: str) -> str:
    """Return an environment variable's value, skipping the test when it is unset."""
    value = os.getenv(var)
    if not value:
        pytest.skip(f"{var} not set; skipping Data Warehouse test")
    return value


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    def __init__(self, kwargs):
        super(AnsibleFailJson, self).__init__(
            kwargs.get("msg", "General module failure"),
        )
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    def __init__(self, kwargs):
        super(AnsibleExitJson, self).__init__(
            kwargs.get("msg", "General module success"),
        )
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


HIVE_CONNECTOR_CONFIG = {
    "connector.name": "hive",
    "fs.cache.directories": "/data/trino/caches/hive",
    "fs.cache.enabled": "true",
    "fs.cache.max-disk-usage-percentages": "30",
    "fs.cache.preferred-hosts-count": "2",
    "fs.cache.ttl": "7d",
    "hive.allow-drop-table": "true",
    "hive.collect-column-statistics-on-write": "false",
    "hive.metastore.uri": "thrift://metastore-service.{{ .Values.warehouseId }}.svc.cluster.local:9083",
    "hive.non-managed-table-writes-enabled": "true",
    "hive.security": "{{ .Values.authorizationMode }}",
    "hive.temporary-staging-directory-enabled": "{{ if and .Values.isPrivateCloud .Values.ozone .Values.ozone.enabled }}false{{ else }}true{{ end }}",
    "ranger.audit_config": "/etc/trino/ranger-hive-audit.xml",
    "ranger.hadoop_config": "/etc/trino/core-site.xml",
    "ranger.policy_mgr_ssl_config": "/etc/trino/ranger-policymgr-ssl.xml",
    "ranger.security_config": "/etc/trino/ranger-hive-security.xml",
    "ranger.service_name": "{{ .Values.rangerHiveSvcName }}",
}

ICEBERG_CONNECTOR_CONFIG = {
    "connector.name": "iceberg",
    "fs.cache.directories": "/data/trino/caches/",  # Needs the "catalog" name appended to this root path
    "fs.cache.enabled": "true",
    "fs.cache.max-disk-usage-percentages": "30",
    "fs.cache.preferred-hosts-count": "2",
    "fs.cache.ttl": "7d",
    "hive.metastore.uri": "thrift://metastore-service.{{ .Values.warehouseId }}.svc.cluster.local:9083",
    "iceberg.catalog.type": "hive_metastore",
    "iceberg.security": "{{ .Values.authorizationMode }}",
    "ranger.audit_config": "/etc/trino/ranger-hive-audit.xml",
    "ranger.hadoop_config": "/etc/trino/core-site.xml",
    "ranger.policy_mgr_ssl_config": "/etc/trino/ranger-policymgr-ssl.xml",
    "ranger.security_config": "/etc/trino/ranger-hive-security.xml",
    "ranger.service_name": "{{ .Values.rangerHiveSvcName }}",
}


# Connection-level failures worth retrying. HTTPError (a URLError subclass) is
# deliberately excluded: HTTP status codes are semantic, not transient, and each
# verb method handles them itself (squelch, 308 redirect, etc.).
_TRANSIENT_ERRORS = (URLError, OSError, TimeoutError)


def with_retry(func):
    """Retry a CdpTestClient HTTP verb on transient failures with exponential backoff.

    Applies the retry behavior originally inlined in C(get()) to every verb:
    up to C(self.max_retries) attempts, backoff of C(0.5 * 2**attempt) seconds
    capped at 5s. Only transient (connection/OS/timeout) errors are retried;
    C(HTTPError) is re-raised immediately so the wrapped method's own status
    handling is preserved.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(self, *args, **kwargs)
            except HTTPError:
                raise
            except _TRANSIENT_ERRORS as e:
                if attempt < self.max_retries - 1:
                    wait_time = min(0.5 * (2**attempt), 5)
                    warnings.warn(
                        f"{func.__name__} request failed: {e}. "
                        f"Retrying in {wait_time:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})...",
                    )
                    time.sleep(wait_time)
                    continue
                raise

    return wrapper


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
    if "tags" in request_data:
        tags_json = '{ "tags": ' + json.dumps(request_data["tags"]) + "}"
        headers["Flow-Definition-Tags"] = quote(tags_json)

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


class CdpTestClient(CdpClient):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        private_key: str,
        default_page_size: int = 100,
        max_retries: int = 3,
    ):
        super().__init__(default_page_size)
        self.request = Request(http_agent="TestCdpClient/1.0")
        self.endpoint = endpoint.rstrip("/")
        self.access_key = access_key
        self.private_key = private_key
        self.cookies = {}  # Cookie storage for XSRF tokens (needed for /dfx endpoints)
        self.max_retries = max_retries

    @with_retry
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

    @with_retry
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

    @with_retry
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

    @with_retry
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
