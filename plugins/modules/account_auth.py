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

DOCUMENTATION = '''
---
module: account_auth
short_description: Gather and set authentication details for a CDP Account
description:
  - Gather and set information for a CDP account.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  enable_sso:
    description:
      - Flag to enable or disable interactive login using the Cloudera SSO for the account.
      - When disabled, only users who are designated account administrators will be able to use Cloudera SSO to 
            login interactively to the account.
      - All other users will only be able to login interactively using other SAML providers defined for the account.
    type: bool
    required: False
    aliases:
      - sso
      - enable_cloudera_sso
  password_lifetime:
    description:
      - The maximum lifetime of workload passwords for the account, in days.
      - If set to C(0), passwords never expire.
      - Changes to the workload password lifetime only affect passwords that are set after the policy has been updated.
    type: int
    required: False
    aliases:
      - workload_password_lifetime
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = '''
# Note: These examples do not set authentication details.

# Disable Cloudera SSO login for all non-admin users
- cloudera.cloud.account_auth:
    disable_sso: yes

# Set the password expiration to 7 days
- cloudera.cloud.account_auth:
    password_lifetime: 7
'''

RETURN = '''
---
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
'''


class AccountAuthentication(CdpModule):
    def __init__(self, module):
        super(AccountAuthentication, self).__init__(module)

        # Set variables
        self.enable_sso = self._get_param('enable_sso')
        self.password_lifetime = self._get_param('password_lifetime')

        # Initialize the return values
        self.account = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.account = self.cdpy.iam.get_account()
        if self.account is None:
            self.module.fail_json(msg="Unable to retrieve CDP Account Information")

        if not self.module.check_mode:
            if self.enable_sso is not None and self.enable_sso != self.account['clouderaSSOLoginEnabled']:
                self.cdpy.iam.set_cloudera_sso(self.enable_sso)
                self.changed = True

            if self.password_lifetime is not None:
                if self.password_lifetime != self.account['workloadPasswordPolicy']['maxPasswordLifetimeDays']:
                    self.cdpy.iam.set_password_lifetime(self.password_lifetime)
                    self.changed = True

        if self.changed:
            self.account = self.cdpy.iam.get_account()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            enable_sso=dict(required=False, type='bool', aliases=['sso', 'enable_cloudera_sso']),
            password_lifetime=dict(required=False, type='int', no_log=False, aliases=['workload_password_lifetime'])
        ),
        supports_check_mode=True
    )

    result = AccountAuthentication(module)

    output = dict(
        changed=result.changed,
        account=result.account,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
