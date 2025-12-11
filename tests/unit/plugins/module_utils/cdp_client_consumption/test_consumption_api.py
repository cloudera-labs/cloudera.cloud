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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_consumption import (
    CdpConsumptionClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

FROM_TIMESTAMP = "2025-10-31T00:00:00Z"
TO_TIMESTAMP = "2025-10-31T12:00:00Z"


class TestCdpConsumptionClient:
    """Unit tests for CdpConsumptionClient."""

    def test_list_compute_usage_records(self, mocker):
        """Test listing compute usage records."""

        # Mock response data
        mock_response = {
            "records": [
                {"id": "record1", "usage": 100},
                {"id": "record2", "usage": 200},
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpConsumptionClient instance
        client = CdpConsumptionClient(api_client=api_client)

        response = client.list_compute_usage_records(
            from_timestamp=FROM_TIMESTAMP,
            to_timestamp=TO_TIMESTAMP,
        )

        assert "records" in response
        assert len(response["records"]) == 2
        assert response["records"][0]["id"] == "record1"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/consumption/listComputeUsageRecords",
            json_data={
                "fromTimestamp": FROM_TIMESTAMP,
                "toTimestamp": TO_TIMESTAMP,
                "pageSize": 100,
            },
        )

    def test_list_compute_usage_records_pagination(self, mocker):
        """Test listing compute usage records."""

        # Mock response data
        mock_response1 = {
            "records": [
                {"id": "record1", "usage": 100},
                {"id": "record2", "usage": 200},
            ],
            "nextPageToken": "token123",
        }

        mock_response2 = {
            "records": [
                {"id": "record3", "usage": 300},
                {"id": "record4", "usage": 400},
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.side_effect = [mock_response1, mock_response2]

        # Create the CdpConsumptionClient instance
        client = CdpConsumptionClient(api_client=api_client)

        response = client.list_compute_usage_records(
            from_timestamp=FROM_TIMESTAMP,
            to_timestamp=TO_TIMESTAMP,
        )

        assert "records" in response
        assert len(response["records"]) == 4
        assert response["records"][0]["id"] == "record1"
        assert response["records"][2]["id"] == "record3"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_has_calls(
            [
                mocker.call(
                    "/api/v1/consumption/listComputeUsageRecords",
                    json_data={
                        "fromTimestamp": FROM_TIMESTAMP,
                        "toTimestamp": TO_TIMESTAMP,
                        "pageSize": 100,
                    },
                ),
                mocker.call(
                    "/api/v1/consumption/listComputeUsageRecords",
                    json_data={
                        "fromTimestamp": FROM_TIMESTAMP,
                        "toTimestamp": TO_TIMESTAMP,
                        "pageSize": 100,
                        "pageToken": "token123",
                    },
                ),
            ],
        )


@pytest.mark.integration_api
class TestCdpConsumptionClientIntegration:
    """Integration tests for CdpConsumptionClient."""

    def test_list_compute_usage_records(self, api_client):
        """Test listing compute usage records."""

        # Create the CdpConsumptionClient instance
        client = CdpConsumptionClient(api_client=api_client)

        response = client.list_compute_usage_records(
            from_timestamp=FROM_TIMESTAMP,
            to_timestamp=TO_TIMESTAMP,
        )

        assert "records" in response
        assert len(response["records"]) > 0
        assert isinstance(response["records"][0], dict)
