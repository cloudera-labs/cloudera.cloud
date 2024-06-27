#!/usr/bin/env python
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: env_auth
short_description: Set authentication details for the current CDP user
description:
  - Set authentication details for the current CDP user for one or more Environments.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The targeted environment(s).
      - If no environment is specified, all environments are affected.
    type: list
    elements: str
    required: False
    aliases:
      - environment
  password:
    description:
      - The workload password to set for the current CDP user.
      - Passwords must be a minimum of 8 characters and no more than 64 characters and should be a combination of
            upper case, lower case, digits, and special characters.
      - Set to 'no_log' within Ansible.
    type: str
    required: True
    aliases:
      - workload_password
  strict:
    description:
      - A flag to ignore I(Conflict) errors on password updates.
    type: bool
    required: False
    default: True
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Set the workload user password for the current CDP user on all environments
- cloudera.cloud.env_auth:
    password: Cloudera@2020!

# Set the workload user password for the current CDP user on selected environments
- cloudera.cloud.env_auth:
    name:
      - one-environment
      - two-environment
    password: Cloudera@2020!
"""

RETURN = r"""
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


class EnvironmentAuthentication(CdpModule):
    def __init__(self, module):
        super(EnvironmentAuthentication, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.password = self._get_param("password")

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if not self.module.check_mode:
            resp = self.cdpy.environments.set_password(self.password, self.name)
            if resp:
                self.changed = True


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(
                required=False, type="list", elements="str", aliases=["environment"]
            ),
            password=dict(
                required=True, type="str", no_log=True, aliases=["workload_password"]
            ),
        ),
        supports_check_mode=True,
    )

    result = EnvironmentAuthentication(module)

    output = dict(changed=result.changed)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
