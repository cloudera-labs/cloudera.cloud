#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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

DOCUMENTATION = """
module: account_cred_info
short_description: Gather information about Account prerequisites for CDP Credentials
description:
  - Gather prerequisites information from the Account for creating CDP Credentials using the CDP SDK.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  cloud:
    description:
      - Designates the cloud provider for the credential prerequisites.
    type: str
    required: True
    choices:
      - aws
      - azure
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = """
# Note: These examples do not set authentication details.

# Gather information about the AWS account credential prerequisites
- cloudera.cloud.account_cred_info:
    cloud: aws
"""

RETURN = """
prerequisites:
    description: Returns a dictionary of the specific cloud provider prerequisites for Credentials
    returned: always
    type: dict
    contains:
        account_id:
            description: The account identifier for the CDP installation.
            returned: always
            type: str
            sample: 3875500000000
        external_id:
            description: The AWS cross-account identifier for the CDP installation.
            returned: when supported
            type: str
            sample: 32b18f82-f868-414f-aedc-b3ee137560e3
        policy:
            description: The policy definition, returned as a base64 string.
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
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class AccountCredentialInfo(CdpModule):
    def __init__(self, module):
        super(AccountCredentialInfo, self).__init__(module)

        # Set variables
        self.cloud = self._get_param("cloud")

        # Initialize the return values
        self.prerequisites = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if not self.module.check_mode:
            result = self.cdpy.environments.get_credential_prerequisites(self.cloud)

            if self.cloud.lower() == "aws":
                self.prerequisites.update(
                    external_id=result["aws"]["externalId"],
                    policy=result["aws"]["policyJson"],
                )
            else:
                self.module.fail_json(msg="Azure not yet supported")

            self.prerequisites.update(account_id=result["accountId"])


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            cloud=dict(
                required=True,
                type="str",
                aliases=["cloud_platform"],
                choices=["aws", "azure"],
            ),
        ),
        supports_check_mode=True,
    )

    result = AccountCredentialInfo(module)

    output = dict(
        changed=False,
        prerequisites=result.prerequisites,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
