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

from ansible_collections.cloudera.cloud.plugins.modules import dw_virtual_warehouse_info
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
def dw_vw_info_module_args(module_args, env_context):
    """Pre-populate common dw_virtual_warehouse_info arguments from the env."""

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


class TestDwVirtualWarehouseInfoIntegration:
    """Drive the info module against a shared, class-scoped Trino warehouse."""

    def test_list_all_includes(self, dw_vw_info_module_args, existing_vw_trino):
        """No filter returns a list that includes the created warehouse."""
        dw_vw_info_module_args()

        with pytest.raises(AnsibleExitJson) as result:
            dw_virtual_warehouse_info.main()

        assert result.value.changed is False
        ids = [vw["id"] for vw in result.value.virtual_warehouses]
        assert existing_vw_trino.id in ids

    def test_get_by_warehouse_id(self, dw_vw_info_module_args, existing_vw_trino):
        """warehouse_id returns exactly the target warehouse."""
        dw_vw_info_module_args({"warehouse_id": existing_vw_trino.id})

        with pytest.raises(AnsibleExitJson) as result:
            dw_virtual_warehouse_info.main()

        assert len(result.value.virtual_warehouses) == 1
        assert result.value.virtual_warehouses[0]["id"] == existing_vw_trino.id

    def test_get_by_name(self, dw_vw_info_module_args, existing_vw_trino):
        """name returns exactly the target warehouse."""
        dw_vw_info_module_args({"name": existing_vw_trino.name})

        with pytest.raises(AnsibleExitJson) as result:
            dw_virtual_warehouse_info.main()

        assert len(result.value.virtual_warehouses) == 1
        assert result.value.virtual_warehouses[0]["id"] == existing_vw_trino.id

    def test_filter_by_catalog_id(self, dw_vw_info_module_args, existing_vw_trino):
        """catalog_id filters to warehouses attached to that Database Catalog."""
        dw_vw_info_module_args({"catalog_id": existing_vw_trino.dbcId})

        with pytest.raises(AnsibleExitJson) as result:
            dw_virtual_warehouse_info.main()

        ids = [vw["id"] for vw in result.value.virtual_warehouses]
        assert existing_vw_trino.id in ids
        assert all(
            vw["dbcId"] == existing_vw_trino.dbcId
            for vw in result.value.virtual_warehouses
        )

    def test_name_no_match(self, dw_vw_info_module_args):
        """A non-existent name returns an empty list."""
        dw_vw_info_module_args({"name": "nonexistent-vw-99999"})

        with pytest.raises(AnsibleExitJson) as result:
            dw_virtual_warehouse_info.main()

        assert result.value.virtual_warehouses == []
