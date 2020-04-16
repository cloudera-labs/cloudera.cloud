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
module: env_cred_info
short_description: Gather information about CDP Credentials
description:
  - Gather information about CDP Credentials using the CDP SDK.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, the module will describe the found Credential. If the Credential is not found, the module
        will return an empty dictionary.
      - If no name is provided, the module will list all found Credentials. If no Credentials are found, the module will
        return an empty list.
    type: str
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Gather information about all Credentials
- cloudera.cloud.env_cred_info:

# Gather information about a named Credential
- cloudera.cloud.env_cred_info:
    name: example-credential
'''

RETURN = r'''
credentials:
    description: Returns an array of objects for the named Credential or all Credentials.
    returned: always
    type: complex
    contains:
        cloudPlatform:
            description: The name of the cloud provider for the Credential.
            returned: always
            type: str
            sample: AWS
        credentialName:
            description: The name of the Credential.
            returned: always
            type: str
            sample: example-credential
        crn:
            description: The CDP CRN value derived from the cross-account Role ARN used during creation.
            returned: always
            type: str
            sample: crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:61eb5b97-226a-4be7-b56d-795d18a043b5
        description:
            description: The description of the Credential.
            returned: when supported
            type: str
            sample: An example Credential
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


class EnvironmentCredentialInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentCredentialInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')

        # Initialize the return values
        self.credentials = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:
            cred = self.cdpy.environments.describe_credential(self.name)
            if cred is not None:
                self.credentials.append(cred[0])
        else:
            self.credentials = self.cdpy.environments.list_credentials()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['credential'])
        ),
        supports_check_mode=True
    )

    result = EnvironmentCredentialInfo(module)

    output = dict(
        changed=False,
        credentials=result.credentials,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
