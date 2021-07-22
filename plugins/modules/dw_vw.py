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
module: dw_vw
short_description: Create CDP Data Warehouse Virtual Warehouse
description:
    - Create CDP Virtual Warehouse
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
requirements:
  - cdpy
options:
  cluster_id:
    description: ID of cluster where Virtual Warehouse should be created.
    type: str
    required: True
  dbc_id:
    description: ID of Database Catalog that the Virtual Warehouse should be attached to.
    type: str
    required: True
  vw_type:
    description: Type of Virtual Warehouse to be created.
    type: str
    required: True
  name:
    description: Name of the Virtual Warehouse.
    type: str
    required: True
  template:
    description: Name of configuration template to use.
    type: str
    required: False
  autoscaling_min_cluster:
    description: Minimum number of available nodes for Virtual Warehouse autoscaling.
    type: int
    required: False
  autoscaling_max_cluster:
    description: Maximum number of available nodes for Virtual Warehouse autoscaling.
    type: int
    required: False
  config:
    description: Configuration settings for the Virtual Warehouse.
    type: dict
    required: False
    contains:
      commonConfigs: 
        description: Configurations that are applied to every application in the service.
        type: dict
        required: False
        contains:
          configBlocks: List of ConfigBlocks for the application.
           type: list
           required: False  
           contains:
            id: 
              description: ID of the ConfigBlock. Unique within an ApplicationConfig.
              type: str
              required: False
            format:
              description: Format of ConfigBlock.
              type: str
              required: False
            content:
              description: Contents of a ConfigBlock.
              type: obj
              required: False
              contains:
                keyValues: 
                  description: Key-value type configurations. 
                  type: obj
                  required: False
                  contains:
                    additionalProperties:
                      description: Key-value type configurations.
                      type: str
                      required: False
                    text:
                      description: Text type configuration.
                      type: str   
                      required: False
                    json:
                      description: JSON type configuration.
                      type: str    
                      required: False
      applicationConfigs:
        description: Application specific configurations.
        type: dict
        required: False
        contains:  
          configBlocks: List of ConfigBlocks for the application.
           type: list
           required: False  
           contains:
            id: 
              description: ID of the ConfigBlock. Unique within an ApplicationConfig.
              type: str
              required: False
            format:
              description: Format of ConfigBlock.
              type: str
              required: False
            content:
              description: Contents of a ConfigBlock.
              type: obj
              required: False
              contains:
                keyValues: 
                  description: Key-value type configurations. 
                  type: obj
                  required: False
                  contains:
                    additionalProperties:
                      description: Key-value type configurations.
                      type: str
                      required: False
                    text:
                      description: Text type configuration.
                      type: str   
                      required: False
                    json:
                      description: JSON type configuration.
                      type: str    
                      required: False
      ldapGroups:
        description: LDAP Groupnames to be enabled for auth.
        type: list
        required: False
      enableSSO:
        description: Should SSO be enabled for this VW.
        type: bool
        required: False    
  tags:
    description: Tags associated with the resources.
    type: dict
    required: False
  state:
    description: The declarative state of the Virtual Warehouse
    type: str
    required: False
    default: present
    choices:
      - present
      - absent  
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout  
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create Virtual Warehouse
- cloudera.cloud.dw_vw:
    cluster_id: "example-cluster-id"
    name: "example-virtual-warehouse"
    vw_type: "hive"
    template: "xsmall"
    autoscaling:
       min_cluster: 3
       max_cluster: 19
    tags:
       tag-key: "tag-value"
    configs:
       enable_sso: true
       ldap_groups: ['group1','group2','group3']
       
# Delete Virtual Warehouse
- cloudera.cloud.dw_vw:
    cluster_id: "example-cluster-id"
    name: "example-virtual-warehouse"
    state: absent      
'''

RETURN = r'''
---
vws:
  description: The information about the named CDW Virtual Warehouses.
  type: list
  returned: always
  elements: complex
  contains:
    vws:
      type: dict
      contains:
        id:
          description: Id of the Virtual Warehouse created.
          returned: always
          type: str
        name:
          description: Name of the Virtual Warehouse created.
          returned: always
          type: str
        vwType:
          description: Virtual Warehouse type.
          returned: always
          type: str
        dbcId:
          description: Database Catalog ID against which Virtual Warehouse was created.
          returned: always
          type: str    
        creationDate:
          description: The creation time of the cluster in UTC.
          returned: always
          type: str
        status:
          description: The status of the Virtual Warehouse.
          returned: always
          type: str
        creator:
          description: The CRN of the cluster creator.
          returned: always
          type: dict
          contains:
            crn:
              type: str
              description: Actor CRN
            email:
              type: str
              description: Email address for users
            workloadUsername:
              type: str
              description: Username for users
            machineUsername:
              type: str
              description: Username for machine users
        tags:
          description: Custom tags that were used to create this Virtual Warehouse.
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


class DwVw(CdpModule):
    def __init__(self, module):
        super(DwVw, self).__init__(module)

        # Set variables
        self.cluster_id = self._get_param('cluster_id')
        self.dbc_id = self._get_param('dbc_id')
        self.vw_type = self._get_param('vw_type')
        self.name = self._get_param('name')
        self.template = self._get_param('template')
        self.autoscaling_min_cluster = self._get_param('autoscaling_min_cluster')
        self.autoscaling_max_cluster = self._get_param('autoscaling_max_cluster')
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
        self.vws = []

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        cluster = self.cdpy.dw.describe_cluster(cluster_id=self.cluster_id)
        if cluster is None:
            self.module.fail_json(msg="Couldn't retrieve cluster info for  %s " % self.cluster_id)
        else:
            dbc = self.cdpy.dw.describe_dbc(cluster_id=self.cluster_id, dbc_id=self.dbc_id)
            if dbc is None:
                self.module.fail_json(msg="Couldn't retrieve dbc info for  %s " % self.dbc_id)
            else:
                self.target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.name)
                # If Virtual Warehouse exists
                if self.target is not None:
                    if self.state == 'absent':
                        if self.module.check_mode:
                            self.clusters.append(self.target)
                        else:
                            if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                                self.module.warn(
                                    "DW Virtual Warehouse not in valid state for Delete operation: %s" % self.target[
                                        'status'])
                            else:
                                _ = self.cdpy.dw.delete_vw(cluster_id=self.cluster_id, vw_id=self.name)
                            if self.wait:
                                self.cdpy.sdk.wait_for_state(
                                    describe_func=self.cdpy.dw.describe_vw,
                                    params=dict(cluster_id=self.cluster_id, vw_id=self.name),
                                    field=None, delay=self.delay, timeout=self.timeout
                                )
                            else:
                                self.cdpy.sdk.sleep(3)  # Wait for consistency sync
                                self.target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.name)
                                self.clusters.append(self.target)
                            # Drop Done
                    elif self.state == 'present':
                        # Begin Config check
                        self.module.warn("DW Virtual Warehouse already present and config validation is not implemented")
                        if self.wait:
                            self.target = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.delete_vw,
                                params=dict(cluster_id=self.cluster_id, vw_id=self.name),
                                state='Running', delay=self.delay, timeout=self.timeout
                            )
                            self.clusters.append(self.target)
                            # End Config check
                    else:
                        self.module.fail_json(msg="State %s is not valid for this module" % self.state)
                    # End handling Virtual Warehouse exists
                else:
                    # Begin handling Virtual Warehouse not found
                    if self.state == 'absent':
                        self.module.warn(
                            "DW Virtual Warehouse %s already absent in Cluster %s" % (self.name, self.cluster_id))
                    elif self.state == 'present':
                        if self.module.check_mode:
                            pass
                        else:
                            self.name = self.cdpy.dw.create_vw(cluster_id=self.cluster_id,
                               dbc_id=self.dbc_id, vw_type=self.vw_type, name=self.name,
                               template=self.template, autoscaling_min_cluster=self.autoscaling_min_cluster,
                               autoscaling_max_cluster=self.autoscaling_max_cluster,
                               common_configs=self.common_configs, application_configs=self.application_configs,
                               ldap_groups=self.ldap_groups, enable_sso=self.enable_sso, tags=self.tags)
                            if self.wait:
                                self.target = self.cdpy.sdk.wait_for_state(
                                    describe_func=self.cdpy.dw.describe_vw,
                                    params=dict(cluster_id=self.cluster_id, vw_id=self.name),
                                    state='Running', delay=self.delay, timeout=self.timeout
                                )
                            else:
                                self.target = self.cdpy.dw.describe_vw(cluster_id=self.cluster_id, vw_id=self.vw_id)
                            self.vws.append(self.target)
                    else:
                        self.module.fail_json(msg="State %s is not valid for this module" % self.state)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            cluster_id=dict(required=True, type='str', aliases=['cluster_id']),
            dbc_id=dict(required=False, type='str', aliases=['dbc_id']),
            vw_type = dict(required=False, type='str', aliases=['vw_type']),
            name = dict(required=True, type='str', aliases=['name']),
            template=dict(required=False, type='str', aliases=['template']),
            autoscaling_min_cluster=dict(required=False, type='int', aliases=['autoscaling_min_cluster']),
            autoscaling_max_cluster=dict(required=False, type='int', aliases=['autoscaling_max_cluster']),
            common_configs=dict(required=False, type='dict', aliases=['common_configs']),
            application_configs=dict(required=False, type='dict', aliases=['application_configs']),
            ldap_groups=dict(required=False, type='list', aliases=['ldap_groups']),
            enable_sso=dict(required=False, type='bool', aliases=['enable_sso']),
            tags=dict(required=False, type='dict', aliases=['tags']),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            wait = dict(required=False, type='bool', default=True),
            delay = dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout = dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        supports_check_mode=True
    )

    result = DwVw(module)
    output = dict(changed=False, vws=result.vws)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
