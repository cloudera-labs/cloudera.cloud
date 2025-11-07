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
A REST client for the Cloudera on Cloud Platform (CDP) Consumption API
"""

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    RestClient,
    CdpClient,
)


class CdpConsumptionClient(CdpClient):
    """CDP Consumption API client."""

    def __init__(self, api_client: RestClient):
        """
        Initialize CDP Consumption client.

        Args:
            api_client: RestClient instance for managing HTTP method calls
        """
        super().__init__(api_client=api_client)

    @RestClient.paginated()
    def list_compute_usage_records(
        self,
        from_timestamp: str,
        to_timestamp: str,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List compute usage records within a time range.

        Args:
            from_timestamp: Start timestamp for usage records
            to_timestamp: End timestamp for usage records
            pageToken: Token for pagination (automatically handled by decorator)
            pageSize: Page size for pagination (automatically handled by decorator)

        Returns:
            Usage records response with automatic pagination handling
        """
        json_data: Dict[str, Any] = {
            "fromTimestamp": from_timestamp,
            "toTimestamp": to_timestamp,
        }

        # Add pagination parameters if provided
        if pageToken is not None:
            json_data["pageToken"] = pageToken
        if pageSize is not None:
            json_data["pageSize"] = pageSize

        return self.post(
            "/api/v1/consumption/listComputeUsageRecords",
            json_data=json_data,
        )
