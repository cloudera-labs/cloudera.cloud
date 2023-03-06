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
module: df_deployment_info
short_description: Gather information about CDP DataFlow Deployments
description:
    - Gather information about CDP DataFlow Deployments
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, the DataFlow Deployment with this name will be described
      - Mutually exclusive with the crn argument
    type: str
    required: False
  crn:
    description:
      - If a crn is provided, that DataFlow Deployment will be described
      - Must be the string CRN of the deployment object
      - Mutually exclusive with the name argument
    type: str
    aliases:
      - dep_crn
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all DataFlow Deployments
- cloudera.cloud.df_deployment_info:

# Gather detailed information about a named DataFlow Deployment using a name
- cloudera.cloud.df_deployment_info:
    name: crn:cdp:df:region:tenant-uuid4:deployment:deployment-uuid4/deployment-uuid4
'''

RETURN = r'''
---
deployments:
  description: The information about the named DataFlow Deployment or DataFlow Deployments
  type: list
  returned: always
  elements: dict
  contains:
    crn:
      description: The DataFlow Deployment's CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Deployment's name.
      returned: always
      type: str
    status:
      description: The status of a DataFlow deployment.
      returned: always
      type: dict
      contains:
        state:
          description: The state of the Deployment.
          returned: always
          type: str
        detailedState:
          description: The state of the Deployment.
          returned: always
          type: str
        message:
          description: A status message for the Deployment.
          returned: always
          type: str
    service:
      description: Metadata about the parent DataFlow service.
      returned: always
      type: dict
      contains:
        crn:
          description: The CRN of the parent service.
          returned: always
          type: str
        name:
          description: The name of the parent environment.
          returned: always
          type: str
        cloudProvider:
          description: The cloud provider for the parent environment.
          returned: always
          type: str
        region:
          description: The region within the parent environment cloud provider.
          returned: always
          type: str
        environmentCrn:
          description: The CDP parent Environment CRN.
          returned: always
          type: str
    updated:
      description: Timestamp of the last time the deployment was modified.
      returned: always
      type: int
    clusterSize:
      description: The initial size of the deployment.
      returned: always
      type: str
    flowVersionCrn:
      description: The deployment's current flow version CRN.
      returned: always
      type: str
    flowCrn:
      description: The deployment's current flow CRN.
      returned: always
      type: str
    nifiUrl:
      description: The url to open the deployed flow in NiFi.
      returned: always
      type: str
    autoscaleMaxNodes:
      description: The maximum number of nodes that the deployment can scale up to, or null if autoscaling is not enabled for this deployment.
      returned: always
      type: complex
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
      type: complex
    autoscalingEnabled:
      description: Whether or not to autoscale the deployment.
      returned: always
      type: bool
    autoscaleMinNodes:
      description: The minimum number of nodes that the deployment will allocate. May only be specified when autoscalingEnabled is true.
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
      description: The static number of nodes that the deployment will allocate. May only be specified when autoscalingEnabled is false.
      returned: always
      type: int
    dfxLocalUrl:
      description: Base URL to the DFX Local instance running this deployment.
      returned: always
      type: string
    lastUpdatedByName:
      description: The name of the person who last updated the deployment.
      returned: always
      type: string
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


class DFDeploymentInfo(CdpModule):
    def __init__(self, module):
        super(DFDeploymentInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.crn = self._get_param('crn')

        # Initialize return values
        self.deployments = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.deployments = self.cdpy.df.list_deployments(dep_crn=self.crn, name=self.name, described=True)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str'),
            crn=dict(required=False, type='str', aliases=['dep_crn'])
        ),
        supports_check_mode=True,
        mutually_exclusive=[('name', 'crn')]
    )

    result = DFDeploymentInfo(module)
    output = dict(changed=False, deployments=result.deployments)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
