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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
)


CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
ENV_NAME = "test-environment"


def make_client():
    """Create a CdpComputeClient with a mocked api_client."""
    api_client = MagicMock()
    return CdpComputeClient(api_client), api_client


# ============================================================================
# list_clusters tests
# ============================================================================


def test_list_clusters_all(mocker):
    """list_clusters returns all clusters when called with no filters."""
    client, api_client = make_client()

    expected = {
        "clusters": [
            {"clusterCrn": CLUSTER_CRN, "clusterName": "cluster-1"},
        ],
        "totalClusters": 1,
        "totalPages": 1,
    }
    api_client.post.return_value = expected

    result = client.list_clusters()

    api_client.post.assert_called_once_with(
        "/api/v1/compute/listClusters",
        data={"pageSize": 100},
        squelch={404: {"clusters": []}},
    )
    assert result == expected


def test_list_clusters_with_env_filter(mocker):
    """list_clusters passes envNameOrCrn when env_name_or_crn is provided."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    client.list_clusters(env_name_or_crn=ENV_CRN)

    call_kwargs = api_client.post.call_args
    assert call_kwargs[1]["data"]["envNameOrCrn"] == ENV_CRN


def test_list_clusters_with_include_deleted(mocker):
    """list_clusters passes includeDeleted when include_deleted is set."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    client.list_clusters(include_deleted=True)

    call_kwargs = api_client.post.call_args
    assert call_kwargs[1]["data"]["includeDeleted"] is True


def test_list_clusters_with_status_filter(mocker):
    """list_clusters passes status when status filter is provided."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    client.list_clusters(status="RUNNING")

    call_kwargs = api_client.post.call_args
    assert call_kwargs[1]["data"]["status"] == "RUNNING"


def test_list_clusters_with_default_only(mocker):
    """list_clusters passes default=True when default_only is requested."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    client.list_clusters(default=True)

    call_kwargs = api_client.post.call_args
    assert call_kwargs[1]["data"]["default"] is True


# ============================================================================
# describe_cluster tests
# ============================================================================


def test_describe_cluster_found(mocker):
    """describe_cluster returns cluster details when found."""
    client, api_client = make_client()

    expected = {
        "clusterCrn": CLUSTER_CRN,
        "clusterName": "cluster-1",
        "status": "RUNNING",
        "envCrn": ENV_CRN,
    }
    api_client.post.return_value = expected

    result = client.describe_cluster(CLUSTER_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/describeCluster",
        data={"clusterCrn": CLUSTER_CRN},
        squelch={404: {}},
    )
    assert result == expected


def test_describe_cluster_not_found(mocker):
    """describe_cluster returns empty dict when cluster is not found (404 squelched)."""
    client, api_client = make_client()

    api_client.post.return_value = {}

    result = client.describe_cluster(CLUSTER_CRN)

    assert result == {}


# ============================================================================
# get_cluster_by_crn tests
# ============================================================================


def test_get_cluster_by_crn_found(mocker):
    """get_cluster_by_crn returns cluster details when the cluster exists."""
    client, api_client = make_client()

    cluster_detail = {
        "clusterCrn": CLUSTER_CRN,
        "clusterName": "cluster-1",
        "status": "RUNNING",
    }
    api_client.post.return_value = cluster_detail

    result = client.get_cluster_by_crn(CLUSTER_CRN)

    assert result == cluster_detail


def test_get_cluster_by_crn_not_found(mocker):
    """get_cluster_by_crn returns None when the cluster does not exist."""
    client, api_client = make_client()

    api_client.post.return_value = {}

    result = client.get_cluster_by_crn(CLUSTER_CRN)

    assert result is None


# ============================================================================
# get_clusters_by_env tests
# ============================================================================


def test_get_clusters_by_env_returns_list(mocker):
    """get_clusters_by_env returns the clusters list from the API response."""
    client, api_client = make_client()

    cluster_list = [
        {"clusterCrn": CLUSTER_CRN, "clusterName": "cluster-1"},
    ]
    api_client.post.return_value = {
        "clusters": cluster_list,
        "totalClusters": 1,
        "totalPages": 1,
    }

    result = client.get_clusters_by_env(ENV_CRN)

    assert result == cluster_list
    call_kwargs = api_client.post.call_args
    assert call_kwargs[1]["data"]["envNameOrCrn"] == ENV_CRN


def test_get_clusters_by_env_empty(mocker):
    """get_clusters_by_env returns empty list when no clusters exist."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    result = client.get_clusters_by_env(ENV_NAME)

    assert result == []


# ============================================================================
# get_all_clusters tests
# ============================================================================


def test_get_all_clusters_returns_list(mocker):
    """get_all_clusters returns the full clusters list from the API response."""
    client, api_client = make_client()

    cluster_list = [
        {"clusterCrn": CLUSTER_CRN, "clusterName": "cluster-1"},
        {
            "clusterCrn": "crn:cdp:compute:us-west-1:tenant:cluster:c2",
            "clusterName": "cluster-2",
        },
    ]
    api_client.post.return_value = {
        "clusters": cluster_list,
        "totalClusters": 2,
        "totalPages": 1,
    }

    result = client.get_all_clusters()

    assert result == cluster_list


def test_get_all_clusters_empty(mocker):
    """get_all_clusters returns an empty list when no clusters exist."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    result = client.get_all_clusters()

    assert result == []


# ============================================================================
# create_cluster tests
# ============================================================================


def test_create_cluster(mocker):
    """create_cluster sends the correct POST body and returns the response."""
    client, api_client = make_client()

    expected = {
        "clusterCrn": CLUSTER_CRN,
        "clusterId": "cluster-uuid",
        "clusterStatus": {"status": "Creating"},
    }
    api_client.post.return_value = expected

    result = client.create_cluster(name="my-cluster", environment=ENV_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/createCluster",
        data={"clusterName": "my-cluster", "environmentCrn": ENV_CRN},
    )
    assert result == expected
    assert result["clusterCrn"] == CLUSTER_CRN


def test_create_cluster_with_all_options(mocker):
    """create_cluster includes optional fields when provided."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN}
    network = {"podCidr": "10.0.0.0/16", "serviceCidr": "10.1.0.0/16"}
    tags = {"env": "test"}

    client.create_cluster(
        name="my-cluster",
        environment=ENV_CRN,
        description="A test cluster",
        network=network,
        tags=tags,
        skip_validation=True,
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["description"] == "A test cluster"
    assert call_data["network"] == network
    assert call_data["tags"] == tags
    assert call_data["skipValidation"] is True


def test_create_cluster_omits_none_options(mocker):
    """create_cluster does not include None optional fields in the request body."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN}

    client.create_cluster(name="my-cluster", environment=ENV_CRN)

    call_data = api_client.post.call_args[1]["data"]
    assert "description" not in call_data
    assert "network" not in call_data
    assert "tags" not in call_data
    assert "skipValidation" not in call_data


# ============================================================================
# delete_cluster tests
# ============================================================================


def test_delete_cluster(mocker):
    """delete_cluster sends the correct POST body with only clusterCrn."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusterStatus": {"status": "Deleting"}}

    client.delete_cluster(CLUSTER_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/deleteCluster",
        data={"clusterCrn": CLUSTER_CRN},
    )


def test_delete_cluster_force(mocker):
    """delete_cluster includes force=True when requested."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusterStatus": {"status": "Deleting"}}

    client.delete_cluster(CLUSTER_CRN, force=True)

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["force"] is True


def test_delete_cluster_with_all_options(mocker):
    """delete_cluster includes all optional flags when provided."""
    client, api_client = make_client()

    api_client.post.return_value = {}

    client.delete_cluster(
        CLUSTER_CRN,
        force=True,
        skip_validation=True,
        skip_workloads_validation=True,
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["clusterCrn"] == CLUSTER_CRN
    assert call_data["force"] is True
    assert call_data["skipValidation"] is True
    assert call_data["skipWorkloadsValidation"] is True


# ============================================================================
# get_cluster_by_name_and_env tests
# ============================================================================


def test_get_cluster_by_name_and_env_found(mocker):
    """get_cluster_by_name_and_env returns the matching cluster when found."""
    client, api_client = make_client()

    cluster = {
        "clusterCrn": CLUSTER_CRN,
        "clusterName": "my-cluster",
        "status": "Running",
    }
    api_client.post.return_value = {
        "clusters": [
            cluster,
            {"clusterCrn": "other-crn", "clusterName": "other-cluster"},
        ],
        "totalClusters": 2,
        "totalPages": 1,
    }

    result = client.get_cluster_by_name_and_env("my-cluster", ENV_CRN)

    assert result == cluster


def test_get_cluster_by_name_and_env_not_found(mocker):
    """get_cluster_by_name_and_env returns None when no cluster matches the name."""
    client, api_client = make_client()

    api_client.post.return_value = {
        "clusters": [{"clusterCrn": "other-crn", "clusterName": "other-cluster"}],
        "totalClusters": 1,
        "totalPages": 1,
    }

    result = client.get_cluster_by_name_and_env("missing-cluster", ENV_CRN)

    assert result is None


def test_get_cluster_by_name_and_env_empty_env(mocker):
    """get_cluster_by_name_and_env returns None when environment has no clusters."""
    client, api_client = make_client()

    api_client.post.return_value = {"clusters": [], "totalClusters": 0, "totalPages": 0}

    result = client.get_cluster_by_name_and_env("my-cluster", ENV_CRN)

    assert result is None


# ============================================================================
# wait_for_cluster_state tests
# ============================================================================


def test_wait_for_cluster_state_already_in_target(mocker):
    """wait_for_cluster_state returns immediately when cluster is already in the target state."""
    client, api_client = make_client()

    cluster = {
        "clusterCrn": CLUSTER_CRN,
        "clusterName": "my-cluster",
        "status": "Running",
    }
    api_client.post.return_value = cluster

    result = client.wait_for_cluster_state(CLUSTER_CRN, ["Running"])

    assert result == cluster
    api_client.post.assert_called_once()


def test_wait_for_cluster_state_polls_until_ready(mocker):
    """wait_for_cluster_state polls until the cluster reaches the target state."""
    client, api_client = make_client()

    mocker.patch("time.sleep")
    api_client.post.side_effect = [
        {"clusterCrn": CLUSTER_CRN, "status": "Creating"},
        {"clusterCrn": CLUSTER_CRN, "status": "Creating"},
        {"clusterCrn": CLUSTER_CRN, "status": "Running"},
    ]

    result = client.wait_for_cluster_state(CLUSTER_CRN, ["Running"])

    assert result["status"] == "Running"
    assert api_client.post.call_count == 3


def test_wait_for_cluster_state_returns_none_when_deleted(mocker):
    """wait_for_cluster_state returns None when cluster no longer exists (deleted)."""
    client, api_client = make_client()

    mocker.patch("time.sleep")
    api_client.post.side_effect = [
        {"clusterCrn": CLUSTER_CRN, "status": "Deleting"},
        {},  # 404 squelched → empty dict → get_cluster_by_crn returns None
    ]

    result = client.wait_for_cluster_state(CLUSTER_CRN, ["Deleted"])

    assert result is None


def test_wait_for_cluster_state_raises_on_failed_state(mocker):
    """wait_for_cluster_state raises CdpError when cluster enters a failed state."""
    from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
        CdpError,
    )

    client, api_client = make_client()

    mocker.patch("time.sleep")
    api_client.post.return_value = {
        "clusterCrn": CLUSTER_CRN,
        "status": "Failed",
        "statusMessage": "Cluster creation failed",
    }

    with pytest.raises(CdpError, match="Failed"):
        client.wait_for_cluster_state(CLUSTER_CRN, ["Running"])


def test_wait_for_cluster_state_timeout(mocker):
    """wait_for_cluster_state raises CdpError after the timeout is exceeded."""
    from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
        CdpError,
    )

    client, api_client = make_client()

    mocker.patch("time.sleep")
    # Mock time.time to simulate elapsed time exceeding the timeout
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute.time.time",
        side_effect=[0, 0, 9999],
    )
    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN, "status": "Creating"}

    with pytest.raises(CdpError, match="Timeout"):
        client.wait_for_cluster_state(CLUSTER_CRN, ["Running"], timeout=60)
