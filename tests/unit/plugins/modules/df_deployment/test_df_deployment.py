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
    AnsibleFailJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import df_deployment


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:svc-123"
FLOW_VERSION_CRN = "crn:cdp:df:us-west-1:tenant:flow-version:fv-123"
DEPLOYMENT_CRN = "crn:cdp:df:us-west-1:tenant:deployment:dep-123"
DEPLOYMENT_NAME = "test-deployment"
DEPLOYMENT_REQUEST_CRN = "crn:cdp:df:us-west-1:tenant:deployment-request:req-123"

EXISTING_DEPLOYMENT = {
    "deployment": {
        "crn": DEPLOYMENT_CRN,
        "name": DEPLOYMENT_NAME,
        "status": {"state": "GOOD_HEALTH"},
        "clusterSize": {"name": "SMALL"},
        "staticNodeCount": 1,
        "autoScalingEnabled": False,
        "autoScaleMinNodes": 1,
        "autoScaleMaxNodes": 3,
        "flowMetricsScalingEnabled": False,
    }
}


@pytest.fixture
def mock_clients(mocker):
    """Fixture to mock all external clients used by df_deployment."""
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
        return_value=(FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION),
    )

    df_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment.CdpDfClient",
        autospec=True,
    ).return_value

    env_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment.CdpEnvClient",
        autospec=True,
    ).return_value

    iam_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment.CdpIamClient",
        autospec=True,
    ).return_value

    # Sensible defaults
    env_client.describe_environment.return_value = {"crn": ENV_CRN}
    df_client.get_service_by_env_crn.return_value = {
        "service": {"crn": SERVICE_CRN}
    }
    df_client.create_workload_client.return_value = mocker.MagicMock()

    return df_client, env_client, iam_client


# ---------------------------------------------------------------------------
# CREATE tests
# ---------------------------------------------------------------------------


def test_df_deployment_create_success(module_args, mock_clients):
    """Test creating a new deployment successfully."""
    df_client, env_client, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "cluster_size": "SMALL",
            "static_node_count": 1,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    df_client.initiate_deployment.return_value = {
        "deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN,
    }
    df_client.create_deployment.return_value = {
        "deployment": {
            "crn": DEPLOYMENT_CRN,
            "name": DEPLOYMENT_NAME,
            "status": {"state": "DEPLOYING"},
        }
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    assert result.value.deployment["crn"] == DEPLOYMENT_CRN

    df_client.initiate_deployment.assert_called_once_with(
        service_crn=SERVICE_CRN,
        flow_version_crn=FLOW_VERSION_CRN,
    )
    df_client.create_deployment.assert_called_once()


def test_df_deployment_create_with_autoscaling(module_args, mock_clients):
    """Test creating a deployment with autoscaling enabled."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "cluster_size": "MEDIUM",
            "autoscaling_enabled": True,
            "autoscale_min_nodes": 2,
            "autoscale_max_nodes": 10,
            "flow_metrics_scaling_enabled": True,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    df_client.initiate_deployment.return_value = {
        "deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN,
    }
    df_client.create_deployment.return_value = {
        "deployment": {"crn": DEPLOYMENT_CRN, "name": DEPLOYMENT_NAME}
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    call_kwargs = df_client.create_deployment.call_args[1]
    assert call_kwargs["auto_scaling_enabled"] is True
    assert call_kwargs["auto_scale_min_nodes"] == 2
    assert call_kwargs["auto_scale_max_nodes"] == 10
    assert call_kwargs["flow_metrics_scaling_enabled"] is True


def test_df_deployment_create_with_df_name(module_args, mock_clients):
    """Test creating a deployment by looking up service via df_name."""
    df_client, env_client, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "df_name": "my-dataflow-service",
            "flow_version_crn": FLOW_VERSION_CRN,
            "cluster_size": "SMALL",
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    df_client.get_service_by_name.return_value = {"crn": SERVICE_CRN}
    df_client.initiate_deployment.return_value = {
        "deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN,
    }
    df_client.create_deployment.return_value = {
        "deployment": {"crn": DEPLOYMENT_CRN, "name": DEPLOYMENT_NAME}
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    df_client.get_service_by_name.assert_called_once_with("my-dataflow-service")


def test_df_deployment_create_idempotent_no_changes(module_args, mock_clients):
    """Test that an existing deployment with no changes is idempotent."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = EXISTING_DEPLOYMENT

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is False
    assert result.value.deployment["crn"] == DEPLOYMENT_CRN
    df_client.create_deployment.assert_not_called()
    df_client.update_deployment.assert_not_called()


# ---------------------------------------------------------------------------
# UPDATE tests
# ---------------------------------------------------------------------------


def test_df_deployment_update_cluster_size(module_args, mock_clients):
    """Test updating an existing deployment's cluster size."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "cluster_size": "LARGE",
            "configuration_version": 1,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = EXISTING_DEPLOYMENT
    df_client.update_deployment.return_value = {
        "deploymentConfiguration": {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
                "clusterSize": {"name": "LARGE"},
            }
        }
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    df_client.update_deployment.assert_called_once()
    call_kwargs = df_client.update_deployment.call_args[1]
    assert call_kwargs["cluster_size"] == "LARGE"


def test_df_deployment_update_static_node_count(module_args, mock_clients):
    """Test updating an existing deployment's static node count."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "static_node_count": 3,
            "configuration_version": 1,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = EXISTING_DEPLOYMENT
    df_client.update_deployment.return_value = {
        "deploymentConfiguration": {
            "deployment": {"crn": DEPLOYMENT_CRN, "name": DEPLOYMENT_NAME}
        }
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    call_kwargs = df_client.update_deployment.call_args[1]
    assert call_kwargs["static_node_count"] == 3


def test_df_deployment_update_parameter_groups(module_args, mock_clients):
    """Test updating deployment parameter groups always triggers a change."""
    df_client, _, _ = mock_clients

    new_params = [
        {
            "name": "parameters",
            "parameters": [{"name": "broker", "value": "new-host:9092"}],
        }
    ]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "parameter_groups": new_params,
            "configuration_version": 2,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = EXISTING_DEPLOYMENT
    df_client.update_deployment.return_value = {
        "deploymentConfiguration": {
            "deployment": {"crn": DEPLOYMENT_CRN, "name": DEPLOYMENT_NAME}
        }
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    call_kwargs = df_client.update_deployment.call_args[1]
    assert call_kwargs["parameter_groups"] == new_params


# ---------------------------------------------------------------------------
# DELETE tests
# ---------------------------------------------------------------------------


def test_df_deployment_delete_success(module_args, mock_clients):
    """Test terminating an existing deployment successfully."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "deployment_crn": DEPLOYMENT_CRN,
            "env_crn": ENV_CRN,
            "state": "absent",
            "wait": False,
        }
    )

    df_client.get_deployment_by_crn.return_value = EXISTING_DEPLOYMENT
    df_client.terminate_deployment.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    assert result.value.deployment == {}
    df_client.terminate_deployment.assert_called_once()


def test_df_deployment_delete_idempotent(module_args, mock_clients):
    """Test that deleting a non-existent deployment is idempotent."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "deployment_crn": DEPLOYMENT_CRN,
            "env_crn": ENV_CRN,
            "state": "absent",
            "wait": False,
        }
    )

    df_client.get_deployment_by_crn.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is False
    df_client.terminate_deployment.assert_not_called()


def test_df_deployment_delete_by_name(module_args, mock_clients):
    """Test terminating a deployment by name."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "state": "absent",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = EXISTING_DEPLOYMENT
    df_client.terminate_deployment.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    df_client.terminate_deployment.assert_called_once()


# ---------------------------------------------------------------------------
# CHECK MODE tests
# ---------------------------------------------------------------------------


def test_df_deployment_check_mode_create(module_args, mock_clients):
    """Test check mode for creating a deployment does not call the API."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "cluster_size": "SMALL",
            "state": "present",
            "wait": False,
            "_ansible_check_mode": True,
        }
    )

    df_client.get_deployment_by_name.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    df_client.initiate_deployment.assert_not_called()
    df_client.create_deployment.assert_not_called()


def test_df_deployment_check_mode_delete(module_args, mock_clients):
    """Test check mode for deleting a deployment does not call the API."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "deployment_crn": DEPLOYMENT_CRN,
            "env_crn": ENV_CRN,
            "state": "absent",
            "wait": False,
            "_ansible_check_mode": True,
        }
    )

    df_client.get_deployment_by_crn.return_value = EXISTING_DEPLOYMENT

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    df_client.terminate_deployment.assert_not_called()


# ---------------------------------------------------------------------------
# FAILURE tests
# ---------------------------------------------------------------------------


def test_df_deployment_fail_service_not_found(module_args, mock_clients):
    """Test that module fails when DataFlow service is not found."""
    df_client, _, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    df_client.get_service_by_env_crn.return_value = None

    with pytest.raises(AnsibleFailJson) as result:
        df_deployment.main()

    assert result.value.failed is True
    assert "DataFlow service is not enabled" in result.value.msg


def test_df_deployment_fail_environment_not_found(module_args, mock_clients):
    """Test that module fails when environment is not found."""
    df_client, env_client, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "env_crn": ENV_CRN,
            "flow_version_crn": FLOW_VERSION_CRN,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    env_client.describe_environment.return_value = None

    with pytest.raises(AnsibleFailJson) as result:
        df_deployment.main()

    assert result.value.failed is True
    assert "Environment not found" in result.value.msg


def test_df_deployment_fail_df_name_not_found(module_args, mock_clients):
    """Test that module fails when df_name service lookup fails."""
    df_client, env_client, _ = mock_clients

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
            "df_name": "nonexistent-service",
            "flow_version_crn": FLOW_VERSION_CRN,
            "state": "present",
            "wait": False,
        }
    )

    df_client.get_deployment_by_name.return_value = None
    df_client.get_service_by_name.return_value = None

    with pytest.raises(AnsibleFailJson) as result:
        df_deployment.main()

    assert result.value.failed is True
    assert "DataFlow service not found" in result.value.msg
