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
from ansible_collections.cloudera.cloud.plugins.modules import iam_machine_user


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Generate unique machine user name for each test run to avoid conflicts
MACHINE_USER_NAME = f"test-machine-user-int-{uuid.uuid4().hex[:8]}"

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def iam_machine_user_delete(
    iam_client,
) -> Generator[Callable[[str], None], None, None]:
    """Fixture to clean up IAM machine users created during tests."""

    machine_user_names = []

    def _iam_machine_user_delete(name: str):
        machine_user_names.append(name)
        return

    yield _iam_machine_user_delete

    for name in machine_user_names:
        try:
            iam_client.delete_machine_user(machine_user_name=name)
        except Exception as e:
            pytest.fail(f"Failed to clean up IAM machine user: {name}. {e}")


@pytest.fixture
def iam_machine_user_create(
    iam_client, iam_machine_user_delete
) -> Callable[[str], None]:
    """Fixture to create IAM machine users for tests."""

    def _iam_machine_user_create(name: str):
        iam_machine_user_delete(name)
        iam_client.create_machine_user(machine_user_name=name)
        return

    return _iam_machine_user_create


@pytest.mark.skip("Utility test, not part of main suite")
def test_iam_user(test_cdp_client, iam_client):
    """Test that the IAM client can successfully make an API call."""

    rest_result = test_cdp_client.post("/iam/getUser", data={})
    assert "user" in rest_result

    iam_result = iam_client.get_user()
    assert iam_result


def test_iam_machine_user_create(module_args, iam_machine_user_delete):
    """Test creating a new IAM machine user with real API calls."""

    # Ensure cleanup after the test
    iam_machine_user_delete(MACHINE_USER_NAME)

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": MACHINE_USER_NAME,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME
    assert "crn" in result.value.machine_user

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME
    assert "crn" in result.value.machine_user


def test_iam_machine_user_delete(module_args, iam_machine_user_create):
    """Test deleting an IAM machine user with real API calls."""

    # Create the machine user to be deleted
    iam_machine_user_create(name=MACHINE_USER_NAME)

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": MACHINE_USER_NAME,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False


def test_iam_machine_user_roles_update(module_args, iam_machine_user_delete):
    """Test updating IAM machine user roles with real API calls."""

    # Ensure cleanup after the test
    iam_machine_user_delete(MACHINE_USER_NAME)

    # Create machine user with initial roles
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": MACHINE_USER_NAME,
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
                "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME
    assert len(result.value.machine_user["roles"]) == 2
    assert (
        "crn:altus:iam:us-west-1:altus:role:BillingAdmin"
        in result.value.machine_user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator"
        in result.value.machine_user["roles"]
    )

    # Update roles - add three new roles
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": MACHINE_USER_NAME,
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogPublisher",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogViewer",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is True
    assert result.value.machine_user["machine_user_name"] == MACHINE_USER_NAME
    assert len(result.value.machine_user["roles"]) == 5
    # Verify all roles are present
    assert (
        "crn:altus:iam:us-west-1:altus:role:BillingAdmin"
        in result.value.machine_user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator"
        in result.value.machine_user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin"
        in result.value.machine_user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogPublisher"
        in result.value.machine_user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogViewer"
        in result.value.machine_user["roles"]
    )

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user.main()

    assert result.value.changed is False
    assert len(result.value.machine_user["roles"]) == 5

