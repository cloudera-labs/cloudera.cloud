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
