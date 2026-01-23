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

from ansible_collections.cloudera.cloud.plugins.modules import iam_resource_role_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

RESOURCE_ROLE_CRN = "crn:altus:iam:us-west-1:altus:resourceRole:ODUser"


def test_iam_resource_role_info_default(module_args, mocker):
    """Test iam_resource_role_info module with no parameters returns all resource roles."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {
        "resourceRoles": [
            {
                "crn": "crn:altus:iam:us-west-1:altus:resourceRole:ODUser",
                "rights": ["odx/describeJob", "odx/listJobs"],
            },
            {
                "crn": "crn:altus:iam:us-west-1:altus:resourceRole:DWAdmin",
                "rights": ["dw/createCluster", "dw/deleteCluster"],
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 2
    assert result.value.resource_roles[0]["crn"] == "crn:altus:iam:us-west-1:altus:resourceRole:ODUser"
    assert result.value.resource_roles[1]["crn"] == "crn:altus:iam:us-west-1:altus:resourceRole:DWAdmin"

    # Verify CdpIamClient was called correctly
    client.list_resource_roles.assert_called_once_with(resource_role_names=None)


def test_iam_resource_role_info_single_name(module_args, mocker):
    """Test iam_resource_role_info module with a single resource role CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": RESOURCE_ROLE_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {
        "resourceRoles": [
            {
                "crn": RESOURCE_ROLE_CRN,
                "rights": [
                    "odx/describeJob",
                    "odx/listJobs",
                    "odx/createJob",
                ],
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 1
    assert result.value.resource_roles[0]["crn"] == RESOURCE_ROLE_CRN
    assert len(result.value.resource_roles[0]["rights"]) == 3

    # Verify CdpIamClient was called correctly with the resource role name
    client.list_resource_roles.assert_called_once_with(
        resource_role_names=[RESOURCE_ROLE_CRN],
    )


def test_iam_resource_role_info_multiple_names(module_args, mocker):
    """Test iam_resource_role_info module with multiple resource role CRNs."""

    resource_role_crns = [
        "crn:altus:iam:us-west-1:altus:resourceRole:ODUser",
        "crn:altus:iam:us-west-1:altus:resourceRole:DWAdmin",
        "crn:altus:iam:us-west-1:altus:resourceRole:DWUser",
    ]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": resource_role_crns,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {
        "resourceRoles": [
            {
                "crn": crn,
                "rights": ["some/right", "another/right"],
            }
            for crn in resource_role_crns
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 3

    # Verify all resource roles are returned
    returned_crns = [rr["crn"] for rr in result.value.resource_roles]
    assert sorted(returned_crns) == sorted(resource_role_crns)

    # Verify CdpIamClient was called correctly with the list of names
    client.list_resource_roles.assert_called_once_with(
        resource_role_names=resource_role_crns,
    )


def test_iam_resource_role_info_empty_result(module_args, mocker):
    """Test iam_resource_role_info module when no resource roles are found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["crn:altus:iam:us-west-1:altus:resourceRole:NonExistent"],
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {"resourceRoles": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 0

    # Verify CdpIamClient was called correctly
    client.list_resource_roles.assert_called_once_with(
        resource_role_names=["crn:altus:iam:us-west-1:altus:resourceRole:NonExistent"],
    )


def test_iam_resource_role_info_check_mode(module_args, mocker):
    """Test iam_resource_role_info module in check mode."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {
        "resourceRoles": [
            {
                "crn": "crn:altus:iam:us-west-1:altus:resourceRole:TestRole",
                "rights": ["test/right"],
            },
        ],
    }

    # Test module execution - should work the same in check mode for info modules
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 1

    # Verify CdpIamClient was called even in check mode (info gathering is safe)
    client.list_resource_roles.assert_called_once_with(resource_role_names=None)


def test_iam_resource_role_info_with_alias(module_args, mocker):
    """Test iam_resource_role_info module using 'crn' alias instead of 'name'."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": RESOURCE_ROLE_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_resource_role_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_resource_roles.return_value = {
        "resourceRoles": [
            {
                "crn": RESOURCE_ROLE_CRN,
                "rights": ["test/right"],
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_resource_role_info.main()

    assert result.value.changed is False
    assert len(result.value.resource_roles) == 1
    assert result.value.resource_roles[0]["crn"] == RESOURCE_ROLE_CRN

    # Verify the alias worked correctly
    client.list_resource_roles.assert_called_once_with(
        resource_role_names=[RESOURCE_ROLE_CRN],
    )
