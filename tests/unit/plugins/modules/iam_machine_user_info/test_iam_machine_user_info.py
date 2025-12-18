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

from ansible_collections.cloudera.cloud.plugins.modules import iam_machine_user_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MACHINE_USER_NAME = "test-machine-user"


def test_iam_machine_user_info_default(module_args, mocker):
    """Test iam_machine_user_info module with no parameters returns all machine users."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_machine_users.return_value = {
        "machineUsers": [
            {
                "machineUserName": "machine-user-1",
                "crn": "crn:cdp:iam:us-west-1:account:machineUser:machine-user-1",
                "creationDate": "2025-01-01T00:00:00Z",
                "status": "ACTIVE",
            },
            {
                "machineUserName": "machine-user-2",
                "crn": "crn:cdp:iam:us-west-1:account:machineUser:machine-user-2",
                "creationDate": "2025-01-02T00:00:00Z",
                "status": "ACTIVE",
            },
        ]
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 2
    assert result.value.machine_users[0]["machine_user_name"] == "machine-user-1"
    assert result.value.machine_users[1]["machine_user_name"] == "machine-user-2"

    # Verify CdpIamClient was called correctly
    client.list_machine_users.assert_called_once_with(machine_user_names=None)


def test_iam_machine_user_info_single_name(module_args, mocker):
    """Test iam_machine_user_info module with a single machine user name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": MACHINE_USER_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_machine_users.return_value = {
        "machineUsers": [
            {
                "machineUserName": MACHINE_USER_NAME,
                "crn": f"crn:cdp:iam:us-west-1:account:machineUser:{MACHINE_USER_NAME}",
                "creationDate": "2025-01-01T00:00:00Z",
                "status": "ACTIVE",
                "workloadUsername": f"wl_{MACHINE_USER_NAME}",
            }
        ]
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 1
    assert result.value.machine_users[0]["machine_user_name"] == MACHINE_USER_NAME
    assert result.value.machine_users[0]["status"] == "ACTIVE"

    # Verify CdpIamClient was called correctly with the machine user name
    client.list_machine_users.assert_called_once_with(
        machine_user_names=[MACHINE_USER_NAME]
    )


def test_iam_machine_user_info_multiple_names(module_args, mocker):
    """Test iam_machine_user_info module with multiple machine user names."""

    machine_user_names = ["machine-user-1", "machine-user-2", "machine-user-3"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": machine_user_names,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_machine_users.return_value = {
        "machineUsers": [
            {
                "machineUserName": name,
                "crn": f"crn:cdp:iam:us-west-1:account:machineUser:{name}",
                "creationDate": "2025-01-01T00:00:00Z",
                "status": "ACTIVE",
            }
            for name in machine_user_names
        ]
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 3

    # Verify all machine users are returned
    returned_names = [mu["machine_user_name"] for mu in result.value.machine_users]
    assert sorted(returned_names) == sorted(machine_user_names)

    # Verify CdpIamClient was called correctly with the list of names
    client.list_machine_users.assert_called_once_with(
        machine_user_names=machine_user_names
    )


def test_iam_machine_user_info_not_found(module_args, mocker):
    """Test iam_machine_user_info module when machine user is not found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-machine-user",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user_info.CdpIamClient",
        autospec=True,
    ).return_value
    client.list_machine_users.return_value = {"machineUsers": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 0

    # Verify CdpIamClient was called correctly
    client.list_machine_users.assert_called_once_with(
        machine_user_names=["nonexistent-machine-user"]
    )
