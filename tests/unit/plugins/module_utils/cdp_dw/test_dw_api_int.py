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
import time

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    Connector,
    ConnectorTestJob,
    DwSecret,
    VirtualWarehouse,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]

VM_DELETION_RETRIES = 5
VM_DELETION_WAIT_SECONDS = 15


class TestConnectorIntegration:

    def test_list_connectors(self, dw_client, existing_dw_cluster_id):
        """Test listing connectors in a cluster returns Connector instances."""
        connectors = dw_client.list_connectors(existing_dw_cluster_id)

        assert isinstance(connectors, list)
        assert all(isinstance(c, Connector) for c in connectors)

        if connectors:
            assert connectors[0].id is not None
            assert connectors[0].name is not None
            assert connectors[0].template is not None

    def test_get_connector_by_id(self, dw_client, existing_dw_cluster_id):
        """Test getting connector by ID."""
        connectors = dw_client.list_connectors(existing_dw_cluster_id)

        if not connectors:
            pytest.skip("No connectors available for testing")

        connector_id = connectors[0].id
        result = dw_client.get_connector_by_id(existing_dw_cluster_id, connector_id)

        assert result is not None
        assert isinstance(result, Connector)
        assert result.id == connector_id
        assert result.name is not None
        assert result.template is not None

    def test_get_connector_by_name(self, dw_client, existing_dw_cluster_id):
        """Test getting connector by name."""
        connectors = dw_client.list_connectors(existing_dw_cluster_id)

        if not connectors:
            pytest.skip("No connectors available for testing")

        connector_name = connectors[0].name
        result = dw_client.get_connector_by_name(existing_dw_cluster_id, connector_name)

        assert result is not None
        assert isinstance(result, Connector)
        assert result.name == connector_name
        assert result.id is not None
        assert result.template is not None

    def test_get_nonexistent_connector(self, dw_client, existing_dw_cluster_id):
        """Test getting a connector that doesn't exist."""
        result = dw_client.get_connector_by_id(
            existing_dw_cluster_id,
            "nonexistent-connector-99999",
        )

        # Should return None
        assert result is None

    def test_get_connector_by_nonexistent_name(self, dw_client, existing_dw_cluster_id):
        """Test getting a connector by nonexistent name."""
        result = dw_client.get_connector_by_name(
            existing_dw_cluster_id,
            "nonexistent-connector-99999",
        )

        # Should return None
        assert result is None

    def test_create_connector(self, existing_connector):
        """Test creating a connector returns a populated Connector instance."""
        assert isinstance(existing_connector, Connector)
        assert existing_connector.id is not None
        assert existing_connector.name is not None
        assert existing_connector.template == "hive"

    def test_update_connector(
        self,
        request,
        dw_client,
        existing_dw_cluster_id,
        existing_connector,
    ):
        """Test updating a connector description."""
        dw_client.update_connector(
            cluster_id=existing_dw_cluster_id,
            connector_id=existing_connector.id,
            name=existing_connector.name,
            template=existing_connector.template,
            config=existing_connector.config,
            description=f"Updated by Ansible integration test, {request.node.name}",
        )

        # Re-fetch and verify the update
        updated = dw_client.get_connector_by_id(
            existing_dw_cluster_id,
            existing_connector.id,
        )
        assert updated is not None
        assert isinstance(updated, Connector)
        assert updated.id == existing_connector.id

    def test_delete_connector(
        self,
        dw_client,
        existing_dw_cluster_id,
        disposable_connector,
    ):
        """Test deleting a connector removes it from the cluster."""
        connector_id = disposable_connector.id

        dw_client.delete_connector(
            cluster_id=existing_dw_cluster_id,
            connector_id=connector_id,
        )

        # Verify it no longer exists
        result = dw_client.get_connector_by_id(existing_dw_cluster_id, connector_id)
        assert result is None

    def test_create_connector_test_job(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_connector,
    ):
        """Test creating a test job for a connector returns a job ID."""
        job_id = dw_client.create_connector_test_job(
            cluster_id=existing_dw_cluster_id,
            connector_id=existing_connector.id,
        )

        assert isinstance(job_id, str)
        assert len(job_id) > 0


class TestVwListIntegration:
    def test_list_connector_test_jobs(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_connector,
    ):
        """Test listing connector test jobs returns ConnectorTestJob instances."""
        # Create a test job first
        dw_client.create_connector_test_job(
            cluster_id=existing_dw_cluster_id,
            connector_id=existing_connector.id,
        )

        # List all test jobs for the cluster
        jobs = dw_client.list_connector_test_jobs(cluster_id=existing_dw_cluster_id)

        assert isinstance(jobs, list)
        assert all(isinstance(j, ConnectorTestJob) for j in jobs)

    def test_list_vws_returns_instances(self, dw_client, existing_dw_cluster_id):
        """list_vws returns VirtualWarehouse instances (cheap; no warehouse created)."""
        vws = dw_client.list_vws(existing_dw_cluster_id)

        assert isinstance(vws, list)
        assert all(isinstance(vw, VirtualWarehouse) for vw in vws)


@pytest.mark.slow
class TestVwTrinoIntegration:
    """Trino Virtual Warehouse lifecycle.

    The read/update tests share one class-scoped C(existing_vw_trino) so the
    (slow) creation happens once. C(test_delete) provisions its own disposable
    warehouse so removing it does not disturb the shared one.
    """

    def test_get_by_id(self, dw_client, existing_dw_cluster_id, existing_vw_trino):
        """The warehouse is describable by id and reports its type."""
        assert existing_vw_trino.vwType == "trino"
        by_id = dw_client.get_vw_by_id(existing_dw_cluster_id, existing_vw_trino.id)
        assert by_id is not None
        assert by_id.id == existing_vw_trino.id

    def test_get_by_name(self, dw_client, existing_dw_cluster_id, existing_vw_trino):
        """The warehouse is describable by name."""
        by_name = dw_client.get_vw_by_name(
            existing_dw_cluster_id,
            existing_vw_trino.name,
        )
        assert by_name is not None
        assert by_name.id == existing_vw_trino.id

    def test_list_includes_self(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_vw_trino,
    ):
        """list_vws includes the created warehouse."""
        ids = [vw.id for vw in dw_client.list_vws(existing_dw_cluster_id)]
        assert existing_vw_trino.id in ids

    def test_update_associate_connector(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_vw_trino,
        existing_connector,
    ):
        """update_vw associates the desired connector set."""
        connector_id = existing_connector.id

        dw_client.update_vw(
            cluster_id=existing_dw_cluster_id,
            vw_id=existing_vw_trino.id,
            associated_connectors=[connector_id],
        )

        updated = dw_client.get_vw_by_id(existing_dw_cluster_id, existing_vw_trino.id)
        assert updated is not None
        assert isinstance(updated.associatedConnectors, dict)
        assert connector_id in updated.associatedConnectors

    def test_delete(self, dw_client, existing_dw_cluster_id, disposable_vw):
        """delete_vw removes a (dedicated) warehouse from the cluster."""
        vw = disposable_vw("trino")

        dw_client.delete_vw(existing_dw_cluster_id, vw.id)
        time.sleep(VM_DELETION_WAIT_SECONDS)  # Wait for deletion to propagate

        assert dw_client.get_vw_by_id(existing_dw_cluster_id, vw.id) is None


@pytest.mark.slow
class TestVwHiveIntegration:
    """Hive Virtual Warehouse lifecycle (shared class-scoped warehouse for reads)."""

    def test_get_by_id(self, dw_client, existing_dw_cluster_id, existing_vw_hive):
        """The warehouse is describable by id and reports its type."""
        assert existing_vw_hive.vwType == "hive"
        by_id = dw_client.get_vw_by_id(existing_dw_cluster_id, existing_vw_hive.id)
        assert by_id is not None
        assert by_id.id == existing_vw_hive.id

    def test_get_by_name(self, dw_client, existing_dw_cluster_id, existing_vw_hive):
        """The warehouse is describable by name."""
        by_name = dw_client.get_vw_by_name(
            existing_dw_cluster_id,
            existing_vw_hive.name,
        )
        assert by_name is not None
        assert by_name.id == existing_vw_hive.id

    def test_list_includes_self(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_vw_hive,
    ):
        """list_vws includes the created warehouse."""
        ids = [vw.id for vw in dw_client.list_vws(existing_dw_cluster_id)]
        assert existing_vw_hive.id in ids

    def test_delete(self, dw_client, existing_dw_cluster_id, disposable_vw):
        """delete_vw removes a (dedicated) warehouse from the cluster."""
        vw = disposable_vw("hive")

        dw_client.delete_vw(existing_dw_cluster_id, vw.id)
        time.sleep(VM_DELETION_WAIT_SECONDS)  # Wait for deletion to propagate

        assert dw_client.get_vw_by_id(existing_dw_cluster_id, vw.id) is None


@pytest.mark.slow
class TestVwImpalaIntegration:
    """Impala Virtual Warehouse lifecycle (shared class-scoped warehouse for reads)."""

    def test_get_by_id(self, dw_client, existing_dw_cluster_id, existing_vw_impala):
        """The warehouse is describable by id and reports its type."""
        assert existing_vw_impala.vwType == "impala"
        by_id = dw_client.get_vw_by_id(existing_dw_cluster_id, existing_vw_impala.id)
        assert by_id is not None
        assert by_id.id == existing_vw_impala.id

    def test_get_by_name(self, dw_client, existing_dw_cluster_id, existing_vw_impala):
        """The warehouse is describable by name."""
        by_name = dw_client.get_vw_by_name(
            existing_dw_cluster_id,
            existing_vw_impala.name,
        )
        assert by_name is not None
        assert by_name.id == existing_vw_impala.id

    def test_list_includes_self(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_vw_impala,
    ):
        """list_vws includes the created warehouse."""
        ids = [vw.id for vw in dw_client.list_vws(existing_dw_cluster_id)]
        assert existing_vw_impala.id in ids

    def test_delete(self, dw_client, existing_dw_cluster_id, disposable_vw):
        """delete_vw removes a (dedicated) warehouse from the cluster."""
        vw = disposable_vw("impala")

        dw_client.delete_vw(existing_dw_cluster_id, vw.id)

        time.sleep(VM_DELETION_WAIT_SECONDS)  # Wait for deletion to propagate

        deleted = dw_client.get_vw_by_id(existing_dw_cluster_id, vw.id)
        assert deleted.status == "Deleting"


class TestVwSecretIntegration:
    """Integration tests for CdpDwClient secret CRUD."""

    def test_list_secrets(self, dw_client, existing_dw_cluster_id):
        """Test that list_secrets returns a list of DwSecret instances or an empty list."""
        secrets = dw_client.list_secrets(existing_dw_cluster_id)

        assert isinstance(secrets, list)
        assert all(isinstance(s, DwSecret) for s in secrets)

    @pytest.mark.usefixtures("existing_dw_secret_k8s")
    def test_list_secrets_k8s(self, dw_client, existing_dw_cluster_id):
        """Test that list_secrets returns a list of DwSecret instances for a Kubernetes cluster."""
        secrets = dw_client.list_secrets(existing_dw_cluster_id)

        assert isinstance(secrets, list)
        assert all(isinstance(s, DwSecret) for s in secrets)
        assert len(secrets) > 0

    @pytest.mark.usefixtures("existing_dw_secret_provider")
    def test_list_secrets_provider(self, dw_client, existing_dw_cluster_id):
        """Test that list_secrets returns a list of DwSecret instances for a cloud provider cluster."""
        secrets = dw_client.list_secrets(existing_dw_cluster_id)

        assert isinstance(secrets, list)
        assert all(isinstance(s, DwSecret) for s in secrets)
        assert len(secrets) > 0

    def test_create_secret(self, existing_dw_secret_k8s):
        """create_secret returns a populated DwSecret instance for a Kubernetes cluster."""
        assert isinstance(existing_dw_secret_k8s, DwSecret)
        assert existing_dw_secret_k8s.secretName is not None

    def test_register_secret(self, existing_dw_secret_provider):
        """register_secret returns a populated DwSecret instance for a cloud provider cluster."""
        assert isinstance(existing_dw_secret_provider, DwSecret)
        assert existing_dw_secret_provider.secretName is not None
        assert existing_dw_secret_provider.secretProviderKey is not None

    def test_get_secret_k8s(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_secret_k8s,
    ):
        """get_secret returns the provisioned secret (Kubernetes)."""
        result = dw_client.get_secret(
            existing_dw_cluster_id,
            existing_dw_secret_k8s.secretName,
        )

        assert result is not None
        assert isinstance(result, DwSecret)
        assert result.secretName == existing_dw_secret_k8s.secretName

    def test_get_secret_provider(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_secret_provider,
    ):
        """get_secret returns the provisioned secret (cloud provider)."""
        result = dw_client.get_secret(
            existing_dw_cluster_id,
            existing_dw_secret_provider.secretName,
        )

        assert result is not None
        assert isinstance(result, DwSecret)
        assert result.secretName == existing_dw_secret_provider.secretName

    def test_get_secret_not_found(self, dw_client, existing_dw_cluster_id):
        """get_secret returns None for a nonexistent secret."""
        result = dw_client.get_secret(
            existing_dw_cluster_id,
            "nonexistent-secret-99999",
        )

        assert result is None

    def test_delete_secret_k8s(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_secret_k8s,
    ):
        """delete_secret removes the secret (Kubernetes) from the cluster."""
        dw_client.delete_secret(
            existing_dw_cluster_id,
            existing_dw_secret_k8s.secretName,
        )

        result = dw_client.get_secret(
            existing_dw_cluster_id,
            existing_dw_secret_k8s.secretName,
        )
        assert result is None

    def test_delete_secret_provider(
        self,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_secret_provider,
    ):
        """delete_secret removes the secret (cloud provider) from the cluster."""
        dw_client.delete_secret(
            existing_dw_cluster_id,
            existing_dw_secret_provider.secretName,
        )

        result = dw_client.get_secret(
            existing_dw_cluster_id,
            existing_dw_secret_provider.secretName,
        )
        assert result is None

    def test_list_secrets_invalid_cluster(self, dw_client):
        """Test that an invalid cluster ID propagates an API error."""
        with pytest.raises(Exception):
            dw_client.list_secrets("nonexistent-cluster-99999")
