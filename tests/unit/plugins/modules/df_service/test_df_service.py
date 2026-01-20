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

from ansible_collections.cloudera.cloud.plugins.modules import df_service


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-456"


def test_df_service_enable_success(module_args, mocker):
    """Test enabling a DataFlow service successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service doesn't exist yet
    client.get_service_by_crn.return_value = None
    client.get_service_by_env_crn.return_value = None

    # Mock enable_service response
    client.enable_service.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "ENABLING", "message": "Service is enabling"},
            "deploymentCount": 0,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 3,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN
    assert result.value.service["status"]["state"] == "ENABLING"

    # Verify CdpDfClient was called correctly
    client.enable_service.assert_called_once()
    call_args = client.enable_service.call_args[1]
    assert call_args["environment_crn"] == ENV_CRN
    assert call_args["min_k8s_node_count"] == 3
    assert call_args["max_k8s_node_count"] == 3


def test_df_service_enable_by_name(module_args, mocker):
    """Test enabling a DataFlow service using environment name (should work if API accepts it)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_NAME,  # Using name instead of CRN
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service doesn't exist yet
    client.get_service_by_env_crn.return_value = None

    client.enable_service.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "status": {"state": "ENABLING"},
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # Module should successfully enable service (API would validate CRN format)
    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN

    # Verify enable_service was called with the provided env_crn (even if it's a name)
    client.enable_service.assert_called_once()
    call_args = client.enable_service.call_args[1]
    assert call_args["environment_crn"] == ENV_NAME


def test_df_service_already_enabled(module_args, mocker):
    """Test when DataFlow service is already enabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service already exists
    client.get_service_by_env_crn.return_value = {
        "crn": SERVICE_CRN,
        "name": ENV_NAME,
        "environmentCrn": ENV_CRN,
        "status": {"state": "ENABLED", "message": "Service is running"},
        "deploymentCount": 5,
        "minK8sNodeCount": 3,
        "maxK8sNodeCount": 10,
    }

    # Mock: No updates needed (patch the function instead of method)
    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {}

    # Test module execution - should warn and not change
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False
    assert result.value.service["status"]["state"] == "ENABLED"

    # Verify enable_service was NOT called
    client.enable_service.assert_not_called()


def test_df_service_disable_success(module_args, mocker):
    """Test disabling a DataFlow service successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service exists and is enabled
    client.get_service_by_crn.return_value = {
        "crn": SERVICE_CRN,
        "name": ENV_NAME,
        "environmentCrn": ENV_CRN,
        "status": {"state": "ENABLED", "message": "Service is running"},
    }

    # Mock disable_service response
    client.disable_service.return_value = {}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    # Verify disable_service was called correctly
    client.disable_service.assert_called_once()
    call_args = client.disable_service.call_args[1]
    assert call_args["crn"] == SERVICE_CRN
    assert call_args["terminate_deployments"] is False


def test_df_service_disable_with_terminate(module_args, mocker):
    """Test disabling a DataFlow service with terminate deployments."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "terminate": True,
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service exists
    client.get_service_by_crn.return_value = {
        "crn": SERVICE_CRN,
        "status": {"state": "ENABLED"},
    }

    client.disable_service.return_value = {}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    # Verify disable_service was called with terminate=True
    client.disable_service.assert_called_once()
    call_args = client.disable_service.call_args[1]
    assert call_args["terminate_deployments"] is True


def test_df_service_disable_with_wait(module_args, mocker):
    """Test disabling a DataFlow service with wait enabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "terminate": True,
            "wait": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    mock_client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    )
    # Set the DISABLED_STATES class attribute
    mock_client_class.DISABLED_STATES = ["NOT_ENABLED"]
    client = mock_client_class.return_value

    # Mock: Service exists
    client.get_service_by_crn.return_value = {
        "crn": SERVICE_CRN,
        "status": {"state": "GOOD_HEALTH"},
    }

    # Mock wait_for_service_state response (module uses wait_for_service_state, not disable_service_and_wait)
    client.wait_for_service_state.return_value = {
        "crn": SERVICE_CRN,
        "status": {"state": "NOT_ENABLED"},
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    # Verify wait_for_service_state was called correctly
    client.wait_for_service_state.assert_called_once()
    call_args = client.wait_for_service_state.call_args[1]
    assert call_args["service_crn"] == SERVICE_CRN
    assert call_args["terminate_deployments"] is True
    assert call_args["target_states"] == ["NOT_ENABLED"]


def test_df_service_disable_already_disabled(module_args, mocker):
    """Test disabling when service is already disabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service doesn't exist
    client.get_service_by_crn.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False

    # Verify disable_service was NOT called
    client.disable_service.assert_not_called()


def test_df_service_enable_check_mode(module_args, mocker):
    """Test enabling a DataFlow service in check mode."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service doesn't exist
    client.get_service_by_env_crn.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # In check mode, should not make changes
    assert result.value.changed is False
    client.enable_service.assert_not_called()


def test_df_service_enable_with_custom_params(module_args, mocker):
    """Test enabling a DataFlow service with custom parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "nodes_min": 5,
            "nodes_max": 20,
            "public_loadbalancer": True,
            "private_cluster": True,
            "k8s_ip_ranges": ["10.0.0.0/16"],
            "loadbalancer_ip_ranges": ["192.168.1.0/24"],
            "cluster_subnets": ["subnet-abc123"],
            "loadbalancer_subnets": ["subnet-def456"],
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service doesn't exist
    client.get_service_by_env_crn.return_value = None

    # Mock enable_service response
    client.enable_service.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "status": {"state": "ENABLING"},
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    # Verify all custom parameters were passed
    client.enable_service.assert_called_once()
    call_args = client.enable_service.call_args[1]
    assert call_args["min_k8s_node_count"] == 5
    assert call_args["max_k8s_node_count"] == 20
    assert call_args["use_public_load_balancer"] is True
    assert call_args["private_cluster"] is True
    assert call_args["kubernetes_ip_cidr_blocks"] == ["10.0.0.0/16"]
    assert call_args["load_balancer_ip_cidr_blocks"] == ["192.168.1.0/24"]
    assert call_args["cluster_subnet_ids"] == ["subnet-abc123"]
    assert call_args["load_balancer_subnet_ids"] == ["subnet-def456"]


def test_df_service_update_success(module_args, mocker):
    """Test updating an existing DataFlow service successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "nodes_min": 5,
            "nodes_max": 15,
            "k8s_ip_ranges": ["10.0.0.0/16", "192.168.1.0/24"],
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service already exists with different configuration
    existing_service = {
        "crn": SERVICE_CRN,
        "name": ENV_NAME,
        "environmentCrn": ENV_CRN,
        "status": {"state": "ENABLED", "message": "Service is running"},
        "minK8sNodeCount": 3,
        "maxK8sNodeCount": 10,
        "kubeApiAuthorizedIpRanges": ["10.0.0.0/16"],
        "loadBalancerAuthorizedIpRanges": [],
    }
    client.get_service_by_env_crn.return_value = existing_service

    # Mock check_service_updates to indicate update is needed
    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "min_k8s_node_count": 5,
        "max_k8s_node_count": 15,
        "kubernetes_ip_cidr_blocks": ["10.0.0.0/16", "192.168.1.0/24"],
    }

    # Mock update_service response
    client.update_service.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "status": {"state": "ENABLED"},
            "minK8sNodeCount": 5,
            "maxK8sNodeCount": 15,
            "kubeApiAuthorizedIpRanges": ["10.0.0.0/16", "192.168.1.0/24"],
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    # Service response from update_service wraps in "service" key, then gets extracted
    assert result.value.service["minK8sNodeCount"] == 5
    assert result.value.service["maxK8sNodeCount"] == 15

    # Verify check_service_updates was called correctly
    check_updates.assert_called_once()
    check_args = check_updates.call_args[1]
    assert check_args["service_crn"] == SERVICE_CRN
    assert check_args["service_details"] == existing_service
    assert check_args["min_k8s_node_count"] == 5
    assert check_args["max_k8s_node_count"] == 15
    assert check_args["kubernetes_ip_cidr_blocks"] == ["10.0.0.0/16", "192.168.1.0/24"]

    # Verify update_service was called
    client.update_service.assert_called_once()


def test_df_service_update_no_changes(module_args, mocker):
    """Test when service exists and no updates are needed."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "nodes_min": 3,
            "nodes_max": 10,
            "k8s_ip_ranges": ["10.0.0.0/16"],
            "wait": False,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service already exists with same configuration
    existing_service = {
        "crn": SERVICE_CRN,
        "name": ENV_NAME,
        "environmentCrn": ENV_CRN,
        "status": {"state": "ENABLED"},
        "minK8sNodeCount": 3,
        "maxK8sNodeCount": 10,
        "kubeApiAuthorizedIpRanges": ["10.0.0.0/16"],
    }
    client.get_service_by_env_crn.return_value = existing_service

    # Mock check_service_updates to indicate no update is needed
    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # No changes should be made
    assert result.value.changed is False
    assert result.value.service["crn"] == SERVICE_CRN

    # Verify check_service_updates was called
    check_updates.assert_called_once()

    # Verify update_service was NOT called
    client.update_service.assert_not_called()


def test_df_service_update_with_wait(module_args, mocker):
    """Test updating a DataFlow service with wait enabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "nodes_min": 5,
            "nodes_max": 20,
            "wait": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service exists
    existing_service = {
        "crn": SERVICE_CRN,
        "status": {"state": "ENABLED"},
        "minK8sNodeCount": 3,
        "maxK8sNodeCount": 10,
    }
    client.get_service_by_env_crn.return_value = existing_service

    # Mock check_service_updates to indicate update is needed
    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "min_k8s_node_count": 5,
        "max_k8s_node_count": 20,
    }

    # Mock update_service response
    client.update_service.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "status": {"state": "UPDATING"},
            "minK8sNodeCount": 5,
            "maxK8sNodeCount": 20,
        },
    }

    # Mock wait_for_service_state response
    client.wait_for_service_state.return_value = {
        "crn": SERVICE_CRN,
        "status": {"state": "GOOD_HEALTH"},
        "minK8sNodeCount": 5,
        "maxK8sNodeCount": 20,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["status"]["state"] == "GOOD_HEALTH"

    # Verify update_service was called
    client.update_service.assert_called_once()

    # Verify wait_for_service_state was called
    client.wait_for_service_state.assert_called_once()
    wait_args = client.wait_for_service_state.call_args[1]
    assert wait_args["service_crn"] == SERVICE_CRN
    assert wait_args["target_states"] == ["GOOD_HEALTH"]


def test_df_service_update_check_mode(module_args, mocker):
    """Test updating a DataFlow service in check mode."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
            "state": "present",
            "nodes_min": 5,
            "nodes_max": 20,
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Service exists
    existing_service = {
        "crn": SERVICE_CRN,
        "status": {"state": "ENABLED"},
        "minK8sNodeCount": 3,
        "maxK8sNodeCount": 10,
    }
    client.get_service_by_env_crn.return_value = existing_service

    # Mock check_service_updates to indicate update is needed
    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "min_k8s_node_count": 5,
        "max_k8s_node_count": 20,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # In check mode, should indicate changes but not make them
    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN

    # Verify check_service_updates was called
    check_updates.assert_called_once()

    # Verify update_service was NOT called in check mode
    client.update_service.assert_not_called()
