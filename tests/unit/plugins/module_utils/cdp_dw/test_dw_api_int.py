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
import re
import warnings

from typing import Generator

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
    ConnectorTestJob,
    DwSecret,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    CdpTestClient,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]

HIVE_CONNECTOR_CONFIG = {
    "connector.name": "hive",
    "fs.cache.directories": "/data/trino/caches/hive",
    "fs.cache.enabled": "true",
    "fs.cache.max-disk-usage-percentages": "30",
    "fs.cache.preferred-hosts-count": "2",
    "fs.cache.ttl": "7d",
    "hive.allow-drop-table": "true",
    "hive.collect-column-statistics-on-write": "false",
    "hive.metastore.uri": "thrift://metastore-service.{{ .Values.warehouseId }}.svc.cluster.local:9083",
    "hive.non-managed-table-writes-enabled": "true",
    "hive.security": "{{ .Values.authorizationMode }}",
    "hive.temporary-staging-directory-enabled": "{{ if and .Values.isPrivateCloud .Values.ozone .Values.ozone.enabled }}false{{ else }}true{{ end }}",
    "ranger.audit_config": "/etc/trino/ranger-hive-audit.xml",
    "ranger.hadoop_config": "/etc/trino/core-site.xml",
    "ranger.policy_mgr_ssl_config": "/etc/trino/ranger-policymgr-ssl.xml",
    "ranger.security_config": "/etc/trino/ranger-hive-security.xml",
    "ranger.service_name": "{{ .Values.rangerHiveSvcName }}",
}

ICEBERG_CONNECTOR_CONFIG = {
    "connector.name": "iceberg",
    "fs.cache.directories": "/data/trino/caches/",  # Needs the "catalog" name appended to this root path
    "fs.cache.enabled": "true",
    "fs.cache.max-disk-usage-percentages": "30",
    "fs.cache.preferred-hosts-count": "2",
    "fs.cache.ttl": "7d",
    "hive.metastore.uri": "thrift://metastore-service.{{ .Values.warehouseId }}.svc.cluster.local:9083",
    "iceberg.catalog.type": "hive_metastore",
    "iceberg.security": "{{ .Values.authorizationMode }}",
    "ranger.audit_config": "/etc/trino/ranger-hive-audit.xml",
    "ranger.hadoop_config": "/etc/trino/core-site.xml",
    "ranger.policy_mgr_ssl_config": "/etc/trino/ranger-policymgr-ssl.xml",
    "ranger.security_config": "/etc/trino/ranger-hive-security.xml",
    "ranger.service_name": "{{ .Values.rangerHiveSvcName }}",
}


@pytest.fixture
def dw_client(env_context) -> CdpDwClient:
    """Provide a live Data Warehouse client, skipping when credentials are absent."""
    api_client = CdpTestClient(
        endpoint=env_context["CDP_API_ENDPOINT"],
        access_key=env_context["CDP_ACCESS_KEY_ID"],
        private_key=env_context["CDP_PRIVATE_KEY"],
    )
    return CdpDwClient(api_client=api_client)


@pytest.fixture
def existing_cluster_id(env_context) -> str:
    """Provide a valid DW cluster id from the environment."""
    return env_context["CDW_CLUSTER_ID"]


@pytest.fixture
def managed_connector(
    request,
    dw_client,
    existing_cluster_id,
) -> Generator[Connector, None, None]:
    """Creates a test connector and ensures cleanup regardless of test outcome."""
    connector_name = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    connector_config = {
        **ICEBERG_CONNECTOR_CONFIG,
        "fs.cache.directories": "/data/trino/caches/" + connector_name,
    }

    connector = dw_client.create_connector(
        cluster_id=existing_cluster_id,
        name=connector_name,
        template="iceberg",
        config=connector_config,
        description="Ansible integration test connector",
    )
    assert isinstance(connector, Connector)
    assert connector.id is not None

    yield connector

    # Cleanup — squelch any error in case test already deleted it
    try:
        dw_client.delete_connector(existing_cluster_id, connector.id)
    except Exception as e:
        warnings.warn(
            f"Failed to delete test connector {connector.id} during cleanup: {e}",
        )


def test_list_connectors(dw_client, existing_cluster_id):
    """Test listing connectors in a cluster returns Connector instances."""
    connectors = dw_client.list_connectors(existing_cluster_id)

    assert isinstance(connectors, list)
    assert all(isinstance(c, Connector) for c in connectors)

    if connectors:
        assert connectors[0].id is not None
        assert connectors[0].name is not None
        assert connectors[0].template is not None


def test_get_connector_by_id(dw_client, existing_cluster_id):
    """Test getting connector by ID."""
    connectors = dw_client.list_connectors(existing_cluster_id)

    if not connectors:
        pytest.skip("No connectors available for testing")

    connector_id = connectors[0].id
    result = dw_client.get_connector_by_id(existing_cluster_id, connector_id)

    assert result is not None
    assert isinstance(result, Connector)
    assert result.id == connector_id
    assert result.name is not None
    assert result.template is not None


def test_get_connector_by_name(dw_client, existing_cluster_id):
    """Test getting connector by name."""
    connectors = dw_client.list_connectors(existing_cluster_id)

    if not connectors:
        pytest.skip("No connectors available for testing")

    connector_name = connectors[0].name
    result = dw_client.get_connector_by_name(existing_cluster_id, connector_name)

    assert result is not None
    assert isinstance(result, Connector)
    assert result.name == connector_name
    assert result.id is not None
    assert result.template is not None


def test_get_nonexistent_connector(dw_client, existing_cluster_id):
    """Test getting a connector that doesn't exist."""
    result = dw_client.get_connector_by_id(
        existing_cluster_id,
        "nonexistent-connector-99999",
    )

    # Should return None
    assert result is None


def test_get_connector_by_nonexistent_name(dw_client, existing_cluster_id):
    """Test getting a connector by nonexistent name."""
    result = dw_client.get_connector_by_name(
        existing_cluster_id,
        "nonexistent-connector-99999",
    )

    # Should return None
    assert result is None


def test_get_connector_by_nonexistent_name(dw_client, existing_cluster_id):
    """Test getting a connector by nonexistent name."""
    result = dw_client.get_connector_by_name(
        existing_cluster_id,
        "nonexistent-connector-99999",
    )

    # Should return None
    assert result is None


def test_create_connector(managed_connector):
    """Test creating a connector returns a populated Connector instance."""
    assert isinstance(managed_connector, Connector)
    assert managed_connector.id is not None
    assert managed_connector.name is not None
    assert managed_connector.template == "iceberg"


def test_update_connector(request, dw_client, existing_cluster_id, managed_connector):
    """Test updating a connector description."""
    dw_client.update_connector(
        cluster_id=existing_cluster_id,
        connector_id=managed_connector.id,
        name=managed_connector.name,
        template=managed_connector.template,
        config=managed_connector.config,
        description=f"Updated by Ansible integration test, {request.node.name}",
    )

    # Re-fetch and verify the update
    updated = dw_client.get_connector_by_id(existing_cluster_id, managed_connector.id)
    assert updated is not None
    assert isinstance(updated, Connector)
    assert updated.id == managed_connector.id


def test_delete_connector(dw_client, existing_cluster_id, managed_connector):
    """Test deleting a connector removes it from the cluster."""
    connector_id = managed_connector.id

    dw_client.delete_connector(
        cluster_id=existing_cluster_id,
        connector_id=connector_id,
    )

    # Verify it no longer exists
    result = dw_client.get_connector_by_id(existing_cluster_id, connector_id)
    assert result is None


def test_create_connector_test_job(
    dw_client,
    existing_cluster_id,
    managed_connector,
):
    """Test creating a test job for a connector returns a job ID."""
    job_id = dw_client.create_connector_test_job(
        cluster_id=existing_cluster_id,
        connector_id=managed_connector.id,
    )

    assert isinstance(job_id, str)
    assert len(job_id) > 0


def test_list_connector_test_jobs(
    dw_client,
    existing_cluster_id,
    managed_connector,
):
    """Test listing connector test jobs returns ConnectorTestJob instances."""
    # Create a test job first
    dw_client.create_connector_test_job(
        cluster_id=existing_cluster_id,
        connector_id=managed_connector.id,
    )

    # List all test jobs for the cluster
    jobs = dw_client.list_connector_test_jobs(cluster_id=existing_cluster_id)

    assert isinstance(jobs, list)
    assert all(isinstance(j, ConnectorTestJob) for j in jobs)


class TestCdpDwClientListSecretsIntegration:
    """Integration tests for CdpDwClient.list_secrets using real CDP API."""

    def test_list_secrets_returns_list(self, dw_client, existing_cluster_id):
        """Test that list_secrets returns a list of DwSecret instances."""
        secrets = dw_client.list_secrets(existing_cluster_id)

        assert isinstance(secrets, list)
        assert all(isinstance(s, DwSecret) for s in secrets)

    # TODO Add existing_secret fixture to test that at least one secret is returned, and that its fields are populated
    def test_list_secrets_fields_populated(self, dw_client, existing_cluster_id):
        """Test that returned secrets have expected fields populated."""
        secrets = dw_client.list_secrets(existing_cluster_id)

        if not secrets:
            pytest.skip("No secrets available in the cluster")

        first = secrets[0]
        assert first.secretName is not None

    def test_list_secrets_invalid_cluster(self, dw_client):
        """Test that an invalid cluster ID propagates an API error."""
        with pytest.raises(Exception):
            dw_client.list_secrets("nonexistent-cluster-99999")
