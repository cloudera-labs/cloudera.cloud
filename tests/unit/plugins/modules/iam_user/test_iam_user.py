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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import CdpError
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    ResourceAssignment,
    User,
    UserDetails,
)
from ansible_collections.cloudera.cloud.plugins.modules import iam_user
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

USER_EMAIL = "test-user@example.com"
USER_ID = "test-user-id"
USER_CRN = f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}"
IDP_USER_ID = "test-idp-user-id"

ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:PowerUser"
OLD_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:role:OldRole"
RESOURCE_CRN = "crn:cdp:environments:us-west-1:altus:environment:dev-env"
RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser"
DEVELOPERS_CRN = "crn:cdp:iam:us-west-1:altus:group:developers/group-id-1"
ADMINS_CRN = "crn:cdp:iam:us-west-1:altus:group:admins/group-id-2"

ASSIGNMENT = ResourceAssignment(
    resourceCrn=RESOURCE_CRN,
    resourceRoleCrn=RESOURCE_ROLE_CRN,
)


@pytest.fixture
def user_module_args(module_args):
    """Pre-populate the common credentials for iam_user module arguments."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    )
    return mock_class.return_value


def _user(**overrides) -> UserDetails:
    """A user with no roles, resource roles or groups, unless overridden."""
    fields = {
        "userId": USER_ID,
        "email": USER_EMAIL,
        "crn": USER_CRN,
        "roles": [],
        "resourceAssignments": [],
        "groups": [],
    }
    fields.update(overrides)
    return UserDetails(**fields)


def test_iam_user_default(user_module_args):
    """Test iam_user module with missing parameters."""

    user_module_args()

    with pytest.raises(
        AnsibleFailJson,
        match="one of the following is required: user_id, email",
    ):
        iam_user.main()


def test_iam_user_absent_missing_identifiers(user_module_args):
    """Test iam_user module with state=absent but missing both user_id and email."""

    user_module_args({"state": "absent"})

    with pytest.raises(
        AnsibleFailJson,
        match="one of the following is required: user_id, email",
    ):
        iam_user.main()


def test_iam_user_create_missing_email(user_module_args, client):
    """Test iam_user module creating a new user without email fails."""

    user_module_args({"user_id": "some-user-id", "state": "present"})
    client.get_user_details.return_value = None

    with pytest.raises(
        AnsibleFailJson,
        match="email is required to create a new user",
    ):
        iam_user.main()

    client.create_user.assert_not_called()


def test_iam_user_create_missing_email_check_mode(user_module_args, client):
    """Test iam_user module fails on a missing email even in check mode."""

    user_module_args(
        {
            "user_id": "some-user-id",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )
    client.get_user_details.return_value = None

    with pytest.raises(
        AnsibleFailJson,
        match="email is required to create a new user",
    ):
        iam_user.main()

    client.create_user.assert_not_called()


# --- state=absent -----------------------------------------------------------


def test_iam_user_absent(user_module_args, client):
    """Test iam_user module with state=absent, identified by user_id."""

    user_module_args({"user_id": USER_EMAIL, "state": "absent"})
    client.get_user_details.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user == {}
    assert "diff" not in result.value

    client.get_user_details.assert_called_once_with(user_id=USER_EMAIL)
    # The resolved user ID is used for deletion, not the identifier that was supplied
    client.delete_user.assert_called_once_with(user_id=USER_ID)


def test_iam_user_absent_by_email(user_module_args, client):
    """Test iam_user module with state=absent, identified by email."""

    user_module_args({"email": USER_EMAIL, "state": "absent"})
    client.get_user_details_by_email.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.get_user_details_by_email.assert_called_once_with(email=USER_EMAIL)
    client.delete_user.assert_called_once_with(user_id=USER_ID)


def test_iam_user_absent_not_found(user_module_args, client):
    """Test iam_user module with state=absent is idempotent for a missing user."""

    user_module_args({"email": USER_EMAIL, "state": "absent"})
    client.get_user_details_by_email.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user == {}
    assert "diff" not in result.value

    client.delete_user.assert_not_called()


def test_iam_user_absent_check_mode(user_module_args, client):
    """Test iam_user module with state=absent reports a change without deleting."""

    user_module_args(
        {"email": USER_EMAIL, "state": "absent", "_ansible_check_mode": True},
    )
    client.get_user_details_by_email.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.delete_user.assert_not_called()


def test_iam_user_absent_reports_diff(user_module_args, client):
    """Test iam_user module with state=absent puts the user in diff.before."""

    user_module_args(
        {"email": USER_EMAIL, "state": "absent", "_ansible_diff": True},
    )
    client.get_user_details_by_email.return_value = _user(
        firstName="Test",
        roles=[ROLE_CRN],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"]["user_id"] == USER_ID
    assert result.value.diff["before"]["first_name"] == "Test"
    assert result.value.diff["before"]["roles"] == [ROLE_CRN]
    assert result.value.diff["after"] == {}


# --- create -----------------------------------------------------------------


def test_iam_user_create(user_module_args, client):
    """Test iam_user module creating a new user."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "first_name": "Test",
            "last_name": "User",
            "saml_provider_name": "mtaabich-test",
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(
        userId=USER_ID,
        email=USER_EMAIL,
        firstName="Test",
        lastName="User",
        crn=USER_CRN,
    )
    client.get_user_details.return_value = _user(firstName="Test", lastName="User")

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL
    assert result.value.user["first_name"] == "Test"
    assert result.value.user["last_name"] == "User"
    assert result.value.user["user_id"] == USER_ID

    client.create_user.assert_called_once_with(
        email=USER_EMAIL,
        identity_provider_user_id=IDP_USER_ID,
        first_name="Test",
        last_name="User",
        saml_provider_name="mtaabich-test",
    )
    client.get_user_details.assert_called_with(user_id=USER_ID)

    # Nothing was requested beyond the user itself
    client.manage_user_groups.assert_not_called()
    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()
    client.set_workload_password.assert_not_called()


def test_iam_user_create_idp_user_id_defaults_to_email(user_module_args, client):
    """Test iam_user module defaults the identity provider user ID to the email."""

    user_module_args({"email": USER_EMAIL, "state": "present"})
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(userId=USER_ID, email=USER_EMAIL)
    client.get_user_details.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.create_user.assert_called_once_with(
        email=USER_EMAIL,
        identity_provider_user_id=USER_EMAIL,
        first_name=None,
        last_name=None,
        saml_provider_name=None,
    )


def test_iam_user_create_with_groups(user_module_args, client):
    """Test iam_user module creating a new user with group assignments."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "groups": ["developers", "admins"],
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(userId=USER_ID, email=USER_EMAIL)
    client.get_user_details.return_value = _user()
    client.manage_user_groups.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Group membership is not part of user creation
    client.create_user.assert_called_once_with(
        email=USER_EMAIL,
        identity_provider_user_id=IDP_USER_ID,
        first_name=None,
        last_name=None,
        saml_provider_name=None,
    )
    client.manage_user_groups.assert_called_once_with(
        user_id=USER_ID,
        current_groups=[],
        desired_groups=["developers", "admins"],
        purge=False,
    )


def test_iam_user_create_with_nonexistent_group(user_module_args, client):
    """Test iam_user module fails when trying to add user to non-existent group."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "groups": ["nonexistent-group"],
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(userId=USER_ID, email=USER_EMAIL)
    client.get_user_details.return_value = _user()
    client.manage_user_groups.side_effect = CdpError(
        "Group 'nonexistent-group' does not exist. "
        "Please create the group using the iam_group module before adding users to it.",
        status=404,
    )

    with pytest.raises(CdpError) as exc_info:
        iam_user.main()

    assert "nonexistent-group" in str(exc_info.value)
    assert "does not exist" in str(exc_info.value)


def test_iam_user_create_with_roles_and_resource_roles(user_module_args, client):
    """Test iam_user module creating a new user with roles and resource roles."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "resource_roles": [
                {"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN},
            ],
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(userId=USER_ID, email=USER_EMAIL)
    client.get_user_details.side_effect = [
        _user(),
        _user(roles=[ROLE_CRN], resourceAssignments=[ASSIGNMENT]),
    ]
    client.manage_user_roles.return_value = True
    client.manage_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["roles"] == [ROLE_CRN]
    assert result.value.user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[],
        desired_roles=[ROLE_CRN],
        purge=False,
    )
    client.manage_user_resource_roles.assert_called_once_with(
        user_id=USER_ID,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )


def test_iam_user_create_with_workload_password(user_module_args, client):
    """Test iam_user module creating a new user with workload password."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "workload_password": "SecurePassword123!",
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = None
    client.create_user.return_value = User(userId=USER_ID, email=USER_EMAIL)
    client.get_user_details.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.create_user.assert_called_once()
    client.set_workload_password.assert_called_once_with(
        password="SecurePassword123!",
        actor_crn=USER_CRN,
    )


def test_iam_user_create_check_mode(user_module_args, client):
    """Test iam_user module reports a create without calling the API."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "groups": ["developers"],
            "state": "present",
            "_ansible_check_mode": True,
        },
    )
    client.get_user_details_by_email.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user == {}

    client.create_user.assert_not_called()
    client.get_user_details.assert_not_called()
    client.manage_user_groups.assert_not_called()


def test_iam_user_create_reports_diff(user_module_args, client):
    """Test iam_user module puts the requested user in diff.after on create."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "first_name": "Test",
            "last_name": "User",
            "groups": ["developers"],
            "roles": [ROLE_CRN],
            "resource_roles": [
                {"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN},
            ],
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "email": USER_EMAIL,
        "first_name": "Test",
        "last_name": "User",
        "groups": ["developers"],
        "roles": [ROLE_CRN],
        "resource_assignments": [
            {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
        ],
    }


# --- update -----------------------------------------------------------------


def test_iam_user_present_no_changes(user_module_args, client):
    """Test iam_user module with state=present but no changes needed."""

    user_module_args({"email": USER_EMAIL, "state": "present"})
    client.get_user_details_by_email.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user["email"] == USER_EMAIL
    assert "diff" not in result.value

    client.get_user_details_by_email.assert_called_once_with(email=USER_EMAIL)
    client.get_user_details.assert_not_called()
    client.manage_user_groups.assert_not_called()
    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_email_takes_precedence_over_user_id(user_module_args, client):
    """Test iam_user module looks the user up by email when both identifiers are given."""

    user_module_args(
        {"email": USER_EMAIL, "user_id": "some-other-id", "state": "present"},
    )
    client.get_user_details_by_email.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False

    client.get_user_details_by_email.assert_called_once_with(email=USER_EMAIL)
    client.get_user_details.assert_not_called()


def test_iam_user_assign_roles(user_module_args, client):
    """Test iam_user module assigning roles to an existing user."""

    user_module_args({"email": USER_EMAIL, "roles": [ROLE_CRN], "state": "present"})
    client.get_user_details_by_email.return_value = _user()
    client.get_user_details.return_value = _user(roles=[ROLE_CRN])
    client.manage_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["roles"] == [ROLE_CRN]

    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[],
        desired_roles=[ROLE_CRN],
        purge=False,
    )
    client.get_user_details.assert_called_once_with(user_id=USER_ID)
    client.manage_user_groups.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_assign_roles_already_assigned(user_module_args, client):
    """Test iam_user module is idempotent when the roles are already assigned."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "state": "present",
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user(roles=[ROLE_CRN])
    client.manage_user_roles.return_value = False

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user["roles"] == [ROLE_CRN]
    assert "diff" not in result.value

    client.get_user_details.assert_not_called()


def test_iam_user_assign_resource_roles(user_module_args, client):
    """Test iam_user module assigning resource roles to an existing user."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "resource_roles": [
                {"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN},
            ],
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = _user()
    client.get_user_details.return_value = _user(resourceAssignments=[ASSIGNMENT])
    client.manage_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["resource_assignments"] == [
        {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
    ]

    client.manage_user_resource_roles.assert_called_once_with(
        user_id=USER_ID,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )
    client.manage_user_roles.assert_not_called()


def test_iam_user_assign_resource_roles_with_aliases(user_module_args, client):
    """Test iam_user module accepts resource_crn/resource_role_crn for resource roles."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "resource_roles": [
                {"resource_crn": RESOURCE_CRN, "resource_role_crn": RESOURCE_ROLE_CRN},
            ],
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = _user()
    client.get_user_details.return_value = _user(resourceAssignments=[ASSIGNMENT])
    client.manage_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.manage_user_resource_roles.assert_called_once_with(
        user_id=USER_ID,
        current_assignments=[],
        desired_assignments=[ASSIGNMENT],
        purge=False,
    )


def test_iam_user_purge_roles(user_module_args, client):
    """Test iam_user module purging roles from a user."""

    user_module_args(
        {"email": USER_EMAIL, "roles": [], "purge": True, "state": "present"},
    )
    client.get_user_details_by_email.return_value = _user(roles=[OLD_ROLE_CRN])
    client.get_user_details.return_value = _user()
    client.manage_user_roles.return_value = True
    client.manage_user_resource_roles.return_value = False

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["roles"] == []

    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[OLD_ROLE_CRN],
        desired_roles=[],
        purge=True,
    )


def test_iam_user_purge_groups(user_module_args, client):
    """Test iam_user module purging group memberships not in the specified groups list."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "groups": ["developers"],
            "purge": True,
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = _user(
        groups=[DEVELOPERS_CRN, ADMINS_CRN],
    )
    client.get_group_names.return_value = ["developers", "admins"]
    client.get_user_details.return_value = _user(groups=[DEVELOPERS_CRN])
    client.manage_user_groups.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["groups"] == [DEVELOPERS_CRN]

    client.get_group_names.assert_called_once_with([DEVELOPERS_CRN, ADMINS_CRN])
    client.manage_user_groups.assert_called_once_with(
        user_id=USER_ID,
        current_groups=[DEVELOPERS_CRN, ADMINS_CRN],
        desired_groups=["developers"],
        purge=True,
    )

    # roles and resource_roles were not specified, so they are left untouched
    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_purge_without_groups_preserves_membership(user_module_args, client):
    """Test iam_user module with purge=True does not touch group membership when groups is not specified.

    Regression test: purge=True previously removed all of a user's group
    memberships whenever the groups attribute was omitted, even though
    purge is only meant to reconcile attributes explicitly managed by the task.
    """

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [],
            "resource_roles": [],
            "purge": True,
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        groups=[DEVELOPERS_CRN, ADMINS_CRN],
    )
    client.get_user_details.return_value = _user(groups=[DEVELOPERS_CRN, ADMINS_CRN])
    client.manage_user_roles.return_value = True
    client.manage_user_resource_roles.return_value = False

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # groups was not specified, so group membership must be left untouched
    client.manage_user_groups.assert_not_called()
    client.get_group_names.assert_not_called()
    assert result.value.user["groups"] == [DEVELOPERS_CRN, ADMINS_CRN]

    # roles was specified, so purge still reconciles roles as before
    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[OLD_ROLE_CRN],
        desired_roles=[],
        purge=True,
    )


def test_iam_user_purge_without_managed_attributes_changes_nothing(
    user_module_args,
    client,
):
    """Test iam_user module with purge=True leaves roles, resource roles and groups alone when none are specified."""

    user_module_args({"email": USER_EMAIL, "purge": True, "state": "present"})
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
        groups=[DEVELOPERS_CRN],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user["roles"] == [OLD_ROLE_CRN]

    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()
    client.manage_user_groups.assert_not_called()
    client.set_workload_password.assert_not_called()


def test_iam_user_purge_without_managed_attributes_reports_no_diff(
    user_module_args,
    client,
):
    """Test iam_user module with purge=True and nothing specified plans no changes in check mode."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "purge": True,
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
        groups=[DEVELOPERS_CRN],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert "diff" not in result.value


def test_iam_user_purge_roles_only_preserves_resource_roles(user_module_args, client):
    """Test iam_user module with purge=True and only roles specified does not touch resource roles."""

    user_module_args(
        {"email": USER_EMAIL, "roles": [ROLE_CRN], "purge": True, "state": "present"},
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )
    client.get_user_details.return_value = _user(
        roles=[ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )
    client.manage_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[OLD_ROLE_CRN],
        desired_roles=[ROLE_CRN],
        purge=True,
    )
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_purge_resource_roles_only_preserves_roles(user_module_args, client):
    """Test iam_user module with purge=True and only resource_roles specified does not touch roles."""

    user_module_args(
        {"email": USER_EMAIL, "resource_roles": [], "purge": True, "state": "present"},
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )
    client.get_user_details.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[],
    )
    client.manage_user_resource_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.manage_user_resource_roles.assert_called_once_with(
        user_id=USER_ID,
        current_assignments=[ASSIGNMENT],
        desired_assignments=[],
        purge=True,
    )
    client.manage_user_roles.assert_not_called()


def test_iam_user_set_workload_password(user_module_args, client):
    """Test iam_user module setting workload password for a user."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "workload_password": "SecurePassword123!",
            "state": "present",
        },
    )
    client.get_user_details_by_email.return_value = _user()
    client.get_user_details.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.set_workload_password.assert_called_once_with(
        password="SecurePassword123!",
        actor_crn=USER_CRN,
    )


def test_iam_user_set_workload_password_by_user_id(user_module_args, client):
    """Test iam_user module resetting the workload password of an existing user without an email."""

    user_module_args(
        {
            "user_id": USER_ID,
            "workload_password": "SecurePassword123!",
            "state": "present",
        },
    )
    client.get_user_details.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["user_id"] == USER_ID

    client.get_user_details_by_email.assert_not_called()
    client.create_user.assert_not_called()
    client.set_workload_password.assert_called_once_with(
        password="SecurePassword123!",
        actor_crn=USER_CRN,
    )


def test_iam_user_assign_roles_by_user_id(user_module_args, client):
    """Test iam_user module updating an existing user identified only by user_id."""

    user_module_args(
        {"user_id": USER_ID, "roles": [ROLE_CRN], "state": "present"},
    )
    client.get_user_details.return_value = _user()
    client.manage_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    client.create_user.assert_not_called()
    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,
        current_roles=[],
        desired_roles=[ROLE_CRN],
        purge=False,
    )


def test_iam_user_set_workload_password_check_mode(user_module_args, client):
    """Test iam_user module reports a workload password change without applying it."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "workload_password": "SecurePassword123!",
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user()

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    # The password is never part of the diff
    assert "diff" not in result.value

    client.set_workload_password.assert_not_called()


def test_iam_user_update_check_mode_reports_diff(user_module_args, client):
    """Test iam_user module diffs additive roles and groups without applying them."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "groups": ["developers", "admins"],
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        groups=[DEVELOPERS_CRN],
    )
    client.get_group_names.return_value = ["developers"]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    # The reported user is the existing one, since nothing was applied
    assert result.value.user["roles"] == [OLD_ROLE_CRN]
    assert result.value.user["groups"] == [DEVELOPERS_CRN]

    # Groups are compared by name on both sides of the diff
    assert result.value.diff["before"] == {
        "roles": [OLD_ROLE_CRN],
        "groups": ["developers"],
    }
    assert result.value.diff["after"] == {
        "roles": sorted([OLD_ROLE_CRN, ROLE_CRN]),
        "groups": ["admins", "developers"],
    }

    client.get_user_details.assert_not_called()
    client.manage_user_groups.assert_not_called()
    client.manage_user_roles.assert_not_called()


def test_iam_user_update_check_mode_purge_reports_diff(user_module_args, client):
    """Test iam_user module diffs a purge of roles and resource roles."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "resource_roles": [],
            "purge": True,
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[OLD_ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

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

    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_check_mode_no_changes(user_module_args, client):
    """Test iam_user module in check mode is idempotent for a matching user."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "resource_roles": [
                {"resource": RESOURCE_CRN, "role": RESOURCE_ROLE_CRN},
            ],
            "groups": ["developers"],
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user(
        roles=[ROLE_CRN],
        resourceAssignments=[ASSIGNMENT],
        groups=[DEVELOPERS_CRN],
    )
    client.get_group_names.return_value = ["developers"]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert "diff" not in result.value

    client.manage_user_groups.assert_not_called()
    client.manage_user_roles.assert_not_called()
    client.manage_user_resource_roles.assert_not_called()


def test_iam_user_update_reports_diff(user_module_args, client):
    """Test iam_user module reports the planned change in diff when applying it."""

    user_module_args(
        {
            "email": USER_EMAIL,
            "roles": [ROLE_CRN],
            "state": "present",
            "_ansible_diff": True,
        },
    )
    client.get_user_details_by_email.return_value = _user()
    client.get_user_details.return_value = _user(roles=[ROLE_CRN])
    client.manage_user_roles.return_value = True

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.diff["before"] == {"roles": []}
    assert result.value.diff["after"] == {"roles": [ROLE_CRN]}
