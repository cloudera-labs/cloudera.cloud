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

from ansible_collections.cloudera.cloud.plugins.modules import compute_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
ENV_NAME = "test-environment"

SAMPLE_CLUSTER_LIST_ITEM = {
    "clusterCrn": CLUSTER_CRN,
    "clusterId": "cluster-uuid",
    "clusterName": "my-cluster",
    "status": "RUNNING",
    "envCrn": ENV_CRN,
    "envName": ENV_NAME,
    "computePlatform": "EKS",
    "isDefault": False,
}

SAMPLE_CLUSTER_DESCRIBE = {
    "clusterCrn": CLUSTER_CRN,
    "clusterId": "cluster-uuid",
    "clusterName": "my-cluster",
    "status": "RUNNING",
    "envCrn": ENV_CRN,
    "envName": ENV_NAME,
    "computePlatform": "EKS",
    "kubernetesVersion": "1.28",
    "isClouderaManaged": True,
    "isDefault": False,
    "clusterSize": 3,
    "region": "us-west-1",
}


def _patch_config(mocker):
    """Helper to patch CDP config loading."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    return config


def _patch_client(mocker):
    """Helper to patch CdpComputeClient."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_info.CdpComputeClient",
        autospec=True,
    ).return_value


# ============================================================================
# List all clusters (no filters)
# ============================================================================


def test_compute_info_list_all(module_args, mocker):
    """compute_info with no parameters returns all clusters."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_all_clusters.return_value = [SAMPLE_CLUSTER_LIST_ITEM]

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.changed is False
    assert len(result.value.clusters) == 1
    assert result.value.clusters[0]["cluster_crn"] == CLUSTER_CRN

    client.get_all_clusters.assert_called_once()


def test_compute_info_list_empty(module_args, mocker):
    """compute_info returns an empty list when no clusters exist."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_all_clusters.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.changed is False
    assert result.value.clusters == []


# ============================================================================
# Filter by environment
# ============================================================================


def test_compute_info_by_env_crn(module_args, mocker):
    """compute_info with environment (CRN) calls get_clusters_by_env."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_CRN,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_clusters_by_env.return_value = [SAMPLE_CLUSTER_LIST_ITEM]

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.changed is False
    assert len(result.value.clusters) == 1
    assert result.value.clusters[0]["env_crn"] == ENV_CRN

    client.get_clusters_by_env.assert_called_once()
    call_args = client.get_clusters_by_env.call_args
    assert call_args[0][0] == ENV_CRN


def test_compute_info_by_env_name(module_args, mocker):
    """compute_info with environment name resolves correctly."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_clusters_by_env.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.clusters == []
    client.get_clusters_by_env.assert_called_once()
    call_args = client.get_clusters_by_env.call_args
    assert call_args[0][0] == ENV_NAME


# ============================================================================
# Describe by cluster CRN
# ============================================================================


def test_compute_info_by_crn(module_args, mocker):
    """compute_info with crn calls get_cluster_by_crn."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_DESCRIBE

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.changed is False
    assert len(result.value.clusters) == 1
    assert result.value.clusters[0]["cluster_crn"] == CLUSTER_CRN
    assert result.value.clusters[0]["kubernetes_version"] == "1.28"

    client.get_cluster_by_crn.assert_called_once_with(CLUSTER_CRN)


def test_compute_info_cluster_crn_alias(module_args, mocker):
    """compute_info accepts 'cluster_crn' as an alias for crn."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_crn": CLUSTER_CRN,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_DESCRIBE

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert len(result.value.clusters) == 1
    client.get_cluster_by_crn.assert_called_once_with(CLUSTER_CRN)


def test_compute_info_crn_not_found(module_args, mocker):
    """compute_info returns empty list when crn resolves to nothing."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.clusters == []


# ============================================================================
# Mutual exclusion
# ============================================================================


def test_compute_info_mutual_exclusion(module_args, mocker):
    """compute_info fails when both crn and environment are specified."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
            "environment": ENV_CRN,
        },
    )

    _patch_config(mocker)

    with pytest.raises(AnsibleFailJson):
        compute_info.main()


# ============================================================================
# Optional filters passed through to list
# ============================================================================


def test_compute_info_with_include_deleted(module_args, mocker):
    """compute_info passes include_deleted filter to the client."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "include_deleted": True,
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_all_clusters.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert result.value.clusters == []
    call_kwargs = client.get_all_clusters.call_args[1]
    assert call_kwargs.get("include_deleted") is True


def test_compute_info_with_status_filter(module_args, mocker):
    """compute_info passes status filter to the client."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "status": "RUNNING",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_all_clusters.return_value = [SAMPLE_CLUSTER_LIST_ITEM]

    with pytest.raises(AnsibleExitJson) as result:
        compute_info.main()

    assert len(result.value.clusters) == 1
    call_kwargs = client.get_all_clusters.call_args[1]
    assert call_kwargs.get("status") == "RUNNING"
