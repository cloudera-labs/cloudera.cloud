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
from ansible_collections.cloudera.cloud.plugins.modules import iam_group_info


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
def existing_group_name(iam_client) -> str:
    """Fixture to provide an existing group name for tests."""
    response = iam_client.list_groups()

    if len(response.get("groups", [])) == 0:
        pytest.skip("No groups available for testing")

    return response["groups"][0]["groupName"]


def test_iam_group_info_list_all(iam_module_args):
    """Test listing all IAM groups with real API calls."""

    iam_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert result.value.groups is not None
    assert isinstance(result.value.groups, list)
    assert len(result.value.groups) > 0

    first_group = result.value.groups[0]
    assert "groupName" in first_group
    assert "crn" in first_group
    assert "creationDate" in first_group


def test_iam_group_info_get_specific_group(iam_module_args, existing_group_name):
    """Test getting details for a specific IAM group."""

    iam_module_args(
        {
            "name": [existing_group_name],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert result.value.groups is not None
    assert len(result.value.groups) == 1

    group = result.value.groups[0]
    assert group["groupName"] == existing_group_name
    assert "crn" in group
    assert "creationDate" in group

    assert "members" in group
    assert "roles" in group
    assert "resourceAssignments" in group
    assert isinstance(group["members"], list)
    assert isinstance(group["roles"], list)
    assert isinstance(group["resourceAssignments"], list)


def test_iam_group_info_nonexistent_group(iam_module_args):
    """Test behavior when querying a non-existent group."""

    nonexistent_group = "ansible-test-group-does-not-exist-12345"

    iam_module_args(
        {
            "name": [nonexistent_group],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert result.value.groups is not None
    assert len(result.value.groups) == 0


def test_iam_group_info_by_crn(iam_module_args, iam_client, existing_group_name):
    """Test getting group details using CRN instead of name."""


    group_details = iam_client.get_group_details(existing_group_name)
    group_crn = group_details["crn"]

    iam_module_args(
        {
            "name": [group_crn],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.groups is not None
    assert len(result.value.groups) == 1
    assert result.value.groups[0]["groupName"] == existing_group_name
    assert result.value.groups[0]["crn"] == group_crn
