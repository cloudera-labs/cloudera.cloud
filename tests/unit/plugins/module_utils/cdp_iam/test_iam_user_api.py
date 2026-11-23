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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
    DeleteUserResponse,
    ResourceAssignment,
    User,
    UserDetails,
    WorkloadPasswordDetails,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import from_dict


USER_ID = "user-id-1"
USER_CRN = "crn:cdp:iam:us-west-1:altus:user:user-id-1"
USER_EMAIL = "user1@example.com"
IDP_CRN = "crn:cdp:iam:us-west-1:altus:samlProvider:default"
ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:PowerUser"
OLD_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:OldRole"
RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:dev-env"
RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser"
OTHER_RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:prod-env"
OTHER_RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentAdmin"
DEVELOPERS_CRN = "crn:cdp:iam:us-west-1:altus:group:developers/group-id-1"
ADMINS_CRN = "crn:cdp:iam:us-west-1:altus:group:admins/group-id-2"

API_USER_1 = {
    "userId": USER_ID,
    "crn": USER_CRN,
    "email": USER_EMAIL,
    "firstName": "User",
    "lastName": "One",
    "workloadUsername": "u_user1",
    "creationDate": "2025-01-01T00:00:00.000Z",
}
API_USER_2 = {
    "userId": "user-id-2",
    "crn": "crn:cdp:iam:us-west-1:altus:user:user-id-2",
    "email": "user2@example.com",
    "firstName": "User",
    "lastName": "Two",
    "workloadUsername": "u_user2",
    "creationDate": "2025-01-02T00:00:00.000Z",
}

USER_1 = User(
    userId=USER_ID,
    crn=USER_CRN,
    email=USER_EMAIL,
    firstName="User",
    lastName="One",
    workloadUsername="u_user1",
    creationDate="2025-01-01T00:00:00.000Z",
)
USER_2 = User(
    userId="user-id-2",
    crn="crn:cdp:iam:us-west-1:altus:user:user-id-2",
    email="user2@example.com",
    firstName="User",
    lastName="Two",
    workloadUsername="u_user2",
    creationDate="2025-01-02T00:00:00.000Z",
)

ASSIGNMENT = ResourceAssignment(
    resourceCrn=RESOURCE_CRN,
    resourceRoleCrn=RESOURCE_ROLE_CRN,
)
OTHER_ASSIGNMENT = ResourceAssignment(
    resourceCrn=OTHER_RESOURCE_CRN,
    resourceRoleCrn=OTHER_RESOURCE_ROLE_CRN,
)


@pytest.fixture
def api_client(mocker):
    return mocker.create_autospec(CdpClient, instance=True)


@pytest.fixture
def client(api_client):
    return CdpIamClient(api_client=api_client)


class TestApiPayloadMapping:
    """Unit tests for loading camelCase IAM API payloads into the user dataclasses."""

    def test_maps_keys_and_nested_objects(self):
        user = from_dict(
            User,
            {
                "userId": USER_ID,
                "firstName": "User",
                "accountAdmin": False,
                "workloadPasswordDetails": {
                    "isPasswordSet": True,
                    "passwordExpirationDate": "2030-01-01T00:00:00.000Z",
                },
                "someFieldAddedByTheApiLater": "ignored",
            },
        )

        assert user == User(
            userId=USER_ID,
            firstName="User",
            accountAdmin=False,
            workloadPasswordDetails=WorkloadPasswordDetails(
                isPasswordSet=True,
                passwordExpirationDate="2030-01-01T00:00:00.000Z",
            ),
        )

    def test_unset_fields_stay_unset(self):
        user = from_dict(User, {"userId": USER_ID})

        assert user == User(userId=USER_ID)


class TestListUsers:
    def test_list_users(self, client, api_client):
        api_client.post.return_value = {"users": [API_USER_1, API_USER_2]}

        users = client.list_users()

        assert users == [USER_1, USER_2]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listUsers",
            json_data={"pageSize": 100},
        )

    def test_list_users_by_ids(self, client, api_client):
        api_client.post.return_value = {"users": [API_USER_1]}

        users = client.list_users(user_ids=[USER_ID])

        assert users == [USER_1]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listUsers",
            json_data={"userIds": [USER_ID], "pageSize": 100},
        )

    def test_list_users_empty(self, client, api_client):
        api_client.post.return_value = {}

        assert client.list_users() == []

    def test_list_users_follows_pagination(self, client, api_client, mocker):
        api_client.post.side_effect = [
            {"users": [API_USER_1], "nextToken": "token-1"},
            {"users": [API_USER_2]},
        ]

        users = client.list_users()

        assert users == [USER_1, USER_2]
        assert api_client.post.call_args_list == [
            mocker.call("/api/v1/iam/listUsers", json_data={"pageSize": 100}),
            mocker.call(
                "/api/v1/iam/listUsers",
                json_data={"startingToken": "token-1", "pageSize": 100},
            ),
        ]


class TestListUsersFiltered:
    @pytest.fixture(autouse=True)
    def users(self, client, mocker):
        no_workload_username = User(userId="user-id-3", email="user3@example.com")
        return mocker.patch.object(
            client,
            "list_users",
            return_value=[USER_1, USER_2, no_workload_username],
        )

    def test_filter_by_camel_case_field(self, client):
        matched = client.list_users_filtered({"workloadUsername": "u_user[0-9]+"})

        assert matched == [USER_1, USER_2]

    def test_filter_by_snake_case_field(self, client):
        matched = client.list_users_filtered({"workload_username": "u_user1"})

        assert matched == [USER_1]

    def test_filter_is_a_regex_search(self, client):
        matched = client.list_users_filtered({"email": "^user2@"})

        assert matched == [USER_2]

    def test_all_filters_must_match(self, client):
        matched = client.list_users_filtered(
            {"workloadUsername": "u_user", "lastName": "Two"},
        )

        assert matched == [USER_2]

    def test_no_match(self, client):
        assert client.list_users_filtered({"workloadUsername": "^admin_"}) == []

    def test_unknown_field_never_matches(self, client):
        assert client.list_users_filtered({"notAUserField": ".*"}) == []

    def test_unset_field_never_matches(self, client):
        matched = client.list_users_filtered({"workloadUsername": ".*"})

        assert [user.userId for user in matched] == [USER_ID, "user-id-2"]


class TestGetUser:
    def test_get_current_user(self, client, api_client):
        api_client.post.return_value = {"user": API_USER_1}

        assert client.get_user() == USER_1
        api_client.post.assert_called_once_with(
            "/api/v1/iam/getUser",
            json_data={},
            squelch={404: {}},
        )

    def test_get_user_by_id(self, client, api_client):
        api_client.post.return_value = {"user": API_USER_1}

        assert client.get_user(user_id=USER_ID) == USER_1
        api_client.post.assert_called_once_with(
            "/api/v1/iam/getUser",
            json_data={"userId": USER_ID},
            squelch={404: {}},
        )

    def test_get_user_not_found(self, client, api_client):
        api_client.post.return_value = {}

        assert client.get_user(user_id="missing") is None


class TestCreateUser:
    def test_create_user(self, client, api_client):
        api_client.post.return_value = {"user": API_USER_1}

        user = client.create_user(
            email=USER_EMAIL,
            identity_provider_user_id="idp-user-1",
            first_name="User",
            last_name="One",
            saml_provider_name="my-saml-provider",
        )

        assert user == USER_1
        api_client.post.assert_called_once_with(
            "/api/v1/iam/createUser",
            json_data={
                "email": USER_EMAIL,
                "identityProviderUserId": "idp-user-1",
                "firstName": "User",
                "lastName": "One",
                "samlProviderName": "my-saml-provider",
            },
        )

    def test_create_user_uses_default_identity_provider(self, client, api_client):
        api_client.post.side_effect = [{"crn": IDP_CRN}, {"user": API_USER_1}]

        client.create_user(email=USER_EMAIL, identity_provider_user_id=USER_EMAIL)

        first_call, second_call = api_client.post.call_args_list
        assert first_call.args == ("/api/v1/iam/getDefaultIdentityProvider",)
        assert second_call.args == ("/api/v1/iam/createUser",)
        assert second_call.kwargs["json_data"] == {
            "email": USER_EMAIL,
            "identityProviderUserId": USER_EMAIL,
            "samlProviderName": IDP_CRN,
        }

    def test_create_user_without_any_identity_provider(self, client, api_client):
        api_client.post.side_effect = [{}, {"user": API_USER_1}]

        client.create_user(email=USER_EMAIL, identity_provider_user_id=USER_EMAIL)

        assert api_client.post.call_args_list[1].kwargs["json_data"] == {
            "email": USER_EMAIL,
            "identityProviderUserId": USER_EMAIL,
        }


class TestUpdateUser:
    def test_update_user(self, client, api_client):
        api_client.post.return_value = {"user": {**API_USER_1, "status": "INACTIVE"}}

        user = client.update_user(user_id=USER_ID, active=False)

        assert user.userId == USER_ID
        assert user.status == "INACTIVE"
        api_client.post.assert_called_once_with(
            "/api/v1/iam/updateUser",
            json_data={"user": USER_ID, "active": False},
        )

    def test_update_user_without_changes(self, client, api_client):
        api_client.post.return_value = {"user": API_USER_1}

        client.update_user(user_id=USER_ID)

        api_client.post.assert_called_once_with(
            "/api/v1/iam/updateUser",
            json_data={"user": USER_ID},
        )


class TestDeleteUser:
    def test_delete_user(self, client, api_client):
        api_client.post.return_value = {
            "accessKeysDeleted": ["access-key-1"],
            "groupsModified": [DEVELOPERS_CRN],
            "resourcesUnassigned": [
                {
                    "resourceCrn": RESOURCE_CRN,
                    "resourceRoleCrn": RESOURCE_ROLE_CRN,
                },
            ],
            "rolesUnassigned": [ROLE_CRN],
        }

        response = client.delete_user(user_id=USER_ID)

        assert response == DeleteUserResponse(
            accessKeysDeleted=["access-key-1"],
            groupsModified=[DEVELOPERS_CRN],
            resourcesUnassigned=[ASSIGNMENT],
            rolesUnassigned=[ROLE_CRN],
        )
        api_client.post.assert_called_once_with(
            "/api/v1/iam/deleteUser",
            json_data={"userId": USER_ID},
        )

    def test_delete_user_empty_response(self, client, api_client):
        api_client.post.return_value = {}

        assert client.delete_user(user_id=USER_ID) == DeleteUserResponse()


class TestUserAssignments:
    def test_list_user_assigned_roles(self, client, api_client):
        api_client.post.return_value = {"roleCrns": [ROLE_CRN]}

        assert client.list_user_assigned_roles(user=USER_ID) == [ROLE_CRN]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listUserAssignedRoles",
            json_data={"user": USER_ID, "pageSize": 100},
        )

    def test_list_user_assigned_resource_roles(self, client, api_client):
        api_client.post.return_value = {
            "resourceAssignments": [
                {"resourceCrn": RESOURCE_CRN, "resourceRoleCrn": RESOURCE_ROLE_CRN},
            ],
        }

        assert client.list_user_assigned_resource_roles(user=USER_ID) == [ASSIGNMENT]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listUserAssignedResourceRoles",
            json_data={"user": USER_ID, "pageSize": 100},
        )

    def test_list_groups_for_user(self, client, api_client):
        api_client.post.return_value = {"groupCrns": [DEVELOPERS_CRN]}

        assert client.list_groups_for_user(user_id=USER_ID) == [DEVELOPERS_CRN]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroupsForUser",
            json_data={"userId": USER_ID, "pageSize": 100},
        )


class TestGetUserDetails:
    def test_get_user_details(self, client, mocker):
        mocker.patch.object(client, "get_user", return_value=USER_1)
        mocker.patch.object(client, "list_user_assigned_roles", return_value=[ROLE_CRN])
        mocker.patch.object(
            client,
            "list_user_assigned_resource_roles",
            return_value=[ASSIGNMENT],
        )
        mocker.patch.object(
            client,
            "list_groups_for_user",
            return_value=[DEVELOPERS_CRN],
        )

        details = client.get_user_details(user_id=USER_ID)

        assert details == UserDetails(
            **vars(USER_1),
            roles=[ROLE_CRN],
            resourceAssignments=[ASSIGNMENT],
            groups=[DEVELOPERS_CRN],
        )
        client.get_user.assert_called_once_with(user_id=USER_ID)
        client.list_user_assigned_roles.assert_called_once_with(user=USER_ID)
        client.list_user_assigned_resource_roles.assert_called_once_with(user=USER_ID)
        client.list_groups_for_user.assert_called_once_with(user_id=USER_ID)

    def test_get_user_details_not_found(self, client, mocker):
        mocker.patch.object(client, "get_user", return_value=None)
        roles = mocker.patch.object(client, "list_user_assigned_roles")

        assert client.get_user_details(user_id="missing") is None
        roles.assert_not_called()

    def test_get_user_details_does_not_swallow_errors(self, client, mocker):
        mocker.patch.object(client, "get_user", return_value=USER_1)
        mocker.patch.object(
            client,
            "list_user_assigned_roles",
            side_effect=CdpError("boom", status=500),
        )

        with pytest.raises(CdpError, match="boom"):
            client.get_user_details(user_id=USER_ID)


class TestGetUserDetailsByEmail:
    def test_found(self, client, mocker):
        mocker.patch.object(client, "list_users", return_value=[USER_2, USER_1])
        details = mocker.patch.object(
            client,
            "get_user_details",
            return_value=UserDetails(**vars(USER_1)),
        )

        result = client.get_user_details_by_email(email=USER_EMAIL)

        assert result is details.return_value
        details.assert_called_once_with(user_id=USER_ID)

    def test_not_found(self, client, mocker):
        mocker.patch.object(client, "list_users", return_value=[USER_1, USER_2])
        details = mocker.patch.object(client, "get_user_details")

        assert client.get_user_details_by_email(email="nobody@example.com") is None
        details.assert_not_called()

    def test_ignores_users_without_an_id(self, client, mocker):
        mocker.patch.object(
            client,
            "list_users",
            return_value=[User(email=USER_EMAIL)],
        )
        details = mocker.patch.object(client, "get_user_details")

        assert client.get_user_details_by_email(email=USER_EMAIL) is None
        details.assert_not_called()


class TestGetGroupNames:
    def test_resolves_group_crns(self, client, api_client):
        api_client.post.return_value = {
            "groups": [
                {"groupName": "developers", "crn": DEVELOPERS_CRN},
                {"groupName": "admins", "crn": ADMINS_CRN},
                {"crn": "crn:cdp:iam:us-west-1:altus:group:unnamed/group-id-3"},
            ],
        }

        names = client.get_group_names([DEVELOPERS_CRN, ADMINS_CRN])

        assert names == ["developers", "admins"]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listGroups",
            json_data={"groupNames": [DEVELOPERS_CRN, ADMINS_CRN], "pageSize": 100},
            squelch={404: {}},
        )

    def test_no_crns_makes_no_request(self, client, api_client):
        assert client.get_group_names([]) == []
        api_client.post.assert_not_called()


class TestManageUserGroups:
    @pytest.fixture(autouse=True)
    def group_api(self, client, mocker):
        mocker.patch.object(client, "get_group_names", return_value=[])
        mocker.patch.object(
            client,
            "get_group_details",
            return_value={"groupName": "admins", "crn": ADMINS_CRN},
        )
        mocker.patch.object(client, "add_user_to_group")
        mocker.patch.object(client, "remove_user_from_group")

    def test_adds_missing_groups(self, client):
        client.get_group_names.return_value = ["developers"]

        changed = client.manage_user_groups(
            user_id=USER_ID,
            current_groups=[DEVELOPERS_CRN],
            desired_groups=["developers", "admins"],
        )

        assert changed is True
        client.get_group_names.assert_called_once_with([DEVELOPERS_CRN])
        client.add_user_to_group.assert_called_once_with(
            user_id=USER_ID,
            group_name="admins",
        )
        client.remove_user_from_group.assert_not_called()

    def test_already_member(self, client):
        client.get_group_names.return_value = ["developers"]

        changed = client.manage_user_groups(
            user_id=USER_ID,
            current_groups=[DEVELOPERS_CRN],
            desired_groups=["developers"],
        )

        assert changed is False
        client.add_user_to_group.assert_not_called()
        client.remove_user_from_group.assert_not_called()

    def test_keeps_other_memberships_without_purge(self, client):
        client.get_group_names.return_value = ["developers", "admins"]

        changed = client.manage_user_groups(
            user_id=USER_ID,
            current_groups=[DEVELOPERS_CRN, ADMINS_CRN],
            desired_groups=["developers"],
        )

        assert changed is False
        client.remove_user_from_group.assert_not_called()

    def test_purge_removes_other_memberships(self, client):
        client.get_group_names.return_value = ["developers", "admins"]

        changed = client.manage_user_groups(
            user_id=USER_ID,
            current_groups=[DEVELOPERS_CRN, ADMINS_CRN],
            desired_groups=["developers"],
            purge=True,
        )

        assert changed is True
        client.remove_user_from_group.assert_called_once_with(
            user_id=USER_ID,
            group_name="admins",
        )
        client.add_user_to_group.assert_not_called()

    def test_nonexistent_group_raises(self, client):
        client.get_group_details.return_value = None

        with pytest.raises(CdpError, match="Group 'ghosts' does not exist"):
            client.manage_user_groups(
                user_id=USER_ID,
                current_groups=[],
                desired_groups=["ghosts"],
            )

        client.add_user_to_group.assert_not_called()


class TestManageUserRoles:
    @pytest.fixture(autouse=True)
    def role_api(self, client, mocker):
        mocker.patch.object(client, "assign_user_role")
        mocker.patch.object(client, "unassign_user_role")

    def test_assigns_missing_roles(self, client):
        changed = client.manage_user_roles(
            user_id=USER_ID,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[OLD_ROLE_CRN, ROLE_CRN],
        )

        assert changed is True
        client.assign_user_role.assert_called_once_with(
            user_id=USER_ID,
            role=ROLE_CRN,
        )
        client.unassign_user_role.assert_not_called()

    def test_already_assigned(self, client):
        changed = client.manage_user_roles(
            user_id=USER_ID,
            current_roles=[ROLE_CRN],
            desired_roles=[ROLE_CRN],
        )

        assert changed is False
        client.assign_user_role.assert_not_called()
        client.unassign_user_role.assert_not_called()

    def test_keeps_other_roles_without_purge(self, client):
        changed = client.manage_user_roles(
            user_id=USER_ID,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[ROLE_CRN],
        )

        assert changed is True
        client.unassign_user_role.assert_not_called()

    def test_purge_replaces_roles(self, client):
        changed = client.manage_user_roles(
            user_id=USER_ID,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[ROLE_CRN],
            purge=True,
        )

        assert changed is True
        client.unassign_user_role.assert_called_once_with(
            user_id=USER_ID,
            role=OLD_ROLE_CRN,
        )
        client.assign_user_role.assert_called_once_with(
            user_id=USER_ID,
            role=ROLE_CRN,
        )

    def test_purge_with_nothing_desired_removes_all(self, client):
        changed = client.manage_user_roles(
            user_id=USER_ID,
            current_roles=[OLD_ROLE_CRN, ROLE_CRN],
            desired_roles=[],
            purge=True,
        )

        assert changed is True
        assert client.unassign_user_role.call_count == 2
        client.assign_user_role.assert_not_called()


class TestManageUserResourceRoles:
    @pytest.fixture(autouse=True)
    def resource_role_api(self, client, mocker):
        mocker.patch.object(client, "assign_user_resource_role")
        mocker.patch.object(client, "unassign_user_resource_role")

    def test_assigns_missing_assignments(self, client):
        changed = client.manage_user_resource_roles(
            user_id=USER_ID,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[ASSIGNMENT, OTHER_ASSIGNMENT],
        )

        assert changed is True
        client.assign_user_resource_role.assert_called_once_with(
            user_id=USER_ID,
            resource_crn=OTHER_RESOURCE_CRN,
            resource_role_crn=OTHER_RESOURCE_ROLE_CRN,
        )
        client.unassign_user_resource_role.assert_not_called()

    def test_already_assigned(self, client):
        changed = client.manage_user_resource_roles(
            user_id=USER_ID,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[
                ResourceAssignment(
                    resourceCrn=RESOURCE_CRN,
                    resourceRoleCrn=RESOURCE_ROLE_CRN,
                ),
            ],
        )

        assert changed is False
        client.assign_user_resource_role.assert_not_called()
        client.unassign_user_resource_role.assert_not_called()

    def test_keeps_other_assignments_without_purge(self, client):
        changed = client.manage_user_resource_roles(
            user_id=USER_ID,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[OTHER_ASSIGNMENT],
        )

        assert changed is True
        client.unassign_user_resource_role.assert_not_called()

    def test_purge_replaces_assignments(self, client):
        changed = client.manage_user_resource_roles(
            user_id=USER_ID,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[OTHER_ASSIGNMENT],
            purge=True,
        )

        assert changed is True
        client.unassign_user_resource_role.assert_called_once_with(
            user_id=USER_ID,
            resource_crn=RESOURCE_CRN,
            resource_role_crn=RESOURCE_ROLE_CRN,
        )
        client.assign_user_resource_role.assert_called_once_with(
            user_id=USER_ID,
            resource_crn=OTHER_RESOURCE_CRN,
            resource_role_crn=OTHER_RESOURCE_ROLE_CRN,
        )
