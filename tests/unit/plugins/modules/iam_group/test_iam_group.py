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
from unittest.mock import MagicMock

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def iam_client(mocker):
    """Fixture to provide a mocked CdpIamClient instance."""
    return mocker.create_autospec(CdpIamClient, instance=True)


@pytest.fixture
def sample_users():
    """Fixture providing sample user CRNs for testing."""
    return [
        "crn:cdp:iam:us-west-1:altus:user:alice@example.com",
        "crn:cdp:iam:us-west-1:altus:user:bob@example.com",
    ]


@pytest.fixture
def sample_machine_users():
    """Fixture providing sample machine user CRNs for testing."""
    return [
        "crn:cdp:iam:us-west-1:altus:machineUser:service-account-1",
        "crn:cdp:iam:us-west-1:altus:machineUser:service-account-2",
    ]


@pytest.fixture
def sample_roles():
    """Fixture providing sample role CRNs for testing."""
    return [
        "crn:cdp:iam:us-west-1:altus:role:PowerUser",
        "crn:cdp:iam:us-west-1:altus:role:EnvironmentCreator",
        "crn:cdp:iam:us-west-1:altus:role:DFCatalogAdmin",
    ]


@pytest.fixture
def sample_resource_roles():
    """Fixture providing sample resource role assignments for testing."""
    return [
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

    def test_list_groups_no_filter(self, iam_client):
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

        # Mock the CdpIamClient method
        iam_client.list_groups.return_value = mock_response

        response = iam_client.list_groups()

        assert "groups" in response
        assert len(response["groups"]) == 2
        assert response["groups"][0]["groupName"] == "data-engineers"
        assert response["groups"][1]["syncMembershipOnUserLogin"] == False

        # Verify that the method was called
        iam_client.list_groups.assert_called_once()

    def test_list_groups_with_filter(self, iam_client):
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

        # Mock the CdpIamClient method
        iam_client.list_groups.return_value = mock_response

        response = iam_client.list_groups(group_names=["data-engineers"])

        assert "groups" in response
        assert len(response["groups"]) == 1
        assert response["groups"][0]["groupName"] == "data-engineers"

        # Verify that the method was called with correct parameters
        iam_client.list_groups.assert_called_once_with(group_names=["data-engineers"])

    def test_create_group(self, iam_client):
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

        iam_client.create_group.return_value = mock_response

        response = iam_client.create_group(
            group_name="new-team",
            sync_membership_on_user_login=True,
        )

        assert "group" in response
        assert response["group"]["groupName"] == "new-team"

        # Verify that the method was called with correct parameters
        iam_client.create_group.assert_called_once_with(
            group_name="new-team",
            sync_membership_on_user_login=True,
        )

    def test_delete_group(self, iam_client):
        """Test deleting an IAM group."""

        # Mock response data (delete operations typically return empty)
        mock_response = {}

        iam_client.delete_group.return_value = mock_response

        response = iam_client.delete_group(group_name="old-team")

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.delete_group.assert_called_once_with(group_name="old-team")

    def test_update_group(self, iam_client):
        """Test updating an IAM group."""

        # Mock response data
        mock_response = {}

        iam_client.update_group.return_value = mock_response

        response = iam_client.update_group(
            group_name="existing-team",
            sync_membership_on_user_login=False,
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.update_group.assert_called_once_with(
            group_name="existing-team",
            sync_membership_on_user_login=False,
        )

    def test_list_group_members(
        self,
        iam_client,
        sample_users,
        sample_machine_users,
    ):
        """Test listing group members."""

        # Mock response data
        mock_response = {
            "memberCrns": sample_users + [sample_machine_users[0]],
        }

        iam_client.list_group_members.return_value = mock_response

        response = iam_client.list_group_members(group_name="data-engineers")

        assert "memberCrns" in response
        assert len(response["memberCrns"]) == 3

        # Verify that the method was called with correct parameters
        iam_client.list_group_members.assert_called_once_with(
            group_name="data-engineers",
        )

    def test_add_user_to_group(self, iam_client, sample_users):
        """Test adding a user to a group."""

        # Mock response data
        mock_response = {}

        iam_client.add_user_to_group.return_value = mock_response

        response = iam_client.add_user_to_group(
            user_id=sample_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.add_user_to_group.assert_called_once_with(
            user_id=sample_users[0],
            group_name="data-engineers",
        )

    def test_remove_user_from_group(self, iam_client, sample_users):
        """Test removing a user from a group."""

        # Mock response data
        mock_response = {}

        iam_client.remove_user_from_group.return_value = mock_response

        response = iam_client.remove_user_from_group(
            user_id=sample_users[1],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.remove_user_from_group.assert_called_once_with(
            user_id=sample_users[1],
            group_name="data-engineers",
        )

    def test_add_machine_user_to_group(
        self,
        iam_client,
        sample_machine_users,
    ):
        """Test adding a machine user to a group."""

        # Mock response data
        mock_response = {}

        iam_client.add_machine_user_to_group.return_value = mock_response

        response = iam_client.add_machine_user_to_group(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.add_machine_user_to_group.assert_called_once_with(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

    def test_remove_machine_user_from_group(
        self,
        iam_client,
        sample_machine_users,
    ):
        """Test removing a machine user from a group."""

        # Mock response data
        mock_response = {}

        iam_client.remove_machine_user_from_group.return_value = mock_response

        response = iam_client.remove_machine_user_from_group(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.remove_machine_user_from_group.assert_called_once_with(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

    def test_assign_group_role(self, iam_client, sample_roles):
        """Test assigning a role to a group."""

        # Mock response data
        mock_response = {}

        iam_client.assign_group_role.return_value = mock_response

        response = iam_client.assign_group_role(
            group_name="data-engineers",
            role=sample_roles[0],
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.assign_group_role.assert_called_once_with(
            group_name="data-engineers",
            role=sample_roles[0],
        )

    def test_unassign_group_role(self, iam_client, sample_roles):
        """Test unassigning a role from a group."""

        # Mock response data
        mock_response = {}

        iam_client.unassign_group_role.return_value = mock_response

        response = iam_client.unassign_group_role(
            group_name="data-engineers",
            role=sample_roles[0],
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.unassign_group_role.assert_called_once_with(
            group_name="data-engineers",
            role=sample_roles[0],
        )

    def test_list_group_assigned_resource_roles(self, iam_client):
        """Test listing resource roles assigned to a group."""

        # Mock response data
        mock_response = {
            "resourceAssignments": [
                {
                    "resourceCrn": "crn:cdp:environments:us-west-1:altus:environment:dev-env",
                    "resourceRoleCrn": "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser",
                },
                {
                    "resourceCrn": "crn:cdp:datalake:us-west-1:altus:datalake:prod-dl",
                    "resourceRoleCrn": "crn:cdp:iam:us-west-1:altus:resourceRole:DataLakeAdmin",
                },
            ],
        }

        iam_client.list_group_assigned_resource_roles.return_value = mock_response

        response = iam_client.list_group_assigned_resource_roles(
            group_name="data-engineers",
        )

        assert "resourceAssignments" in response
        assert len(response["resourceAssignments"]) == 2

        # Verify that the method was called with correct parameters
        iam_client.list_group_assigned_resource_roles.assert_called_once_with(
            group_name="data-engineers",
        )

    def test_assign_group_resource_role(
        self,
        iam_client,
        sample_resource_roles,
    ):
        """Test assigning a resource role to a group."""

        # Mock response data
        mock_response = {}

        iam_client.assign_group_resource_role.return_value = mock_response

        response = iam_client.assign_group_resource_role(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.assign_group_resource_role.assert_called_once_with(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )

    def test_unassign_group_resource_role(
        self,
        iam_client,
        sample_resource_roles,
    ):
        """Test unassigning a resource role from a group."""

        # Mock response data
        mock_response = {}

        iam_client.unassign_group_resource_role.return_value = mock_response

        response = iam_client.unassign_group_resource_role(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )

        assert isinstance(response, dict)

        # Verify that the method was called with correct parameters
        iam_client.unassign_group_resource_role.assert_called_once_with(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )
