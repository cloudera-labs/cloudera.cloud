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

from typing import Callable

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_user_info


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common IAM module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def current_user(iam_client) -> dict:
    """Fixture to get the current authenticated user for test setup."""
    user = iam_client.get_user()
    return user


@pytest.mark.slow
def test_iam_user_info_list_all(iam_module_args):
    """Test listing all IAM users returns at least one user with expected fields."""

    iam_module_args(
        {
            "view": "summary",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users is not None
    assert isinstance(result.value.users, list)
    assert len(result.value.users) > 0

    first_user = result.value.users[0]
    assert "userId" in first_user
    assert "crn" in first_user
    assert "workloadUsername" in first_user


def test_iam_user_info_current_user(iam_module_args):
    """Test retrieving the current authenticated user."""

    iam_module_args({"current_user": True})

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users is not None
    assert len(result.value.users) == 1

    user = result.value.users[0]
    assert "userId" in user
    assert "crn" in user
    assert "workloadUsername" in user
    assert "roles" in user
    assert "resource_roles" in user
    assert "groups" in user


@pytest.mark.slow
def test_iam_user_info_get_by_name(iam_module_args, current_user):
    """Test retrieving a user by workload username."""

    workload_username = current_user.get("workloadUsername")

    iam_module_args({"name": [workload_username]})

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users is not None
    assert len(result.value.users) >= 1

    found = next(
        (u for u in result.value.users if u["workloadUsername"] == workload_username),
        None,
    )
    assert (
        found is not None
    ), f"User with workloadUsername '{workload_username}' not found"
    assert "roles" in found
    assert "resource_roles" in found
    assert "groups" in found


def test_iam_user_info_get_by_user_id(iam_module_args, current_user):
    """Test retrieving a user by user ID."""

    user_id = current_user.get("userId")

    iam_module_args({"user_id": [user_id]})

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users is not None
    assert len(result.value.users) == 1

    user = result.value.users[0]
    assert user["userId"] == user_id
    assert "roles" in user
    assert "resource_roles" in user
    assert "groups" in user


@pytest.mark.slow
def test_iam_user_info_filter_by_workload_username(iam_module_args, current_user):
    """Test filtering users by workload username regex."""

    workload_username = current_user.get("workloadUsername")

    # Use a regex that matches the known username
    iam_module_args({"filter": {"workloadUsername": f"^{workload_username}$"}})

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users is not None
    assert len(result.value.users) >= 1

    found = next(
        (u for u in result.value.users if u["workloadUsername"] == workload_username),
        None,
    )
    assert (
        found is not None
    ), f"Filtered result did not include user '{workload_username}'"


@pytest.mark.slow
def test_iam_user_info_nonexistent_user(iam_module_args):
    """Test that querying a non-existent user returns an empty list."""

    iam_module_args({"name": ["ansible-test-user-does-not-exist-12345"]})

    with pytest.raises(AnsibleExitJson) as result:
        iam_user_info.main()

    assert result.value.changed is False
    assert result.value.users == []
