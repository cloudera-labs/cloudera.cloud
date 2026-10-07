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
import re
import warnings

import pytest

from ansible_collections.cloudera.cloud.plugins.modules import dw_virtual_warehouse
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    ICEBERG_CONNECTOR_CONFIG,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]


@pytest.fixture
def dw_vw_module_args(module_args, env_context):
    """Pre-populate common dw_virtual_warehouse module arguments from the env."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": env_context["CDP_API_ENDPOINT"],
            "access_key": env_context["CDP_ACCESS_KEY_ID"],
            "private_key": env_context["CDP_PRIVATE_KEY"],
            "cluster_id": env_context["CDW_CLUSTER_ID"],
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


def _vw_name(request):
    return "ansible-" + re.sub(r"[^a-z0-9]", "", request.node.name.lower())[:20]


@pytest.fixture
def cleanup_vw(dw_client, existing_dw_cluster_id):
    """Register VW ids for deletion at teardown.

    Call the returned function with a vw_id to schedule it for cleanup
    regardless of test outcome.
    """
    vw_ids = []

    def register(vw_id):
        vw_ids.append(vw_id)

    try:
        yield register
    finally:
        for vw_id in vw_ids:
            try:
                existing = dw_client.get_vw_by_id(existing_dw_cluster_id, vw_id)
                if existing:
                    dw_client.delete_vw(existing_dw_cluster_id, vw_id)
            except Exception as e:
                warnings.warn(f"cleanup_vw: failed to delete '{vw_id}': {e}")


@pytest.fixture
def connector_pair(request, dw_client, existing_dw_cluster_id):
    """Create two disposable Iceberg connectors for Trino association tests."""
    slug = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    names = [slug + "A", slug + "B"]
    connectors = []

    for name in names:
        connector_config = {
            **ICEBERG_CONNECTOR_CONFIG,
            "fs.cache.directories": "/data/trino/caches/" + name,
        }
        connector = dw_client.create_connector(
            cluster_id=existing_dw_cluster_id,
            name=name,
            template="iceberg",
            config=connector_config,
            description="Ansible integration test connector",
        )
        connectors.append(connector)

    yield connectors

    for connector in connectors:
        try:
            dw_client.delete_connector(existing_dw_cluster_id, connector.id)
        except Exception as e:
            warnings.warn(
                f"connector_pair: failed to delete connector '{connector.id}': {e}",
            )


# TODO Convert to proper cleanup fixture that deletes any warehouses created by the test, rather than relying on the test to clean up after itself.
@pytest.mark.slow
@pytest.mark.parametrize("vw_type", ["trino", "hive", "impala"])
def test_present_create_then_absent(
    request,
    vw_type,
    dw_vw_module_args,
    dw_client,
    existing_dw_cluster_id,
    existing_dw_dbc_id,
):
    """Create a warehouse of each type via the module, then delete it (gated by CDW_DBC_ID)."""
    name = _vw_name(request)
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))

    create_args = {
        "name": name,
        "type": vw_type,
        "catalog_id": existing_dw_dbc_id,
        "state": "present",
        "wait": True,
        "timeout": timeout,
    }
    # Connector association is a Trino-only capability.
    connector_id = os.getenv("CDW_CONNECTOR_ID") if vw_type == "trino" else None
    if connector_id:
        create_args["connectors"] = [connector_id]

    vw_id = None
    try:
        # Create
        dw_vw_module_args(create_args)
        with pytest.raises(AnsibleExitJson) as exc:
            dw_virtual_warehouse.main()

        assert exc.value.changed is True
        vw_id = exc.value.virtual_warehouse["id"]
        assert exc.value.virtual_warehouse["vwType"] == vw_type

        if connector_id:
            assert connector_id in exc.value.virtual_warehouse["associatedConnectors"]

        # Idempotent re-run of present (no reconcilable drift)
        dw_vw_module_args(create_args)
        with pytest.raises(AnsibleExitJson) as exc:
            dw_virtual_warehouse.main()
        assert exc.value.changed is False

        # Delete
        dw_vw_module_args(
            {
                "warehouse_id": vw_id,
                "state": "absent",
                "wait": True,
                "timeout": timeout,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            dw_virtual_warehouse.main()
        assert exc.value.changed is True

        assert dw_client.get_vw_by_id(existing_dw_cluster_id, vw_id) is None
        vw_id = None
    finally:
        if vw_id is not None:
            try:
                dw_client.delete_vw(existing_dw_cluster_id, vw_id)
            except Exception as e:
                warnings.warn(f"Cleanup failed for Virtual Warehouse {vw_id}: {e}")


@pytest.mark.slow
@pytest.mark.parametrize("vw_type", ["hive", "impala", "trino"])
def test_present_create_with_autoscaling(
    request,
    vw_type,
    dw_vw_module_args,
    cleanup_vw,
    existing_dw_dbc_id,
):
    """Create a VW of each type with autoscaling options (gated by CDW_DBC_ID)."""
    name = _vw_name(request)
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))

    dw_vw_module_args(
        {
            "name": name,
            "type": vw_type,
            "catalog_id": existing_dw_dbc_id,
            "state": "present",
            "wait": True,
            "timeout": timeout,
            "autoscaling": {
                "min_clusters": 1,
                "max_clusters": 3,
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    cleanup_vw(exc.value.virtual_warehouse["id"])
    assert exc.value.changed is True
    assert exc.value.virtual_warehouse["vwType"] == vw_type


@pytest.mark.slow
def test_present_create_impala_with_ha(
    request,
    dw_vw_module_args,
    cleanup_vw,
    existing_dw_dbc_id,
):
    """Create an Impala VW with HA settings at creation time (gated by CDW_DBC_ID)."""
    name = _vw_name(request)
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))

    dw_vw_module_args(
        {
            "name": name,
            "type": "impala",
            "catalog_id": existing_dw_dbc_id,
            "state": "present",
            "wait": True,
            "timeout": timeout,
            "impala_ha": {
                "high_availability_mode": "ACTIVE_PASSIVE",
                "enable_catalog_high_availability": True,
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    cleanup_vw(exc.value.virtual_warehouse["id"])
    assert exc.value.changed is True
    assert exc.value.virtual_warehouse["vwType"] == "impala"


@pytest.mark.slow
def test_present_create_impala_with_autoscaling_and_ha(
    request,
    dw_vw_module_args,
    cleanup_vw,
    existing_dw_dbc_id,
):
    """Create an Impala VW with both autoscaling and HA settings (gated by CDW_DBC_ID)."""
    name = _vw_name(request)
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))

    dw_vw_module_args(
        {
            "name": name,
            "type": "impala",
            "catalog_id": existing_dw_dbc_id,
            "state": "present",
            "wait": True,
            "timeout": timeout,
            "autoscaling": {
                "min_clusters": 1,
                "max_clusters": 3,
                "impala_scale_down_delay_seconds": 60,
                "impala_scale_up_delay_seconds": 30,
            },
            "impala_ha": {
                "high_availability_mode": "ACTIVE_PASSIVE",
                "enable_catalog_high_availability": True,
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    cleanup_vw(exc.value.virtual_warehouse["id"])
    assert exc.value.changed is True
    assert exc.value.virtual_warehouse["vwType"] == "impala"


@pytest.mark.slow
@pytest.mark.parametrize("vw_type", ["hive", "impala", "trino"])
def test_reconcile_node_count(
    vw_type,
    dw_vw_module_args,
    disposable_vw,
    existing_dw_dbc_id,
):
    """Reconcile node_count on an existing VW of each type (gated by CDW_DBC_ID)."""
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))
    vw = disposable_vw(vw_type)

    current_count = vw.nodeCount if isinstance(vw.nodeCount, int) else 0
    target_node_count = 2 if current_count != 2 else 3

    reconcile_args = {
        "name": vw.name,
        "type": vw_type,
        "catalog_id": existing_dw_dbc_id,
        "state": "present",
        "wait": True,
        "timeout": timeout,
        "node_count": target_node_count,
    }

    # Update
    dw_vw_module_args(reconcile_args)
    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is True
    assert exc.value.virtual_warehouse["nodeCount"] == target_node_count

    # Idempotent re-run
    dw_vw_module_args(reconcile_args)
    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is False
    assert exc.value.virtual_warehouse["nodeCount"] == target_node_count


@pytest.mark.slow
def test_reconcile_connectors_trino(
    dw_vw_module_args,
    disposable_vw,
    connector_pair,
    existing_dw_dbc_id,
):
    """Reconcile connector associations (full-sync) on a Trino VW (gated by CDW_DBC_ID)."""
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))
    vw = disposable_vw("trino")
    conn_a, conn_b = connector_pair

    base_args = {
        "name": vw.name,
        "type": "trino",
        "catalog_id": existing_dw_dbc_id,
        "state": "present",
        "wait": True,
        "timeout": timeout,
    }

    # Associate both connectors
    dw_vw_module_args({**base_args, "connectors": [conn_a.id, conn_b.id]})
    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is True
    assert conn_a.id in exc.value.virtual_warehouse["associatedConnectors"]
    assert conn_b.id in exc.value.virtual_warehouse["associatedConnectors"]

    # Idempotent re-run with same connector set
    dw_vw_module_args({**base_args, "connectors": [conn_a.id, conn_b.id]})
    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is False

    # Full-sync: drop conn_b by listing only conn_a
    dw_vw_module_args({**base_args, "connectors": [conn_a.id]})
    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is True
    assert conn_a.id in exc.value.virtual_warehouse["associatedConnectors"]
    assert conn_b.id not in exc.value.virtual_warehouse["associatedConnectors"]


@pytest.mark.slow
@pytest.mark.parametrize("vw_type", ["hive", "impala", "trino"])
def test_reconcile_no_drift_is_idempotent(
    vw_type,
    dw_vw_module_args,
    disposable_vw,
    existing_dw_dbc_id,
):
    """Re-running state=present with no reconcilable drift reports changed=False."""
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))
    vw = disposable_vw(vw_type)

    dw_vw_module_args(
        {
            "name": vw.name,
            "type": vw_type,
            "catalog_id": existing_dw_dbc_id,
            "state": "present",
            "wait": True,
            "timeout": timeout,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_virtual_warehouse.main()

    assert exc.value.changed is False
    assert exc.value.virtual_warehouse["id"] == vw.id
