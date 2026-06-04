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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import iam_user_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MOCK_USER_1_BASIC = {
    "userId": "user-id-1",
    "crn": "crn:cdp:iam:us-west-1:account:user:user-id-1",
    "email": "user1@example.com",
    "firstName": "User",
    "lastName": "One",
    "workloadUsername": "u_user1",
    "creationDate": "2025-01-01T00:00:00.000Z",
}

MOCK_USER_2_BASIC = {
    "userId": "user-id-2",
    "crn": "crn:cdp:iam:us-west-1:account:user:user-id-2",
    "email": "user2@example.com",
    "firstName": "User",
    "lastName": "Two",
    "workloadUsername": "u_user2",
    "creationDate": "2025-01-02T00:00:00.000Z",
}

MOCK_USER_1_DETAILS = {
    **MOCK_USER_1_BASIC,
    "status": "active",
    "roles": [],
    "resourceAssignments": [],
    "groups": [],
}

MOCK_USER_2_DETAILS = {
    **MOCK_USER_2_BASIC,
    "status": "active",
    "roles": ["crn:cdp:iam:us-west-1:account:role:IAMUser"],
    "resourceAssignments": [
        {
            "resourceCrn": "crn:cdp:environments:us-west-1:account:environment:env1",
            "resourceRoleCrn": "crn:cdp:iam:us-west-1:account:resourceRole:EnvironmentUser",
        }
    ],
    "groups": ["crn:cdp:iam:us-west-1:account:group:test-group"],
}


def _patch_common(mocker):
    """Helper to patch load_cdp_config for all tests."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    return config


def _patch_client(mocker):
    """Helper to patch CdpIamClient for all tests."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user_info.CdpIamClient",
        autospec=True,
    ).return_value


def test_iam_user_info_list_all_users(module_args, mocker):
    """Test listing all IAM users with summary view returns basic info without details."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "view": "summary",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}

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

    client.list_users.assert_called_once()
    client.get_user_details.assert_not_called()


def test_iam_user_info_current_user(module_args, mocker):
    """Test retrieving the current authenticated user."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "current_user": True,
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.get_user.return_value = MOCK_USER_1_BASIC
    client.get_user_details.return_value = MOCK_USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" in result.value.users[0]

    client.get_user.assert_called_once_with()
    client.get_user_details.assert_called_once_with("user-id-1")


def test_iam_user_info_current_user_not_found(module_args, mocker):
    """Test current_user returns empty list when no user is found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "current_user": True,
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.get_user.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.get_user_details.assert_not_called()


def test_iam_user_info_get_by_name(module_args, mocker):
    """Test filtering users by workload username."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "u_user1",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}
    client.get_user_details.return_value = MOCK_USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" in result.value.users[0]

    client.list_users.assert_called_once()
    client.get_user_details.assert_called_once_with("user-id-1")


def test_iam_user_info_get_by_multiple_names(module_args, mocker):
    """Test filtering users by multiple workload usernames."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["u_user1", "u_user2"],
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}
    client.get_user_details.side_effect = [MOCK_USER_1_DETAILS, MOCK_USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    assert client.get_user_details.call_count == 2


def test_iam_user_info_get_by_user_id(module_args, mocker):
    """Test retrieving a user by user ID (view=full, default)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": ["user-id-1"],
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC]}
    client.get_user_details.return_value = MOCK_USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["userId"] == "user-id-1"
    assert "roles" in result.value.users[0]

    client.list_users.assert_called_once_with(user_ids=["user-id-1"])
    client.get_user_details.assert_called_once_with("user-id-1")


def test_iam_user_info_get_by_multiple_user_ids(module_args, mocker):
    """Test retrieving users by multiple user IDs (view=full, default)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": ["user-id-1", "user-id-2"],
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}
    client.get_user_details.side_effect = [MOCK_USER_1_DETAILS, MOCK_USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    client.list_users.assert_called_once_with(user_ids=["user-id-1", "user-id-2"])
    assert client.get_user_details.call_count == 2


def test_iam_user_info_user_id_not_found(module_args, mocker):
    """Test that a missing user ID results in an empty list."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": ["nonexistent-user-id"],
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": []}

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.list_users.assert_called_once_with(user_ids=["nonexistent-user-id"])
    client.get_user_details.assert_not_called()


def test_iam_user_info_name_not_found(module_args, mocker):
    """Test that searching for a non-existent username returns an empty list."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["u_nonexistent"],
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.get_user_details.assert_not_called()


def test_iam_user_info_filter(module_args, mocker):
    """Test filtering users by a regex pattern on a field (view=full, default)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "filter": {"workloadUsername": "u_user[0-9]+"},
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users_filtered.return_value = [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]
    client.get_user_details.side_effect = [MOCK_USER_1_DETAILS, MOCK_USER_2_DETAILS]

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 2
    client.list_users_filtered.assert_called_once_with({"workloadUsername": "u_user[0-9]+"})
    assert client.get_user_details.call_count == 2


def test_iam_user_info_filter_no_match(module_args, mocker):
    """Test that a filter with no matches returns an empty list."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "filter": {"workloadUsername": "^admin_.*"},
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users_filtered.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
    client.list_users_filtered.assert_called_once_with({"workloadUsername": "^admin_.*"})
    client.get_user_details.assert_not_called()


def test_iam_user_info_filter_partial_match(module_args, mocker):
    """Test that a filter matches only some users."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "filter": {"workloadUsername": "u_user1"},
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users_filtered.return_value = [MOCK_USER_1_BASIC]
    client.get_user_details.return_value = MOCK_USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    client.get_user_details.assert_called_once_with("user-id-1")


def test_iam_user_info_check_mode(module_args, mocker):
    """Test that check mode works correctly (read-only operation)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "_ansible_check_mode": True,
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC]}
    client.get_user_details.return_value = MOCK_USER_1_DETAILS

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1


def test_iam_user_info_view_summary(module_args, mocker):
    """Test view=summary returns basic user info without calling get_user_details."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "view": "summary",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}

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


def test_iam_user_info_view_summary_by_name(module_args, mocker):
    """Test view=summary with name filter returns basic user info."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["u_user1"],
            "view": "summary",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC, MOCK_USER_2_BASIC]}

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" not in result.value.users[0]
    client.get_user_details.assert_not_called()


def test_iam_user_info_view_summary_by_user_id(module_args, mocker):
    """Test view=summary with user_id returns basic user info from list_users."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": ["user-id-1"],
            "view": "summary",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.list_users.return_value = {"users": [MOCK_USER_1_BASIC]}

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["userId"] == "user-id-1"
    assert "roles" not in result.value.users[0]
    client.list_users.assert_called_once_with(user_ids=["user-id-1"])
    client.get_user_details.assert_not_called()


def test_iam_user_info_view_summary_current_user(module_args, mocker):
    """Test view=summary with current_user returns basic user info."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "current_user": True,
            "view": "summary",
        }
    )

    _patch_common(mocker)
    client = _patch_client(mocker)

    client.get_user.return_value = MOCK_USER_1_BASIC

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert len(result.value.users) == 1
    assert result.value.users[0]["workloadUsername"] == "u_user1"
    assert "roles" not in result.value.users[0]
    client.get_user.assert_called_once_with()
    client.get_user_details.assert_not_called()
