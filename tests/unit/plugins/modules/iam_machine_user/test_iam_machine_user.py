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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    MachineUser,
    MachineUserDetails,
    ResourceAssignment,
)
from ansible_collections.cloudera.cloud.plugins.modules import iam_machine_user
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MACHINE_USER_NAME = "test-machine-user"
MACHINE_USER_CRN = f"crn:cdp:iam:us-west-1:altus:machineUser:{MACHINE_USER_NAME}/id-1"

ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:PowerUser"
OLD_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:OldRole"
RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:dev-env"
RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser"
OTHER_RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:prod-env"
OTHER_RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentAdmin"

ASSIGNMENT = ResourceAssignment(
    resourceCrn=RESOURCE_CRN,
    resourceRoleCrn=RESOURCE_ROLE_CRN,
)
OTHER_ASSIGNMENT = ResourceAssignment(
    resourceCrn=OTHER_RESOURCE_CRN,
    resourceRoleCrn=OTHER_RESOURCE_ROLE_CRN,
)

RESOURCE_ROLES_ARG = [{"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN}]


@pytest.fixture
def machine_user_module_args(module_args):
    """Pre-populate the common credentials for iam_machine_user module arguments."""

    def wrapped_args(args=None):
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        }
        merged.update(args or {})
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def client(mocker):
    """Patch load_cdp_config and CdpIamClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user.CdpIamClient",
        autospec=True,
    )
    return mock_class.return_value


def _machine_user(**overrides) -> MachineUserDetails:
    """A machine user with no roles or resource roles, unless overridden."""
    fields = {
        "machineUserName": MACHINE_USER_NAME,
        "crn": MACHINE_USER_CRN,
        "status": "ACTIVE",
        "roles": [],
        "resourceAssignments": [],
    }
    fields.update(overrides)
    return MachineUserDetails(**fields)


def test_iam_machine_user_default(machine_user_module_args):
    """Test iam_machine_user module with missing parameters."""

    machine_user_module_args()

    with pytest.raises(AnsibleFailJson, match="missing required arguments: name"):
        iam_machine_user.main()


def test_iam_machine_user_name_alias(machine_user_module_args, client):
    """Test that machine_user_name is accepted as an alias of name."""

    machine_user_module_args({"machine_user_name": MACHINE_USER_NAME})
    client.get_machine_user_details.return_value = _machine_user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    client.get_machine_user_details.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
    )


def test_iam_machine_user_absent(machine_user_module_args, client):
    """Test iam_machine_user module with state=absent deletes an existing machine user."""

    machine_user_module_args({"name": MACHINE_USER_NAME, "state": "absent"})
    client.get_machine_user_details.return_value = _machine_user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user == {}
    assert "diff" not in result.value

    client.get_machine_user_details.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
    )
    client.delete_machine_user.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
    )


def test_iam_machine_user_absent_not_found(machine_user_module_args, client):
    """Test iam_machine_user module with state=absent is a no-op for a missing machine user."""

    machine_user_module_args({"name": MACHINE_USER_NAME, "state": "absent"})
    client.get_machine_user_details.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert result.value.machine_user == {}

    client.delete_machine_user.assert_not_called()


def test_iam_machine_user_absent_check_mode(machine_user_module_args, client):
    """Test iam_machine_user module with state=absent in check mode reports the machine user that would be deleted."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME

    client.delete_machine_user.assert_not_called()


def test_iam_machine_user_absent_reports_diff(machine_user_module_args, client):
    """Test iam_machine_user module reports the removed machine user in diff."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "state": "absent",
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(roles=[ROLE_CRN])

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {
        "machine_user_name": MACHINE_USER_NAME,
        "crn": MACHINE_USER_CRN,
        "status": "ACTIVE",
        "roles": [ROLE_CRN],
        "resource_assignments": [],
    }
    assert result.value.diff["after"] == {}


def test_iam_machine_user_create(machine_user_module_args, client):
    """Test iam_machine_user module creates a missing machine user."""

    machine_user_module_args({"name": MACHINE_USER_NAME})
    client.get_machine_user_details.side_effect = [
        None,
        _machine_user(),
        _machine_user(),
    ]
    client.create_machine_user.return_value = MachineUser(
        machineUserName=MACHINE_USER_NAME,
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user == {
        "machine_user_name": MACHINE_USER_NAME,
        "crn": MACHINE_USER_CRN,
        "status": "ACTIVE",
        "roles": [],
        "resource_assignments": [],
    }
    assert "diff" not in result.value

    client.create_machine_user.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
    )
    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_create_with_roles_and_resource_roles(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module assigns roles and resource roles to a new machine user."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "resource_roles": RESOURCE_ROLES_ARG,
        },
    )
    client.get_machine_user_details.side_effect = [
        None,
        _machine_user(),
        _machine_user(roles=[ROLE_CRN], resourceAssignments=[ASSIGNMENT]),
    ]
    client.create_machine_user.return_value = MachineUser(
        machineUserName=MACHINE_USER_NAME,
    )
    client.manage_machine_user_roles.return_value = True
    client.manage_machine_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["roles"] == [ROLE_CRN]
    assert result.value.machine_user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_machine_user_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_roles=[],
        desired_roles=[ROLE_CRN],
        purge=False,
    )
    client.manage_machine_user_resource_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )


def test_iam_machine_user_create_check_mode(machine_user_module_args, client):
    """Test iam_machine_user module reports a change without creating the machine user in check mode."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "_ansible_check_mode": True,
        },
    )
    client.get_machine_user_details.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user == {}

    client.create_machine_user.assert_not_called()
    client.manage_machine_user_roles.assert_not_called()


def test_iam_machine_user_create_reports_diff(machine_user_module_args, client):
    """Test iam_machine_user module reports the requested machine user in diff when creating it."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "resource_roles": RESOURCE_ROLES_ARG,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "machine_user_name": MACHINE_USER_NAME,
        "roles": [ROLE_CRN],
        "resource_assignments": [
            {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
        ],
    }


def test_iam_machine_user_present_no_changes(machine_user_module_args, client):
    """Test iam_machine_user module is idempotent for an existing machine user."""

    machine_user_module_args({"name": MACHINE_USER_NAME})
    client.get_machine_user_details.return_value = _machine_user(roles=[ROLE_CRN])

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME
    assert result.value.machine_user["roles"] == [ROLE_CRN]
    assert "diff" not in result.value

    client.create_machine_user.assert_not_called()
    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()
    client.get_machine_user_details.assert_called_once()


def test_iam_machine_user_assign_roles(machine_user_module_args, client):
    """Test iam_machine_user module assigns missing roles to an existing machine user."""

    machine_user_module_args({"name": MACHINE_USER_NAME, "roles": [ROLE_CRN]})
    client.get_machine_user_details.side_effect = [
        _machine_user(roles=[OLD_ROLE_CRN]),
        _machine_user(roles=[OLD_ROLE_CRN, ROLE_CRN]),
    ]
    client.manage_machine_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["roles"] == [OLD_ROLE_CRN, ROLE_CRN]

    client.manage_machine_user_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_roles=[OLD_ROLE_CRN],
        desired_roles=[ROLE_CRN],
        purge=False,
    )
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_assign_roles_already_assigned(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module is idempotent when the roles are already assigned."""

    machine_user_module_args({"name": MACHINE_USER_NAME, "roles": [ROLE_CRN]})
    client.get_machine_user_details.return_value = _machine_user(roles=[ROLE_CRN])
    client.manage_machine_user_roles.return_value = False

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert result.value.machine_user["roles"] == [ROLE_CRN]
    client.get_machine_user_details.assert_called_once()


def test_iam_machine_user_assign_resource_roles(machine_user_module_args, client):
    """Test iam_machine_user module assigns resource roles to an existing machine user."""

    machine_user_module_args(
        {"name": MACHINE_USER_NAME, "resource_roles": RESOURCE_ROLES_ARG},
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(),
        _machine_user(resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_machine_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_machine_user_resource_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )
    client.manage_machine_user_roles.assert_not_called()


def test_iam_machine_user_assign_resource_roles_with_aliases(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module accepts the resource_crn and resource_role_crn aliases."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "resource_roles": [
                {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
            ],
        },
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(),
        _machine_user(resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_machine_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    client.manage_machine_user_resource_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )


def test_iam_machine_user_purge_roles(machine_user_module_args, client):
    """Test iam_machine_user module replaces roles when purge is set."""

    machine_user_module_args(
        {"name": MACHINE_USER_NAME, "roles": [ROLE_CRN], "purge": True},
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(roles=[OLD_ROLE_CRN]),
        _machine_user(roles=[ROLE_CRN]),
    ]
    client.manage_machine_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["roles"] == [ROLE_CRN]

    client.manage_machine_user_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_roles=[OLD_ROLE_CRN],
        desired_roles=[ROLE_CRN],
        purge=True,
    )
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_purge_resource_roles(machine_user_module_args, client):
    """Test iam_machine_user module replaces resource roles when purge is set."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "resource_roles": RESOURCE_ROLES_ARG,
            "purge": True,
        },
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(resourceAssignments=[OTHER_ASSIGNMENT]),
        _machine_user(resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_machine_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True

    client.manage_machine_user_resource_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_assignments=[OTHER_ASSIGNMENT],
        desired_assignments=[ASSIGNMENT],
        purge=True,
    )
    client.manage_machine_user_roles.assert_not_called()


def test_iam_machine_user_purge_with_empty_list_removes_all_roles(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module removes every role when roles is an explicit empty list with purge."""

    machine_user_module_args(
        {"name": MACHINE_USER_NAME, "roles": [], "purge": True},
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(roles=[OLD_ROLE_CRN, ROLE_CRN]),
        _machine_user(roles=[]),
    ]
    client.manage_machine_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["roles"] == []

    client.manage_machine_user_roles.assert_called_once_with(
        machine_user_name=MACHINE_USER_NAME,
        current_roles=[OLD_ROLE_CRN, ROLE_CRN],
        desired_roles=[],
        purge=True,
    )


def test_iam_machine_user_purge_without_managed_attributes_changes_nothing(
    machine_user_module_args,
    client,
):
    """Test that purge alone leaves roles and resource roles untouched, since neither is specified."""

    machine_user_module_args({"name": MACHINE_USER_NAME, "purge": True})
    client.get_machine_user_details.return_value = _machine_user(
        roles=[ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert result.value.machine_user["roles"] == [ROLE_CRN]
    assert result.value.machine_user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_purge_without_managed_attributes_reports_no_diff(
    machine_user_module_args,
    client,
):
    """Test that purge alone reports neither a change nor a diff in check mode."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "purge": True,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(
        roles=[ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert "diff" not in result.value


def test_iam_machine_user_purge_roles_only_preserves_resource_roles(
    machine_user_module_args,
    client,
):
    """Test that purging roles never touches resource roles when they are not specified."""

    machine_user_module_args(
        {"name": MACHINE_USER_NAME, "roles": [ROLE_CRN], "purge": True},
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(roles=[OLD_ROLE_CRN], resourceAssignments=[ASSIGNMENT]),
        _machine_user(roles=[ROLE_CRN], resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_machine_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_machine_user_roles.assert_called_once()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_purge_resource_roles_only_preserves_roles(
    machine_user_module_args,
    client,
):
    """Test that purging resource roles never touches roles when they are not specified."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "resource_roles": RESOURCE_ROLES_ARG,
            "purge": True,
        },
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(roles=[ROLE_CRN], resourceAssignments=[OTHER_ASSIGNMENT]),
        _machine_user(roles=[ROLE_CRN], resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_machine_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["roles"] == [ROLE_CRN]

    client.manage_machine_user_resource_roles.assert_called_once()
    client.manage_machine_user_roles.assert_not_called()


def test_iam_machine_user_update_check_mode_reports_diff(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module diffs additive roles and resource roles without applying them."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "resource_roles": RESOURCE_ROLES_ARG,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[OTHER_ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    # The reported machine user is the existing one, since nothing was applied
    assert result.value.machine_user["roles"] == [OLD_ROLE_CRN]

    assert result.value.diff["before"] == {
        "roles": [OLD_ROLE_CRN],
        "resource_assignments": [
            {
                "resource_crn": OTHER_RESOURCE_CRN,
                "resource_role_crn": OTHER_RESOURCE_ROLE_CRN,
            },
        ],
    }
    assert result.value.diff["after"] == {
        "roles": sorted([OLD_ROLE_CRN, ROLE_CRN]),
        "resource_assignments": sorted(
            [
                {
                    "resource_crn": OTHER_RESOURCE_CRN,
                    "resource_role_crn": OTHER_RESOURCE_ROLE_CRN,
                },
                {
                    "resource_crn": RESOURCE_CRN,
                    "resource_role_crn": RESOURCE_ROLE_CRN,
                },
            ],
            key=lambda assignment: assignment["resource_crn"],
        ),
    }

    client.get_machine_user_details.assert_called_once()
    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_update_check_mode_purge_reports_diff(
    machine_user_module_args,
    client,
):
    """Test iam_machine_user module diffs a purge of roles and resource roles."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "resource_roles": [],
            "purge": True,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {
        "roles": [OLD_ROLE_CRN],
        "resource_assignments": [
            {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
        ],
    }
    assert result.value.diff["after"] == {
        "roles": [ROLE_CRN],
        "resource_assignments": [],
    }

    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_check_mode_no_changes(machine_user_module_args, client):
    """Test iam_machine_user module in check mode is idempotent for a matching machine user."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "resource_roles": RESOURCE_ROLES_ARG,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(
        roles=[ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert "diff" not in result.value

    client.manage_machine_user_roles.assert_not_called()
    client.manage_machine_user_resource_roles.assert_not_called()


def test_iam_machine_user_check_mode_ignores_ordering(machine_user_module_args, client):
    """Test that the order of roles and resource roles never registers as a change."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN, OLD_ROLE_CRN],
            "resource_roles": [
                {"resource": OTHER_RESOURCE_CRN, "role": OTHER_RESOURCE_ROLE_CRN},
                {"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN},
            ],
            "purge": True,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.return_value = _machine_user(
        roles=[OLD_ROLE_CRN, ROLE_CRN],
        resourceAssignments=[ASSIGNMENT, OTHER_ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert "diff" not in result.value


def test_iam_machine_user_update_reports_diff(machine_user_module_args, client):
    """Test iam_machine_user module reports the planned change in diff when applying it."""

    machine_user_module_args(
        {
            "name": MACHINE_USER_NAME,
            "roles": [ROLE_CRN],
            "_ansible_diff": True,
        },
    )
    client.get_machine_user_details.side_effect = [
        _machine_user(),
        _machine_user(roles=[ROLE_CRN]),
    ]
    client.manage_machine_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {"roles": []}
    assert result.value.diff["after"] == {"roles": [ROLE_CRN]}
