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

import os
import pytest

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_role_info


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def existing_role_crn(iam_client) -> str:
    """Fixture to provide an existing role CRN for tests."""
    response = iam_client.list_roles()

    if len(response.get("roles", [])) == 0:
        pytest.skip("No roles available for testing")

    return response["roles"][0]["crn"]


def test_iam_role_info_list_all(module_args):
    """Test listing all IAM roles with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert isinstance(result.value.roles, list)
    assert len(result.value.roles) > 0


def test_iam_role_info_list_by_crn(module_args, existing_role_crn):
    """Test listing IAM roles by CRN with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": [existing_role_crn],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 1
    assert any(role["crn"] == existing_role_crn for role in result.value.roles)


def test_iam_role_info_nonexistent(module_args):
    """Test querying for a non-existent role."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["crn:iam:us-east-1:cm:role:NonExistentRole112233"],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 0


def test_iam_role_info_multiple_crns(module_args, iam_client):
    """Test listing multiple IAM roles by CRN with real API calls."""

    response = iam_client.list_roles()
    roles = response.get("roles", [])

    if len(roles) < 2:
        pytest.skip("Need at least 2 roles for testing")

    role_crns = [roles[0]["crn"], roles[1]["crn"]]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": role_crns,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 2

    returned_crns = [role["crn"] for role in result.value.roles]
    assert sorted(returned_crns) == sorted(role_crns)
