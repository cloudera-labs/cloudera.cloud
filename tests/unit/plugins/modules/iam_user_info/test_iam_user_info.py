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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    ResourceAssignment,
    User,
    UserDetails,
)
from ansible_collections.cloudera.cloud.plugins.modules import iam_user_info
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

ROLE_CRN = "crn:cdp:iam:us-west-1:account:role:IAMUser"
RESOURCE_CRN = "crn:cdp:environments:us-west-1:account:environment:env1"
RESOURCE_ROLE_CRN = "crn:cdp:iam:us-west-1:account:resourceRole:EnvironmentUser"
GROUP_CRN = "crn:cdp:iam:us-west-1:account:group:test-group"

USER_1_BASIC = User(
    userId="user-id-1",
    crn="crn:cdp:iam:us-west-1:account:user:user-id-1",
    email="user1@example.com",
    firstName="User",
    lastName="One",
    workloadUsername="u_user1",
    creationDate="2025-01-01T00:00:00.000Z",
)

USER_2_BASIC = User(
    userId="user-id-2",
    crn="crn:cdp:iam:us-west-1:account:user:user-id-2",
    email="user2@example.com",
    firstName="User",
    lastName="Two",
    workloadUsername="u_user2",
    creationDate="2025-01-02T00:00:00.000Z",
)

USER_1_DETAILS = UserDetails(
    **{**vars(USER_1_BASIC), "status": "active"},
    roles=[],
    resourceAssignments=[],
    groups=[],
)

USER_2_DETAILS = UserDetails(
    **{**vars(USER_2_BASIC), "status": "active"},
    roles=[ROLE_CRN],
    resourceAssignments=[
        ResourceAssignment(
            resourceCrn=RESOURCE_CRN,
            resourceRoleCrn=RESOURCE_ROLE_CRN,
        ),
    ],
    groups=[GROUP_CRN],
)


@pytest.fixture
def user_info_module_args(module_args):
    """Pre-populate the common credentials for iam_user_info module arguments."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user_info.CdpIamClient",
        autospec=True,
    )
    return mock_class.return_value


def test_iam_user_info_mutually_exclusive(user_info_module_args):
    """Test that name and current_user cannot be combined."""

    user_info_module_args({"name": "u_user1", "current_user": True})

    with pytest.raises(AnsibleFailJson) as result:
        iam_user_info.main()

    assert "mutually exclusive" in result.value.msg


def test_iam_user_info_list_all_users(user_info_module_args, client):
    """Test listing all IAM users with summary view returns basic info without details."""

    user_info_module_args({"view": "summary"})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert result.value.users[1]["workloadUsername"] == "u_user2"
    # summary view should NOT include roles/groups/resource_roles
    assert "roles" not in result.value.users[0]
    assert "groups" not in result.value.users[0]
    assert "resource_roles" not in result.value.users[0]

    client.list_users.assert_called_once_with()
    client.get_user_details.assert_not_called()


def test_iam_user_info_output_shape(user_info_module_args, client):
    """Test that the documented output keys are produced from the dataclass fields."""

    user_info_module_args({"user_id": ["user-id-2"]})

    client.list_users.return_value = [USER_2_BASIC]
    client.get_user_details.return_value = USER_2_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.users == [
        {
            "userId": "user-id-2",
            "crn": "crn:cdp:iam:us-west-1:account:user:user-id-2",
            "email": "user2@example.com",
            "firstName": "User",
            "lastName": "Two",
            "workloadUsername": "u_user2",
            "creationDate": "2025-01-02T00:00:00.000Z",
            "status": "active",
            "roles": [ROLE_CRN],
            "groups": [GROUP_CRN],
            "resource_roles": [
                {
                    "resourceCrn": RESOURCE_CRN,
                    "resourceRoleCrn": RESOURCE_ROLE_CRN,
                },
            ],
        },
    ]


def test_iam_user_info_current_user(user_info_module_args, client):
    """Test retrieving the current authenticated user."""

    user_info_module_args({"current_user": True})

    client.get_user.return_value = USER_1_BASIC
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" in result.value.users[0]

    client.get_user.assert_called_once_with()
    client.get_user_details.assert_called_once_with(user_id="user-id-1")


def test_iam_user_info_current_user_not_found(user_info_module_args, client):
    """Test current_user returns empty list when no user is found."""

    user_info_module_args({"current_user": True})

    client.get_user.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.get_user_details.assert_not_called()


def test_iam_user_info_get_by_name(user_info_module_args, client):
    """Test filtering users by workload username."""

    user_info_module_args({"name": "u_user1"})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" in result.value.users[0]

    client.list_users.assert_called_once_with()
    client.get_user_details.assert_called_once_with(user_id="user-id-1")


def test_iam_user_info_get_by_multiple_names(user_info_module_args, client):
    """Test filtering users by multiple workload usernames."""

    user_info_module_args({"name": ["u_user1", "u_user2"]})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]
    client.get_user_details.side_effect = [USER_1_DETAILS, USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert [u["workloadUsername"] for u in result.value.users] == ["u_user1", "u_user2"]
    assert client.get_user_details.call_count == 2


def test_iam_user_info_get_by_user_id(user_info_module_args, client):
    """Test retrieving a user by user ID (view=full, default)."""

    user_info_module_args({"user_id": ["user-id-1"]})

    client.list_users.return_value = [USER_1_BASIC]
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["userId"] == "user-id-1"
    assert "roles" in result.value.users[0]

    client.list_users.assert_called_once_with(user_ids=["user-id-1"])
    client.get_user_details.assert_called_once_with(user_id="user-id-1")


def test_iam_user_info_get_by_multiple_user_ids(user_info_module_args, client):
    """Test retrieving users by multiple user IDs (view=full, default)."""

    user_info_module_args({"user_id": ["user-id-1", "user-id-2"]})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]
    client.get_user_details.side_effect = [USER_1_DETAILS, USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    client.list_users.assert_called_once_with(user_ids=["user-id-1", "user-id-2"])
    assert client.get_user_details.call_count == 2


def test_iam_user_info_user_id_not_found(user_info_module_args, client):
    """Test that a missing user ID results in an empty list."""

    user_info_module_args({"user_id": ["nonexistent-user-id"]})

    client.list_users.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.list_users.assert_called_once_with(user_ids=["nonexistent-user-id"])
    client.get_user_details.assert_not_called()


def test_iam_user_info_name_not_found(user_info_module_args, client):
    """Test that searching for a non-existent username returns an empty list."""

    user_info_module_args({"name": ["u_nonexistent"]})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.get_user_details.assert_not_called()


def test_iam_user_info_full_view_skips_users_without_details(
    user_info_module_args,
    client,
):
    """Test that a user that cannot be resolved to details (for example removed in the meantime) is skipped."""

    user_info_module_args({})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]
    client.get_user_details.side_effect = [None, USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert [u["userId"] for u in result.value.users] == ["user-id-2"]


def test_iam_user_info_filter(user_info_module_args, client):
    """Test filtering users by a regex pattern on a field (view=full, default)."""

    user_info_module_args({"filter": {"workloadUsername": "u_user[0-9]+"}})

    client.list_users_filtered.return_value = [USER_1_BASIC, USER_2_BASIC]
    client.get_user_details.side_effect = [USER_1_DETAILS, USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    client.list_users_filtered.assert_called_once_with(
        {"workloadUsername": "u_user[0-9]+"},
    )
    assert client.get_user_details.call_count == 2


def test_iam_user_info_filter_snake_case_field(user_info_module_args, client):
    """Test that the filter field is handed to the client as given, so snake_case is accepted too."""

    user_info_module_args({"filter": {"workload_username": "u_user1"}})

    client.list_users_filtered.return_value = [USER_1_BASIC]
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    client.list_users_filtered.assert_called_once_with(
        {"workload_username": "u_user1"},
    )


def test_iam_user_info_filter_no_match(user_info_module_args, client):
    """Test that a filter with no matches returns an empty list."""

    user_info_module_args({"filter": {"workloadUsername": "^admin_.*"}})

    client.list_users_filtered.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.list_users_filtered.assert_called_once_with(
        {"workloadUsername": "^admin_.*"},
    )
    client.get_user_details.assert_not_called()


def test_iam_user_info_filter_partial_match(user_info_module_args, client):
    """Test that a filter matches only some users."""

    user_info_module_args({"filter": {"workloadUsername": "u_user1"}})

    client.list_users_filtered.return_value = [USER_1_BASIC]
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    client.get_user_details.assert_called_once_with(user_id="user-id-1")


def test_iam_user_info_check_mode(user_info_module_args, client):
    """Test that check mode works correctly (read-only operation)."""

    user_info_module_args({"_ansible_check_mode": True})

    client.list_users.return_value = [USER_1_BASIC]
    client.get_user_details.return_value = USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1


def test_iam_user_info_view_summary(user_info_module_args, client):
    """Test view=summary returns basic user info without calling get_user_details."""

    user_info_module_args({"view": "summary"})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    # summary view should NOT include roles/groups/resource_roles
    assert "roles" not in result.value.users[0]
    assert "groups" not in result.value.users[0]
    assert "resource_roles" not in result.value.users[0]
    client.get_user_details.assert_not_called()


def test_iam_user_info_view_summary_by_name(user_info_module_args, client):
    """Test view=summary with name filter returns basic user info."""

    user_info_module_args({"name": ["u_user1"], "view": "summary"})

    client.list_users.return_value = [USER_1_BASIC, USER_2_BASIC]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" not in result.value.users[0]
    client.get_user_details.assert_not_called()


def test_iam_user_info_view_summary_by_user_id(user_info_module_args, client):
    """Test view=summary with user_id returns basic user info from list_users."""

    user_info_module_args({"user_id": ["user-id-1"], "view": "summary"})

    client.list_users.return_value = [USER_1_BASIC]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["userId"] == "user-id-1"
    assert "roles" not in result.value.users[0]
    client.list_users.assert_called_once_with(user_ids=["user-id-1"])
    client.get_user_details.assert_not_called()


def test_iam_user_info_view_summary_current_user(user_info_module_args, client):
    """Test view=summary with current_user returns basic user info."""

    user_info_module_args({"current_user": True, "view": "summary"})

    client.get_user.return_value = USER_1_BASIC

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" not in result.value.users[0]
    client.get_user.assert_called_once_with()
    client.get_user_details.assert_not_called()
