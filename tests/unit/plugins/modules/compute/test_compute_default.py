# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
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

from ansible_collections.cloudera.cloud.plugins.modules import compute_default

# ============================================================================
# Test constants
# ============================================================================

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
OPERATION_ID = "op-uuid-1234"

# Sample environment summaries returned by get_environment_by_name
SAMPLE_ENV_AWS = {
    "environmentName": ENV_NAME,
    "crn": "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid",
    "cloudPlatform": "AWS",
    "status": "AVAILABLE",
    "region": "us-west-1",
    "credentialName": "my-credential",
}

SAMPLE_ENV_AZURE = {
    "environmentName": ENV_NAME,
    "crn": "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid",
    "cloudPlatform": "AZURE",
    "status": "AVAILABLE",
    "region": "westeurope",
    "credentialName": "my-credential",
}

# Sample cluster returned by get_clusters_by_env when a default cluster exists
SAMPLE_DEFAULT_CLUSTER_RUNNING = {
    "clusterCrn": CLUSTER_CRN,
    "clusterId": "cluster-uuid",
    "clusterName": "default-cluster",
    "status": "Running",
    "envName": ENV_NAME,
    "isDefault": True,
    "computePlatform": "EKS",
}

# ============================================================================
# Patch helpers
# ============================================================================


def _patch_config(mocker):
    """Patch load_cdp_config to prevent reading real credential files."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    return config


def _patch_compute_client(mocker):
    """Patch CdpComputeClient in the compute_default module namespace.

    Class-level state constants (ACTIVE_STATES, FAILED_STATES) are restored
    to their real values so that containment checks inside process() and
    _wait_for_default_cluster() behave correctly rather than testing against
    a MagicMock object.
    """
    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_default.CdpComputeClient",
        autospec=True,
    )
    mock_class.ACTIVE_STATES = ["Running"]
    mock_class.FAILED_STATES = ["Failed", "CreateFailed", "DeleteFailed"]
    return mock_class.return_value


def _patch_env_client(mocker):
    """Patch CdpEnvClient in the compute_default module namespace."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_default.CdpEnvClient",
        autospec=True,
    ).return_value


# ============================================================================
# AWS — initialize
# ============================================================================


def test_compute_default_aws_initialize(module_args, mocker):
    """AWS environment with no existing default cluster initializes one."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    env_client.initialize_aws_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    # First call: existence check → no cluster; second call: wait poll → running
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.value.cluster["status"] == "Running"
    assert result.value.operation_id is None  # not exposed when wait=True

    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=None,
        kube_api_authorized_ip_ranges=None,
        worker_node_subnets=None,
    )
    env_client.initialize_azure_compute_cluster.assert_not_called()


# ============================================================================
# AWS — idempotent
# ============================================================================


def test_compute_default_aws_idempotent(module_args, mocker):
    """AWS environment when default cluster already exists is idempotent."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    compute_client.get_clusters_by_env.return_value = [SAMPLE_DEFAULT_CLUSTER_RUNNING]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is False
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.value.cluster["status"] == "Running"

    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()


# ============================================================================
# AWS — with optional parameters
# ============================================================================


def test_compute_default_aws_with_options(module_args, mocker):
    """AWS environment passes worker_node_subnets and kube_api_authorized_ip_ranges."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "worker_node_subnets": ["subnet-abc", "subnet-def"],
            "kube_api_authorized_ip_ranges": ["10.0.0.0/8"],
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    env_client.initialize_aws_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True

    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=None,
        kube_api_authorized_ip_ranges=["10.0.0.0/8"],
        worker_node_subnets=["subnet-abc", "subnet-def"],
    )


def test_compute_default_aws_private_cluster(module_args, mocker):
    """AWS environment passes private_cluster=True to the init API."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "private_cluster": True,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    env_client.initialize_aws_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True

    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=True,
        kube_api_authorized_ip_ranges=None,
        worker_node_subnets=None,
    )


# ============================================================================
# Azure — initialize
# ============================================================================


def test_compute_default_azure_initialize(module_args, mocker):
    """Azure environment with no existing default cluster initializes one."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AZURE
    env_client.initialize_azure_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.value.cluster["status"] == "Running"

    env_client.initialize_azure_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=None,
        kube_api_authorized_ip_ranges=None,
        worker_node_subnets=None,
        outbound_type=None,
    )
    env_client.initialize_aws_compute_cluster.assert_not_called()


# ============================================================================
# Azure — idempotent
# ============================================================================


def test_compute_default_azure_idempotent(module_args, mocker):
    """Azure environment when default cluster already exists is idempotent."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AZURE
    compute_client.get_clusters_by_env.return_value = [SAMPLE_DEFAULT_CLUSTER_RUNNING]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is False
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN

    env_client.initialize_azure_compute_cluster.assert_not_called()
    env_client.initialize_aws_compute_cluster.assert_not_called()


# ============================================================================
# Azure — with outbound_type
# ============================================================================


def test_compute_default_azure_with_outbound_type(module_args, mocker):
    """Azure environment passes outbound_type to the Azure initialize method."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "outbound_type": "udr",
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AZURE
    env_client.initialize_azure_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True

    env_client.initialize_azure_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=None,
        kube_api_authorized_ip_ranges=None,
        worker_node_subnets=None,
        outbound_type="udr",
    )


# ============================================================================
# outbound_type silently ignored for AWS
# ============================================================================


def test_compute_default_outbound_type_ignored_for_aws(module_args, mocker):
    """outbound_type set for an AWS environment is silently ignored; AWS init called without it."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "outbound_type": "udr",  # Azure-only — silently ignored for AWS
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    env_client.initialize_aws_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }
    compute_client.get_clusters_by_env.side_effect = [
        [],
        [SAMPLE_DEFAULT_CLUSTER_RUNNING],
    ]

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True

    # AWS init was called — without outbound_type (it is not a parameter of that method)
    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        environment_name=ENV_NAME,
        private_cluster=None,
        kube_api_authorized_ip_ranges=None,
        worker_node_subnets=None,
    )
    # Azure init was NOT called
    env_client.initialize_azure_compute_cluster.assert_not_called()


# ============================================================================
# check_mode
# ============================================================================


def test_compute_default_check_mode(module_args, mocker):
    """check_mode does not call any initialize methods but still reports changed=True."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "_ansible_check_mode": True,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    compute_client.get_clusters_by_env.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True
    assert result.value.cluster == {}

    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()


# ============================================================================
# wait=False
# ============================================================================


def test_compute_default_no_wait(module_args, mocker):
    """wait=False returns operation_id immediately without polling."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "wait": False,
            "state": "present",
        },
    )

    _patch_config(mocker)
    compute_client = _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = SAMPLE_ENV_AWS
    compute_client.get_clusters_by_env.return_value = []
    env_client.initialize_aws_compute_cluster.return_value = {
        "operationId": OPERATION_ID,
    }

    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True
    assert result.value.operation_id == OPERATION_ID
    assert result.value.cluster == {}
    # Only the initial existence check — no wait-poll call
    compute_client.get_clusters_by_env.assert_called_once()


# ============================================================================
# Error handling — environment not found / unsupported platform
# ============================================================================


def test_compute_default_environment_not_found(module_args, mocker):
    """Module fails with a clear message when the environment does not exist."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": "nonexistent-env",
            "state": "present",
        },
    )

    _patch_config(mocker)
    _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = None

    with pytest.raises(AnsibleFailJson) as result:
        compute_default.main()

    assert "nonexistent-env" in str(result.value)


def test_compute_default_unsupported_platform(module_args, mocker):
    """Module fails with a clear message for unsupported cloud platforms (e.g. GCP)."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "state": "present",
        },
    )

    _patch_config(mocker)
    _patch_compute_client(mocker)
    env_client = _patch_env_client(mocker)

    env_client.get_environment_by_name.return_value = {
        "environmentName": ENV_NAME,
        "crn": "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid",
        "cloudPlatform": "GCP",
        "status": "AVAILABLE",
        "region": "us-central1",
        "credentialName": "my-credential",
    }

    with pytest.raises(AnsibleFailJson) as result:
        compute_default.main()

    assert "GCP" in str(result.value)
