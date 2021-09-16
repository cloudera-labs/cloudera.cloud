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
module: dw_virtual_warehouse
short_description: Create, manage, and destroy CDP Data Warehouse Virtual Warehouses
description:
    - Create CDP Virtual Warehouse
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
      - Required if C(state=absent).
    type: str
    aliases:
      - vw_id
      - id
  cluster_id:
    description: 
      - The identifier of the parent Data Warehouse Cluster of the Virtual Warehouse.
    type: str
    required: True
  catalog_id:
    description:
      - The identifier of the parent Database Catalog attached to the Virtual Warehouse.
      - Required if C(state=present)
    type: str
    aliases:
      - dbc_id
  type:
    description:
      - The type of Virtual Warehouse to be created.
      - Required if C(state=present)
    type: str
    choices:
      - hive
      - impala
  name:
    description:
      - The name of the Virtual Warehouse.
      - Required if C(state=present)
    type: str
  template:
    description: The name of deployment template for the Virtual Warehouse
    type: str
    choices:
      - xsmall
      - small
      - medium
      - large
  autoscaling_min_nodes:
    description: The minimum number of available nodes for Virtual Warehouse autoscaling.
    type: int
  autoscaling_max_nodes:
    description: The maximum number of available nodes for Virtual Warehouse autoscaling.
    type: int
  common_configs: 
    description: Configurations that are applied to every application in the Virtual Warehouse service.
    type: dict
    suboptions:
      configBlocks: 
        description: List of I(ConfigBlocks) for the application.
        type: list
        elements: dict
        suboptions:
          id: 
            description:
              - ID of the ConfigBlock. 
              - Unique within an I(ApplicationConfig).
            type: str
          format:
            description: Format of the ConfigBlock.
            type: str
            choices:
              - HADOOP_XML
              - PROPERTIES
              - TEXT
              - JSON
              - BINARY
              - ENV
              - FLAGFILE
          content:
            description: Contents of the ConfigBlock.
            type: dict
            suboptions:
              keyValues: 
                description: Key-value type configuration. 
                type: dict
              text:
                description: Text type configuration.
                type: str   
              json:
                description: JSON type configuration.
                type: str    
  application_configs:
    description: Configurations that are applied to specific applications in the Virtual Warehouse service.
    type: dict
    suboptions:
      __application_name__:
        description: The application name or identifier.
        type: dict
        suboptions:  
          configBlocks:
            description: List of I(ConfigBlocks) for the specified application.
            type: list
            required: False  
            elements: dict
            suboptions:
              id: 
                description:
                  - ID of the ConfigBlock.
                  - Unique within an ApplicationConfig.
                type: str
              format:
                description: Format of ConfigBlock.
                type: str
              content:
                description: Contents of a ConfigBlock.
                type: dict
                suboptions:
                  keyValues: 
                    description: Key-value type configuration. 
                    type: dict
                  text:
                    description: Text type configuration.
                    type: str   
                  json:
                    description: JSON type configuration.
                    type: str    
  ldap_groups:
    description: LDAP Groupnames to enabled for authentication to the Virtual Warehouse.
    type: list
    elements: str
  enable_sso:
    description: Flag to enable Single Sign-On (SSO) for the Virtual Warehouse.
    type: bool
    default: False    
  tags:
    description: Key-value tags associated with the Virtual Warehouse cloud provider resources.
    type: dict
  state:
    description: The declarative state of the Virtual Warehouse
    type: str
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Virtual Warehouse to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    default: True
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

# Create a Virtual Warehouse
- cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    name: example-virtual-warehouse
    type: hive
    template: xsmall
    autoscaling_min_nodes: 3
    autoscaling_max_nodes: 19
    tags:
       some_key: "some value"
    enable_sso: true
    ldap_groups: ['group1', 'group2', 'group3']

# Create a Virtual Warehouse with configurations
- cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    name: example-virtual-warehouse
    type: "hive"
    template: "xsmall"
    enable_sso: true
    ldap_groups: ['group1','group2','group3']
    common_configs:
        configBlocks:
            - id: das-ranger-policymgr
              format: HADOOP_XML
              content:
                  keyValues:
                      'xasecure.policymgr.clientssl.truststore': '/path_to_ca_cert/cacerts'
    application_configs: 
        das-webapp:
            configBlocks:
                - id: hive-kerberos-config
                  format: TEXT
                  content:
                      text: "\n[libdefaults]\n\trenew_lifetime = 7d"   
                      
# Delete a Virtual Warehouse
- cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    warehouse_id: example-virtual-warehouse-id
    state: absent      
'''

RETURN = r'''
---
virtual_warehouse:
  description: The details about the CDP Data Warehouse Virtual Warehouse.
  type: dict
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


class DwVirtualWarehouse(CdpModule):
    def __init__(self, module):
        super(DwVirtualWarehouse, self).__init__(module)

        # Set variables
        self.warehouse_id = self._get_param('warehouse_id')
        self.cluster_id = self._get_param('cluster_id')
        self.dbc_id = self._get_param('catalog_id')
        self.type = self._get_param('type')
        self.name = self._get_param('name')
        self.template = self._get_param('template')
        self.autoscaling_min_nodes = self._get_param('autoscaling_min_nodes')
        self.autoscaling_max_nodes = self._get_param('autoscaling_max_nodes')
        self.common_configs = self._get_param('common_configs')
        self.application_configs = self._get_param('application_configs')
        self.ldap_groups = self._get_param('ldap_groups')
        self.enable_sso = self._get_param('enable_sso')
        self.state = self._get_param('state')
        self.tags = self._get_param('tags')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.virtual_warehouse = {}

        # Initialize internal values
        self.target = None
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.warehouse_id is None:
            vws = self.cdpy.dw.list_vws(cluster_id=self.cluster_id)
            for vw in vws:
                if self.name is not None and vw['name'] == self.name:
                    self.target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=vw['id'])
        else:
            self.target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.warehouse_id)
        
        if self.target is not None:
            # Begin Virtual Warehouse Exists
            if self.state == 'absent':
                if self.module.check_mode:
                    self.virtual_warehouse = self.target
                else:
                    # Begin Drop
                    if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.fail_json(msg="Virtual Warehouse not in valid state for Delete operation: %s" % 
                                              self.target['status'])
                    else:
                        _ = self.cdpy.dw.delete_vw(cluster_id=self.cluster_id, vw_id=self.target['id'])
                        self.changed = True
                        if self.wait:
                            self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.describe_vw,
                                params=dict(cluster_id=self.cluster_id, vw_id=self.target['id']),
                                field=None, delay=self.delay, timeout=self.timeout
                            )
                        else:
                            self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                            self.virtual_warehouse = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.target['id'])
                    # End Drop
            elif self.state == 'present':
                # Begin Config check
                self.module.warn("Virtual Warehouse already present and reconciliation is not yet implemented")
                if self.wait and not self.module.check_mode:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.dw.describe_vw,
                        params=dict(cluster_id=self.cluster_id, vw_id=self.target['id']),
                        state=self.cdpy.sdk.STARTED_STATES + self.cdpy.sdk.STOPPED_STATES, delay=self.delay, 
                        timeout=self.timeout
                    )
                self.virtual_warehouse = self.target
                # End Config check
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End Virtual Warehouse Exists
        else:
            # Begin Virtual Warehouse Not Found
            if self.state == 'absent':
                self.module.warn("Virtual Warehouse is already absent in Cluster %s" % self.cluster_id)
            elif self.state == 'present':
                if not self.module.check_mode:
                    vw_id = self.cdpy.dw.create_vw(cluster_id=self.cluster_id,
                                                   dbc_id=self.dbc_id, vw_type=self.type, name=self.name,
                                                   template=self.template,
                                                   autoscaling_min_cluster=self.autoscaling_min_nodes,
                                                   autoscaling_max_cluster=self.autoscaling_max_nodes,
                                                   common_configs=self.common_configs,
                                                   application_configs=self.application_configs,
                                                   ldap_groups=self.ldap_groups, enable_sso=self.enable_sso,
                                                   tags=self.tags)
                    self.changed = True
                    if self.wait:
                        self.virtual_warehouse = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_vw,
                            params=dict(cluster_id=self.cluster_id, vw_id=vw_id),
                            state=self.cdpy.sdk.STARTED_STATES, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.virtual_warehouse = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=vw_id)
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End Virtual Warehouse Not Found

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            warehouse_id=dict(type='str', aliases=['vw_id', 'id']),
            cluster_id=dict(required=True, type='str'),
            catalog_id=dict(type='str', aliases=['dbc_id']),
            type = dict(type='str'),
            name = dict(type='str'),
            template=dict(type='str', choices=['xsmall', 'small', 'medium', 'large']),
            autoscaling_min_nodes=dict(type='int'),
            autoscaling_max_nodes=dict(type='int'),
            common_configs=dict(type='dict', options=dict(
                configBlocks = dict(type='list', elements='dict', options=dict(
                    id=dict(type='str'),
                    format=dict(type='str', choices=['HADOOP_XML', 'PROPERTIES', 'TEXT', 'JSON', 'BINARY', 'ENV', 'FLAGFILE']),
                    content=dict(type='dict', options=dict(
                        keyValues=dict(type='dict'),
                        text=dict(type='str'),
                        json=dict(type='json')
                    ))
                ))
            )),
            application_configs=dict(type='dict'),
            ldap_groups=dict(type='list'),
            enable_sso=dict(type='bool', default=False),
            tags=dict(type='dict'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            wait = dict(type='bool', default=True),
            delay = dict(type='int', aliases=['polling_delay'], default=15),
            timeout = dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        required_if=[
            ['state', 'absent', ['warehouse_id']],
            ['state', 'present', ['catalog_id', 'type', 'name']]
        ],
        supports_check_mode=True
    )

    result = DwVirtualWarehouse(module)
    output = dict(changed=result.changed, virtual_warehouse=result.virtual_warehouse)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
