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

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "SAML_PROVIDER_NAME",
]

# Generate unique user identifier for each test run to avoid conflicts
USER_EMAIL = f"test-user-int-{uuid.uuid4().hex[:8]}@example.com"
IDENTITY_PROVIDER_USER_ID = USER_EMAIL
TEST_WORKLOAD_PASSWORD = f"SecurePassword{uuid.uuid4().hex[:8]}!"
TEST_WORKLOAD_PASSWORD_UPDATE = f"UpdatedPassword{uuid.uuid4().hex[:8]}!"

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
            if hasattr(e, "code") and e.code == 404:
                continue
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


def test_iam_user_create(iam_module_args, iam_user_delete):
    """Test creating a new IAM user with real API calls."""

    iam_module_args(
        {
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
    iam_module_args(
        {
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


def test_iam_user_delete(iam_module_args, iam_user_create, env_context):
    """Test deleting an IAM user with real API calls using user_id."""

    # Create the user to be deleted
    created_user = iam_user_create(
        email=USER_EMAIL,
        idp_user_id=IDENTITY_PROVIDER_USER_ID,
        saml_provider_name=env_context["SAML_PROVIDER_NAME"],
    )

    # Execute function - use userId from created user (API returns camelCase)
    iam_module_args(
        {
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


def test_iam_user_roles_update(iam_module_args, iam_user_delete, env_context):
    """Test updating IAM user roles with real API calls."""

    # Create user with initial roles
    iam_module_args(
        {
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
    iam_module_args(
        {
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


def test_iam_user_create_with_workload_password(iam_module_args, iam_user_delete):
    """Test creating a new IAM user with workload password using real API calls."""

    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": USER_EMAIL,
            "workload_password": TEST_WORKLOAD_PASSWORD,
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


def test_iam_user_update_workload_password(
    iam_module_args,
    iam_user_delete,
    env_context,
):
    """Test updating workload password for an existing IAM user."""

    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "saml_provider_name": env_context["SAML_PROVIDER_NAME"],
            "workload_password": TEST_WORKLOAD_PASSWORD,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    user_id = result.value.user["user_id"]

    # Register for cleanup after the test
    iam_user_delete(user_id)

    # Update with workload password
    iam_module_args(
        {
            "email": USER_EMAIL,
            "workload_password": TEST_WORKLOAD_PASSWORD_UPDATE,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL


def test_iam_user_create_diff_mode_int(iam_module_args, iam_user_delete):
    """Test creating a new IAM user with diff mode enabled."""

    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "first_name": "John",
            "last_name": "Doe",
            "roles": ["crn:altus:iam:us-west-1:altus:role:BillingAdmin"],
            "state": "present",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL
    assert result.value.user["first_name"] == "John"
    assert result.value.user["last_name"] == "Doe"

    # Verify diff structure
    assert hasattr(result.value, "diff")
    assert result.value.diff["before"] == {}
    assert "after" in result.value.diff

    # Verify diff contains the expected fields
    assert result.value.diff["after"]["email"] == USER_EMAIL
    assert result.value.diff["after"]["first_name"] == "John"
    assert result.value.diff["after"]["last_name"] == "Doe"
    assert result.value.diff["after"]["roles"] == [
        "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
    ]

    # Register for cleanup after the test
    iam_user_delete(result.value.user["user_id"])


def test_iam_user_delete_diff_mode_int(iam_module_args, iam_user_create, env_context):
    """Test deleting an IAM user with diff mode enabled."""

    # Create the user to be deleted
    created_user = iam_user_create(
        email=USER_EMAIL,
        idp_user_id=IDENTITY_PROVIDER_USER_ID,
        saml_provider_name=env_context["SAML_PROVIDER_NAME"],
    )

    # Execute delete with diff mode
    iam_module_args(
        {
            "email": USER_EMAIL,
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert hasattr(result.value, "diff")
    assert "before" in result.value.diff
    assert result.value.diff["before"]["email"] == USER_EMAIL
    assert result.value.diff["after"] == {}


@pytest.mark.slow
def test_iam_user_update_roles_diff_mode_int(
    iam_module_args,
    iam_user_delete,
    env_context,
):
    """Test updating user roles with diff mode enabled."""

    # Create user with initial roles
    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "saml_provider_name": env_context["SAML_PROVIDER_NAME"],
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    user_id = result.value.user["user_id"]

    # Register for cleanup after the test
    iam_user_delete(user_id)

    # Update roles with diff mode
    iam_module_args(
        {
            "email": USER_EMAIL,
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin",
            ],
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert hasattr(result.value, "diff")
    assert "before" in result.value.diff
    assert "after" in result.value.diff
    assert "roles" in result.value.diff["before"]
    assert "roles" in result.value.diff["after"]
    assert len(result.value.diff["after"]["roles"]) == 2


def test_iam_user_check_mode_create_int(iam_module_args, iam_client):
    """Test creating a user in check mode - should not create actual user."""

    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "first_name": "Check",
            "last_name": "Mode",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify user was NOT actually created
    existing_user = iam_client.get_user_details_by_email(email=USER_EMAIL)
    assert existing_user is None


def test_iam_user_check_mode_delete_int(
    iam_module_args,
    iam_user_create,
    iam_client,
    env_context,
):
    """Test deleting a user in check mode - should not delete actual user."""

    # Create the user
    created_user = iam_user_create(
        email=USER_EMAIL,
        idp_user_id=IDENTITY_PROVIDER_USER_ID,
        saml_provider_name=env_context["SAML_PROVIDER_NAME"],
    )

    # Try to delete in check mode
    iam_module_args(
        {
            "email": USER_EMAIL,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify user still exists
    existing_user = iam_client.get_user_details_by_email(email=USER_EMAIL)
    assert existing_user is not None
    assert existing_user["email"] == USER_EMAIL


def test_iam_user_check_mode_update_diff_int(
    iam_module_args,
    iam_user_delete,
    env_context,
):
    """Test updating user in check mode with diff - should show changes without applying."""

    # Create user with initial roles
    iam_module_args(
        {
            "email": USER_EMAIL,
            "identity_provider_user_id": IDENTITY_PROVIDER_USER_ID,
            "saml_provider_name": env_context["SAML_PROVIDER_NAME"],
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    user_id = result.value.user["user_id"]
    original_roles = result.value.user["roles"]

    # Register for cleanup after the test
    iam_user_delete(user_id)

    # Update roles in check mode with diff
    iam_module_args(
        {
            "email": USER_EMAIL,
            "state": "present",
            "roles": [
                "crn:altus:iam:us-west-1:altus:role:BillingAdmin",
                "crn:altus:iam:us-west-1:altus:role:DFCatalogAdmin",
            ],
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert hasattr(result.value, "diff")
    assert "before" in result.value.diff
    assert "after" in result.value.diff

    # Verify roles were NOT actually changed
    assert result.value.user["roles"] == original_roles
