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

"""Integration tests for CdpDwClient cluster management methods.

These tests hit the live CDP API and are gated on environment variables.
Read-only tests use the session-scoped ``existing_dw_cluster`` fixture
(never torn down). Create/delete tests use ``cleanup_dw_cluster`` or
``disposable_dw_cluster`` and are slow (~20-40 min).

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDW_CLUSTER_ID or CDP_ENVIRONMENT_NAME (for read tests)
    CDP_ENVIRONMENT_NAME (for create/delete tests)
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    ActorResponse,
    AwsOptionsResponse,
    AzureOptionsResponse,
    ClusterSummary,
    DW_CLUSTER_RUNNING_STATUSES,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


class TestClusterIntegration:
    """Integration tests for CdpDwClient cluster describe/list operations."""

    def test_list_clusters(self, dw_client, existing_dw_cluster):
        """list_clusters returns ClusterSummary instances; the existing cluster is in the list."""
        clusters = dw_client.list_clusters()

        assert isinstance(clusters, list)
        assert all(isinstance(c, ClusterSummary) for c in clusters)
        assert any(c.id == existing_dw_cluster.id for c in clusters)

    def test_list_clusters_by_environment(self, dw_client, existing_dw_cluster):
        """list_clusters filtered by env_crn returns only clusters in that environment."""
        env_crn = existing_dw_cluster.environmentCrn
        clusters = dw_client.list_clusters(env_crn=env_crn)

        assert isinstance(clusters, list)
        assert len(clusters) >= 1
        assert all(c.environmentCrn == env_crn for c in clusters)
        assert any(c.id == existing_dw_cluster.id for c in clusters)

    def test_describe_cluster(self, dw_client, existing_dw_cluster):
        """describe_cluster returns a populated ClusterSummary with expected core fields."""
        cluster = dw_client.describe_cluster(existing_dw_cluster.id)

        assert cluster is not None
        assert isinstance(cluster, ClusterSummary)
        assert cluster.id == existing_dw_cluster.id
        assert cluster.name is not None
        assert cluster.status is not None
        assert cluster.environmentCrn is not None
        assert cluster.cloudPlatform is not None
        assert cluster.crn is not None

    def test_describe_nonexistent_cluster(self, dw_client):
        """describe_cluster returns None for a cluster that does not exist."""
        result = dw_client.describe_cluster("nonexistent-12345")

        assert result is None

    def test_cluster_details_completeness(self, dw_client, existing_dw_cluster):
        """describe returns nested structures matching the platform."""
        cluster = dw_client.describe_cluster(existing_dw_cluster.id)
        assert cluster is not None

        if cluster.creator is not None:
            assert isinstance(cluster.creator, ActorResponse)

        platform = cluster.cloudPlatform
        if platform == "AWS" and cluster.awsOptions is not None:
            assert isinstance(cluster.awsOptions, AwsOptionsResponse)
        elif platform == "AZURE" and cluster.azureOptions is not None:
            assert isinstance(cluster.azureOptions, AzureOptionsResponse)

    def test_get_cluster_by_name(self, dw_client, existing_dw_cluster):
        """get_cluster_by_name returns the matching ClusterSummary."""
        result = dw_client.get_cluster_by_name(
            existing_dw_cluster.name,
            env_crn=existing_dw_cluster.environmentCrn,
        )

        assert result is not None
        assert isinstance(result, ClusterSummary)
        assert result.id == existing_dw_cluster.id

    def test_get_cluster_by_name_not_found(self, dw_client):
        """get_cluster_by_name returns None for a name that doesn't exist."""
        result = dw_client.get_cluster_by_name("nonexistent-12345")

        assert result is None


@pytest.mark.slow
class TestClusterCreateDeleteIntegration:
    """Create/delete integration tests for CdpDwClient.

    These are slow (~20-40 min) and gated on CDP_ENVIRONMENT_NAME.
    """

    def test_create_and_delete_cluster(self, dw_client, disposable_dw_cluster):
        """A freshly created cluster is readable, then deletes to gone."""
        cluster_id = disposable_dw_cluster.id

        assert disposable_dw_cluster.status in DW_CLUSTER_RUNNING_STATUSES
        assert dw_client.describe_cluster(cluster_id) is not None

        dw_client.delete_cluster(cluster_id, force=True)
        result = dw_client.wait_for_cluster_state(
            cluster_id,
            target_statuses=set(),
        )
        assert result is None

    def test_delete_nonexistent_cluster(self, dw_client):
        """delete_cluster on a nonexistent ID is squelched (no error)."""
        dw_client.delete_cluster("nonexistent-12345")

    def test_delete_with_force(self, dw_client, disposable_dw_cluster):
        """Force-delete on a running cluster succeeds."""
        cluster_id = disposable_dw_cluster.id

        dw_client.delete_cluster(cluster_id, force=True)

        result = dw_client.wait_for_cluster_state(
            cluster_id,
            target_statuses=set(),
        )
        assert result is None
