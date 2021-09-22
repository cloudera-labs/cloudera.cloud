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
module: dw_database_catalog
short_description: Create, manage, and destroy CDP Data Warehouse Database Catalogs
description:
    - Create, manage, and destroy CDP Data Warehouse Database Catalogs
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
      - Required if C(state=absent).
    type: str
    aliases:
      - id
  cluster_id:
    description:
      - The identifier of the parent DW Cluster of the Database Catalog.
    type: str
    required: True
  name:
    description:
      - The name of the Database Catalog.
      - Required if C(state=present).
    type: str
  load_demo_data:
    description:
      - Flag to load demonstration data into the Database Catalog during creation.
    type: str
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Catalog to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Catalog to achieve the declared
        state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Catalog to achieve the declared
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

# Create Database Catalog
- cloudera.cloud.dw_database_catalog:
    name: example-database-catalog-name
    cluster_id: example-cluster-id
    
# Delete Database Catalog
- cloudera.cloud.dw_database_catalog:
    catalog_id: example-database-id
    cluster_id: example-cluster-id
    state: absent
'''

RETURN = r'''
---
database_catalog:
  description: Details about the Database Catalog.
  returned: always
  type: dict
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


class DwDatabaseCatalog(CdpModule):
    def __init__(self, module):
        super(DwDatabaseCatalog, self).__init__(module)

        # Set variables
        self.catalog_id = self._get_param('catalog_id')
        self.cluster_id = self._get_param('cluster_id')
        self.name = self._get_param('name')
        self.load_demo_data = self._get_param('load_demo_data')
        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.database_catalog = {}
        self.changed = False

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.catalog_id is None:
            dbcs = self.cdpy.dw.list_dbcs(cluster_id=self.cluster_id)
            for dbc in dbcs:
                if dbc['name'] == self.name:
                    self.target = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=dbc['id'])
        else:
            self.target = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=self.catalog_id)
        
        if self.target is not None:
            # Begin Database Catalog Exists
            if self.state == 'absent':
                if self.module.check_mode:
                    self.database_catalog = self.target
                else:
                    # Begin Drop
                    if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.fail_json(msg=
                            "Database Catalog is not in a valid state for Delete operations: %s" % self.target['status'])
                    else:
                        _ = self.cdpy.dw.delete_dbc(cluster_id=self.cluster_id, dbc_id=self.target['id'])
                        self.changed = True
                        if self.wait:
                            self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.describe_dbc,
                                params=dict(cluster_id=self.cluster_id, dbc_id=self.target['id']),
                                field=None, delay=self.delay, timeout=self.timeout
                            )
                        else:
                            self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                            self.database_catalog = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=self.target['id'])
                    # End Drop
            elif self.state == 'present':
                # Begin Config Check
                self.module.warn("Database Catalog already present and reconciliation is not yet implemented")
                if self.wait:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.dw.describe_dbc,
                        params=dict(cluster_id=self.cluster_id, dbc_id=self.target['id']),
                        state=self.cdpy.sdk.STARTED_STATES, delay=self.delay, timeout=self.timeout
                    )
                self.database_catalog = self.target
                # End Config Check
            else:
                self.module.fail_json(msg="Invalid state %s" % self.state)
            # End Database Catalog Exists
        else:
            # Begin Database Catalog Not Found
            if self.state == 'absent':
                self.module.warn("Database Catalog %s already absent in Cluster %s" % (self.name, self.cluster_id))
            elif self.state == 'present':
                if not self.module.check_mode:
                    dbc_id = self.cdpy.dw.create_dbc(cluster_id=self.cluster_id, name=self.name,
                                                     load_demo_data=self.load_demo_data)
                    self.changed = True
                    if self.wait:
                        self.database_catalog = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_dbc,
                            params=dict(cluster_id=self.cluster_id, dbc_id=dbc_id),
                            state=self.cdpy.sdk.STARTED_STATES, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.database_catalog = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=dbc_id)
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End Database Catalog Not Found

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            catalog_id=dict(type='str', aliases=['id']),
            cluster_id=dict(required=True, type='str'),
            name = dict(type='str'),
            load_demo_data=dict(type='bool'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            wait = dict(type='bool', default=True),
            delay = dict(type='int', aliases=['polling_delay'], default=15),
            timeout = dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        required_if=[
            ['state', 'present', ['name']],
            ['state', 'absent', ['name', 'id'], True],
        ],
        mutually_exclusive=[['name', 'id']],
        supports_check_mode=True
    )

    result = DwDatabaseCatalog(module)
    output = dict(changed=result.changed, database_catalog=result.database_catalog)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
