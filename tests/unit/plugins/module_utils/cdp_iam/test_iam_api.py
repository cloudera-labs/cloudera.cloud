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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

SAMPLE_USERS = [
    "crn:cdp:iam:us-west-1:altus:user:alice@example.com",
    "crn:cdp:iam:us-west-1:altus:user:bob@example.com",
]
SAMPLE_MACHINE_USERS = [
    "crn:cdp:iam:us-west-1:altus:machineUser:service-account-1",
    "crn:cdp:iam:us-west-1:altus:machineUser:service-account-2",
]
SAMPLE_ROLES = [
    "crn:cdp:iam:us-west-1:altus:role:PowerUser",
    "crn:cdp:iam:us-west-1:altus:role:EnvironmentCreator",
    "crn:cdp:iam:us-west-1:altus:role:DFCatalogAdmin",
]
SAMPLE_RESOURCE_ROLES = [
    {
        "resource": "crn:cdp:environments:us-west-1:altus:environment:dev-env",
        "role": "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser",
    },
    {
        "resource": "crn:cdp:datalake:us-west-1:altus:datalake:prod-dl",
        "role": "crn:cdp:iam:us-west-1:altus:resourceRole:DataLakeAdmin",
    },
]


class TestCdpIamClient:
    """Unit tests for CdpIamClient group management methods."""

    def test_list_groups_no_filter(self, mocker):
        """Test listing all IAM groups without filtering."""

        # Mock response data
        mock_response = {
            "groups": [
                {
                    "groupName": "data-engineers",
                    "crn": "crn:cdp:iam:us-west-1:altus:group:data-engineers",
                    "creationDate": "2024-01-15T10:30:00.000Z",
                    "syncMembershipOnUserLogin": True,
                },
                {
                    "groupName": "data-scientists",
                    "crn": "crn:cdp:iam:us-west-1:altus:group:data-scientists",
                    "creationDate": "2024-01-20T14:45:00.000Z",
                    "syncMembershipOnUserLogin": False,
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)
        response = client.list_groups()

        # Validate the response
        assert "groups" in response
        assert len(response["groups"]) == 2
        assert response["groups"][0]["groupName"] == "data-engineers"
        assert response["groups"][1]["syncMembershipOnUserLogin"] == False

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            json_data={
                "pageSize": 100,
            },
            squelch={404: {}},
        )

    def test_list_groups_with_filter(self, mocker):
        """Test listing IAM groups filtered by name."""

        # Mock response data
        mock_response = {
            "groups": [
                {
                    "groupName": "data-engineers",
                    "crn": "crn:cdp:iam:us-west-1:altus:group:data-engineers",
                    "creationDate": "2024-01-15T10:30:00.000Z",
                    "syncMembershipOnUserLogin": True,
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.list_groups(group_names=["data-engineers"])

        assert "groups" in response
        assert len(response["groups"]) == 1
        assert response["groups"][0]["groupName"] == "data-engineers"

        # Verify that the method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            json_data={
                "pageSize": 100,
                "groupNames": ["data-engineers"],
            },
            squelch={404: {}},
        )

    def test_create_group(self, mocker):
        """Test creating a new IAM group."""

        # Mock response data
        mock_response = {
            "group": {
                "groupName": "new-team",
                "crn": "crn:cdp:iam:us-west-1:altus:group:new-team",
                "creationDate": "2024-02-01T09:00:00.000Z",
                "syncMembershipOnUserLogin": True,
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.create_group(
            group_name="new-team",
            sync_membership_on_user_login=True,
        )

        assert "group" in response
        assert response["group"]["groupName"] == "new-team"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/createGroup",
            json_data={
                "groupName": "new-team",
                "syncMembershipOnUserLogin": True,
            },
        )

    def test_delete_group(self, mocker):
        """Test deleting an IAM group."""

        # Mock response data (delete operations typically return empty)
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.delete_group(group_name="old-team")

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/deleteGroup",
            json_data={
                "groupName": "old-team",
            },
        )

    def test_update_group(self, mocker):
        """Test updating an IAM group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.update_group(
            group_name="existing-team",
            sync_membership_on_user_login=False,
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/updateGroup",
            json_data={
                "groupName": "existing-team",
                "syncMembershipOnUserLogin": False,
            },
        )

    def test_list_group_members(self, mocker):
        """Test listing group members."""

        # Mock response data
        mock_response = {
            "memberCrns": SAMPLE_USERS + [SAMPLE_MACHINE_USERS[0]],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.list_group_members(group_name="data-engineers")

        assert "memberCrns" in response
        assert len(response["memberCrns"]) == 3

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroupMembers",
            json_data={
                "pageSize": 100,
                "groupName": "data-engineers",
            },
        )

    def test_add_user_to_group(self, mocker):
        """Test adding a user to a group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.add_user_to_group(
            user_id=SAMPLE_USERS[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/addUserToGroup",
            json_data={
                "userId": SAMPLE_USERS[0],
                "groupName": "data-engineers",
            },
        )

    def test_remove_user_from_group(self, mocker):
        """Test removing a user from a group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.remove_user_from_group(
            user_id=SAMPLE_USERS[1],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/removeUserFromGroup",
            json_data={
                "userId": SAMPLE_USERS[1],
                "groupName": "data-engineers",
            },
        )

    def test_add_machine_user_to_group(self, mocker):
        """Test adding a machine user to a group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.add_machine_user_to_group(
            machine_user_name=SAMPLE_MACHINE_USERS[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/addMachineUserToGroup",
            json_data={
                "machineUserName": SAMPLE_MACHINE_USERS[0],
                "groupName": "data-engineers",
            },
        )

    def test_remove_machine_user_from_group(self, mocker):
        """Test removing a machine user from a group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.remove_machine_user_from_group(
            machine_user_name=SAMPLE_MACHINE_USERS[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/removeMachineUserFromGroup",
            json_data={
                "machineUserName": SAMPLE_MACHINE_USERS[0],
                "groupName": "data-engineers",
            },
        )

    def test_assign_group_role(self, mocker):
        """Test assigning a role to a group."""

        # Mock response data
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpIamClient instance
        client = CdpIamClient(api_client=api_client)

        response = client.assign_group_role(
            group_name="data-engineers",
            role=SAMPLE_ROLES[0],
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/iam/assignGroupRole",
            json_data={
                "groupName": "data-engineers",
                "role": SAMPLE_ROLES[0],
            },
        )
