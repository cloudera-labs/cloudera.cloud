#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Cloudera, Inc. All Rights Reserved.
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: dw_virtual_warehouse_info
short_description: Gather information about CDP Data Warehouse Virtual Warehouses
description:
    - Gather information about CDP Virtual Warehouses
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
requirements:
  - cdpy
options:
  warehouse_id:
    description:
      - The identifier of the Virtual Warehouse.
      - Requires I(cluster_id).
      - Mutually exclusive with I(name) and I(catalog_id).
    type: str
    aliases:
      - vw_id
      - id
  cluster_id:
    description: 
      - The identifier of the parent Data Warehouse Cluster of the Virtual Warehouse(s).
    type: str
  catalog_id:
    description:
      - The identifier of the parent Database Catalog attached to the Virtual Warehouse(s).
      - Requires I(cluster_id).
      - Mutally exclusive with I(warehouse_id) and I(name).
    type: str
    aliases:
      - dbc_id
  name:
    description:
      - The name of the Virtual Warehouse.
      - Requires I(cluster_id).
      - Mutually exclusive with I(warehouse_id) and I(catalog_id).
    type: str
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Virtual Warehouse to achieve the declared
        state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Virtual Warehouse to achieve the declared
        state.
    type: int
    default: 3600
    aliases:
      - polling_timeout  
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List all Virtual Warehouses in a Cluster
- cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id

# List all Virtual Warehouses associated with a Data Catalog
- cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    catalog_id: example-data-catalog-id

# Describe a Virtual Warehouse by ID
- cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    warehouse_id: example-virtual-warehouse-id

# Describe a Virtual Warehouse by name
- cloudera.cloud.dw_virtual_warehouse_info:
    cluster_id: example-cluster-id
    name: example-virtual-warehouse
'''

RETURN = r'''
---
virtual_warehouses:
  description: The details about the CDP Data Warehouse Virtual Warehouse(s).
  type: list
  elements: dict
  contains:
    id:
      description: The identifier of the Virtual Warehouse.
      returned: always
      type: str
    name:
      description: The name of the Virtual Warehouse.
      returned: always
      type: str
    vwType:
      description: The Virtual Warehouse type.
      returned: always
      type: str
    dbcId:
      description: The Database Catalog ID associated with the Virtual Warehouse.
      returned: always
      type: str    
    creationDate:
      description: The creation time of the Virtual Warehouse in UTC.
      returned: always
      type: str
    status:
      description: The status of the Virtual Warehouse.
      returned: always
      type: str
    creator:
      description: Details about the Virtual Warehouse creator.
      returned: always
      type: dict
      suboptions:
        crn:
          description: The creator's Actor CRN.
          type: str
          returned: always
        email:
          description: Email address (for users).
          type: str
          returned: when supported
        workloadUsername:
          description: Username (for users).
          type: str
          returned: when supported
        machineUsername:
          description: Username (for machine users).
          type: str
          returned: when supported
    tags:
      description: Custom tags applied to the Virtual Warehouse.
      returned: always
      type: dict
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when supported
  type: list
  elements: str
'''


class DwVirtualWarehouseInfo(CdpModule):
    def __init__(self, module):
        super(DwVirtualWarehouseInfo, self).__init__(module)

        # Set variables
        self.warehouse_id = self._get_param('warehouse_id')
        self.cluster_id = self._get_param('cluster_id')
        self.catalog_id = self._get_param('catalog_id')
        self.type = self._get_param('type')
        self.name = self._get_param('name')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.virtual_warehouses = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.warehouse_id is not None:
            target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.warehouse_id)
            if target is not None:
                self.virtual_warehouses.append(target)
        else:
            vws = self.cdpy.dw.list_vws(cluster_id=self.cluster_id)
            if self.name is not None:
                for vw in vws:
                    if vw['name'] == self.name:
                        self.virtual_warehouses.append(
                          self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=vw['id'])
                        )
            elif self.catalog_id is not None:
                self.virtual_warehouses =[v for v in vws if v['dbcId'] == self.catalog_id]
            else:
                self.virtual_warehouses = vws


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            warehouse_id=dict(type='str', aliases=['vw_id', 'id']),
            cluster_id=dict(required=True, type='str'),
            catalog_id=dict(type='str', aliases=['dbc_id']),
            name=dict(type='str'),
            delay=dict(type='int', aliases=['polling_delay'], default=15),
            timeout=dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        mutually_exclusive=[
            ['warehouse_id', 'name', 'catalog_id']
        ],
        supports_check_mode=True
    )

    result = DwVirtualWarehouseInfo(module)
    output = dict(changed=False, virtual_warehouses=result.virtual_warehouses)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
