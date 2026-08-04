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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
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
