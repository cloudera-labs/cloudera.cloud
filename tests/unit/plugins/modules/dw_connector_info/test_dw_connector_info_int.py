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

from ansible_collections.cloudera.cloud.plugins.modules import (
    dw_connector_info,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]


@pytest.fixture
def dw_connector_info_module_args(module_args, env_context) -> dict:
    """Fixture to pre-populate common dw_connector_info module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context.get("CDP_ACCESS_KEY_ID"),
                "private_key": env_context.get("CDP_PRIVATE_KEY"),
                "cluster_id": env_context.get("CDW_CLUSTER_ID"),
            },
        )
        return module_args(args)

    return wrapped_args


def test_list_all_connectors(dw_connector_info_module_args):
    """Test listing all connectors in a cluster."""
    dw_connector_info_module_args({})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    assert result.changed is False
    assert "connectors" in result
    assert isinstance(result["connectors"], list)


def test_get_connector_by_id(dw_connector_info_module_args):
    """Test getting connector by ID."""
    # Temporarily set up to list all and get first ID
    dw_connector_info_module_args({})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    connectors = result.connectors if hasattr(result, "connectors") else []

    if not connectors:
        pytest.skip("No connectors available for testing")

    connector_id = connectors[0]["id"]

    # Now test with specific connector_id
    dw_connector_info_module_args({"connector_id": connector_id})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    assert result.changed is False
    assert hasattr(result, "connectors")
    assert len(result.connectors) == 1
    assert result.connectors[0]["id"] == connector_id


def test_get_connector_by_name(dw_connector_info_module_args):
    """Test getting connector by name."""
    # Temporarily set up to list all and get first name
    dw_connector_info_module_args({})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    connectors = result.connectors if hasattr(result, "connectors") else []

    if not connectors:
        pytest.skip("No connectors available for testing")

    connector_name = connectors[0]["name"]

    # Now test with specific name
    dw_connector_info_module_args({"name": connector_name})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    assert result.changed is False
    assert hasattr(result, "connectors")
    assert len(result.connectors) == 1
    assert result.connectors[0]["name"] == connector_name


def test_get_nonexistent_connector(dw_connector_info_module_args):
    """Test getting a connector that doesn't exist."""
    dw_connector_info_module_args(
        {"connector_id": "nonexistent-connector-99999"},
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_connector_info.main()

    result = exc.value
    assert result.changed is False
    assert hasattr(result, "connectors")
    assert len(result.connectors) == 0
