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





# @pytest.fixture
# def iam_group_cleanup():
#     """Fixture to clean up IAM groups created during tests."""

#     group_names = []

#     def _iam_group_module(name:str):
#         group_names.append(name)
#         return
    
#     yield _iam_group_module

#     for name in group_names:
#         try:


def test_iam_user(iam_client):
    """Test that the IAM client can successfully make an API call."""
    result = iam_client.post("/iam/getUser", data={})
    assert "user" in result


def test_iam_group_create(module_args):
    """Test creating a new IAM group with real API calls."""
    # Step 1: Create the group
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

    try:
        with pytest.raises(AnsibleExitJson) as result:
            iam_group.main()

        assert result.value.changed is True
        assert result.value.group["groupName"] == GROUP_NAME
        assert result.value.group["syncMembershipOnUserLogin"] is True
        assert "crn" in result.value.group

    finally:
        # Cleanup: Delete the test group
        cleanup_module_args = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": GROUP_NAME,
            "state": "absent",
        }
        try:
            module_args(cleanup_module_args)
            with pytest.raises(AnsibleExitJson):
                iam_group.main()
        except Exception:
            pass


def test_iam_group_update_and_delete(module_args):
    """Test creating, updating, and deleting an IAM group with real API calls."""

    unique_group = f"test-group-update-{uuid.uuid4().hex[:8]}"
    # Step 1: Create the group
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": unique_group,
            "state": "present",
            "sync": True,
        },
    )

    try:
        with pytest.raises(AnsibleExitJson) as result:
            iam_group.main()

        assert result.value.changed is True
        assert result.value.group["groupName"] == unique_group
        assert result.value.group["syncMembershipOnUserLogin"] is True

        # Step 2: Update the sync setting
        module_args(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
                "name": unique_group,
                "state": "present",
                "sync": False,
            },
        )

        with pytest.raises(AnsibleExitJson) as result:
            iam_group.main()

        assert result.value.changed is True
        assert result.value.group["syncMembershipOnUserLogin"] is False

    finally:
        # Step 3: Delete the group
        module_args(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
                "name": unique_group,
                "state": "absent",
            },
        )

        try:
            with pytest.raises(AnsibleExitJson) as result:
                iam_group.main()
            assert result.value.changed is True
        except Exception:
            pass
