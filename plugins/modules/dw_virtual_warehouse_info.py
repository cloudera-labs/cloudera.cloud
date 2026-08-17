#!/usr/bin/python
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

DOCUMENTATION = r"""
module: dw_virtual_warehouse_info
short_description: Gather information about CDP Data Warehouse Virtual Warehouses
description:
  - Gather information about CDP Data Warehouse (CDW) Virtual Warehouses in a cluster.
  - Optionally filter by Virtual Warehouse id, name, or parent Database Catalog.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.5.0"
options:
  warehouse_id:
    description:
      - The identifier of the Virtual Warehouse.
      - Mutually exclusive with O(name) and O(catalog_id).
    type: str
    aliases:
      - vw_id
      - id
  cluster_id:
    description:
      - The identifier of the parent Data Warehouse Cluster of the Virtual Warehouse(s).
    type: str
    required: true
  catalog_id:
    description:
      - The identifier of the parent Database Catalog attached to the Virtual Warehouse(s).
      - Mutually exclusive with O(warehouse_id) and O(name).
    type: str
    aliases:
      - dbc_id
  name:
    description:
      - The name of the Virtual Warehouse.
      - Mutually exclusive with O(warehouse_id) and O(catalog_id).
    type: str
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
attributes:
  check_mode:
    support: full
  diff_mode:
    support: N/A
  platform:
    platforms: all
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: List all Virtual Warehouses in a Cluster
  cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id

- name: List all Virtual Warehouses associated with a Database Catalog
  cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    catalog_id: example-data-catalog-id

- name: Describe a Virtual Warehouse by ID
  cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    warehouse_id: example-virtual-warehouse-id

- name: Describe a Virtual Warehouse by name
  cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    name: example-virtual-warehouse
"""

RETURN = r"""
virtual_warehouses:
  description: The details about the CDP Data Warehouse Virtual Warehouse(s).
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The identifier of the Virtual Warehouse.
      returned: when available
      type: str
    name:
      description: The name of the Virtual Warehouse.
      returned: when available
      type: str
    vwType:
      description: The Virtual Warehouse type.
      returned: when available
      type: str
    dbcId:
      description: The Database Catalog ID associated with the Virtual Warehouse.
      returned: when available
      type: str
    status:
      description: The status of the Virtual Warehouse.
      returned: when available
      type: str
    instanceType:
      description: The underlying compute instance type.
      returned: when available
      type: str
    nodeCount:
      description: The node count (compute cluster size) of the Virtual Warehouse.
      returned: when available
      type: int
    creator:
      description: Details about the Virtual Warehouse creator.
      returned: when available
      type: dict
    creationDate:
      description: The creation time of the Virtual Warehouse in UTC.
      returned: when available
      type: str
    configId:
      description: The identifier of the Virtual Warehouse configuration.
      returned: when available
      type: str
    tags:
      description: Custom tags applied to the Virtual Warehouse.
      returned: when available
      type: list
      elements: dict
    associatedConnectors:
      description:
        - The connectors associated with the Virtual Warehouse, keyed by
          connector id.
      returned: when available
      type: dict
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when debug is true
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when debug is true
  type: list
  elements: str
"""

from typing import Any, Dict, List

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    VirtualWarehouse,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)


class DwVirtualWarehouseInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                warehouse_id=dict(type="str", aliases=["vw_id", "id"]),
                cluster_id=dict(required=True, type="str"),
                catalog_id=dict(type="str", aliases=["dbc_id"]),
                name=dict(type="str"),
            ),
            mutually_exclusive=[["warehouse_id", "name", "catalog_id"]],
            supports_check_mode=True,
        )
        self.warehouse_id = self.get_param("warehouse_id")
        self.cluster_id = self.get_param("cluster_id")
        self.catalog_id = self.get_param("catalog_id")
        self.name = self.get_param("name")

        self.virtual_warehouses: List[VirtualWarehouse] = []

    def process(self):
        client = CdpDwClient(api_client=self.api_client)

        if self.warehouse_id is not None:
            vw = client.get_vw_by_id(self.cluster_id, self.warehouse_id)
            self.virtual_warehouses = [vw] if vw is not None else []
        elif self.name is not None:
            vw = client.get_vw_by_name(self.cluster_id, self.name)
            self.virtual_warehouses = [vw] if vw is not None else []
        elif self.catalog_id is not None:
            self.virtual_warehouses = [
                vw
                for vw in client.list_vws(self.cluster_id)
                if vw.dbcId == self.catalog_id
            ]
        else:
            self.virtual_warehouses = client.list_vws(self.cluster_id)


def main():
    result = DwVirtualWarehouseInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        virtual_warehouses=[to_dict(vw) for vw in result.virtual_warehouses],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
