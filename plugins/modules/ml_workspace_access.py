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
from ..module_utils.cdp_common import CdpModule


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ml_workspace_access
short_description: Grant and revoke user access to CDP Machine Learning Workspaces
description:
    - Grant and revoke user access to CDP Machine Learning Workspaces
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the ML Workspace
    type: str
    required: True
    aliases:
      - workspace
  environment:
    description:
      - The name of the Environment for the ML Workspace
    type: str
    required: True
    aliases:
      - env
  user:
    description:
      - The cloud provider identifier for the user.
      - For C(AWS), this is the User ARN.
    type: str
    required: True
    aliases:
      - identifier
  state:
    description:
      - The declarative state of the access to the ML Workspace
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Grant access for user (and register the output to capture the kubeconfig)
- cloudera.cloud.ml_workspace_access:
    name: ml-example
    env: cdp-env
    user: some-cloud-provider-specific-id
  register: access_output

# Revoke access for user
- cloudera.cloud.ml_workspace_acces:
    name: ml-k8s-example
    env: cdp-env
    user: some-cloud-provider-specific-id
    state: absent
'''

RETURN = r'''
---
workspace:
  description: The information about the user's access to the ML Workspace
  type: dict
  returned: on success
  contains:
    kubeconfig:
      description: The kubeconfig file as a string
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


class MLWorkspaceAccess(CdpModule):
    def __init__(self, module):
        super().__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('environment')
        self.user = self._get_param('user')
        self.state = self._get_param('state')
        
        # Initialize return values
        self.access = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):        
        existing = self.cdpy.ml.list_workspace_access(
            name=self.name, env=self.env)

        # If the access exists
        if self.user in existing:
            # Revoke
            if self.state == 'absent':
                if not self.module.check_mode:
                    self.changed = True
                    self.cdpy.ml.revoke_workspace_access(
                      name=self.name, env=self.env, identifier=self.user
                    )
            # Reinstate to get the kubeconfig
            else:
              self.module.warn(
                    "Refreshing access for user %s in ML Workspace, %s" % (self.user, self.name))
              if not self.module.check_mode:
                  self.changed = True
                  self.cdpy.ml.revoke_workspace_access(
                    name=self.name, env=self.env, identifier=self.user
                  )
                  self.access = self.cdpy.ml.grant_workspace_access(
                    name=self.name, env=self.env, identifier=self.user
                  )
        # Else the access does not exist
        else:
            if self.state == 'absent':
                self.module.log(
                    "User %s absent in ML Workspace %s" % (self.user, self.name))
            # Grant
            else:
                if not self.module.check_mode:
                  self.changed = True
                  self.access = self.cdpy.ml.grant_workspace_access(
                    name=self.name, env=self.env, identifier=self.user
                  )

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['workspace']),
            environment=dict(required=True, type='str', aliases=['env']),
            user=dict(required=True, type='str', aliases=['identifier']),
            state=dict(required=False, type='str', choices=[
                       'present', 'absent'], default='present')
        ),
        supports_check_mode=True
    )

    result = MLWorkspaceAccess(module)
    output = dict(changed=result.changed, workspace=result.access)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
