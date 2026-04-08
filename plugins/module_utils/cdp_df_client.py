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
