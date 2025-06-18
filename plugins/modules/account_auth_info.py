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

DOCUMENTATION = r"""
module: account_auth_info
short_description: Gather information about CDP Account authentication settings
description:
  - Gather information about the authentication settings for a CDP Account.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  debug:
    description:
      - Flag to capture and return the debugging log of the underlying CDP SDK.
      - If set, the log level will be set from ERROR to DEBUG.
    aliases:
      - debug_cdpsdk
    default: False
    type: bool
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Gather information about the Account authentication settings
- cloudera.cloud.account_auth_info:
"""

RETURN = r"""
account:
    description: Returns the authentication settings for the CDP Account
    returned: always
    type: dict
    contains:
        clouderaSSOLoginEnabled:
            description: Flag indicating whether interactive login using Cloudera SSO is enabled.
            returned: always
            type: bool
        workloadPasswordPolicy:
            description: Information about the workload password policy for an account.
            returned: always
            type: dict
            contains:
                maxPasswordLifetimeDays:
                    description: The max lifetime, in days, of the password. If '0', passwords never expire.
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
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class AccountAuthenticationInfo(CdpModule):
    def __init__(self, module):
        super(AccountAuthenticationInfo, self).__init__(module)

        # Initialize the return values
        self.account = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.account = self.cdpy.iam.get_account()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(), supports_check_mode=True
    )

    result = AccountAuthenticationInfo(module)

    output = dict(
        changed=False,
        account=result.account,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
