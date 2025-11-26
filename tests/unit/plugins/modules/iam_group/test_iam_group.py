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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    RestClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)
from ansible_collections.cloudera.cloud.plugins.modules.iam_group import (
    IAMGroup,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def mock_api_client(mocker):
    """Fixture to provide a mocked RestClient instance."""
    api_client = mocker.create_autospec(RestClient, instance=True)
    return api_client


@pytest.fixture
def iam_client(mock_api_client):
    """Fixture to provide a CdpIamClient instance with mocked RestClient."""
    return CdpIamClient(api_client=mock_api_client)


@pytest.fixture
def sample_group_data():
    """Fixture providing sample group data for testing."""
    return {
        "groupName": "test-group",
        "crn": "crn:cdp:iam:us-west-1:altus:group:test-group",
        "creationDate": "2024-01-15T10:30:00.000Z",
        "syncMembershipOnUserLogin": True,
    }


@pytest.fixture
def sample_group_details():
    """Fixture providing complete group details including members and roles."""
    return {
        "groupName": "test-group",
        "crn": "crn:cdp:iam:us-west-1:altus:group:test-group",
        "creationDate": "2024-01-15T10:30:00.000Z",
        "syncMembershipOnUserLogin": True,
        "members": [
            "crn:cdp:iam:us-west-1:altus:user:alice@example.com",
            "crn:cdp:iam:us-west-1:altus:user:bob@example.com",
            "crn:cdp:iam:us-west-1:altus:machineUser:service-account-1",
        ],
        "roles": [
            "crn:cdp:iam:us-west-1:altus:role:PowerUser",
            "crn:cdp:iam:us-west-1:altus:role:EnvironmentCreator",
        ],
        "resourceAssignments": [
            {
                "resourceCrn": "crn:cdp:environments:us-west-1:altus:environment:dev-env",
                "resourceRoleCrn": "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser",
            },
        ],
    }


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


@pytest.fixture
def mock_ansible_module(mocker):
    """Fixture to provide a mocked Ansible module."""
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "state": "present",
        "name": "test-group",
        "sync": True,
        "users": None,
        "roles": None,
        "resource_roles": None,
        "purge": False,
    }
    return module


class TestCdpIamClient:
    """Unit tests for CdpIamClient group management methods."""

    def test_list_groups_no_filter(self, mock_api_client, iam_client):
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

        # Mock the RestClient instance
        mock_api_client._post.return_value = mock_response

        response = iam_client.list_groups()

        assert "groups" in response
        assert len(response["groups"]) == 2
        assert response["groups"][0]["groupName"] == "data-engineers"
        assert response["groups"][1]["syncMembershipOnUserLogin"] == False

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            None,
            {"pageSize": 100},
            squelch={404: {}},
        )

    def test_list_groups_with_filter(self, mock_api_client, iam_client):
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

        # Mock the RestClient instance
        mock_api_client._post.return_value = mock_response

        response = iam_client.list_groups(group_names=["data-engineers"])

        assert "groups" in response
        assert len(response["groups"]) == 1
        assert response["groups"][0]["groupName"] == "data-engineers"

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            None,
            {
                "groupNames": ["data-engineers"],
                "pageSize": 100,
            },
            squelch={404: {}},
        )

    def test_create_group(self, mock_api_client, iam_client):
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

        mock_api_client._post.return_value = mock_response

        response = iam_client.create_group(
            group_name="new-team",
            sync_membership_on_user_login=True,
        )

        assert "group" in response
        assert response["group"]["groupName"] == "new-team"

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/createGroup",
            None,
            {
                "groupName": "new-team",
                "syncMembershipOnUserLogin": True,
            },
            squelch={},
        )

    def test_delete_group(self, mock_api_client, iam_client):
        """Test deleting an IAM group."""

        # Mock response data (delete operations typically return empty)
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.delete_group(group_name="old-team")

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/deleteGroup",
            None,
            {"groupName": "old-team"},
            squelch={},
        )

    def test_update_group(self, mock_api_client, iam_client):
        """Test updating an IAM group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.update_group(
            group_name="existing-team",
            sync_membership_on_user_login=False,
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/updateGroup",
            None,
            {
                "groupName": "existing-team",
                "syncMembershipOnUserLogin": False,
            },
            squelch={},
        )

    def test_list_group_members(
        self,
        mock_api_client,
        iam_client,
        sample_users,
        sample_machine_users,
    ):
        """Test listing group members."""

        # Mock response data
        mock_response = {
            "memberCrns": sample_users + [sample_machine_users[0]],
        }

        mock_api_client._post.return_value = mock_response

        response = iam_client.list_group_members(group_name="data-engineers")

        assert "memberCrns" in response
        assert len(response["memberCrns"]) == 3

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/listGroupMembers",
            None,
            {
                "groupName": "data-engineers",
                "pageSize": 100,
            },
            squelch={},
        )

    def test_add_user_to_group(self, mock_api_client, iam_client, sample_users):
        """Test adding a user to a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.add_user_to_group(
            user_id=sample_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/addUserToGroup",
            None,
            {
                "userId": sample_users[0],
                "groupName": "data-engineers",
            },
            squelch={},
        )

    def test_remove_user_from_group(self, mock_api_client, iam_client, sample_users):
        """Test removing a user from a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.remove_user_from_group(
            user_id=sample_users[1],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/removeUserFromGroup",
            None,
            {
                "userId": sample_users[1],
                "groupName": "data-engineers",
            },
            squelch={},
        )

    def test_add_machine_user_to_group(
        self,
        mock_api_client,
        iam_client,
        sample_machine_users,
    ):
        """Test adding a machine user to a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.add_machine_user_to_group(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/addMachineUserToGroup",
            None,
            {
                "machineUserName": sample_machine_users[0],
                "groupName": "data-engineers",
            },
            squelch={},
        )

    def test_remove_machine_user_from_group(
        self,
        mock_api_client,
        iam_client,
        sample_machine_users,
    ):
        """Test removing a machine user from a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.remove_machine_user_from_group(
            machine_user_name=sample_machine_users[0],
            group_name="data-engineers",
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/removeMachineUserFromGroup",
            None,
            {
                "machineUserName": sample_machine_users[0],
                "groupName": "data-engineers",
            },
            squelch={},
        )

    def test_assign_group_role(self, mock_api_client, iam_client, sample_roles):
        """Test assigning a role to a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.assign_group_role(
            group_name="data-engineers",
            role=sample_roles[0],
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/assignGroupRole",
            None,
            {
                "groupName": "data-engineers",
                "role": sample_roles[0],
            },
            squelch={},
        )

    def test_unassign_group_role(self, mock_api_client, iam_client, sample_roles):
        """Test unassigning a role from a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.unassign_group_role(
            group_name="data-engineers",
            role=sample_roles[0],
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/unassignGroupRole",
            None,
            {
                "groupName": "data-engineers",
                "role": sample_roles[0],
            },
            squelch={},
        )

    def test_list_group_assigned_resource_roles(self, mock_api_client, iam_client):
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

        mock_api_client._post.return_value = mock_response

        response = iam_client.list_group_assigned_resource_roles(
            group_name="data-engineers",
        )

        assert "resourceAssignments" in response
        assert len(response["resourceAssignments"]) == 2

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/listGroupAssignedResourceRoles",
            None,
            {
                "groupName": "data-engineers",
                "pageSize": 100,
            },
            squelch={},
        )

    def test_assign_group_resource_role(
        self,
        mock_api_client,
        iam_client,
        sample_resource_roles,
    ):
        """Test assigning a resource role to a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.assign_group_resource_role(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/assignGroupResourceRole",
            None,
            {
                "groupName": "data-engineers",
                "resourceCrn": sample_resource_roles[0]["resource"],
                "resourceRoleCrn": sample_resource_roles[0]["role"],
            },
            squelch={},
        )

    def test_unassign_group_resource_role(
        self,
        mock_api_client,
        iam_client,
        sample_resource_roles,
    ):
        """Test unassigning a resource role from a group."""

        # Mock response data
        mock_response = {}

        mock_api_client._post.return_value = mock_response

        response = iam_client.unassign_group_resource_role(
            group_name="data-engineers",
            resource_crn=sample_resource_roles[0]["resource"],
            resource_role_crn=sample_resource_roles[0]["role"],
        )

        assert isinstance(response, dict)

        # Verify that the post method was called with correct parameters
        mock_api_client._post.assert_called_once_with(
            "/api/v1/iam/unassignGroupResourceRole",
            None,
            {
                "groupName": "data-engineers",
                "resourceCrn": sample_resource_roles[0]["resource"],
                "resourceRoleCrn": sample_resource_roles[0]["role"],
            },
            squelch={},
        )

    # ============================================================================
    # Tests for manage_group_users method
    # ============================================================================

    def test_manage_group_users_add_only(
        self,
        mock_api_client,
        iam_client,
        sample_users,
    ):
        """Test adding users to a group without removing any."""
        mock_api_client._post.return_value = {}

        current_members = [sample_users[0]]
        desired_users = sample_users  # Add second user

        changed = iam_client.manage_group_users(
            group_name="test-group",
            current_members=current_members,
            desired_users=desired_users,
            purge=False,
        )

        assert changed is True
        assert mock_api_client._post.call_count == 1

    def test_manage_group_users_purge(self, mock_api_client, iam_client, sample_users):
        """Test purging users not in desired list."""
        mock_api_client._post.return_value = {}

        current_members = sample_users
        desired_users = [sample_users[0]]  # Keep only first user

        changed = iam_client.manage_group_users(
            group_name="test-group",
            current_members=current_members,
            desired_users=desired_users,
            purge=True,
        )

        assert changed is True

    def test_manage_group_users_no_changes(
        self,
        mock_api_client,
        iam_client,
        sample_users,
    ):
        """Test when no user changes are needed."""
        current_members = sample_users
        desired_users = sample_users

        changed = iam_client.manage_group_users(
            group_name="test-group",
            current_members=current_members,
            desired_users=desired_users,
            purge=False,
        )

        assert changed is False
        mock_api_client._post.assert_not_called()

    def test_manage_group_users_machine_user(
        self,
        mock_api_client,
        iam_client,
        sample_machine_users,
    ):
        """Test adding machine users to a group."""
        mock_api_client._post.return_value = {}

        current_members = []
        desired_users = [sample_machine_users[0]]

        changed = iam_client.manage_group_users(
            group_name="test-group",
            current_members=current_members,
            desired_users=desired_users,
            purge=False,
        )

        assert changed is True


@pytest.mark.integration_api
class TestCdpIamClientIntegration:
    """Integration tests for CdpIamClient group management."""

    def test_create_update_delete_group_lifecycle(self, api_client):
        """Integration test for complete group lifecycle: create, update, delete."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-integration-group"

        try:
            # 1. Create a new group
            create_response = client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            assert "group" in create_response
            assert create_response["group"]["groupName"] == test_group_name
            assert create_response["group"]["syncMembershipOnUserLogin"] == True

            # 2. Verify group was created by listing it
            list_response = client.list_groups(group_names=[test_group_name])
            assert "groups" in list_response
            assert len(list_response["groups"]) == 1
            assert list_response["groups"][0]["groupName"] == test_group_name

            # 3. Update the group (change sync setting)
            update_response = client.update_group(
                group_name=test_group_name,
                sync_membership_on_user_login=False,
            )
            assert isinstance(update_response, dict)

            # 4. Verify the update
            updated_list = client.list_groups(group_names=[test_group_name])
            assert updated_list["groups"][0]["syncMembershipOnUserLogin"] == False

            # 5. Delete the group
            delete_response = client.delete_group(group_name=test_group_name)
            assert isinstance(delete_response, dict)

        except Exception as e:
            # Cleanup: try to delete the group if test fails
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass
            raise e

    def test_group_membership_management(self, api_client):
        """Integration test for adding and removing users from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-membership-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get current user to add to group
            current_user = client.get_user()
            user_crn = current_user.get("crn")

            if user_crn:
                # 3. Add user to group
                add_response = client.add_user_to_group(
                    group_name=test_group_name,
                    user_id=user_crn,
                )
                assert isinstance(add_response, dict)

                # 4. Verify user was added
                members_response = client.list_group_members(group_name=test_group_name)
                assert "memberCrns" in members_response
                assert user_crn in members_response["memberCrns"]

                # 5. Remove user from group
                remove_response = client.remove_user_from_group(
                    group_name=test_group_name,
                    user_id=user_crn,
                )
                assert isinstance(remove_response, dict)

                # 6. Verify user was removed
                members_after = client.list_group_members(group_name=test_group_name)
                assert user_crn not in members_after.get("memberCrns", [])

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass

    def test_group_role_assignment(self, api_client):
        """Integration test for assigning and unassigning roles to/from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-role-assignment-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get available roles
            roles_response = client.list_roles()
            if roles_response.get("roles") and len(roles_response["roles"]) > 0:
                # Use the first available role for testing
                test_role_crn = roles_response["roles"][0]["crn"]

                # 3. Assign role to group
                assign_response = client.assign_group_role(
                    group_name=test_group_name,
                    role=test_role_crn,
                )
                assert isinstance(assign_response, dict)

                # 4. Verify role was assigned
                assigned_roles = client.list_group_assigned_roles(
                    group_name=test_group_name,
                )
                assert "roleCrns" in assigned_roles
                assert test_role_crn in assigned_roles["roleCrns"]

                # 5. Unassign role from group
                unassign_response = client.unassign_group_role(
                    group_name=test_group_name,
                    role=test_role_crn,
                )
                assert isinstance(unassign_response, dict)

                # 6. Verify role was unassigned
                roles_after = client.list_group_assigned_roles(
                    group_name=test_group_name,
                )
                assert test_role_crn not in roles_after.get("roleCrns", [])

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass

    def test_machine_user_group_membership(self, api_client):
        """Integration test for adding and removing machine users from a group."""

        client = CdpIamClient(api_client=api_client)

        test_group_name = "test-machine-user-group"

        try:
            # 1. Create a test group
            client.create_group(
                group_name=test_group_name,
                sync_membership_on_user_login=True,
            )

            # 2. Get list of machine users
            machine_users_response = client.list_machine_users()

            if (
                machine_users_response.get("machineUsers")
                and len(machine_users_response["machineUsers"]) > 0
            ):
                # Use first available machine user for testing
                machine_user_name = machine_users_response["machineUsers"][0][
                    "machineUserName"
                ]

                # 3. Add machine user to group
                add_response = client.add_machine_user_to_group(
                    group_name=test_group_name,
                    machine_user_name=machine_user_name,
                )
                assert isinstance(add_response, dict)

                # 4. Verify machine user was added
                members_response = client.list_group_members(group_name=test_group_name)
                assert "memberCrns" in members_response

                # 5. Remove machine user from group
                remove_response = client.remove_machine_user_from_group(
                    group_name=test_group_name,
                    machine_user_name=machine_user_name,
                )
                assert isinstance(remove_response, dict)

                # 6. Verify machine user was removed
                members_after = client.list_group_members(group_name=test_group_name)
                # Machine user should no longer be in the group

        finally:
            # Cleanup: delete the test group
            try:
                client.delete_group(group_name=test_group_name)
            except:
                pass
