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

"""Integration tests for CdpComputeClient.

These tests hit the live CDP API and are gated on environment variables.
Read-only tests use the session-scoped ``existing_compute_cluster`` fixture
(never torn down). The create/delete test is slow (~35 min create + ~15 min
delete) and bills real cloud resources; it is marked ``slow``.

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_DELETED_STATUSES,
    ComputeCluster,
    ComputeClusterSummary,
    CreateClusterResponse,
    DeleteClusterResponse,
)
from ansible_collections.cloudera.cloud.tests.unit import required_or_skip


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


class TestComputeReadIntegration:
    """Read-only integration tests."""

    def test_get_clusters_by_env(self, compute_client, existing_compute_cluster):
        """The environment listing returns summaries including the existing cluster."""
        clusters = compute_client.get_clusters_by_env(existing_compute_cluster.envName)

        assert all(isinstance(c, ComputeClusterSummary) for c in clusters)
        assert any(
            c.clusterCrn == existing_compute_cluster.clusterCrn for c in clusters
        )

    def test_get_all_clusters(self, compute_client, existing_compute_cluster):
        clusters = compute_client.get_all_clusters()

        assert any(
            c.clusterCrn == existing_compute_cluster.clusterCrn for c in clusters
        )

    def test_deleted_clusters_hidden_unless_requested(
        self,
        compute_client,
        existing_compute_cluster,
    ):
        """Verified live: DELETED records are only listed with includeDeleted."""
        env = existing_compute_cluster.envName

        default = compute_client.get_clusters_by_env(env)
        with_deleted = compute_client.get_clusters_by_env(env, include_deleted=True)

        assert all(c.status not in COMPUTE_CLUSTER_DELETED_STATUSES for c in default)
        assert len(with_deleted) >= len(default)

    def test_describe_cluster(self, compute_client, existing_compute_cluster):
        cluster = compute_client.describe_cluster(existing_compute_cluster.clusterCrn)

        assert isinstance(cluster, ComputeCluster)
        assert cluster.clusterCrn == existing_compute_cluster.clusterCrn
        assert cluster.clusterName == existing_compute_cluster.clusterName
        assert cluster.status == existing_compute_cluster.status
        assert cluster.envCrn is not None

    def test_describe_nonexistent_cluster(
        self,
        compute_client,
        existing_compute_cluster,
    ):
        """describe_cluster returns None for a well-formed CRN that does not exist."""
        prefix = existing_compute_cluster.clusterCrn.rsplit(":", 1)[0]

        assert compute_client.describe_cluster(f"{prefix}:nonexistent-12345") is None

    def test_get_cluster_by_name_and_env_skips_default_and_embedded(
        self,
        compute_client,
        existing_compute_cluster,
    ):
        """Name lookup only ever returns user-managed externalized clusters."""
        found = compute_client.get_cluster_by_name_and_env(
            existing_compute_cluster.clusterName,
            existing_compute_cluster.envName,
        )

        if existing_compute_cluster.isDefault or (
            existing_compute_cluster.clusterShape != "Externalized"
        ):
            assert found is None
        else:
            assert found is not None
            assert found.clusterCrn == existing_compute_cluster.clusterCrn

    def test_get_cluster_by_name_and_env_not_found(
        self,
        compute_client,
        existing_compute_cluster,
    ):
        assert (
            compute_client.get_cluster_by_name_and_env(
                "nonexistent-12345",
                existing_compute_cluster.envName,
            )
            is None
        )


@pytest.mark.slow
class TestComputeCreateDeleteIntegration:
    """Create -> round trip -> delete. Slow (~50 min) and bills cloud resources."""

    def test_create_and_delete_cluster(self, compute_client, cleanup_compute_cluster):
        env_name = required_or_skip("CDP_ENVIRONMENT_NAME")
        name = f"ansible-inttest-{time.strftime('%m%d%H%M')}"
        tags = {"purpose": "ansible-inttest", "Mixed_Case": "Value"}

        created = compute_client.create_cluster(
            name=name,
            environment=env_name,  # a name is accepted by the API, as is a CRN
            description="ansible integration test",
            tags=tags,
        )
        assert isinstance(created, CreateClusterResponse)
        crn = created.clusterCrn
        cleanup_compute_cluster(crn)
        assert created.clusterStatus.status == "CREATING"

        cluster = compute_client.wait_for_cluster_state(
            crn,
            COMPUTE_CLUSTER_ACTIVE_STATUSES,
            timeout=3600,
        )
        assert cluster.status == "RUNNING"
        # Verified live: description is returned as sent and tags come back as labels
        assert cluster.description == "ansible integration test"
        assert cluster.labels == tags

        deleted = compute_client.delete_cluster(crn)
        assert isinstance(deleted, DeleteClusterResponse)
        assert deleted.clusterStatus.status == "DELETING"

        final = compute_client.wait_for_cluster_state(
            crn,
            COMPUTE_CLUSTER_DELETED_STATUSES,
            timeout=3600,
        )
        # Describe keeps returning the record with status DELETED (no 404)
        assert final.status == "DELETED"
        assert compute_client.get_cluster_by_name_and_env(name, env_name) is None
