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
module: freeipa_info
short_description: Gather information about FreeIPA 
description:
    - Gather information about FreeIPA
author:
  - "Webster Mudge (@wmudge)"
  - "Jim Enright (@jenright)"
requirements:
  - cdpy
options:
  name:
    description:
      - The FreeIPA environment specified will be described
    type: str
    required: True
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List FreeIPA information about a named Environment
- cloudera.cloud.freeipa_info:
    name: example-environment
'''

RETURN = r'''
environments: 
  description: The information about the named Environment or Environments
  type: dict
  returned: on success
  elements: complex
  contains:
    environmentCrn:
      description: CDP CRN value for the Environment.
      returned: always
      type: str
    environmentName:
      description: Name of the Environment.
      returned: always
      type: str
      sample: a-cdp-environment-name
    instances:
      description: Details about the instances.
      returned: always
      type: list
      elements: dict
      contains:
        id:
            description: The identifier of the instance.
            returned: always
            type: str
            sample: i-00b58f27be
        state:
            description: The state of the instance.
            returned: always
            type: str
            sample: CREATED
        hostname:
            description: The hostname of the instance.
            returned: always
            type: str
            sample: ipaserver0.a-cdp-environment-name.example.site
        issues:
            description: Details of any issues encountered with server.
            returned: always
            type: list
            sample: []
'''


class FreeIPAInfo(CdpModule):
    def __init__(self, module):
        super(FreeIPAInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')

        # Initialize return values
        self.freeipa = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:
          self.freeipa = self.cdpy.sdk.call(svc='environments', func='get_freeipa_status', environmentName=self.name)     


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['environment'])
        ),
        supports_check_mode=True
    )

    result = FreeIPAInfo(module)
    output = dict(changed=False, environments=result.freeipa)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)

if __name__ == '__main__':
    main()
