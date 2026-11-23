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

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    MachineUser,
    WorkloadPasswordDetails,
)
from ansible_collections.cloudera.cloud.plugins.modules import iam_machine_user_info
from ansible_collections.cloudera.cloud.tests.unit import AnsibleExitJson


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MACHINE_USER_NAME = "test-machine-user"

MACHINE_USER_1 = MachineUser(
    machineUserName="machine-user-1",
    crn="crn:cdp:iam:us-west-1:account:machineUser:machine-user-1",
    creationDate="2025-01-01T00:00:00Z",
    status="ACTIVE",
)

MACHINE_USER_2 = MachineUser(
    machineUserName="machine-user-2",
    crn="crn:cdp:iam:us-west-1:account:machineUser:machine-user-2",
    creationDate="2025-01-02T00:00:00Z",
    status="ACTIVE",
    workloadUsername="mu_two",
    workloadPasswordDetails=WorkloadPasswordDetails(
        isPasswordSet=True,
        passwordExpirationDate="2030-01-01T00:00:00Z",
    ),
)


@pytest.fixture
def machine_user_info_module_args(module_args):
    """Pre-populate the common credentials for iam_machine_user_info module arguments."""

    def wrapped_args(args=None):
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        }
        merged.update(args or {})
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def client(mocker):
    """Patch load_cdp_config and CdpIamClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_machine_user_info.CdpIamClient",
        autospec=True,
    )
    return mock_class.return_value


def test_iam_machine_user_info_default(machine_user_info_module_args, client):
    """Test iam_machine_user_info module with no parameters returns all machine users."""

    machine_user_info_module_args()

    client.list_machine_users.return_value = [MACHINE_USER_1, MACHINE_USER_2]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 2
    assert result.value.machine_users[0]["machine_user_name"] == "machine-user-1"
    assert result.value.machine_users[1]["machine_user_name"] == "machine-user-2"

    client.list_machine_users.assert_called_once_with(machine_user_names=None)


def test_iam_machine_user_info_single_name(machine_user_info_module_args, client):
    """Test iam_machine_user_info module with a single machine user name."""

    machine_user_info_module_args({"name": MACHINE_USER_NAME})

    client.list_machine_users.return_value = [
        MachineUser(
            machineUserName=MACHINE_USER_NAME,
            crn=f"crn:cdp:iam:us-west-1:account:machineUser:{MACHINE_USER_NAME}",
            creationDate="2025-01-01T00:00:00Z",
            status="ACTIVE",
            workloadUsername=f"wl_{MACHINE_USER_NAME}",
        ),
    ]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 1
    assert result.value.machine_users[0]["machine_user_name"] == MACHINE_USER_NAME
    assert result.value.machine_users[0]["status"] == "ACTIVE"

    client.list_machine_users.assert_called_once_with(
        machine_user_names=[MACHINE_USER_NAME],
    )


def test_iam_machine_user_info_name_alias(machine_user_info_module_args, client):
    """Test that machine_user_name is accepted as an alias of name."""

    machine_user_info_module_args({"machine_user_name": MACHINE_USER_NAME})

    client.list_machine_users.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.machine_users == []
    client.list_machine_users.assert_called_once_with(
        machine_user_names=[MACHINE_USER_NAME],
    )


def test_iam_machine_user_info_multiple_names(machine_user_info_module_args, client):
    """Test iam_machine_user_info module with multiple machine user names."""

    machine_user_names = ["machine-user-1", "machine-user-2", "machine-user-3"]

    machine_user_info_module_args({"name": machine_user_names})

    client.list_machine_users.return_value = [
        MachineUser(
            machineUserName=name,
            crn=f"crn:cdp:iam:us-west-1:account:machineUser:{name}",
            creationDate="2025-01-01T00:00:00Z",
            status="ACTIVE",
        )
        for name in machine_user_names
    ]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert [mu["machine_user_name"] for mu in result.value.machine_users] == (
        machine_user_names
    )

    client.list_machine_users.assert_called_once_with(
        machine_user_names=machine_user_names,
    )


def test_iam_machine_user_info_not_found(machine_user_info_module_args, client):
    """Test iam_machine_user_info module when machine user is not found."""

    machine_user_info_module_args({"name": "nonexistent-machine-user"})

    client.list_machine_users.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert result.value.machine_users == []

    client.list_machine_users.assert_called_once_with(
        machine_user_names=["nonexistent-machine-user"],
    )


def test_iam_machine_user_info_output_shape(machine_user_info_module_args, client):
    """Test that the documented output keys are produced from the dataclass fields."""

    machine_user_info_module_args({"name": "machine-user-2"})

    client.list_machine_users.return_value = [MACHINE_USER_2]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.machine_users == [
        {
            "machine_user_name": "machine-user-2",
            "crn": "crn:cdp:iam:us-west-1:account:machineUser:machine-user-2",
            "creation_date": "2025-01-02T00:00:00Z",
            "status": "ACTIVE",
            "workload_username": "mu_two",
            "workload_password_details": {
                "is_password_set": True,
                "password_expiration_date": "2030-01-01T00:00:00Z",
            },
        },
    ]


def test_iam_machine_user_info_omits_unset_fields(
    machine_user_info_module_args,
    client,
):
    """Test that fields the API did not return are left out of the output."""

    machine_user_info_module_args()

    client.list_machine_users.return_value = [MACHINE_USER_1]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.machine_users == [
        {
            "machine_user_name": "machine-user-1",
            "crn": "crn:cdp:iam:us-west-1:account:machineUser:machine-user-1",
            "creation_date": "2025-01-01T00:00:00Z",
            "status": "ACTIVE",
        },
    ]


def test_iam_machine_user_info_check_mode(machine_user_info_module_args, client):
    """Test that the module is read-only and still returns data in check mode."""

    machine_user_info_module_args({"_ansible_check_mode": True})

    client.list_machine_users.return_value = [MACHINE_USER_1, MACHINE_USER_2]

    with pytest.raises(AnsibleExitJson) as result:
        iam_machine_user_info.main()

    assert result.value.changed is False
    assert len(result.value.machine_users) == 2
