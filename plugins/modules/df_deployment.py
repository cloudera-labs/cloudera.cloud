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
#TODO: Update docs
DOCUMENTATION = r'''
---
module: df_deployment
short_description: Enable or Disable CDP DataFlow Deployments
description:
    - Enable or Disable CDP DataFlow Deployments
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the Deployed Flow, or Flow to be Deployed
    type: str
    required: False
  dep_crn:
    description: 
      - The CRN of the Deployed Flow to be terminated
      - Required if C(name) is not supplied for termination
    type: str
    required: False
  df_crn:
    description:
      - The CRN of the Dataflow Service
      - Required if the C(df_name) is not supplied
    type: str
    required: False
  df_name:
    description:
      - The Name of the Dataflow Service
      - Required if C(df_crn) is not supplied
    type: str
    required: False
  flow_ver_crn:
    description:
      - The CRN of the specific Version of the Flow to be Deployed
      - Required for creating a Deployment if C(flow_name) is not supplied
    type: str
    required: False
  flow_name:
    description:
      - The Name of the Flow to be Deployed
      - Required for creating a Deployment if C(flow_ver_crn) is not supplied
    type: str
    required: False
  flow_ver:
    description:
      - The Version number of the Flow to be Deployed
      - If not supplied, the latest version available will be Deployed
    type: int
    required: False
  size:
    description:
      - The Size of the Pod for the Flow to be Deployed into
    type: str
    default: SMALL
    choices:
      - EXTRA_SMALL
      - SMALL
      - MEDIUM
      - LARGE
    required: False
    aliases:
      - size_name
  static_node_count:
    description:
      - The number of nodes to build the Pod on if not using Autoscaling
    type: int
    required: False
    default: 1
  autoscale:
    description:
      - Whether to use autoscaling of pods for this Deployment
    type: bool
    required: False
    default: False
  autoscale_nodes_min:
    description:
      - The minimum number of nodes to use when Autoscaling
    type: int
    required: False
    default: 1
  autoscale_nodes_max:
    description:
      - The maximum number of nodes to use when Autoscaling
    type: int
    required: False
    default: 3
  nifi_ver:
    description:
      - The specific version of NiFi to use in the Deployment
    type: str
    required: False
    default: latest
  wait:
    description:
      - Flag to enable internal polling to wait for the Dataflow Service to achieve the declared state.
      - If set to C(FALSE), the module will return immediately.
    type: bool
    required: False
    default: True
  autostart_flow:
    description:
      - Whether to automatically start the Flow once Deployment is complete
    type: bool
    required: False
    default: True
  parameter_groups:
    description:
      - Definitions of Parameters to apply to the Deployed Flow
    type: list
    required: False
  kpis:
    description:
      - Definitions of KPIs to apply to the Deployed Flow
    type: list
    required: False
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

# Deploy a Dataflow with defaults
- cloudera.cloud.df_deployment:
    name: my-flow

# Remove a Dataflow Service with Async wait
- cloudera.cloud.df_deployment:
    name: my-flow-name
    df_name: my-env-name
    state: absent
    wait: yes
  async: 3600
  poll: 0
  register: __my_teardown_request

'''

RETURN = r'''
---
deployment:
  description: The information about the named DataFlow Deployment
  type: dict
  returned: always
  contains:
    crn:
      description: The deployment CRN.
      returned: always
      type: str
    name:
      description: The deployment name.
      returned: always
      type: str
    status:
      description: The status of a DataFlow enabled environment.
      returned: always
      type: dict
      contains:
        detailedState:
          description: The detailed state that the deployment is currently in.
          returned: always
          type: str
        message:
          description: A status message for the environment.
          returned: always
          type: str
        state:
          description: The state that the deployment is currently in
          returned: always
          type: str
    service:
      description: Metadata about the DataFlow service.
      returned: always
      type: dict
      contains:
        crn:
          description: The crn of the DataFlow service.
          returned: always
          type: str
        name:
          description: The name of the CDP Environment.
          returned: always
          type: str
        cloudProvider:
          description: The cloud provider
          returned: always
          type: str
        region:
          description: The region within the cloud provider
          returned: always
          type: str
        environmentCrn:
          description: The CDP Environment CRN
          returned: always
          type: str
    updated:
      description: Timestamp of the last time the deployment was modified.
      returned: always
      type: int
    clusterSize:
      description:  The initial size of the deployment.
      returned: always
      type: str
    flowVersionCrn:
      description: The deployment's current flow version CRN.
      returned: always
      type: str
    flowCrn:
      description: The deployment's current flow CRN.
      returned: always
      type: int
    nifiUrl:
      description: The url to open the deployed flow in NiFi.
      returned: always
      type: str
    autoscaleMaxNodes:
      description:  The maximum number of nodes that the deployment can scale up to, or null if autoscaling is not enabled for this deployment.
      returned: always
      type: int
    flowName:
      description: The name of the flow.
      returned: always
      type: str
    flowVersion:
      description: The version of the flow.
      returned: always
      type: int
    currentNodeCount:
      description: The current node count.
      returned: always
      type: int
    deployedByCrn:
      description: The actor CRN of the person who deployed the flow.
      returned: always
      type: str
    deployedByName:
      description: The name of the person who deployed the flow.
      returned: always
      type: str
    autoscalingEnabled:
      description: Whether or not to autoscale the deployment.
      returned: always
      type: bool
    autoscaleMinNodes:
      description: 
        - The  minimum  number of nodes that the deployment will allocate.
        - May only be specified when autoscalingEnabled is true.
      returned: always
      type: int
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning.
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error.
      returned: always
      type: int
    staticNodeCount:
      description: 
        - The static number of nodes that the  deployment  will  allocate.
        - May only be specified when autoscalingEnabled is false.
      returned: always
      type: int
    dfxLocalUrl:
      description: Base URL to the dfx-local instance running this deployment.
      returned: always
      type: str
    lastUpdatedByName:
      description: The name of the person who last updated the deployment.
      returned: always
      type: str
    configurationVersion:
      description: The version of the configuration for this deployment.
      returned: always
      type: int
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


class DFDeployment(CdpModule):
    def __init__(self, module):
        super(DFDeployment, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.dep_crn = self._get_param('dep_crn')
        self.df_crn = self._get_param('df_crn')
        self.df_name = self._get_param('df_name')
        self.flow_ver_crn = self._get_param('flow_ver_crn')
        self.flow_name = self._get_param('flow_name')
        self.flow_ver = self._get_param('flow_ver')
        self.size = self._get_param('size')
        self.static_node_count = self._get_param('static_node_count')
        self.autoscale_enabled = self._get_param('autoscale_enabled')
        self.autoscale_nodes_min = self._get_param('autoscale_nodes_min')
        self.autoscale_nodes_max = self._get_param('autoscale_nodes_max')
        self.nifi_ver = self._get_param('nifi_ver')
        self.autostart_flow = self._get_param('autostart_flow')
        self.parameter_groups = self._get_param('parameter_groups')
        self.kpis = self._get_param('kpis')

        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Additional checks that can't be coded using the AnsibleModule rules
        if self.state == 'absent' and self.dep_crn is None and self.df_crn is None and self.df_name is None:
            self.module.fail_json(msg='name is specified but any of the following are missing: df_crn, df_name')

        # Initialize return values
        self.deployment = None
        self.changed = False

        # Initialize internal values
        self.target = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        # Prepare information
        if self.dep_crn is not None:
            self.target = self.cdpy.df.describe_deployment(dep_crn=self.dep_crn)
            self.df_crn = self.target['service']['crn']
        if self.df_crn is None:
            self.df_crn = self.cdpy.df.resolve_service_crn_from_name(self.df_name)
            if self.df_crn is None:
                self.module.fail_json(
                    msg="Either df_crn must be supplied or resolvable from df_name")
        if self.name is not None and self.df_crn is not None:
            self.target = self.cdpy.df.describe_deployment(df_crn=self.df_crn, name=self.name)
            if self.target is not None:
                self.dep_crn = self.target['crn']
        # Process execution
        if self.target is not None:
            # DF Deployment exists
            if self.state in ['absent']:
                # Existing Deployment to be removed
                if self.module.check_mode:
                    self.module.log(
                        "Check mode enabled, skipping termination of Deployment %s" % self.dep_crn)
                    self.deployment = self.target
                else:
                    self._terminate_deployment()
            elif self.state in ['present']:
                # Existing deployment to be retained
                self.module.warn(
                    "Dataflow Deployment already exists and configuration validation and reconciliation " +
                    "is not supported;" +
                    "to change a Deployment, explicitly terminate and recreate it or use the UI")
                if self.wait:
                    self.deployment = self._wait_for_deployed()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)
        else:
            # Deployment CRN not found in Tenant, and probably doesn't exist
            if self.state in ['absent']:
                # Deployment not found, and not wanted, return
                self.module.log(
                    "Dataflow Deployment not found in CDP Tenant %s" % self.dep_crn)
            elif self.state in ['present']:
                # create Deployment
                if not self.module.check_mode:
                    self._create_deployment()
                    if self.wait:
                        self.deployment = self._wait_for_deployed()
                else:
                    pass  # Check mode can return the described deployment
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

    def _create_deployment(self):
        if self.flow_ver_crn is None:
            # flow_name must be populated if flow_ver_crn is None
            self.flow_ver_crn = self.cdpy.df.get_version_crn_from_flow_definition(self.flow_name, self.flow_ver)
        self.deployment = self.cdpy.df.create_deployment(
            df_crn=self.df_crn,
            flow_ver_crn=self.flow_ver_crn,
            deployment_name=self.name,
            size_name=self.size,
            static_node_count=self.static_node_count,
            autoscale_enabled=self.autoscale_enabled,
            autoscale_nodes_min=self.autoscale_nodes_min,
            autoscale_nodes_max=self.autoscale_nodes_max,
            nifi_ver=self.nifi_ver,
            autostart_flow=self.autostart_flow,
            parameter_groups=self.parameter_groups,
            kpis=self.kpis,
        )
        self.changed = True

    def _wait_for_deployed(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.df.describe_deployment,
            params=dict(dep_crn=self.dep_crn, df_crn=self.df_crn, name=self.name),
            field=['status', 'state'], state=self.cdpy.sdk.STARTED_STATES,
            delay=self.delay, timeout=self.timeout
        )

    def _terminate_deployment(self):
        if self.target['status']['state'] in self.cdpy.sdk.REMOVABLE_STATES:
            self.deployment = self.cdpy.df.terminate_deployment(
                dep_crn=self.dep_crn
            )
            self.changed = True
        else:
            self.module.warn("Attempting to disable DataFlow Deployment but state %s not in Removable States %s"
                             % (self.target['status']['state'], self.cdpy.sdk.REMOVABLE_STATES))
        if self.wait:
            self.deployment = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.df.describe_deployment,
                params=dict(dep_crn=self.dep_crn), field=None,
                delay=self.delay, timeout=self.timeout
            )
        else:
            self.deployment = self.cdpy.df.describe_deployment(dep_crn=self.dep_crn)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(type='str'),
            df_crn=dict(type='str', default=None),
            df_name=dict(type='str', default=None),
            dep_crn=dict(type='str', default=None),
            flow_ver_crn=dict(type='str', default=None),
            flow_name=dict(type='str', default=None),
            flow_ver=dict(type='int', default=None),
            size=dict(type='str',
                           choices=['EXTRA_SMALL', 'SMALL', 'MEDIUM', 'LARGE'],
                           default='EXTRA_SMALL', aliases=['size_name']),
            static_node_count=dict(type='int', default=1),
            autoscale=dict(type='bool', default=False, aliases=['autoscale_enabled']),
            autoscale_nodes_min=dict(type='int', default=1),
            autoscale_nodes_max=dict(type='int', default=3),
            nifi_ver=dict(type='str', default=None),
            autostart_flow=dict(type='bool', default=True),
            parameter_groups=dict(type='list', default=None),
            kpis=dict(type='list', default=None),
            state=dict(type='str', choices=['present', 'absent'],
                       default='present'),
            wait=dict(type='bool', default=True),
            delay=dict(type='int', aliases=['polling_delay'], default=15),
            timeout=dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['dep_crn', 'df_crn', 'df_name'],
        ],
        required_if=[
            ['state', 'absent', ['dep_crn', 'name'], True],  # One of for termination
            ['state', 'present', ['flow_ver_crn', 'flow_name'], True],  # One of
            ['state', 'present', ['df_crn', 'df_name'], True],  # One of
            ['state', 'present', ['name']]
        ],
    )

    result = DFDeployment(module)
    output = dict(changed=result.changed, deployment=result.deployment)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
