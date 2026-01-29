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
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_resource_role_info


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
def existing_resource_role_crn(iam_client) -> str:
    """Fixture to provide an existing resource role CRN for tests."""
    response = iam_client.list_resource_roles()

    if len(response.get("resourceRoles", [])) == 0:
        pytest.skip("No resource roles available for testing")

    return response["resourceRoles"][0]["crn"]


def test_iam_resource_role_info_list_all(module_args):
    """Test listing all IAM resource roles with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert isinstance(result.value.resource_roles, list)
    assert len(result.value.resource_roles) > 0


def test_iam_resource_role_info_list_by_crn(module_args, existing_resource_role_crn):
    """Test listing IAM resource roles by CRN with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": [existing_resource_role_crn],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 1
    assert any(
        rr["crn"] == existing_resource_role_crn for rr in result.value.resource_roles
    )


def test_iam_resource_role_info_nonexistent(module_args):
    """Test querying for a non-existent resource role."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["crn:altus:iam:us-west-1:altus:resourceRole:NonExistent112233"],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 0


def test_iam_resource_role_info_multiple_crns(module_args, iam_client):
    """Test listing multiple IAM resource roles by CRN with real API calls."""

    response = iam_client.list_resource_roles()
    resource_roles = response.get("resourceRoles", [])

    if len(resource_roles) < 2:
        pytest.skip("Need at least 2 resource roles for testing")

    resource_role_crns = [resource_roles[0]["crn"], resource_roles[1]["crn"]]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": resource_role_crns,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 2

    returned_crns = [rr["crn"] for rr in result.value.resource_roles]
    assert sorted(returned_crns) == sorted(resource_role_crns)
