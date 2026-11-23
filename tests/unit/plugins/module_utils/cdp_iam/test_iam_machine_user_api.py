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
    DeleteMachineUserResponse,
    MachineUser,
    MachineUserDetails,
    ResourceAssignment,
    WorkloadPasswordDetails,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import from_dict


MACHINE_USER_NAME = "test-machine-user"
MACHINE_USER_CRN = "crn:cdp:iam:us-west-1:altus:machineUser:test-machine-user/id-1"
OTHER_MACHINE_USER_NAME = "other-machine-user"
OTHER_MACHINE_USER_CRN = (
    "crn:cdp:iam:us-west-1:altus:machineUser:other-machine-user/id-2"
)
GROUP_CRN = "crn:cdp:iam:us-west-1:altus:group:developers/group-id-1"
ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:PowerUser"
OLD_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:OldRole"
RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:dev-env"
RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser"
OTHER_RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:prod-env"
OTHER_RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentAdmin"

API_MACHINE_USER_1 = {
    "machineUserName": MACHINE_USER_NAME,
    "crn": MACHINE_USER_CRN,
    "creationDate": "2025-01-01T00:00:00.000Z",
    "status": "ACTIVE",
    "workloadUsername": "mu_one",
    "workloadPasswordDetails": {
        "isPasswordSet": True,
        "passwordExpirationDate": "2030-01-01T00:00:00.000Z",
    },
}
API_MACHINE_USER_2 = {
    "machineUserName": OTHER_MACHINE_USER_NAME,
    "crn": OTHER_MACHINE_USER_CRN,
    "creationDate": "2025-01-02T00:00:00.000Z",
    "status": "ACTIVE",
    "workloadUsername": "mu_two",
}

MACHINE_USER_1 = MachineUser(
    machineUserName=MACHINE_USER_NAME,
    crn=MACHINE_USER_CRN,
    creationDate="2025-01-01T00:00:00.000Z",
    status="ACTIVE",
    workloadUsername="mu_one",
    workloadPasswordDetails=WorkloadPasswordDetails(
        isPasswordSet=True,
        passwordExpirationDate="2030-01-01T00:00:00.000Z",
    ),
)
MACHINE_USER_2 = MachineUser(
    machineUserName=OTHER_MACHINE_USER_NAME,
    crn=OTHER_MACHINE_USER_CRN,
    creationDate="2025-01-02T00:00:00.000Z",
    status="ACTIVE",
    workloadUsername="mu_two",
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
    """Unit tests for loading camelCase IAM API payloads into the machine user dataclasses."""

    def test_maps_keys_and_nested_objects(self):
        machine_user = from_dict(
            MachineUser,
            {
                **API_MACHINE_USER_1,
                "someFieldAddedByTheApiLater": "ignored",
            },
        )

        assert machine_user == MACHINE_USER_1

    def test_unset_fields_stay_unset(self):
        machine_user = from_dict(MachineUser, {"machineUserName": MACHINE_USER_NAME})

        assert machine_user == MachineUser(machineUserName=MACHINE_USER_NAME)


class TestListMachineUsers:
    def test_list_machine_users(self, client, api_client):
        api_client.post.return_value = {
            "machineUsers": [API_MACHINE_USER_1, API_MACHINE_USER_2],
        }

        machine_users = client.list_machine_users()

        assert machine_users == [MACHINE_USER_1, MACHINE_USER_2]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listMachineUsers",
            json_data={"pageSize": 100},
            squelch={404: {}},
        )

    def test_list_machine_users_by_names(self, client, api_client):
        api_client.post.return_value = {"machineUsers": [API_MACHINE_USER_1]}

        machine_users = client.list_machine_users(
            machine_user_names=[MACHINE_USER_NAME],
        )

        assert machine_users == [MACHINE_USER_1]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listMachineUsers",
            json_data={"machineUserNames": [MACHINE_USER_NAME], "pageSize": 100},
            squelch={404: {}},
        )

    def test_list_machine_users_empty(self, client, api_client):
        api_client.post.return_value = {}

        assert client.list_machine_users() == []

    def test_list_machine_users_follows_pagination(self, client, api_client, mocker):
        api_client.post.side_effect = [
            {"machineUsers": [API_MACHINE_USER_1], "nextToken": "token-1"},
            {"machineUsers": [API_MACHINE_USER_2]},
        ]

        machine_users = client.list_machine_users()

        assert machine_users == [MACHINE_USER_1, MACHINE_USER_2]
        assert api_client.post.call_args_list == [
            mocker.call(
                "/api/v1/iam/listMachineUsers",
                json_data={"pageSize": 100},
                squelch={404: {}},
            ),
            mocker.call(
                "/api/v1/iam/listMachineUsers",
                json_data={"startingToken": "token-1", "pageSize": 100},
                squelch={404: {}},
            ),
        ]


class TestCreateMachineUser:
    def test_create_machine_user(self, client, api_client):
        api_client.post.return_value = {"machineUser": API_MACHINE_USER_1}

        machine_user = client.create_machine_user(machine_user_name=MACHINE_USER_NAME)

        assert machine_user == MACHINE_USER_1
        api_client.post.assert_called_once_with(
            "/api/v1/iam/createMachineUser",
            json_data={"machineUserName": MACHINE_USER_NAME},
        )

    def test_create_machine_user_empty_response(self, client, api_client):
        api_client.post.return_value = {}

        assert (
            client.create_machine_user(machine_user_name=MACHINE_USER_NAME)
            == MachineUser()
        )


class TestDeleteMachineUser:
    def test_delete_machine_user(self, client, api_client):
        api_client.post.return_value = {
            "accessKeysDeleted": ["access-key-1"],
            "groupsModified": [GROUP_CRN],
            "resourcesUnassigned": [
                {
                    "resourceCrn": RESOURCE_CRN,
                    "resourceRoleCrn": RESOURCE_ROLE_CRN,
                },
            ],
            "rolesUnassigned": [ROLE_CRN],
        }

        response = client.delete_machine_user(machine_user_name=MACHINE_USER_NAME)

        assert response == DeleteMachineUserResponse(
            accessKeysDeleted=["access-key-1"],
            groupsModified=[GROUP_CRN],
            resourcesUnassigned=[ASSIGNMENT],
            rolesUnassigned=[ROLE_CRN],
        )
        api_client.post.assert_called_once_with(
            "/api/v1/iam/deleteMachineUser",
            json_data={"machineUserName": MACHINE_USER_NAME},
        )

    def test_delete_machine_user_empty_response(self, client, api_client):
        api_client.post.return_value = {}

        assert (
            client.delete_machine_user(machine_user_name=MACHINE_USER_NAME)
            == DeleteMachineUserResponse()
        )


class TestMachineUserAssignments:
    def test_list_machine_user_assigned_roles(self, client, api_client):
        api_client.post.return_value = {"roleCrns": [ROLE_CRN]}

        roles = client.list_machine_user_assigned_roles(
            machine_user_name=MACHINE_USER_NAME,
        )

        assert roles == [ROLE_CRN]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listMachineUserAssignedRoles",
            json_data={"machineUserName": MACHINE_USER_NAME, "pageSize": 100},
        )

    def test_list_machine_user_assigned_roles_empty(self, client, api_client):
        api_client.post.return_value = {}

        assert (
            client.list_machine_user_assigned_roles(
                machine_user_name=MACHINE_USER_NAME,
            )
            == []
        )

    def test_list_machine_user_assigned_roles_follows_pagination(
        self,
        client,
        api_client,
        mocker,
    ):
        api_client.post.side_effect = [
            {"roleCrns": [OLD_ROLE_CRN], "nextToken": "token-1"},
            {"roleCrns": [ROLE_CRN]},
        ]

        roles = client.list_machine_user_assigned_roles(
            machine_user_name=MACHINE_USER_NAME,
        )

        assert roles == [OLD_ROLE_CRN, ROLE_CRN]
        assert api_client.post.call_args_list == [
            mocker.call(
                "/api/v1/iam/listMachineUserAssignedRoles",
                json_data={"machineUserName": MACHINE_USER_NAME, "pageSize": 100},
            ),
            mocker.call(
                "/api/v1/iam/listMachineUserAssignedRoles",
                json_data={
                    "machineUserName": MACHINE_USER_NAME,
                    "startingToken": "token-1",
                    "pageSize": 100,
                },
            ),
        ]

    def test_list_machine_user_assigned_resource_roles(self, client, api_client):
        api_client.post.return_value = {
            "resourceAssignments": [
                {"resourceCrn": RESOURCE_CRN, "resourceRoleCrn": RESOURCE_ROLE_CRN},
            ],
        }

        assignments = client.list_machine_user_assigned_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
        )

        assert assignments == [ASSIGNMENT]
        api_client.post.assert_called_once_with(
            "/api/v1/iam/listMachineUserAssignedResourceRoles",
            json_data={"machineUserName": MACHINE_USER_NAME, "pageSize": 100},
        )

    def test_list_machine_user_assigned_resource_roles_empty(self, client, api_client):
        api_client.post.return_value = {}

        assert (
            client.list_machine_user_assigned_resource_roles(
                machine_user_name=MACHINE_USER_NAME,
            )
            == []
        )

    def test_list_machine_user_assigned_resource_roles_follows_pagination(
        self,
        client,
        api_client,
    ):
        api_client.post.side_effect = [
            {
                "resourceAssignments": [
                    {
                        "resourceCrn": RESOURCE_CRN,
                        "resourceRoleCrn": RESOURCE_ROLE_CRN,
                    },
                ],
                "nextToken": "token-1",
            },
            {
                "resourceAssignments": [
                    {
                        "resourceCrn": OTHER_RESOURCE_CRN,
                        "resourceRoleCrn": OTHER_RESOURCE_ROLE_CRN,
                    },
                ],
            },
        ]

        assignments = client.list_machine_user_assigned_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
        )

        assert assignments == [ASSIGNMENT, OTHER_ASSIGNMENT]
        assert api_client.post.call_count == 2


class TestGetMachineUserDetails:
    def test_get_machine_user_details(self, client, mocker):
        mocker.patch.object(client, "list_machine_users", return_value=[MACHINE_USER_1])
        mocker.patch.object(
            client,
            "list_machine_user_assigned_roles",
            return_value=[ROLE_CRN],
        )
        mocker.patch.object(
            client,
            "list_machine_user_assigned_resource_roles",
            return_value=[ASSIGNMENT],
        )

        details = client.get_machine_user_details(machine_user_name=MACHINE_USER_NAME)

        assert details == MachineUserDetails(
            **vars(MACHINE_USER_1),
            roles=[ROLE_CRN],
            resourceAssignments=[ASSIGNMENT],
        )
        client.list_machine_users.assert_called_once_with(
            machine_user_names=[MACHINE_USER_NAME],
        )
        client.list_machine_user_assigned_roles.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
        )
        client.list_machine_user_assigned_resource_roles.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
        )

    def test_get_machine_user_details_not_found(self, client, mocker):
        mocker.patch.object(client, "list_machine_users", return_value=[])
        roles = mocker.patch.object(client, "list_machine_user_assigned_roles")

        assert client.get_machine_user_details(machine_user_name="missing") is None
        roles.assert_not_called()

    def test_get_machine_user_details_does_not_swallow_errors(self, client, mocker):
        mocker.patch.object(client, "list_machine_users", return_value=[MACHINE_USER_1])
        mocker.patch.object(
            client,
            "list_machine_user_assigned_roles",
            side_effect=CdpError("boom", status=500),
        )

        with pytest.raises(CdpError, match="boom"):
            client.get_machine_user_details(machine_user_name=MACHINE_USER_NAME)


class TestManageMachineUserRoles:
    @pytest.fixture(autouse=True)
    def role_api(self, client, mocker):
        mocker.patch.object(client, "assign_machine_user_role")
        mocker.patch.object(client, "unassign_machine_user_role")

    def test_assigns_missing_roles(self, client):
        changed = client.manage_machine_user_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[OLD_ROLE_CRN, ROLE_CRN],
        )

        assert changed is True
        client.assign_machine_user_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            role=ROLE_CRN,
        )
        client.unassign_machine_user_role.assert_not_called()

    def test_already_assigned(self, client):
        changed = client.manage_machine_user_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_roles=[ROLE_CRN],
            desired_roles=[ROLE_CRN],
        )

        assert changed is False
        client.assign_machine_user_role.assert_not_called()
        client.unassign_machine_user_role.assert_not_called()

    def test_keeps_other_roles_without_purge(self, client):
        changed = client.manage_machine_user_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[ROLE_CRN],
        )

        assert changed is True
        client.unassign_machine_user_role.assert_not_called()

    def test_purge_replaces_roles(self, client):
        changed = client.manage_machine_user_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_roles=[OLD_ROLE_CRN],
            desired_roles=[ROLE_CRN],
            purge=True,
        )

        assert changed is True
        client.unassign_machine_user_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            role=OLD_ROLE_CRN,
        )
        client.assign_machine_user_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            role=ROLE_CRN,
        )

    def test_purge_with_nothing_desired_removes_all(self, client):
        changed = client.manage_machine_user_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_roles=[OLD_ROLE_CRN, ROLE_CRN],
            desired_roles=[],
            purge=True,
        )

        assert changed is True
        assert client.unassign_machine_user_role.call_count == 2
        client.assign_machine_user_role.assert_not_called()


class TestManageMachineUserResourceRoles:
    @pytest.fixture(autouse=True)
    def resource_role_api(self, client, mocker):
        mocker.patch.object(client, "assign_machine_user_resource_role")
        mocker.patch.object(client, "unassign_machine_user_resource_role")

    def test_assigns_missing_assignments(self, client):
        changed = client.manage_machine_user_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[ASSIGNMENT, OTHER_ASSIGNMENT],
        )

        assert changed is True
        client.assign_machine_user_resource_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            resource_crn=OTHER_RESOURCE_CRN,
            resource_role_crn=OTHER_RESOURCE_ROLE_CRN,
        )
        client.unassign_machine_user_resource_role.assert_not_called()

    def test_already_assigned(self, client):
        changed = client.manage_machine_user_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[
                ResourceAssignment(
                    resourceCrn=RESOURCE_CRN,
                    resourceRoleCrn=RESOURCE_ROLE_CRN,
                ),
            ],
        )

        assert changed is False
        client.assign_machine_user_resource_role.assert_not_called()
        client.unassign_machine_user_resource_role.assert_not_called()

    def test_keeps_other_assignments_without_purge(self, client):
        changed = client.manage_machine_user_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[OTHER_ASSIGNMENT],
        )

        assert changed is True
        client.unassign_machine_user_resource_role.assert_not_called()

    def test_purge_replaces_assignments(self, client):
        changed = client.manage_machine_user_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_assignments=[ASSIGNMENT],
            desired_assignments=[OTHER_ASSIGNMENT],
            purge=True,
        )

        assert changed is True
        client.unassign_machine_user_resource_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            resource_crn=RESOURCE_CRN,
            resource_role_crn=RESOURCE_ROLE_CRN,
        )
        client.assign_machine_user_resource_role.assert_called_once_with(
            machine_user_name=MACHINE_USER_NAME,
            resource_crn=OTHER_RESOURCE_CRN,
            resource_role_crn=OTHER_RESOURCE_ROLE_CRN,
        )

    def test_purge_with_nothing_desired_removes_all(self, client):
        changed = client.manage_machine_user_resource_roles(
            machine_user_name=MACHINE_USER_NAME,
            current_assignments=[ASSIGNMENT, OTHER_ASSIGNMENT],
            desired_assignments=[],
            purge=True,
        )

        assert changed is True
        assert client.unassign_machine_user_resource_role.call_count == 2
        client.assign_machine_user_resource_role.assert_not_called()
