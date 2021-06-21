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
module: df
short_description: Enable or Disable CDP DataFlow Services
description:
    - Enable or Disable CDP DataFlow Services
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  crn:
    description: The name or crn of the CDP Environment to host the Dataflow Service
    type: str
    required: True
    aliases:
      - name
      - env_crn
  state:
    description:
      - The declarative state of the Dataflow Service
    type: str
    required: False
    default: present
    choices:
      - present
      - enabled
      - absent
      - disabled
  nodes_min:
    description: The minimum number of kubernetes nodes needed for the environment.
      Note that the lowest minimum is 3 nodes.
    type: int
    default: 3
    required: False
    aliases:
      - min_k8s_node_count
  nodes_max:
    description: The maximum number of  kubernetes  nodes that environment may scale up under high-demand situations.
    type: int
    default: 3
    required: False
    aliases:
      - max_k8s_node_count
  public_loadbalancer:
    description: Indicates whether or not to use a public load balancer when deploying dependencies stack.
    type: bool
    required: False
    aliases:
      - use_public_load_balancer
  ip_ranges:
    description: The IP ranges authorized to connect to the Kubernetes API server
    type: list
    required: False
    aliases:
      - authorized_ip_ranges
  persist:
    description: Whether or not to retain the database records of related entities during removal.
    type: bool
    required: False
    default: False
  wait:
    description:
      - Flag to enable internal polling to wait for the Dataflow Service to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Dataflow Service to achieve the 
        declared state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Dataflow Service to achieve the 
        declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
notes:
  - This feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create a Dataflow Service
- cloudera.cloud.df:
    name: my-service
    nodes_min: 3
    nodes_max: 10
    public_loadbalancer: True
    ip_ranges: ['192.168.0.1/24']
    state: present
    wait: yes

# Remove a Dataflow Service with Async wait
- cloudera.cloud.df:
    name: my-service
    persist: False
    state: absent
    wait: yes
  async: 3600
  poll: 0
  register: __my_teardown_request

'''

RETURN = r'''
---
environments:
  description: The information about the named DataFlow Service or DataFlow Services
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description:  The DataFlow Service's parent environment CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Service's parent environment name.
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform of the environment.
      returned: always
      type: str
    region:
      description: The region of the environment.
      returned: always
      type: str
    deploymentCount:
      description: The deployment count.
      returned: always
      type: str
    minK8sNodeCount:
      description: The  minimum number of Kubernetes nodes that need to be provisioned in the environment.
      returned: always
      type: int
    maxK8sNodeCount:
      description:  The maximum number of kubernetes nodes that environment may scale up under high-demand situations.
      returned: always
      type: str
    status:
      description: The status of a DataFlow enabled environment.
      returned: always
      type: dict
      contains:
        state:
          description: The state of the environment.
          returned: always
          type: str
        message:
          description: A status message for the environment.
          returned: always
          type: str
    k8sNodeCount:
      description: The number of kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: int
    instanceType:
      description: The instance type of the kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: str
    dfLocalUrl:
      description: The URL of the environment local DataFlow application.
      returned: always
      type: str
    authorizedIpRanges:
      description: The authorized IP Ranges.
      returned: always
      type: list
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning.
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error.
      returned: always
      type: int
    clusterId:
      description: Cluster id of the environment.
      returned: if enabled
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


class DFService(CdpModule):
    def __init__(self, module):
        super(DFService, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.nodes_min = self._get_param('nodes_min')
        self.nodes_max = self._get_param('nodes_max')
        self.public_loadbalancer = self._get_param('public_loadbalancer')
        self.ip_ranges = self._get_param('ip_ranges')
        self.persist = self._get_param('persist')

        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.service = {}

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.name = self.cdpy.environments.resolve_environment_crn(self.name)
        self.target = self.cdpy.df.describe_environment(env_crn=self.name)

        if self.target is not None:
            # DF Database Entry exists
            if self.state in ['absent']:
                if self.module.check_mode:
                    self.service = self.target
                else:
                    if self.target['status']['state'] != 'NOT_ENABLED':
                        self.service = self.cdpy.df.disable_environment(
                            env_crn=self.name,
                            persist=self.persist
                        )
                        if self.wait:
                            self.service = self._wait_for_disabled()
                        else:
                            self.service = self.target
            elif self.state in ['present']:
                self.module.warn(
                    "Dataflow Service already enabled and configuration validation and reconciliation is not supported;" +
                    "to change a Dataflow Service, explicitly disable and recreate the Service or use the UI")
                if self.wait:
                    self.service = self._wait_for_enabled()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)
        else:
            # Environment does not have DF database entry, and probably doesn't exist
            if self.state in ['absent']:
                self.module.log(
                    "Dataflow Service %s already disabled in CDP Environment" % self.name)
            elif self.state in ['present']:
                # create DF Service
                if not self.module.check_mode:
                    self.service = self.cdpy.df.enable_environment(
                        env_crn=self.name,
                        authorized_ips=self.ip_ranges,
                        min_nodes=self.nodes_min,
                        max_nodes=self.nodes_max,
                        enable_public_ip=self.public_loadbalancer
                    )
                    if self.wait:
                        self.service = self._wait_for_enabled()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

    def _wait_for_enabled(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.df.describe_environment, params=dict(env_crn=self.name),
            field=['status', 'state'], state=self.cdpy.sdk.STARTED_STATES,
            delay=self.delay, timeout=self.timeout
        )

    def _wait_for_disabled(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.df.describe_environment, params=dict(env_crn=self.name), state=None,
            delay=self.delay, timeout=self.timeout
        )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['crn', 'env_crn']),
            nodes_min=dict(required=False, type='int', default=3, aliases=['min_k8s_node_count']),
            nodes_max=dict(required=False, type='int', default=3, aliases=['max_k8s_node_count']),
            public_loadbalancer=dict(required=False, type='bool', default=False, aliases=['use_public_load_balancer']),
            ip_ranges=dict(required=False, type='list', elements='str', default=list(),
                           aliases=['authorized_ip_ranges']),
            persist=dict(required=False, type='bool', default=False),
            state=dict(required=False, type='str', choices=['present', 'absent'],
                       default='present'),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        supports_check_mode=True,
    )

    result = DFService(module)
    output = dict(changed=False, service=result.service)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
