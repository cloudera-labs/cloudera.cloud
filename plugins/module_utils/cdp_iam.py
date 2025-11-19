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
A REST client for the Cloudera on Cloud Platform (CDP) IAM API
"""

from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    RestClient,
    CdpClient,
)


class CdpIamClient(CdpClient):
    """CDP IAM API client."""

    def __init__(self, api_client: RestClient):
        """
        Initialize CDP IAM client.

        Args:
            api_client: RestClient instance for managing HTTP method calls
        """
        super().__init__(api_client=api_client)

    @RestClient.paginated()
    def list_groups(
        self,
        group_names: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List IAM groups with automatic pagination.

        Args:
            group_names: Optional list of group names or CRNs to filter by
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Response with automatic pagination handling containing groups list
        """
        json_data: Dict[str, Any] = {}

        # Add group names filter if provided
        if group_names is not None:
            json_data["groupNames"] = group_names

        # Add pagination parameters if provided
        # Note: IAM API uses "startingToken" for requests, but decorator uses "pageToken"
        if pageToken is not None:
            json_data["startingToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.post(
            "/api/v1/iam/listGroups",
            json_data=json_data,
        )
