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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import iam_user


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

USER_EMAIL = "test-user@example.com"
USER_ID = "test-user-id"
IDP_USER_ID = "test-idp-user-id"


def test_iam_user_default(module_args):
    """Test iam_user module with missing parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Expect the module to fail due to missing required parameter (need either user_id or email)
    with pytest.raises(
        AnsibleFailJson,
        match="one of the following is required: user_id, email",
    ):
        iam_user.main()


def test_iam_user_absent_missing_identifiers(module_args):
    """Test iam_user module with state=absent but missing both user_id and email."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "state": "absent",
        },
    )

    # Expect the module to fail due to missing required parameter (need either user_id or email)
    with pytest.raises(
        AnsibleFailJson, 
        match="one of the following is required: user_id, email"
    ):
        iam_user.main()


def test_iam_user_absent(module_args, mocker):
    """Test iam_user module with state=absent."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": USER_EMAIL,
            "state": "absent",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    client.get_user_details.return_value = {
        "userId": USER_ID,
        "email": USER_EMAIL,
        "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user == {}

    # Verify CdpIamClient was called correctly
    client.get_user_details.assert_called_once_with(user_id=USER_EMAIL)
    client.delete_user.assert_called_once_with(user_id=USER_EMAIL)


def test_iam_user_create_missing_email(module_args, mocker):
    """Test iam_user module creating a new user without email fails."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "user_id": "some-user-id",  # Only user_id, no email
            "state": "present",
        },
    )

    # Expect the module to fail due to missing email (required_if validation)
    with pytest.raises(
        AnsibleFailJson,
        match="state is present but all of the following are missing: email"
    ):
        iam_user.main()


def test_iam_user_create(module_args, mocker):
    """Test iam_user module creating a new user."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "first_name": "Test",
            "last_name": "User",
            "saml_provider_name": "mtaabich-test",
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    
    # User doesn't exist initially (lookup by email)
    client.get_user_details_by_email.return_value = None
    
    # After creation, get_user_details returns the created user
    client.get_user_details.return_value = {
        "userId": USER_ID,
        "email": USER_EMAIL,
        "firstName": "Test",
        "lastName": "User",
        "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
        "roles": [],
        "resourceAssignments": [],
    }
    
    client.create_user.return_value = {
        "user": {
            "userId": USER_ID,
            "email": USER_EMAIL,
            "firstName": "Test",
            "lastName": "User",
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
        }
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True
    assert result.value.user["email"] == USER_EMAIL

    # Verify CdpIamClient was called correctly
    client.create_user.assert_called_once_with(
        email=USER_EMAIL,
        identity_provider_user_id=IDP_USER_ID,
        first_name="Test",
        last_name="User",
        saml_provider_name="mtaabich-test",
        groups=None,
    )


def test_iam_user_create_with_groups(module_args, mocker):
    """Test iam_user module creating a new user with group assignments."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "identity_provider_user_id": IDP_USER_ID,
            "groups": ["developers", "admins"],
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    
    # User doesn't exist initially (lookup by email)
    client.get_user_details_by_email.return_value = None
    
    # After creation, get_user_details returns the created user
    client.get_user_details.return_value = {
        "userId": USER_ID,
        "email": USER_EMAIL,
        "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
        "roles": [],
        "resourceAssignments": [],
    }
    
    client.create_user.return_value = {
        "user": {
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
        }
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify CdpIamClient was called correctly
    client.create_user.assert_called_once_with(
        email=USER_EMAIL,
        identity_provider_user_id=IDP_USER_ID,
        first_name=None,
        last_name=None,
        saml_provider_name=None,
        groups=["developers", "admins"],
    )


def test_iam_user_present_no_changes(module_args, mocker):
    """Test iam_user module with state=present but no changes needed."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,  
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    client.get_user_details_by_email.return_value = {
        "userId": USER_ID,
        "email": USER_EMAIL,
        "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
        "roles": [],
        "resourceAssignments": [],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is False
    assert result.value.user["email"] == USER_EMAIL

    # Verify CdpIamClient was called correctly
    client.get_user_details_by_email.assert_called_once_with(email=USER_EMAIL)


def test_iam_user_assign_roles(module_args, mocker):
    """Test iam_user module assigning roles to an existing user."""

    role_crn = "crn:cdp:iam:us-west-1:altus:role:PowerUser"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,
            "roles": [role_crn],
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    
    client.get_user_details_by_email.side_effect = [
        {  # Initial state - no roles
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [],
            "resourceAssignments": [],
        },
        {  # After role assignment
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [role_crn],
            "resourceAssignments": [],
        },
    ]
    
    client.manage_user_roles.return_value = True

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify CdpIamClient was called correctly
    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,  # Uses userId from the fetched user object
        current_roles=[],
        desired_roles=[role_crn],
        purge=False,
    )


def test_iam_user_assign_resource_roles(module_args, mocker):
    """Test iam_user module assigning resource roles to an existing user."""

    resource_crn = "crn:cdp:environments:us-west-1:altus:environment:dev-env"
    resource_role_crn = "crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,  
            "resource_roles": [
                {
                    "resource": resource_crn,
                    "role": resource_role_crn,
                }
            ],
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    
    client.get_user_details_by_email.side_effect = [
        {  # Initial state - no resource roles
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [],
            "resourceAssignments": [],
        },
        {  # After resource role assignment
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [],
            "resourceAssignments": [
                {
                    "resourceCrn": resource_crn,
                    "resourceRoleCrn": resource_role_crn,
                }
            ],
        },
    ]
    
    client.manage_user_resource_roles.return_value = True

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify CdpIamClient was called correctly
    client.manage_user_resource_roles.assert_called_once_with(
        user_id=USER_ID,  # Uses userId from the fetched user object
        current_assignments=[],
        desired_assignments=[
            {
                "resource": resource_crn,
                "role": resource_role_crn,
            }
        ],
        purge=False,
    )


def test_iam_user_purge_roles(module_args, mocker):
    """Test iam_user module purging roles from a user."""

    existing_role = "crn:cdp:iam:us-west-1:altus:role:OldRole"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "email": USER_EMAIL,  
            "roles": [],
            "purge": True,
            "state": "present",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_user.CdpIamClient",
        autospec=True,
    ).return_value
    
    client.get_user_details_by_email.side_effect = [
        {  # Initial state - has old role
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [existing_role],
            "resourceAssignments": [],
        },
        {  # After purge - no roles
            "userId": USER_ID,
            "email": USER_EMAIL,
            "crn": f"crn:cdp:iam:us-west-1:altus:user:{USER_ID}",
            "roles": [],
            "resourceAssignments": [],
        },
    ]
    
    client.manage_user_roles.return_value = True

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_user.main()

    assert result.value.changed is True

    # Verify CdpIamClient was called correctly
    client.manage_user_roles.assert_called_once_with(
        user_id=USER_ID,  # Uses userId from the fetched user object
        current_roles=[existing_role],
        desired_roles=[],
        purge=True,
    )
