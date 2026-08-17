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

from ansible_collections.cloudera.cloud.plugins.modules import dw_virtual_warehouse
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    VirtualWarehouse,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "env-cluster-id"
CATALOG_ID = "warehouse-catalog-id"
VW_ID = "trino-abc123"
VW_NAME = "test-vw"
CONNECTOR_1 = "connector-1"
CONNECTOR_2 = "connector-2"
CONNECTOR_3 = "connector-3"


@pytest.fixture
def dw_vw_module_args(module_args):
    """Pre-populate common dw_virtual_warehouse module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "wait": False,
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def dw_vw_client(mocker):
    """Patch load_cdp_config and CdpDwClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_virtual_warehouse.CdpDwClient",
        autospec=True,
    ).return_value


def _running_vw(**overrides):
    base = dict(id=VW_ID, name=VW_NAME, vwType="trino", status="Running")
    base.update(overrides)
    return VirtualWarehouse(**base)


def test_present_create_hive(dw_vw_module_args, dw_vw_client):
    """A new Hive warehouse is created; no connector association step runs."""
    dw_vw_client.get_vw_by_name.return_value = None
    dw_vw_client.create_vw.return_value = _running_vw(vwType="hive")

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "hive",
            "catalog_id": CATALOG_ID,
            "tshirt_size": "xsmall",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    assert result.value.virtual_warehouse["id"] == VW_ID
    dw_vw_client.create_vw.assert_called_once()
    assert dw_vw_client.create_vw.call_args.kwargs["vw_type"] == "hive"
    assert dw_vw_client.create_vw.call_args.kwargs["name"] == VW_NAME
    dw_vw_client.update_vw.assert_not_called()


def test_present_create_trino_two_step(dw_vw_module_args, dw_vw_client):
    """A new Trino warehouse is created, then connectors are associated (step 2)."""
    dw_vw_client.get_vw_by_name.return_value = None
    dw_vw_client.create_vw.return_value = _running_vw()
    dw_vw_client.update_vw.return_value = _running_vw(
        associatedConnectors={CONNECTOR_1: {}, CONNECTOR_2: {}},
    )

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "connectors": [CONNECTOR_2, CONNECTOR_1],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.create_vw.assert_called_once()
    dw_vw_client.update_vw.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vw_id=VW_ID,
        associated_connectors=[CONNECTOR_1, CONNECTOR_2],
    )


def test_present_create_trino_no_connectors(dw_vw_module_args, dw_vw_client):
    """Creating a Trino warehouse without connectors skips the association step."""
    dw_vw_client.get_vw_by_name.return_value = None
    dw_vw_client.create_vw.return_value = _running_vw()

    dw_vw_module_args(
        {"name": VW_NAME, "type": "trino", "catalog_id": CATALOG_ID},
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.update_vw.assert_not_called()


def test_present_idempotent(dw_vw_module_args, dw_vw_client):
    """An existing warehouse matching the desired state reports no change."""
    dw_vw_client.get_vw_by_name.return_value = _running_vw(
        nodeCount=3,
        associatedConnectors={CONNECTOR_1: {"name": "hive", "configId": "cfg"}},
    )

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "node_count": 3,
            "connectors": [CONNECTOR_1],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is False
    dw_vw_client.update_vw.assert_not_called()


def test_reconcile_node_count(dw_vw_module_args, dw_vw_client):
    """A node_count difference triggers an update of only that field."""
    dw_vw_client.get_vw_by_name.return_value = _running_vw(nodeCount=3)
    dw_vw_client.update_vw.return_value = _running_vw(nodeCount=5)

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "node_count": 5,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.update_vw.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vw_id=VW_ID,
        node_count=5,
        associated_connectors=None,
    )


def test_reconcile_connectors_full_sync(dw_vw_module_args, dw_vw_client):
    """A differing connector set is fully synced (add and remove)."""
    dw_vw_client.get_vw_by_name.return_value = _running_vw(
        nodeCount=3,
        associatedConnectors={CONNECTOR_1: {}, CONNECTOR_2: {}},
    )
    dw_vw_client.update_vw.return_value = _running_vw(
        nodeCount=3,
        associatedConnectors={CONNECTOR_1: {}, CONNECTOR_3: {}},
    )

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "connectors": [CONNECTOR_3, CONNECTOR_1],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.update_vw.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vw_id=VW_ID,
        node_count=None,
        associated_connectors=[CONNECTOR_1, CONNECTOR_3],
    )


def test_empty_connectors_warns_and_noops(dw_vw_module_args, dw_vw_client):
    """An empty connector set cannot detach all; it is a warned no-op."""
    dw_vw_client.get_vw_by_name.return_value = _running_vw(
        nodeCount=3,
        associatedConnectors={CONNECTOR_1: {}},
    )

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "connectors": [],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is False
    dw_vw_client.update_vw.assert_not_called()


def test_connectors_on_non_trino_fails(dw_vw_module_args, dw_vw_client):
    """Supplying connectors for a non-Trino warehouse fails."""
    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "hive",
            "catalog_id": CATALOG_ID,
            "connectors": [CONNECTOR_1],
        },
    )

    with pytest.raises(AnsibleFailJson):
        dw_virtual_warehouse.main()


def test_absent_deletes(dw_vw_module_args, dw_vw_client):
    """state=absent deletes an existing warehouse by id."""
    dw_vw_client.get_vw_by_id.return_value = _running_vw()

    dw_vw_module_args({"warehouse_id": VW_ID, "state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.delete_vw.assert_called_once_with(CLUSTER_ID, VW_ID)


def test_absent_noop(dw_vw_module_args, dw_vw_client):
    """state=absent is a no-op when the warehouse does not exist."""
    dw_vw_client.get_vw_by_id.return_value = None

    dw_vw_module_args({"warehouse_id": VW_ID, "state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is False
    dw_vw_client.delete_vw.assert_not_called()


def test_check_mode_create_does_not_call_api(dw_vw_module_args, dw_vw_client):
    """check_mode reports changed without creating the warehouse."""
    dw_vw_client.get_vw_by_name.return_value = None

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "connectors": [CONNECTOR_1],
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.changed is True
    dw_vw_client.create_vw.assert_not_called()
    dw_vw_client.update_vw.assert_not_called()


def test_create_reports_diff(dw_vw_module_args, dw_vw_client):
    """Creating a warehouse populates diff.after under --diff."""
    dw_vw_client.get_vw_by_name.return_value = None
    dw_vw_client.create_vw.return_value = _running_vw(vwType="hive")

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "hive",
            "catalog_id": CATALOG_ID,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "name": VW_NAME,
        "vwType": "hive",
        "dbcId": CATALOG_ID,
    }


def test_reconcile_reports_diff(dw_vw_module_args, dw_vw_client):
    """Reconciling node_count reports before/after under --diff."""
    dw_vw_client.get_vw_by_name.return_value = _running_vw(nodeCount=3)
    dw_vw_client.update_vw.return_value = _running_vw(nodeCount=5)

    dw_vw_module_args(
        {
            "name": VW_NAME,
            "type": "trino",
            "catalog_id": CATALOG_ID,
            "node_count": 5,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.diff["before"] == {"nodeCount": 3}
    assert result.value.diff["after"] == {"nodeCount": 5}


def test_absent_reports_diff(dw_vw_module_args, dw_vw_client):
    """Deleting a warehouse reports its full representation in diff.before."""
    existing = _running_vw(nodeCount=3)
    dw_vw_client.get_vw_by_id.return_value = existing

    dw_vw_module_args(
        {"warehouse_id": VW_ID, "state": "absent", "_ansible_diff": True},
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_virtual_warehouse.main()

    assert result.value.diff["before"]["id"] == VW_ID
    assert result.value.diff["after"] == {}
