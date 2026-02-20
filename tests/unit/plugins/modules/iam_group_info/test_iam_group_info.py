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

from ansible_collections.cloudera.cloud.plugins.modules import iam_group_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MOCK_GROUP_1 = {
    "groupName": "test-group-1",
    "crn": "crn:cdp:iam:us-west-1:account:group:test-group-1",
    "creationDate": "2025-01-01T00:00:00.000Z",
    "syncMembershipOnUserLogin": True,
}

MOCK_GROUP_2 = {
    "groupName": "test-group-2",
    "crn": "crn:cdp:iam:us-west-1:account:group:test-group-2",
    "creationDate": "2025-01-02T00:00:00.000Z",
    "syncMembershipOnUserLogin": False,
}

MOCK_GROUP_DETAILS = {
    "groupName": "test-group-1",
    "crn": "crn:cdp:iam:us-west-1:account:group:test-group-1",
    "creationDate": "2025-01-01T00:00:00.000Z",
    "syncMembershipOnUserLogin": True,
    "members": [
        "crn:cdp:iam:us-west-1:account:user:user1",
        "crn:cdp:iam:us-west-1:account:machineUser:machine1",
    ],
    "roles": [
        "crn:cdp:iam:us-west-1:account:role:IAMUser",
    ],
    "resourceAssignments": [
        {
            "resourceCrn": "crn:cdp:environments:us-west-1:account:environment:env1",
            "resourceRoleCrn": "crn:cdp:iam:us-west-1:account:resourceRole:EnvironmentUser",
        },
    ],
}


def test_iam_group_info_list_all_groups(module_args, mocker):
    """Test listing all IAM groups without filters."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group_info.CdpIamClient",
        autospec=True,
    ).return_value

    # Mock list_groups response
    client.list_groups.return_value = {
        "groups": [MOCK_GROUP_1, MOCK_GROUP_2],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert len(result.value.groups) == 2
    assert result.value.groups[0]["groupName"] == "test-group-1"
    assert result.value.groups[1]["groupName"] == "test-group-2"

    # Verify CdpIamClient was called correctly
    client.list_groups.assert_called_once_with(group_names=None)


def test_iam_group_info_get_specific_group(module_args, mocker):
    """Test getting details for a specific IAM group."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["test-group-1"],
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group_info.CdpIamClient",
        autospec=True,
    ).return_value

    # Mock get_group_details response
    client.get_group_details.return_value = MOCK_GROUP_DETAILS

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert len(result.value.groups) == 1
    assert result.value.groups[0]["groupName"] == "test-group-1"
    assert "members" in result.value.groups[0]
    assert "roles" in result.value.groups[0]
    assert "resourceAssignments" in result.value.groups[0]
    assert len(result.value.groups[0]["members"]) == 2
    assert len(result.value.groups[0]["roles"]) == 1
    assert len(result.value.groups[0]["resourceAssignments"]) == 1

    # Verify get_group_details was called
    client.get_group_details.assert_called_once_with("test-group-1")


def test_iam_group_info_get_multiple_groups(module_args, mocker):
    """Test getting details for multiple specific IAM groups."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["test-group-1", "test-group-2"],
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group_info.CdpIamClient",
        autospec=True,
    ).return_value

    # Mock get_group_details responses
    mock_group_2_details = {
        **MOCK_GROUP_2,
        "members": [],
        "roles": [],
        "resourceAssignments": [],
    }

    client.get_group_details.side_effect = [
        MOCK_GROUP_DETAILS,
        mock_group_2_details,
    ]

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert len(result.value.groups) == 2
    assert result.value.groups[0]["groupName"] == "test-group-1"
    assert result.value.groups[1]["groupName"] == "test-group-2"
    assert "members" in result.value.groups[0]
    assert "members" in result.value.groups[1]

    # Verify get_group_details was called twice
    assert client.get_group_details.call_count == 2


def test_iam_group_info_group_not_found(module_args, mocker):
    """Test behavior when a specific group is not found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ["nonexistent-group"],
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group_info.CdpIamClient",
        autospec=True,
    ).return_value

    # Mock get_group_details returning None (group not found)
    client.get_group_details.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    assert result.value.changed is False
    assert len(result.value.groups) == 0

    # Verify get_group_details was called
    client.get_group_details.assert_called_once_with("nonexistent-group")


def test_iam_group_info_check_mode(module_args, mocker):
    """Test check mode operation."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group_info.CdpIamClient",
        autospec=True,
    ).return_value

    # Mock list_groups response
    client.list_groups.return_value = {
        "groups": [MOCK_GROUP_1],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group_info.main()

    # Check mode should still work (info modules are read-only)
    assert result.value.changed is False
    assert len(result.value.groups) == 1
