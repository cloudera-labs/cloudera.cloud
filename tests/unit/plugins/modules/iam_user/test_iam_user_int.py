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

import pytest

__metaclass__ = type

import os

import uuid

from typing import Callable, Generator

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)
from ansible_collections.cloudera.cloud.plugins.modules import iam_user


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Generate unique user identifier for each test run to avoid conflicts
USER_EMAIL = f"test-user-int-{uuid.uuid4().hex[:8]}@example.com"
IDENTITY_PROVIDER_USER_ID = USER_EMAIL

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def iam_user_delete(
    iam_client,
) -> Generator[Callable[[str], None], None, None]:
    """Fixture to clean up IAM users created during tests."""

    user_ids = []

    def _iam_user_delete(user_id: str):
        user_ids.append(user_id)
        return

    yield _iam_user_delete

    for user_id in user_ids:
        try:
            iam_client.delete_user(user_id=user_id)
        except CdpError as e:
            if e.status == 404:
                continue
        except Exception as e:
            pytest.fail(f"Failed to clean up IAM user: {user_id}. {e}")


@pytest.fixture
def iam_user_create(
    iam_client,
    iam_user_delete,
) -> Callable[[str, str, str], dict]:
    """Fixture to create IAM users for tests."""

    def _iam_user_create(email: str, idp_user_id: str, saml_provider_name: str):
        result = iam_client.create_user(
            email=email,
            identity_provider_user_id=idp_user_id,
            saml_provider_name=saml_provider_name,
        )
        iam_user_delete(result["user"]["userId"])
        return result["user"]

    return _iam_user_create


@pytest.mark.skip("Utility test, not part of main suite")
def test_iam_user(test_cdp_client, iam_client):
    """Test that the IAM client can successfully make an API call."""

    rest_result = test_cdp_client.post("/iam/getUser", data={})
    assert "user" in rest_result

    iam_result = iam_client.get_user()
    assert iam_result


def test_iam_user_create(module_args, iam_user_delete):
    """Test creating a new IAM user with real API calls."""

    # Execute function
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL
    assert "crn" in result.value.user

    # Register for cleanup after the test
    iam_user_delete(result.value.user["user_id"])

    # Idempotency check - update module_args with user_id from created user
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user["email"] == USER_EMAIL
    assert "crn" in result.value.user


def test_iam_user_delete(module_args, iam_user_create, env_context):
    """Test deleting an IAM user with real API calls using user_id."""

    # Validate required environment variables
    if not env_context.get("SAML_PROVIDER_NAME"):
        pytest.skip("SAML_PROVIDER_NAME environment variable not set")

    # Create the user to be deleted
    created_user = iam_user_create(
        email=USER_EMAIL,
        idp_user_id=IDENTITY_PROVIDER_USER_ID,
        saml_provider_name=env_context["SAML_PROVIDER_NAME"],
    )

    # Execute function - use userId from created user (API returns camelCase)
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False


def test_iam_user_roles_update(module_args, iam_user_delete, env_context):
    """Test updating IAM user roles with real API calls."""

    # Validate required environment variables
    if not env_context.get("SAML_PROVIDER_NAME"):
        pytest.skip("SAML_PROVIDER_NAME environment variable not set")

    # Create user with initial roles
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "saml_provider_name": env_context["SAML_PROVIDER_NAME"],
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
                "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL
    assert len(result.value.user["roles"]) == 2
    assert (
        "crn:altus:iam:us-west-1:altus:role:BillingAdmin" in result.value.user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator"
        in result.value.user["roles"]
    )

    # Register for cleanup after the test
    iam_user_delete(result.value.user["user_id"])

    # Update roles - add three new roles (use user_id instead of email)
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogPublisher",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogViewer",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL
    assert len(result.value.user["roles"]) == 5
    # Verify all roles are present
    assert (
        "crn:altus:iam:us-west-1:altus:role:BillingAdmin" in result.value.user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:ClassicClustersCreator"
        in result.value.user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin"
        in result.value.user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogPublisher"
        in result.value.user["roles"]
    )
    assert (
        "crn:altus:iam:us-west-1:altus:role:DFCatalogViewer"
        in result.value.user["roles"]
    )

    # Idempotency check
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert len(result.value.user["roles"]) == 5
