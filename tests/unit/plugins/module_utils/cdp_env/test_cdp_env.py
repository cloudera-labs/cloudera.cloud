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
)


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
    """initialize_aws_compute_cluster with only environment_name sends minimal body."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    result = client.initialize_aws_compute_cluster(ENV_NAME)

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAWSComputeCluster",
        data={"environmentName": ENV_NAME},
    )
    assert result == {"operationId": OPERATION_ID}


def test_initialize_aws_compute_cluster_with_all_options(mocker):
    """initialize_aws_compute_cluster includes computeClusterConfiguration when options are set."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(
        environment_name=ENV_NAME,
        worker_node_subnets=["subnet-abc", "subnet-def"],
        kube_api_authorized_ip_ranges=["10.0.0.0/8", "192.168.0.0/16"],
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["environmentName"] == ENV_NAME
    assert call_data["computeClusterConfiguration"]["workerNodeSubnets"] == [
        "subnet-abc",
        "subnet-def",
    ]
    assert call_data["computeClusterConfiguration"]["kubeApiAuthorizedIpRanges"] == [
        "10.0.0.0/8",
        "192.168.0.0/16",
    ]


def test_initialize_aws_compute_cluster_private(mocker):
    """initialize_aws_compute_cluster sets privateCluster when requested."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(
        environment_name=ENV_NAME,
        private_cluster=True,
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["computeClusterConfiguration"]["privateCluster"] is True


def test_initialize_aws_compute_cluster_omits_none_options(mocker):
    """initialize_aws_compute_cluster omits computeClusterConfiguration when all options are None."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_aws_compute_cluster(ENV_NAME)

    call_data = api_client.post.call_args[1]["data"]
    assert "computeClusterConfiguration" not in call_data


# ============================================================================
# initialize_azure_compute_cluster tests
# ============================================================================


def test_initialize_azure_compute_cluster_minimal(mocker):
    """initialize_azure_compute_cluster with only environment_name sends minimal body."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    result = client.initialize_azure_compute_cluster(ENV_NAME)

    api_client.post.assert_called_once_with(
        "/api/v1/environments2/initializeAzureComputeCluster",
        data={"environmentName": ENV_NAME},
    )
    assert result == {"operationId": OPERATION_ID}


def test_initialize_azure_compute_cluster_with_outbound_type(mocker):
    """initialize_azure_compute_cluster includes outboundType in configuration."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(
        environment_name=ENV_NAME,
        outbound_type="udr",
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["computeClusterConfiguration"]["outboundType"] == "udr"


def test_initialize_azure_compute_cluster_with_all_options(mocker):
    """initialize_azure_compute_cluster includes all configuration fields when set."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(
        environment_name=ENV_NAME,
        private_cluster=True,
        worker_node_subnets=["subnet-abc"],
        outbound_type="udr",
    )

    call_data = api_client.post.call_args[1]["data"]
    config = call_data["computeClusterConfiguration"]
    assert config["privateCluster"] is True
    assert config["workerNodeSubnets"] == ["subnet-abc"]
    assert config["outboundType"] == "udr"


def test_initialize_azure_compute_cluster_omits_none_options(mocker):
    """initialize_azure_compute_cluster omits computeClusterConfiguration when all options are None."""
    client, api_client = make_client()

    api_client.post.return_value = {"operationId": OPERATION_ID}

    client.initialize_azure_compute_cluster(ENV_NAME)

    call_data = api_client.post.call_args[1]["data"]
    assert "computeClusterConfiguration" not in call_data
