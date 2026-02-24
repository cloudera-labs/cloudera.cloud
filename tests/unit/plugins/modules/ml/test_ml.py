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

from ansible_collections.cloudera.cloud.plugins.modules import ml
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_ml import CdpMlClient


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
WORKSPACE_NAME = "test-workspace"
WORKSPACE_CRN = "crn:cdp:ml:us-west-1:tenant:workspace:ws-456"


def test_ml_create_workspace_success(module_args, mocker):
    """Test creating a new ML workspace with minimal required parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist yet
    client.describe_workspace.return_value = {}

    # Mock create_workspace response (returns None, side effect only)
    client.create_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify CdpMlClient methods were called correctly
    client.describe_workspace.assert_called_once_with(name=WORKSPACE_NAME, env=ENV_NAME)
    client.create_workspace.assert_called_once()
    call_args = client.create_workspace.call_args[1]
    assert call_args["workspace_name"] == WORKSPACE_NAME
    assert call_args["environment_name"] == ENV_NAME
    assert call_args["disable_tls"] is False
    assert call_args["enable_monitoring"] is False
    assert call_args["enable_governance"] is False
    assert call_args["enable_model_metrics"] is False


def test_ml_create_workspace_with_k8s_request(module_args, mocker):
    """Test creating workspace with custom Kubernetes provisioning request."""

    k8s_request = {
        "environmentName": ENV_NAME,
        "instanceGroups": [
            {
                "instanceType": "m5.2xlarge",
                "instanceCount": 3,
            },
        ],
        "tags": {
            "project": "analytics",
            "owner": "data-team",
        },
    }

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "k8s_request": k8s_request,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist yet
    client.describe_workspace.return_value = {}
    client.create_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify create_workspace was called with k8s_request
    client.create_workspace.assert_called_once()
    call_args = client.create_workspace.call_args[1]
    assert call_args["provision_k8s_request"] is not None

    # Verify tags were converted from dict to list of dicts
    k8s_req = call_args["provision_k8s_request"]
    assert "tags" in k8s_req
    assert isinstance(k8s_req["tags"], list)
    assert len(k8s_req["tags"]) == len(k8s_request["tags"])
    # Tags should be converted to key/value pairs
    tag_keys = [t["key"] for t in k8s_req["tags"]]
    assert set(tag_keys) == set(k8s_request["tags"].keys())


def test_ml_create_workspace_with_wait(module_args, mocker):
    """Test creating workspace with wait enabled until READY state."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": True,
            "delay": 10,
            "timeout": 600,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist yet
    client.describe_workspace.return_value = {}
    client.create_workspace.return_value = None

    # Mock wait_for_workspace_state to return a completed workspace
    client.wait_for_workspace_state.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
            "instanceUrl": f"https://{WORKSPACE_NAME}.cloudera.site",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True
    assert result.value.workspace is not None
    assert "workspace" in result.value.workspace
    assert (
        result.value.workspace["workspace"]["instanceStatus"] == "installation:finished"
    )

    # Verify wait_for_workspace_state was called with correct parameters
    client.wait_for_workspace_state.assert_called_once()
    call_args = client.wait_for_workspace_state.call_args[0]
    assert call_args[0] == ENV_NAME
    assert call_args[1] == WORKSPACE_NAME


def test_ml_create_workspace_check_mode(module_args, mocker):
    """Test creating workspace in check mode (no actual creation)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": False,
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist yet
    client.describe_workspace.return_value = {}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    # In check mode, changed should be False and no actual creation
    assert result.value.changed is False

    # Verify create_workspace was NOT called
    client.create_workspace.assert_not_called()

    # describe_workspace should have been called to check existence
    client.describe_workspace.assert_called_once()


def test_ml_create_workspace_missing_environment(module_args, mocker):
    """Test failure when environment parameter is missing."""

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient to avoid real API calls
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            # Missing environment parameter
            "state": "present",
        },
    )

    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="missing: environment"):
        ml.main()


def test_ml_workspace_already_created(module_args, mocker):
    """Test creating workspace when workspace is already existing."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace already exists
    client.describe_workspace.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
            "instanceUrl": f"https://{WORKSPACE_NAME}.cloudera.site",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    # When workspace already exists, changed should be False
    assert result.value.changed is False

    # Verify create_workspace was NOT called
    client.create_workspace.assert_not_called()

    # Verify describe_workspace was called
    client.describe_workspace.assert_called_once()


def test_ml_create_workspace_with_namespace(module_args, mocker):
    """Test creating workspace for Cloudera on premise."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "namespace": "cdp-ml-workspace",
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist yet
    client.describe_workspace.return_value = {}
    client.create_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify create_workspace was called with namespace parameter
    client.create_workspace.assert_called_once()
    call_args = client.create_workspace.call_args[1]
    assert call_args["workspace_name"] == WORKSPACE_NAME
    assert call_args["environment_name"] == ENV_NAME
    assert call_args["namespace"] == "cdp-ml-workspace"


def test_ml_delete_workspace_success(module_args, mocker):
    """Test deleting an existing workspace."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )
    # Set class attributes to real values to avoid mocking them
    client_class.REMOVABLE_STATES = CdpMlClient.REMOVABLE_STATES
    client = client_class.return_value

    # Mock: Workspace exists and is in a removable state
    client.describe_workspace.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
            "instanceUrl": f"https://{WORKSPACE_NAME}.cloudera.site",
        },
    }

    # Mock delete_workspace response
    client.delete_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify delete_workspace was called correctly
    client.describe_workspace.assert_called_once_with(name=WORKSPACE_NAME, env=ENV_NAME)
    client.delete_workspace.assert_called_once()
    call_args = client.delete_workspace.call_args[1]
    assert call_args["workspace_name"] == WORKSPACE_NAME
    assert call_args["environment_name"] == ENV_NAME
    assert call_args["force"] is False
    assert call_args["remove_storage"] is True


def test_ml_delete_workspace_with_force(module_args, mocker):
    """Test force deleting workspace even with errors."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "force": True,
            "storage": False,
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )
    # Set class attributes to real values to avoid mocking them
    client_class.REMOVABLE_STATES = CdpMlClient.REMOVABLE_STATES
    client = client_class.return_value

    # Mock: Workspace exists
    client.describe_workspace.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
        },
    }

    client.delete_workspace.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify delete_workspace was called with force=True and remove_storage=False
    client.delete_workspace.assert_called_once()
    call_args = client.delete_workspace.call_args[1]
    assert call_args["force"] is True
    assert call_args["remove_storage"] is False


def test_ml_delete_workspace_with_wait(module_args, mocker):
    """Test deleting workspace with wait until removed."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": True,
            "delay": 10,
            "timeout": 600,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )
    # Set class attributes to real values to avoid mocking them
    client_class.REMOVABLE_STATES = CdpMlClient.REMOVABLE_STATES
    client = client_class.return_value

    # Mock: Workspace exists
    client.describe_workspace.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
        },
    }

    client.delete_workspace.return_value = None
    client.wait_for_workspace_state.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    assert result.value.changed is True

    # Verify delete_workspace was called
    client.delete_workspace.assert_called_once()

    # Verify wait_for_workspace_state was called with None (waiting for removal)
    client.wait_for_workspace_state.assert_called_once()
    call_args = client.wait_for_workspace_state.call_args[0]
    assert call_args[0] == ENV_NAME
    assert call_args[1] == WORKSPACE_NAME
    assert call_args[2] is None  # Waiting for workspace to be removed


def test_ml_delete_workspace_already_absent(module_args, mocker):
    """Test when workspace is already deleted/doesn't exist."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist
    client.describe_workspace.return_value = {}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    # When workspace is already absent, changed should be False
    assert result.value.changed is False

    # Verify delete_workspace was NOT called
    client.delete_workspace.assert_not_called()

    # Verify describe_workspace was called
    client.describe_workspace.assert_called_once()


def test_ml_create_workspace_api_failure(module_args, mocker):
    """Test handling API failure during creation."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist
    client.describe_workspace.return_value = {}

    # Mock create_workspace to raise an exception
    client.create_workspace.side_effect = Exception("API connection failed")

    # Test module execution - should propagate the exception
    with pytest.raises(Exception, match="API connection failed"):
        ml.main()


def test_ml_delete_workspace_api_failure(module_args, mocker):
    """Test handling API failure during deletion."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )
    # Set class attributes to real values
    client_class.REMOVABLE_STATES = CdpMlClient.REMOVABLE_STATES
    client = client_class.return_value

    # Mock: Workspace exists
    client.describe_workspace.return_value = {
        "workspace": {
            "instanceName": WORKSPACE_NAME,
            "environmentName": ENV_NAME,
            "crn": WORKSPACE_CRN,
            "instanceStatus": "installation:finished",
        },
    }

    # Mock delete_workspace to raise an exception
    client.delete_workspace.side_effect = Exception("Delete operation failed")

    # Test module execution - should propagate the exception
    with pytest.raises(Exception, match="Delete operation failed"):
        ml.main()


def test_ml_workspace_invalid_state(module_args, mocker):
    """Test with invalid state parameter."""

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "invalid_state",
        },
    )

    # Expect the module to fail due to invalid state value
    with pytest.raises(AnsibleFailJson, match="value of state must be one of"):
        ml.main()


def test_ml_workspace_invalid_k8s_request(module_args, mocker):
    """Test with malformed k8s_request configuration."""

    # Missing required fields in k8s_request
    k8s_request = {
        # Missing environmentName (required)
        "instanceGroups": [],
    }

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "k8s_request": k8s_request,
            "state": "present",
        },
    )

    # Expect the module to fail due to missing required field in k8s_request
    with pytest.raises(AnsibleFailJson, match="environmentName"):
        ml.main()


def test_ml_workspace_wait_timeout(module_args, mocker):
    """Test timeout during wait operation."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": WORKSPACE_NAME,
            "environment": ENV_NAME,
            "state": "present",
            "wait": True,
            "timeout": 60,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpMlClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.ml.CdpMlClient",
        autospec=True,
    ).return_value

    # Mock: Workspace doesn't exist
    client.describe_workspace.return_value = {}
    client.create_workspace.return_value = None

    # Mock wait_for_workspace_state to raise a timeout exception
    from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import (
        CdpError,
    )

    client.wait_for_workspace_state.side_effect = CdpError(
        "Timeout waiting for workspace to reach ready state"
    )

    # Test module execution - should propagate the timeout exception
    with pytest.raises(CdpError, match="Timeout waiting for workspace"):
        ml.main()
