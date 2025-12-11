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

import os
import pytest
import uuid

from typing import Callable, Generator

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)


from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_group


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Generate unique group name for each test run to avoid conflicts
GROUP_NAME = f"test-group-int-{uuid.uuid4().hex[:8]}"

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def iam_group_delete(iam_client) -> Generator[Callable[[str], None], None, None]:
    """Fixture to clean up IAM groups created during tests."""

    group_names = []

    def _iam_group_module(name: str):
        group_names.append(name)
        return
    
    yield _iam_group_module

    for name in group_names:
        try:
            iam_client.delete_group(group_name=name)
        except Exception as e:
            pytest.fail(f"Failed to clean up IAM group: {name}. {e}")


@pytest.fixture
def iam_group_create(iam_client, iam_group_delete) -> Callable[[str], None]:
    """Fixture to clean up IAM groups created during tests."""

    def _iam_group_module(name: str, sync: bool = False):
        iam_group_delete(name)
        iam_client.create_group(group_name=name, sync_membership_on_user_login=sync)
        return

    return _iam_group_module

@pytest.mark.skip("Utility test, not part of main suite")
def test_iam_user(test_cdp_client, iam_client):
    """Test that the IAM client can successfully make an API call."""

    rest_result = test_cdp_client.post("/iam/getUser", data={})
    assert "user" in rest_result

    iam_result = iam_client.get_user()
    assert iam_result


def test_iam_group_create(module_args, iam_group_delete):
    """Test creating a new IAM group with real API calls."""

    # Ensure cleanup after the test
    iam_group_delete(GROUP_NAME)

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": GROUP_NAME,
            "state": "present",
            "sync": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is True
    assert result.value.group["groupName"] == GROUP_NAME
    assert result.value.group["syncMembershipOnUserLogin"] is True
    assert "crn" in result.value.group

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is False
    assert result.value.group["groupName"] == GROUP_NAME
    assert result.value.group["syncMembershipOnUserLogin"] is True
    assert "crn" in result.value.group


def test_iam_group_delete(module_args, iam_group_create):
    """Test deleting an IAM group with real API calls."""

    # Create the group to be deleted
    iam_group_create(name=GROUP_NAME, sync=True)

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": GROUP_NAME,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is True

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is False


def test_iam_group_update(module_args, iam_group_create):
    """Test updating an IAM group with real API calls."""

    # Create the group to be updated
    iam_group_create(name=GROUP_NAME, sync=False)

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": GROUP_NAME,
            "state": "present",
            "sync": True, # Update sync setting to True
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is True
    assert result.value.group["groupName"] == GROUP_NAME
    assert result.value.group["syncMembershipOnUserLogin"] is True

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is False
    assert result.value.group["syncMembershipOnUserLogin"] is True
