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

from unittest.mock import MagicMock

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
    ComputeClusterConfig,
    InitializeComputeClusterResponse,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import NULLABLE


ENV_NAME = "test-environment"
OPERATION_ID = "op-uuid-1234"


def make_client():
    """Create a CdpEnvClient with a mocked api_client."""
    api_client = MagicMock()
    return CdpEnvClient(api_client), api_client


# ============================================================================
# initialize_aws_compute_cluster tests
# ============================================================================


def test_initialize_aws_compute_cluster_minimal(mocker):
    """initialize_aws_compute_cluster with an empty config sends only environmentName."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    result = client.initialize_aws_compute_cluster(ENV_NAME, ComputeClusterConfig())

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAWSComputeCluster",
        json_data={"environmentName": ENV_NAME},
    )
    assert isinstance(result, InitializeComputeClusterResponse)
    assert result.operationId == OPERATION_ID


def test_initialize_aws_compute_cluster_rejects_outbound_type(mocker):
    """initialize_aws_compute_cluster raises ValueError for Azure-only outboundType."""
    client, api_client = make_client()

    with pytest.raises(ValueError, match="outboundType"):
        client.initialize_aws_compute_cluster(
            ENV_NAME,
            ComputeClusterConfig(outboundType="udr"),
        )

    api_client.post.assert_not_called()


def test_initialize_aws_compute_cluster_with_all_options(mocker):
    """initialize_aws_compute_cluster nests every set option under computeClusterConfiguration."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(
            privateCluster=False,
            kubeApiAuthorizedIpRanges=["10.0.0.0/8", "192.168.0.0/16"],
            workerNodeSubnets=["subnet-abc", "subnet-def"],
        ),
    )

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAWSComputeCluster",
        json_data={
            "environmentName": ENV_NAME,
            "computeClusterConfiguration": {
                "privateCluster": False,
                "kubeApiAuthorizedIpRanges": ["10.0.0.0/8", "192.168.0.0/16"],
                "workerNodeSubnets": ["subnet-abc", "subnet-def"],
            },
        },
    )


def test_initialize_aws_compute_cluster_omits_unset_options(mocker):
    """Unset (NULLABLE) options are omitted; only the set ones are sent."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(privateCluster=True),
    )

    config = api_client.post.call_args[1]["json_data"]["computeClusterConfiguration"]
    assert config == {"privateCluster": True}


def test_initialize_aws_compute_cluster_explicit_none_is_sent(mocker):
    """An explicit None is sent as null, unlike an unset (NULLABLE) field."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(workerNodeSubnets=None),
    )

    config = api_client.post.call_args[1]["json_data"]["computeClusterConfiguration"]
    assert config == {"workerNodeSubnets": None}


def test_compute_cluster_config_defaults_are_unset():
    """A default ComputeClusterConfig leaves every field NULLABLE."""
    config = ComputeClusterConfig()

    assert config.privateCluster is NULLABLE
    assert config.kubeApiAuthorizedIpRanges is NULLABLE
    assert config.workerNodeSubnets is NULLABLE
    assert config.outboundType is NULLABLE


# ============================================================================
# initialize_azure_compute_cluster tests
# ============================================================================


def test_initialize_azure_compute_cluster_minimal(mocker):
    """initialize_azure_compute_cluster with an empty config sends only environmentName."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    result = client.initialize_azure_compute_cluster(ENV_NAME, ComputeClusterConfig())

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAzureComputeCluster",
        json_data={"environmentName": ENV_NAME},
    )
    assert isinstance(result, InitializeComputeClusterResponse)
    assert result.operationId == OPERATION_ID


def test_initialize_azure_compute_cluster_with_outbound_type(mocker):
    """initialize_azure_compute_cluster sends outboundType in the configuration."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(outboundType="udr"),
    )

    config = api_client.post.call_args[1]["json_data"]["computeClusterConfiguration"]
    assert config == {"outboundType": "udr"}


def test_initialize_azure_compute_cluster_without_outbound_type(mocker):
    """initialize_azure_compute_cluster omits outboundType when it is unset."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(privateCluster=True),
    )

    config = api_client.post.call_args[1]["json_data"]["computeClusterConfiguration"]
    assert "outboundType" not in config


def test_initialize_azure_compute_cluster_with_all_options(mocker):
    """initialize_azure_compute_cluster nests every set option under computeClusterConfiguration."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(
        ENV_NAME,
        ComputeClusterConfig(
            privateCluster=True,
            kubeApiAuthorizedIpRanges=["10.0.0.0/8"],
            workerNodeSubnets=["subnet-abc"],
            outboundType="udr",
        ),
    )

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAzureComputeCluster",
        json_data={
            "environmentName": ENV_NAME,
            "computeClusterConfiguration": {
                "privateCluster": True,
                "kubeApiAuthorizedIpRanges": ["10.0.0.0/8"],
                "workerNodeSubnets": ["subnet-abc"],
                "outboundType": "udr",
            },
        },
    )
