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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_machine_user_info


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
def existing_machine_user_name(iam_client) -> str:
    """Fixture to provide an existing machine user name for tests."""
    response = iam_client.list_machine_users()

    if len(response.get("machineUsers", [])) == 0:
        pytest.skip("No machine users available for testing")

    return response["machineUsers"][0]["machineUserName"]


def test_iam_machine_user_info_list_all(module_args):
    """Test listing all IAM machine users with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False

    assert isinstance(result.value.machine_users, list)


def test_iam_machine_user_info_list_by_name(module_args, existing_machine_user_name):
    """Test listing IAM machine users by name with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": [existing_machine_user_name],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 1
    assert any(
        mu["machine_user_name"] == existing_machine_user_name
        for mu in result.value.machine_users
    )


def test_iam_machine_user_info_nonexistent(module_args):
    """Test querying for a non-existent machine user."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["nonexistent-machine-user-112233"],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 0
