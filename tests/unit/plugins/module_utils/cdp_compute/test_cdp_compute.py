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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_DELETED_STATUSES,
    COMPUTE_CLUSTER_FAILED_STATUSES,
    CdpComputeClient,
    CommonNetwork,
    ComputeCluster,
    ComputeClusterSummary,
    CreateClusterResponse,
    DeleteClusterResponse,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    to_dict,
)


CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
ENV_NAME = "test-environment"


def make_client():
    """Create a CdpComputeClient with a mocked api_client."""
    api_client = MagicMock()
    return CdpComputeClient(api_client), api_client


def summary(name="cluster-1", crn=CLUSTER_CRN, **overrides):
    """A list-item payload as returned by listClusters."""
    item = {
        "clusterCrn": crn,
        "clusterName": name,
        "status": "RUNNING",
        "clusterShape": "Externalized",
        "isDefault": False,
        "envCrn": ENV_CRN,
        "envName": ENV_NAME,
        "clusterStateVersion": 0,
    }
    item.update(overrides)
    return item


# ============================================================================
# Status constants and models
# ============================================================================


def test_status_constants_are_verified_upper_case_sets():
    assert COMPUTE_CLUSTER_ACTIVE_STATUSES == {"RUNNING"}
    assert COMPUTE_CLUSTER_DELETED_STATUSES == {"DELETED"}
    assert isinstance(COMPUTE_CLUSTER_FAILED_STATUSES, set)


def test_compute_cluster_from_api_ignores_unknown_keys():
    client, api_client = make_client()
    api_client.post.return_value = {**summary(), "someFutureField": {"a": 1}}

    result = client.describe_cluster(CLUSTER_CRN)

    assert isinstance(result, ComputeCluster)
    assert result.clusterName == "cluster-1"
    assert result.status == "RUNNING"
    assert result.clusterStateVersion == 0
    assert result.isDefault is False


def test_compute_cluster_unset_fields_are_nullable():
    client, api_client = make_client()
    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN, "message": None}

    result = client.describe_cluster(CLUSTER_CRN)

    assert result.status is NULLABLE
    assert result.message is None  # explicit null from the API
    assert to_dict(result) == {"clusterCrn": CLUSTER_CRN, "message": None}


# ============================================================================
# list_clusters (raw, paginated) tests
# ============================================================================


def test_list_clusters_all(mocker):
    """list_clusters returns the raw paginated response when called with no filters."""
    client, api_client = make_client()

    expected = {
        "clusters": [summary()],
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


def test_list_clusters_with_all_filters():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": []}

    client.list_clusters(
        env_name_or_crn=ENV_NAME,
        cluster_shape="Externalized",
        default=False,
        include_deleted=True,
        status="RUNNING",
        workloads="ml",
    )

    data = api_client.post.call_args[1]["data"]
    assert data == {
        "envNameOrCrn": ENV_NAME,
        "clusterShape": "Externalized",
        "default": False,
        "includeDeleted": True,
        "status": "RUNNING",
        "workloads": "ml",
        "pageSize": 100,
    }


def test_list_clusters_follows_next_token():
    """Multiple pages are merged by the paginated decorator (nextToken/startingToken)."""
    client, api_client = make_client()
    api_client.post.side_effect = [
        {"clusters": [summary("a", "crn-a")], "nextToken": "tok-2"},
        {"clusters": [summary("b", "crn-b")]},
    ]

    result = client.list_clusters()

    assert [c["clusterName"] for c in result["clusters"]] == ["a", "b"]
    assert api_client.post.call_args_list[1][1]["data"]["startingToken"] == "tok-2"


# ============================================================================
# describe_cluster / get_cluster_by_crn tests
# ============================================================================


def test_describe_cluster_found():
    client, api_client = make_client()
    api_client.post.return_value = summary()

    result = client.describe_cluster(CLUSTER_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/describeCluster",
        data={"clusterCrn": CLUSTER_CRN},
        squelch={404: {}},
    )
    assert isinstance(result, ComputeCluster)
    assert result.clusterCrn == CLUSTER_CRN


def test_describe_cluster_not_found_returns_none():
    client, api_client = make_client()
    api_client.post.return_value = {}

    assert client.describe_cluster(CLUSTER_CRN) is None


def test_get_cluster_by_crn_found():
    client, api_client = make_client()
    api_client.post.return_value = summary()

    result = client.get_cluster_by_crn(CLUSTER_CRN)

    assert isinstance(result, ComputeCluster)
    assert result.status == "RUNNING"


def test_get_cluster_by_crn_not_found():
    client, api_client = make_client()
    api_client.post.return_value = {}

    assert client.get_cluster_by_crn(CLUSTER_CRN) is None


def test_get_cluster_by_crn_returns_deleted_record():
    """The API returns the full record with status DELETED rather than a 404."""
    client, api_client = make_client()
    api_client.post.return_value = summary(status="DELETED")

    result = client.get_cluster_by_crn(CLUSTER_CRN)

    assert result.status == "DELETED"


# ============================================================================
# get_clusters_by_env / get_all_clusters tests
# ============================================================================


def test_get_clusters_by_env_returns_typed_list():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": [summary(), summary("c2", "crn-2")]}

    result = client.get_clusters_by_env(ENV_NAME)

    assert api_client.post.call_args[1]["data"]["envNameOrCrn"] == ENV_NAME
    assert all(isinstance(c, ComputeClusterSummary) for c in result)
    assert [c.clusterName for c in result] == ["cluster-1", "c2"]


def test_get_clusters_by_env_empty():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": []}

    assert client.get_clusters_by_env(ENV_NAME) == []


def test_get_all_clusters_passes_filters():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": [summary()]}

    result = client.get_all_clusters(include_deleted=True)

    assert api_client.post.call_args[1]["data"]["includeDeleted"] is True
    assert isinstance(result[0], ComputeClusterSummary)


# ============================================================================
# get_cluster_by_name_and_env tests
# ============================================================================


def test_get_cluster_by_name_and_env_found():
    client, api_client = make_client()
    api_client.post.return_value = {
        "clusters": [summary("other", "other-crn"), summary("my-cluster")],
    }

    result = client.get_cluster_by_name_and_env("my-cluster", ENV_CRN)

    assert isinstance(result, ComputeClusterSummary)
    assert result.clusterCrn == CLUSTER_CRN
    data = api_client.post.call_args[1]["data"]
    assert data["envNameOrCrn"] == ENV_CRN
    assert data["clusterShape"] == "Externalized"


def test_get_cluster_by_name_and_env_not_found():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": [summary("other", "other-crn")]}

    assert client.get_cluster_by_name_and_env("missing", ENV_CRN) is None


def test_get_cluster_by_name_and_env_empty_env():
    client, api_client = make_client()
    api_client.post.return_value = {"clusters": []}

    assert client.get_cluster_by_name_and_env("my-cluster", ENV_CRN) is None


def test_get_cluster_by_name_and_env_ignores_default_cluster():
    client, api_client = make_client()
    api_client.post.return_value = {
        "clusters": [summary("my-cluster", isDefault=True)],
    }

    assert client.get_cluster_by_name_and_env("my-cluster", ENV_CRN) is None


def test_get_cluster_by_name_and_env_ignores_embedded_cluster():
    client, api_client = make_client()
    api_client.post.return_value = {
        "clusters": [summary("my-cluster", clusterShape="Embedded")],
    }

    assert client.get_cluster_by_name_and_env("my-cluster", ENV_CRN) is None


def test_get_cluster_by_name_and_env_ignores_deleted_cluster():
    client, api_client = make_client()
    api_client.post.return_value = {
        "clusters": [summary("my-cluster", status="DELETED")],
    }

    assert client.get_cluster_by_name_and_env("my-cluster", ENV_CRN) is None


# ============================================================================
# create_cluster tests
# ============================================================================


def test_create_cluster():
    """create_cluster sends the correct POST body and returns a typed response."""
    client, api_client = make_client()
    api_client.post.return_value = {
        "clusterCrn": CLUSTER_CRN,
        "clusterId": "cluster-uuid",
        "clusterStatus": {"status": "CREATING"},
    }

    result = client.create_cluster(name="my-cluster", environment=ENV_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/createCluster",
        data={"name": "my-cluster", "environment": ENV_CRN},
    )
    assert isinstance(result, CreateClusterResponse)
    assert result.clusterCrn == CLUSTER_CRN
    assert result.clusterStatus.status == "CREATING"


def test_create_cluster_with_all_options():
    """create_cluster includes optional fields; CommonNetwork is serialised to camelCase."""
    client, api_client = make_client()
    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN}

    client.create_cluster(
        name="my-cluster",
        environment=ENV_CRN,
        description="A test cluster",
        network=CommonNetwork(
            subnets=["subnet-1"],
            podCidr="10.0.0.0/16",
            serviceCidr="10.1.0.0/16",
        ),
        tags={"env": "test"},
        skip_validation=True,
    )

    call_data = api_client.post.call_args[1]["data"]
    assert call_data["description"] == "A test cluster"
    assert call_data["network"] == {
        "subnets": ["subnet-1"],
        "podCidr": "10.0.0.0/16",
        "serviceCidr": "10.1.0.0/16",
    }
    assert call_data["tags"] == {"env": "test"}
    assert call_data["skipValidation"] is True


def test_create_cluster_omits_none_options():
    client, api_client = make_client()
    api_client.post.return_value = {"clusterCrn": CLUSTER_CRN}

    client.create_cluster(name="my-cluster", environment=ENV_CRN)

    call_data = api_client.post.call_args[1]["data"]
    for key in ("description", "network", "tags", "skipValidation"):
        assert key not in call_data


# ============================================================================
# delete_cluster tests
# ============================================================================


def test_delete_cluster():
    """delete_cluster sends only clusterCrn by default and returns a typed response."""
    client, api_client = make_client()
    api_client.post.return_value = {"clusterStatus": {"status": "DELETING"}}

    result = client.delete_cluster(CLUSTER_CRN)

    api_client.post.assert_called_once_with(
        "/api/v1/compute/deleteCluster",
        data={"clusterCrn": CLUSTER_CRN},
    )
    assert isinstance(result, DeleteClusterResponse)
    assert result.clusterStatus.status == "DELETING"


def test_delete_cluster_force():
    client, api_client = make_client()
    api_client.post.return_value = {}

    client.delete_cluster(CLUSTER_CRN, force=True)

    assert api_client.post.call_args[1]["data"] == {
        "clusterCrn": CLUSTER_CRN,
        "force": True,
    }


def test_delete_cluster_with_all_options():
    client, api_client = make_client()
    api_client.post.return_value = {}

    client.delete_cluster(
        CLUSTER_CRN,
        force=True,
        skip_validation=True,
        skip_workloads_validation=True,
    )

    assert api_client.post.call_args[1]["data"] == {
        "clusterCrn": CLUSTER_CRN,
        "force": True,
        "skipValidation": True,
        "skipWorkloadsValidation": True,
    }


# ============================================================================
# wait_for_cluster_state tests
# ============================================================================


def test_wait_for_cluster_state_already_in_target():
    client, api_client = make_client()
    api_client.post.return_value = summary()

    result = client.wait_for_cluster_state(CLUSTER_CRN, COMPUTE_CLUSTER_ACTIVE_STATUSES)

    assert isinstance(result, ComputeCluster)
    assert result.status == "RUNNING"
    api_client.post.assert_called_once()


def test_wait_for_cluster_state_polls_until_ready(mocker):
    client, api_client = make_client()
    mocker.patch("time.sleep")
    api_client.post.side_effect = [
        summary(status="CREATING"),
        summary(status="CREATING"),
        summary(status="RUNNING"),
    ]

    result = client.wait_for_cluster_state(CLUSTER_CRN, COMPUTE_CLUSTER_ACTIVE_STATUSES)

    assert result.status == "RUNNING"
    assert api_client.post.call_count == 3


def test_wait_for_cluster_state_keeps_polling_when_not_yet_visible(mocker):
    """Right after create the cluster may not be describable; keep polling for active."""
    client, api_client = make_client()
    sleep = mocker.patch("time.sleep")
    api_client.post.side_effect = [{}, {}, summary(status="RUNNING")]

    result = client.wait_for_cluster_state(CLUSTER_CRN, COMPUTE_CLUSTER_ACTIVE_STATUSES)

    assert result.status == "RUNNING"
    assert sleep.call_count == 2


def test_wait_for_cluster_state_deleted_record_is_target():
    """Describe returns the record with DELETED status (no 404)."""
    client, api_client = make_client()
    api_client.post.return_value = summary(status="DELETED")

    result = client.wait_for_cluster_state(
        CLUSTER_CRN,
        COMPUTE_CLUSTER_DELETED_STATUSES,
    )

    assert result.status == "DELETED"


def test_wait_for_cluster_state_returns_none_when_gone_and_waiting_for_delete(mocker):
    client, api_client = make_client()
    mocker.patch("time.sleep")
    api_client.post.side_effect = [summary(status="DELETING"), {}]

    result = client.wait_for_cluster_state(
        CLUSTER_CRN,
        COMPUTE_CLUSTER_DELETED_STATUSES,
    )

    assert result is None


def test_wait_for_cluster_state_raises_on_failed_state(mocker):
    client, api_client = make_client()
    mocker.patch("time.sleep")
    api_client.post.return_value = summary(
        status="CREATE_FAILED",
        message="Cluster creation failed",
    )

    with pytest.raises(CdpError, match="CREATE_FAILED.*Cluster creation failed"):
        client.wait_for_cluster_state(CLUSTER_CRN, COMPUTE_CLUSTER_ACTIVE_STATUSES)


def test_wait_for_cluster_state_failed_without_message(mocker):
    client, api_client = make_client()
    mocker.patch("time.sleep")
    api_client.post.return_value = summary(status="FAILED")

    with pytest.raises(CdpError, match="Unknown error"):
        client.wait_for_cluster_state(CLUSTER_CRN, COMPUTE_CLUSTER_ACTIVE_STATUSES)


def test_wait_for_cluster_state_timeout(mocker):
    client, api_client = make_client()
    mocker.patch("time.sleep")
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute.time.time",
        side_effect=[0, 0, 9999],
    )
    api_client.post.return_value = summary(status="CREATING")

    with pytest.raises(CdpError, match="Timeout"):
        client.wait_for_cluster_state(
            CLUSTER_CRN,
            COMPUTE_CLUSTER_ACTIVE_STATUSES,
            timeout=60,
        )
