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

# pylint: disable=redefined-outer-name,unused-argument

from ansible_collections.cloudera.cloud.plugins.modules import dw_cluster_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    ClusterSummary,
    ActorResponse,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

ENV_NAME = "my-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-uuid"

CLUSTER_ONE = ClusterSummary(
    id="cluster-abc123",
    name="test-cluster-one",
    crn="crn:cdp:dw:us-west-1:tenant:cluster:cluster-abc123",
    environmentCrn=ENV_CRN,
    status="Running",
    cloudPlatform="AWS",
    creationDate="2026-01-01T00:00:00Z",
    creator=ActorResponse(
        crn="crn:cdp:iam:us-west-1:tenant:user:test-user",
        email="test@example.com",
    ),
)

CLUSTER_TWO = ClusterSummary(
    id="cluster-def456",
    name="test-cluster-two",
    crn="crn:cdp:dw:us-west-1:tenant:cluster:cluster-def456",
    environmentCrn=ENV_CRN,
    status="Running",
    cloudPlatform="AZURE",
    creationDate="2026-02-01T00:00:00Z",
    creator=ActorResponse(
        crn="crn:cdp:iam:us-west-1:tenant:user:test-user-2",
    ),
)


@pytest.fixture
def dw_info_module_args(module_args):
    """Fixture to pre-populate common dw_cluster_info module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def dw_info_clients(mocker):
    """Fixture that patches load_cdp_config, CdpDwClient, and CdpEnvClient."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    dw_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_cluster_info.CdpDwClient",
        autospec=True,
    ).return_value

    env_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_cluster_info.CdpEnvClient",
        autospec=True,
    ).return_value

    return dw_client, env_client


class TestDescribeSingleCluster:
    """Tests for describing a single cluster by ID."""

    def test_describe_by_cluster_id(self, dw_info_module_args, dw_info_clients):
        """Describe a single cluster by its ID."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"cluster_id": "cluster-abc123"})
        dw_client.describe_cluster.return_value = CLUSTER_ONE

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert len(result.value.clusters) == 1
        assert result.value.clusters[0]["id"] == "cluster-abc123"
        assert result.value.clusters[0]["status"] == "Running"

        dw_client.describe_cluster.assert_called_once_with(
            cluster_id="cluster-abc123",
        )
        env_client.get_environment_crn.assert_not_called()

    def test_describe_by_id_alias(self, dw_info_module_args, dw_info_clients):
        """The 'id' alias maps to cluster_id."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"id": "cluster-abc123"})
        dw_client.describe_cluster.return_value = CLUSTER_ONE

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert len(result.value.clusters) == 1
        dw_client.describe_cluster.assert_called_once_with(
            cluster_id="cluster-abc123",
        )

    def test_cluster_not_found(self, dw_info_module_args, dw_info_clients):
        """Nonexistent cluster_id returns empty list, not fail_json."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"cluster_id": "nonexistent-12345"})
        dw_client.describe_cluster.return_value = None

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert result.value.clusters == []


class TestListClustersByEnvironment:
    """Tests for listing clusters by environment."""

    def test_list_by_environment_name(self, dw_info_module_args, dw_info_clients):
        """List clusters by environment name resolves the CRN first."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"environment": ENV_NAME})
        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = [CLUSTER_ONE, CLUSTER_TWO]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert len(result.value.clusters) == 2
        assert result.value.clusters[0]["id"] == "cluster-abc123"
        assert result.value.clusters[1]["id"] == "cluster-def456"

        env_client.get_environment_crn.assert_called_once_with(ENV_NAME)
        dw_client.list_clusters.assert_called_once_with(env_crn=ENV_CRN)

    def test_list_by_env_alias(self, dw_info_module_args, dw_info_clients):
        """The 'env' alias maps to environment."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"env": ENV_NAME})
        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = [CLUSTER_ONE]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert len(result.value.clusters) == 1
        env_client.get_environment_crn.assert_called_once_with(ENV_NAME)

    def test_list_by_environment_crn(self, dw_info_module_args, dw_info_clients):
        """When environment is already a CRN, skip CRN resolution."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"environment": ENV_CRN})
        dw_client.list_clusters.return_value = [CLUSTER_ONE]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert len(result.value.clusters) == 1
        env_client.get_environment_crn.assert_not_called()
        dw_client.list_clusters.assert_called_once_with(env_crn=ENV_CRN)

    def test_environment_not_found(self, dw_info_module_args, dw_info_clients):
        """When environment CRN resolution returns None, return empty list."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"environment": "nonexistent-env"})
        env_client.get_environment_crn.return_value = None

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert result.value.clusters == []
        dw_client.list_clusters.assert_not_called()

    def test_environment_with_no_clusters(self, dw_info_module_args, dw_info_clients):
        """Environment exists but has no clusters."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({"environment": ENV_NAME})
        env_client.get_environment_crn.return_value = ENV_CRN
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert result.value.clusters == []


class TestListAllClusters:
    """Tests for listing all clusters (no filter)."""

    def test_list_all_clusters(self, dw_info_module_args, dw_info_clients):
        """No parameters returns all clusters."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({})
        dw_client.list_clusters.return_value = [CLUSTER_ONE, CLUSTER_TWO]

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert len(result.value.clusters) == 2

        dw_client.list_clusters.assert_called_once_with()
        dw_client.describe_cluster.assert_not_called()
        env_client.get_environment_crn.assert_not_called()

    def test_list_all_empty(self, dw_info_module_args, dw_info_clients):
        """No clusters returns empty list."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args({})
        dw_client.list_clusters.return_value = []

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert result.value.clusters == []


class TestMutualExclusivity:
    """Tests that cluster_id and environment are mutually exclusive."""

    def test_cluster_id_and_environment_mutually_exclusive(
        self,
        dw_info_module_args,
        dw_info_clients,
    ):
        """Providing both cluster_id and environment fails."""
        dw_info_module_args(
            {
                "cluster_id": "cluster-abc123",
                "environment": ENV_NAME,
            },
        )

        with pytest.raises(AnsibleFailJson):
            dw_cluster_info.main()


class TestCheckMode:
    """Tests for check_mode support."""

    def test_check_mode_describe(self, dw_info_module_args, dw_info_clients):
        """Check mode still returns data (info modules are read-only)."""
        dw_client, env_client = dw_info_clients

        dw_info_module_args(
            {
                "cluster_id": "cluster-abc123",
                "_ansible_check_mode": True,
            },
        )
        dw_client.describe_cluster.return_value = CLUSTER_ONE

        with pytest.raises(AnsibleExitJson) as result:
            dw_cluster_info.main()

        assert result.value.changed is False
        assert len(result.value.clusters) == 1
