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
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import iam_role_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ROLE_CRN = "crn:iam:us-east-1:cm:role:ClassicClustersCreator"


def test_iam_role_info_default(module_args, mocker):
    """Test iam_role_info module with no parameters returns all roles."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_roles.return_value = {
        "roles": [
            {
                "crn": "crn:iam:us-east-1:cm:role:ClassicClustersCreator",
                "policies": [
                    {
                        "right": "environment/createEnvironment",
                        "resource": "*",
                    },
                ],
            },
            {
                "crn": "crn:iam:us-east-1:cm:role:DFCatalogAdmin",
                "policies": [
                    {
                        "right": "df/viewFlow",
                        "resource": "*",
                    },
                ],
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 2
    assert (
        result.value.roles[0]["crn"]
        == "crn:iam:us-east-1:cm:role:ClassicClustersCreator"
    )
    assert result.value.roles[1]["crn"] == "crn:iam:us-east-1:cm:role:DFCatalogAdmin"

    # Verify CdpIamClient was called correctly
    client.list_roles.assert_called_once_with(role_names=None)


def test_iam_role_info_single_name(module_args, mocker):
    """Test iam_role_info module with a single role CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ROLE_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_roles.return_value = {
        "roles": [
            {
                "crn": ROLE_CRN,
                "policies": [
                    {
                        "right": "environment/createEnvironment",
                        "resource": "*",
                    },
                    {
                        "right": "environments/describeEnvironment",
                        "resource": "*",
                    },
                ],
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 1
    assert result.value.roles[0]["crn"] == ROLE_CRN
    assert len(result.value.roles[0]["policies"]) == 2

    # Verify CdpIamClient was called correctly with the role name
    client.list_roles.assert_called_once_with(role_names=[ROLE_CRN])


def test_iam_role_info_multiple_names(module_args, mocker):
    """Test iam_role_info module with multiple role CRNs."""

    role_crns = [
        "crn:iam:us-east-1:cm:role:ClassicClustersCreator",
        "crn:iam:us-east-1:cm:role:DFCatalogAdmin",
        "crn:iam:us-east-1:cm:role:EnvironmentAdmin",
    ]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": role_crns,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_roles.return_value = {
        "roles": [
            {
                "crn": crn,
                "policies": [
                    {
                        "right": "some/right",
                        "resource": "*",
                    },
                ],
            }
            for crn in role_crns
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 3

    # Verify all roles are returned
    returned_crns = [role["crn"] for role in result.value.roles]
    assert sorted(returned_crns) == sorted(role_crns)

    # Verify CdpIamClient was called correctly with the list of names
    client.list_roles.assert_called_once_with(role_names=role_crns)


def test_iam_role_info_empty_result(module_args, mocker):
    """Test iam_role_info module when no roles are found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["crn:iam:us-east-1:cm:role:NonExistentRole"],
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_roles.return_value = {"roles": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 0

    # Verify CdpIamClient was called correctly
    client.list_roles.assert_called_once_with(
        role_names=["crn:iam:us-east-1:cm:role:NonExistentRole"],
    )


def test_iam_role_info_check_mode(module_args, mocker):
    """Test iam_role_info module in check mode."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_roles.return_value = {
        "roles": [
            {
                "crn": "crn:iam:us-east-1:cm:role:TestRole",
                "policies": [],
            },
        ],
    }

    # Test module execution - should work the same in check mode for info modules
    with pytest.raises(AnsibleExitJson) as result:
        iam_role_info.main()

    assert result.value.changed is False
    assert len(result.value.roles) == 1

    # Verify CdpIamClient was called even in check mode (info gathering is safe)
    client.list_roles.assert_called_once_with(role_names=None)
