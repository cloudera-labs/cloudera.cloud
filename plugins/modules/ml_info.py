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
module: ml_info
short_description: Gather information about CDP ML Workspaces
description:
    - Gather information about CDP ML Workspaces
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that ML Workspace will be described.
      - C(environment) must be provided if using name to retrieve a Workspace
    type: str
    required: False
    aliases:
      - workspace
  environment:
    description:
      - The name of the Environment in which to find and describe the ML Workspaces.
      - Required with C(name) to retrieve a Workspace
    type: str
    required: False
    aliases:
      - env
  crn:
    description:
      - The CRN of the Workspace to describe.
    type: str
    required: False
    aliases:
      - workspace_crn
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all ML Workspaces
- cloudera.cloud.ml_info:

# Gather detailed information about a named Workspace
- cloudera.cloud.ml_info:
    name: example-workspace
    env: example-environment

# Gather detailed information about a named Workspace using a CRN
- cloudera.cloud.ml_info:
    crn: example-workspace-crn
'''

RETURN = r'''
---
workspaces:
  description: The information about the named Workspace or Workspaces
  type: list
  returned: always
  elements: complex
  contains:
    instanceName:
      description: The name of the workspace.
      returned: always
      type: str
    environmentName:
      description: The name of the workspace's environment.
      returned: always
      type: str
    instanceStatus:
      description: The workspace's current status.
      returned: always
      type: str
    instanceUrl:
      description: URL of the workspace's user interface.
      returned: always
      type: str
    environmentCrn:
      description: CRN of the environment.
      returned: always
      type: str
    crn:
      description: The CRN of the workspace.
      returned: always
      type: str
    k8sClusterName:
      description: The Kubernetes cluster name.
      returned: always
      type: str
    creatorCrn:
      description: The CRN of the creator of the workspace.
      returned: always
      type: str
    version:
      description: The version of Cloudera Machine Learning that  was  installed on the workspace.
      returned: always
      type: str
    httpsEnabled:
      description: Indicates   if   HTTPs  communication  was  enabled  on  this workspace when provisioned.
      returned: always
      type: bool
    filesystemID:
      description: A filesystem ID referencing the filesystem that  was  created on the cloud provider environment that this workspace uses.
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform of the environment that was used to create this workspace.
      returned: always
      type: str
    monitoringEnabled:
      description: If usage monitoring is enabled or not on this workspace.
      returned: always
      type: bool
    loadBalancerIPWhitelists:
      description: The whitelist of ips for loadBalancer.
      returned: always
      type: array
    creationDate:
      description: Creation date of workspace.
      returned: always
      type: str
    failureMessage:
      description: Failure  message  from  the  most  recent  failure  that  has occurred during workspace provisioning.
      returned: during failure
      type: str
    healthInfoLists:
      description: The health info information of the workspace.
      type: list
      contains:
        HealthInfo:
          description: Healthinfo  object  contains  the health information of a resource.
          type: array
          returned: always
          contains:
            resourceName:
              description: The resource name being checked.
              returned: always
              type: str
            isHealthy:
              description: The boolean that indicates the health status.
              returned: always
              type: bool
            updatedAt:
              description: The unix timestamp for the heartbeat.
              returned: always
              type: str
            message:
              description: The message to show for the health info.
              returned: always
              type: str
            details:
              description: The detail of the health info.
              returned: always
              type: array
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


class MLInfo(CdpModule):
    def __init__(self, module):
        super(MLInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('environment')
        self.crn = self._get_param('crn')

        # Initialize return values
        self.workspaces = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if (self.name and self.env) or self.crn:  # Note that both None and '' will trigger this
            workspace_single = self.cdpy.ml.describe_workspace(name=self.name, env=self.env, crn=self.crn)
            if workspace_single is not None:
                self.workspaces.append(workspace_single)
        else:
            self.workspaces = self.cdpy.ml.describe_all_workspaces(self.env)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['workspace']),
            environment=dict(required=False, type='str', aliases=['env']),
            crn=dict(required=False, type='str', aliases=['workspace_crn'])
        ),
        supports_check_mode=True,
        required_by={
            'name': ('environment')
        }
    )

    result = MLInfo(module)
    output = dict(changed=False, workspaces=result.workspaces)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
