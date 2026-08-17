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

# pylint: disable=redefined-outer-name,unused-argument

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cloudera.cloud.plugins.modules import dw_virtual_warehouse_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    VirtualWarehouse,
)

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

CLUSTER_ID = "env-abc123"
CATALOG_ID = "warehouse-abc123"

MOCK_VWS = [
    VirtualWarehouse(id="trino-1", name="vw-one", vwType="trino", dbcId=CATALOG_ID),
    VirtualWarehouse(id="hive-2", name="vw-two", vwType="hive", dbcId="other-dbc"),
]


@pytest.fixture
def mock_client(mocker):
    """Patch load_cdp_config and return the CdpDwClient mock."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_virtual_warehouse_info.CdpDwClient",
        autospec=True,
    ).return_value


def _args(**extra):
    base = {
        "endpoint": BASE_URL,
        "access_key": ACCESS_KEY,
        "private_key": PRIVATE_KEY,
    }
    base.update(extra)
    return base


def test_cluster_id_required(module_args):
    """Module fails when cluster_id is not provided."""
    module_args(_args())

    with pytest.raises(AnsibleFailJson):
        dw_virtual_warehouse_info.main()


def test_lookup_keys_mutually_exclusive(module_args, mock_client):
    """warehouse_id, name, and catalog_id are mutually exclusive."""
    module_args(
        _args(cluster_id=CLUSTER_ID, warehouse_id="trino-1", name="vw-one"),
    )

    with pytest.raises(AnsibleFailJson):
        dw_virtual_warehouse_info.main()


def test_list_all(module_args, mock_client):
    """No filter returns every warehouse in the cluster."""
    module_args(_args(cluster_id=CLUSTER_ID))
    mock_client.list_vws.return_value = MOCK_VWS

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert result.value.changed is False
    assert len(result.value.virtual_warehouses) == 2
    assert result.value.virtual_warehouses[0]["id"] == "trino-1"
    mock_client.list_vws.assert_called_once_with(CLUSTER_ID)


def test_get_by_warehouse_id(module_args, mock_client):
    """warehouse_id describes a single warehouse by id."""
    module_args(_args(cluster_id=CLUSTER_ID, warehouse_id="trino-1"))
    mock_client.get_vw_by_id.return_value = MOCK_VWS[0]

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert len(result.value.virtual_warehouses) == 1
    assert result.value.virtual_warehouses[0]["id"] == "trino-1"
    mock_client.get_vw_by_id.assert_called_once_with(CLUSTER_ID, "trino-1")
    mock_client.list_vws.assert_not_called()


def test_get_by_warehouse_id_not_found(module_args, mock_client):
    """A missing warehouse_id yields an empty list."""
    module_args(_args(cluster_id=CLUSTER_ID, warehouse_id="missing"))
    mock_client.get_vw_by_id.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert result.value.virtual_warehouses == []


def test_get_by_name(module_args, mock_client):
    """name describes a single warehouse by name."""
    module_args(_args(cluster_id=CLUSTER_ID, name="vw-two"))
    mock_client.get_vw_by_name.return_value = MOCK_VWS[1]

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert len(result.value.virtual_warehouses) == 1
    assert result.value.virtual_warehouses[0]["name"] == "vw-two"
    mock_client.get_vw_by_name.assert_called_once_with(CLUSTER_ID, "vw-two")


def test_filter_by_catalog_id(module_args, mock_client):
    """catalog_id filters the listing by dbcId."""
    module_args(_args(cluster_id=CLUSTER_ID, catalog_id=CATALOG_ID))
    mock_client.list_vws.return_value = MOCK_VWS

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert len(result.value.virtual_warehouses) == 1
    assert result.value.virtual_warehouses[0]["dbcId"] == CATALOG_ID
    mock_client.list_vws.assert_called_once_with(CLUSTER_ID)


def test_empty_api_result(module_args, mock_client):
    """An empty cluster returns an empty list."""
    module_args(_args(cluster_id=CLUSTER_ID))
    mock_client.list_vws.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse_info.main()

    assert result.value.virtual_warehouses == []
