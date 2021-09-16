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
module: dw_database_catalog_info
short_description: Gather information about CDP Data Warehouse Database Catalogs
description:
    - Gather information about CDP Data Warehouse Database Catalogs
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
requirements:
  - cdpy
options:
  catalog_id:
    description:
      - The identifier of the Database Catalog.
      - If undefined, will return a list of all Database Catalogs in the Cluster.
      - Exclusive with I(name).
    type: str
    aliases:
      - id
  cluster_id:
    description:
      - The identifier of the parent Cluster of the Database Catalog or Catalogs.
    type: str
    required: True
  name:
    description:
      - The name of the Database Catalog.
      - If undefined, will return a list of all Database Catalogs in the Cluster.
      - Exclusive with I(id).
    type: str
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Get a single Database Catalog
- cloudera.cloud.dw_database_catalog_info:
    name: example-database-catalog-name
    cluster_id: example-cluster-id
    
# Get all Database Catalogs within a Cluster
- cloudera.cloud.dw_database_catalog_info:
    cluster_id: example-cluster-id
'''

RETURN = r'''
---
database_catalogs:
  description: Details about the Database Catalogs.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The identifier of the Database Catalog.
      returned: always
      type: str
    name:
      description: The name of the Database Catalog.
      returned: always
      type: str
    status:
      description: The status of the Database Catalog.
      returned: always
      type: str
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


class DwDatabaseCatalogInfo(CdpModule):
    def __init__(self, module):
        super(DwDatabaseCatalogInfo, self).__init__(module)

        # Set variables
        self.catalog_id = self._get_param('catalog_id')
        self.cluster_id = self._get_param('cluster_id')
        self.name = self._get_param('name')

        # Initialize return values
        self.database_catalogs = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.catalog_id is not None:
          target = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=self.catalog_id)
          if target is not None:
            self.database_catalogs.append(target)
        else:
          dbcs = self.cdpy.dw.list_dbcs(cluster_id=self.cluster_id)
          if self.name is not None:
            for dbc in dbcs:
                if dbc['name'] == self.name:
                    self.database_catalogs.append(self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=dbc['id']))
          else:
            self.database_catalogs = dbcs


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            catalog_id=dict(type='str', aliases=['id']),
            cluster_id=dict(required=True, type='str'),
            name = dict(type='str'),
        ),
        mutually_exclusive=[['id', 'name']],
        supports_check_mode=True
    )

    result = DwDatabaseCatalogInfo(module)
    output = dict(changed=False, database_catalogs=result.database_catalogs)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
