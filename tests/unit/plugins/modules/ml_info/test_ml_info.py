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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import ml_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

# Mock workspace data
MOCK_WORKSPACES = [
    {
        "instanceName": "workspace1",
        "environmentName": "test-env",
        "crn": "crn:cdp:ml:us-west-1:account:workspace:ws1",
        "instanceStatus": "installation:finished",
        "instanceUrl": "https://workspace1.cloudera.site",
    },
    {
        "instanceName": "workspace2",
        "environmentName": "test-env",
        "crn": "crn:cdp:ml:us-west-1:account:workspace:ws2",
        "instanceStatus": "installation:finished",
        "instanceUrl": "https://workspace2.cloudera.site",
    },
]

MOCK_WORKSPACE_SINGLE = {
    "workspace": {
        "instanceName": "my-workspace",
        "environmentName": "my-env",
        "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123",
        "instanceStatus": "installation:finished",
        "instanceUrl": "https://my-workspace.cloudera.site",
    },
}


def test_ml_info_name_without_environment_fails(module_args):
    """Test ml_info module fails when name is provided without environment."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "my-workspace",
            # environment is intentionally omitted
        },
    )

    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="environment"):
        ml_info.main()


def test_ml_info_default_list_all(module_args, mocker):
    """Test ml_info module listing all workspaces."""

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

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_all_workspaces to return list of workspaces
    client.describe_all_workspaces.return_value = MOCK_WORKSPACES

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces is a list
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 2

    # Verify describe_all_workspaces was called with env=None
    client.describe_all_workspaces.assert_called_once_with(None)


def test_ml_info_list_by_environment(module_args, mocker):
    """Test ml_info module listing workspaces by environment."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": "test-env",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_all_workspaces to return filtered list
    client.describe_all_workspaces.return_value = MOCK_WORKSPACES

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces is a list
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 2

    # Verify all workspaces are from test-env
    for workspace in result.value.workspaces:
        assert workspace["environmentName"] == "test-env"

    # Verify describe_all_workspaces was called with env="test-env"
    client.describe_all_workspaces.assert_called_once_with("test-env")


def test_ml_info_describe_by_name_and_env(module_args, mocker):
    """Test ml_info module describing a workspace by name and environment."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "my-workspace",
            "environment": "my-env",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_workspace to return single workspace wrapped in "workspace" key
    client.describe_workspace.return_value = MOCK_WORKSPACE_SINGLE

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces is a list with 1 element
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 1

    # Assert workspace details are correct
    workspace = result.value.workspaces[0]
    assert workspace["instanceName"] == "my-workspace"
    assert workspace["environmentName"] == "my-env"

    # Verify describe_workspace was called with correct name and env parameters
    client.describe_workspace.assert_called_once_with(
        name="my-workspace",
        env="my-env",
        crn=None,
    )

    # Verify describe_all_workspaces was NOT called
    client.describe_all_workspaces.assert_not_called()


def test_ml_info_describe_by_crn(module_args, mocker):
    """Test ml_info module describing a workspace by CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_workspace to return single workspace
    client.describe_workspace.return_value = MOCK_WORKSPACE_SINGLE

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces contains single workspace
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 1

    # Assert workspace CRN matches
    workspace = result.value.workspaces[0]
    assert (
        workspace["crn"]
        == "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123"
    )

    # Verify describe_workspace was called with crn parameter
    client.describe_workspace.assert_called_once_with(
        name=None,
        env=None,
        crn="crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123",
    )

    # Verify describe_all_workspaces was NOT called
    client.describe_all_workspaces.assert_not_called()


def test_ml_info_empty_workspaces_list(module_args, mocker):
    """Test ml_info module with empty workspaces list."""

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

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_all_workspaces to return empty list
    client.describe_all_workspaces.return_value = []

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces is empty list
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 0
    assert result.value.workspaces == []

    # Verify describe_all_workspaces was called
    client.describe_all_workspaces.assert_called_once_with(None)


def test_ml_info_workspace_not_found(module_args, mocker):
    """Test ml_info module when workspace is not found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "non-existent-workspace",
            "environment": "non-existent-env",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml_info.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock describe_workspace to return None (not found)
    client.describe_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    # Assert result.value.changed is False
    assert result.value.changed is False

    # Assert result.value.workspaces is empty (None is not appended)
    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert len(result.value.workspaces) == 0

    # Verify describe_workspace was called with correct parameters
    client.describe_workspace.assert_called_once_with(
        name="non-existent-workspace",
        env="non-existent-env",
        crn=None,
    )

    # Verify describe_all_workspaces was NOT called
    client.describe_all_workspaces.assert_not_called()
