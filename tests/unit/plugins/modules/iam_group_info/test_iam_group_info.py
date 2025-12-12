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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


class TestCdpIamClient:
    """Unit tests for CdpIamClient."""

    def test_list_groups_no_filter(self, mocker):
        """Test listing all IAM groups."""

        # Mock response data
        mock_response = {
            "groups": [
                {
                    "groupName": "group1",
                    "crn": "crn:cdp:iam:us-west-1:account:group:group1",
                    "creationDate": "2025-01-01T00:00:00Z",
                },
                {
                    "groupName": "group2",
                    "crn": "crn:cdp:iam:us-west-1:account:group:group2",
                    "creationDate": "2025-01-02T00:00:00Z",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.list_groups()

        assert "groups" in response
        assert len(response["groups"]) == 2
        assert response["groups"][0]["groupName"] == "group1"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            json_data={"pageSize": 100},
            squelch={404: {}},
        )

    def test_list_groups_with_filter(self, mocker):
        """Test listing IAM groups with group name filter."""

        # Mock response data
        mock_response = {
            "groups": [
                {
                    "groupName": "specific-group",
                    "crn": "crn:cdp:iam:us-west-1:account:group:specific-group",
                    "creationDate": "2025-01-01T00:00:00Z",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.list_groups(group_names=["specific-group"])

        assert "groups" in response
        assert len(response["groups"]) == 1
        assert response["groups"][0]["groupName"] == "specific-group"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            json_data={"groupNames": ["specific-group"], "pageSize": 100},
            squelch={404: {}},
        )


@pytest.mark.integration_api
class TestCdpIamClientIntegration:
    """Integration tests for CdpIamClient."""

    def test_list_groups(self, ansible_cdp_client):
        """Integration test for listing IAM groups."""

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=ansible_cdp_client)

        response = client.list_groups()

        assert "groups" in response
        assert len(response["groups"]) > 0
        assert isinstance(response["groups"][0], dict)
