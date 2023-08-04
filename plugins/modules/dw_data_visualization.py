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
module: dw_data_visualization
short_description: Create or Delete CDP Data Visualization Instance
description:
    - Create or Delete CDP Data Visualization Instance
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
  - "Webster Mudge (@wmudge)"
  - "Ronald Suplina (@rsuplina)"
requirements:
  - cdpy
options:
  environment:
    description:
      - The name of the target environment.
      - Mutually exclusive with I(cluster_id).
    type: str
    aliases:
      - env
      - env_crn
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
      - Mutually exclusive with I(environment).
    type: str
  name:
    description: 
      - The name of the Data Visualization Instance.
      - This name must be unique, must have between 5 and 20 characters, and must contain only lowercase letters,
        numbers, and hyphens.
    type: str
  config:
    description:
      - User and Admin groups that can access the Data Visualization Instance.
      - "userGroups: List of user groups that have access to the instance. Example: ['group1', 'group2']"
      - "adminGroups: List of admin groups that have full control over the instance. Example: ['admin_group1', 'admin_group2']"
    type: dict
    suboptions:
      userGroups:
        description:
          - List of user groups that have access to the Data Visualization Instance.
          - Must be a list of strings, e.g., ['group1', 'group2'].
        type: list
        elements: str
      adminGroups:
        description:
          - List of admin groups that have full control over the Data Visualization Instance.
          - Must be a list of strings, e.g., ['admin_group1', 'admin_group2'].
        type: list
        elements: str
  state:
    description: The state of the Data Visualization Instance
    type: str
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Visualization Instance to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Visualization Instance to achieve the declared
        state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Visualization Instance to achieve the declared
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

# Create Data Visualization Instance
- cloudera.cloud.dw_data_visualization:
    environment: example-env
    name: example-name
    config:
      userGroups:  "[ example_user_group ]"
      adminGroups: "[ example_admin_group ]"
    state: present

# Delete Data Visualization Instance
- cloudera.cloud.dw_data_visualization:
    environment: example-env
    name: example-name
    config:
      userGroups:  "[ example_user_group ]"
      adminGroups: "[ example_admin_group ]"
    state: absent
'''

RETURN = r'''
---
cluster:
  description: Details for the Data Visualization Instance
  type: dict
  contains:
    creatorCrn:
      description: The CRN of the creator of the Data Visualization Instance.
      returned: always
      type: str
    id:
      description: The unique id of the Data Visualization instance
      returned: always
      type: str
    imageVersion:
      description: The current version of Data Visualization 
      returned: always
      type: str
    name:
      description: The name of the Data Visualization instance
      returned: always
      type: str
    size:
      description: The size of the Data Visualization instance
      returned: always
      type: str
    status:
      description: The status of the Data Visualization instance
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


class DwCluster(CdpModule):
    def __init__(self, module):
        super(DwCluster, self).__init__(module)

        # Set variables
        self.cluster_id = self._get_param('cluster_id')
        self.env = self._get_param('env')
        self.id = self._get_param('id')
        self.name = self._get_param('name')
        self.config = self._get_param('config')
        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.data_visualization = {}
        self.changed = False

        # Initialize internal values
        self.target = None
        self.cluster = None

    @CdpModule._Decorators.process_debug
    def process(self):
        # Check if Cluster exists
        if self.cluster_id is not None:
            self.cluster = self.cdpy.dw.describe_cluster(cluster_id=self.cluster_id)
        elif self.env is not None:
            env_crn = self.cdpy.environments.resolve_environment_crn(self.env)
            listing = self.cdpy.dw.list_clusters(env_crn)  # Always returns a list
            if len(listing) == 1:
                self.cluster = self.cdpy.dw.describe_cluster(cluster_id=listing[0]['id'])
            elif len(listing) == 0:
                self.cluster = None
            else:
                self.module.fail_json(msg="Received multiple (i.e. ambiguous) Clusters in Environment {}".format(
                    self.env))

        if not self.cluster:
            self.module.warn("No cluster found with id {} or in environment {}.".format(self.cluster_id, self.env))
            return

        # Retrieves target data visualization, if any
        if self.id:
            self.target = self.cdpy.dw.describe_data_visualization(cluster_id=self.cluster_id, data_viz_id=self.id)
        else:
            listing = self.cdpy.dw.list_data_visualizations(cluster_id=self.cluster['id'])
            listing = [v for v in listing
                       if (self.id is None or v['id'] == self.id)
                       and (self.name is None or v['name'] == self.name)]
            if len(listing) == 1:
                self.target = listing[0]
            elif len(listing) == 0:
                self.target = None
            else:
                self.module.fail_json(msg="Received multiple (i.e. ambiguous)"
                                          " Data Visualizations in Cluster {}".format(self.cluster['name']))

        if self.target is not None:
            if self.state == 'absent':
                if self.module.check_mode:
                    self.data_visualization = self.target
                else:
                    self.changed = True
                    self.cdpy.dw.delete_data_visualization(cluster_id=self.cluster['id'], data_viz_id=self.target['id'])
                    
                    if self.wait:
                        self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_data_visualization,
                            params=dict(cluster_id=self.cluster['id'], data_viz_id=self.target['id']),
                            field=None, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                        self.data_visualization = self.cdpy.dw.describe_data_visualization(
                            cluster_id=self.cluster['id'], data_viz_id=self.target['id'])
            elif self.state == 'present':
                if self.module.check_mode:
                    self.data_visualization = self.target
                else:
                    self.changed = True
                    self.cdpy.dw.update_data_visualization(cluster_id=self.cluster['id'], data_viz_id=self.target['id'],
                                                           config=self.config)

                    if self.wait:
                        self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                        self.target = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_data_visualization,
                            params=dict(cluster_id=self.cluster['id'], data_viz_id=self.target['id']),
                            state='Running', delay=self.delay, timeout=self.timeout
                        )
                self.cluster = self.target
        else:
            if self.state == 'absent':
                self.module.warn("Data Visualization {} already absent in Environment {}".format(self.name, self.env))
            elif self.state == 'present':
                if not self.module.check_mode:
                    self.changed = True
                    data_visualization_id = self.cdpy.dw.create_data_visualization(
                        cluster_id=self.cluster['id'],
                        name=self.name,
                        config=self.config,
                    )
                    if self.wait:
                        self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                        self.data_visualization = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_data_visualization,
                            params=dict(cluster_id=self.cluster['id'], data_viz_id=data_visualization_id),
                            state='Running', delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.data_visualization = self.cdpy.dw.describe_cluster(
                            cluster_id=self.name, data_viz_id=data_visualization_id)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            cluster_id=dict(type='str'),
            env=dict(type='str', aliases=['environment', 'env_crn']),
            id=dict(type='str'),
            name=dict(type='str'),
            config=dict(type='dict'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            wait=dict(type='bool', default=True),
            delay=dict(type='int', aliases=['polling_delay'], default=15),
            timeout=dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        mutually_exclusive=[
            ('cluster_id', 'env'),
            ('id', 'name'),
        ],
        required_if=[
            ('state', 'present', ('cluster_id', 'env'), True),
            ('state', 'present', ('name', 'config')),
            ('state', 'absent', ('cluster_id', 'env'), True),
            ('state', 'absent', ('name', 'id'), True),
        ],
        supports_check_mode=True
    )

    instance = DwCluster(module)
    instance.process()
    output = dict(changed=instance.changed, data_visualization=instance.data_visualization)

    if instance.debug:
        output.update(sdk_out=instance.log_out, sdk_out_lines=instance.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
