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

import os
import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def dw_client(test_cdp_client) -> CdpDwClient:
    """Fixture to provide a Data Warehouse client for tests."""
    return CdpDwClient(api_client=test_cdp_client)


# TODO: Convert valid_cluster_id into a fixture factory that discovers available cluster IDs
# dynamically (e.g., by calling list_clusters) rather than requiring a static env var,
# so tests can run against any available cluster without manual configuration.
@pytest.fixture
def valid_cluster_id(dw_client):
    """
    Fixture to discover a valid DW cluster for testing.

    Skips test if no clusters are available.
    """
    # This would require listing clusters. For now, we'll skip if not provided.
    cluster_id = os.getenv("CDW_CLUSTER_ID")
    if not cluster_id:
        pytest.skip("CDW_CLUSTER_ID environment variable not set")
    return cluster_id


class TestCdpDwClientIntegration:
    """Integration tests for CdpDwClient using real CDP API."""

    def test_list_connectors(self, dw_client, valid_cluster_id):
        """Test listing connectors in a cluster returns Connector instances."""
        connectors = dw_client.list_connectors(valid_cluster_id)

        assert isinstance(connectors, list)
        assert all(isinstance(c, Connector) for c in connectors)

        if connectors:
            assert connectors[0].id is not None
            assert connectors[0].name is not None
            assert connectors[0].template is not None

    def test_get_connector_by_id(self, dw_client, valid_cluster_id):
        """Test getting connector by ID."""
        connectors = dw_client.list_connectors(valid_cluster_id)

        if not connectors:
            pytest.skip("No connectors available for testing")

        connector_id = connectors[0].id
        result = dw_client.get_connector_by_id(valid_cluster_id, connector_id)

        assert result is not None
        assert isinstance(result, Connector)
        assert result.id == connector_id
        assert result.name is not None
        assert result.template is not None

    def test_get_connector_by_name(self, dw_client, valid_cluster_id):
        """Test getting connector by name."""
        connectors = dw_client.list_connectors(valid_cluster_id)

        if not connectors:
            pytest.skip("No connectors available for testing")

        connector_name = connectors[0].name
        result = dw_client.get_connector_by_name(valid_cluster_id, connector_name)

        assert result is not None
        assert isinstance(result, Connector)
        assert result.name == connector_name
        assert result.id is not None
        assert result.template is not None

    def test_get_nonexistent_connector(self, dw_client, valid_cluster_id):
        """Test getting a connector that doesn't exist."""
        result = dw_client.get_connector_by_id(
            valid_cluster_id,
            "nonexistent-connector-99999",
        )

        # Should return None
        assert result is None

    def test_get_connector_by_nonexistent_name(self, dw_client, valid_cluster_id):
        """Test getting a connector by nonexistent name."""
        result = dw_client.get_connector_by_name(
            valid_cluster_id,
            "nonexistent-connector-99999",
        )

        # Should return None
        assert result is None
