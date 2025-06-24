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
module: iam_resource_role_info
short_description: Gather information about CDP Public IAM resource roles
description:
    - Gather information about CDP Public IAM resource role or roles
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
options:
  name:
    description:
      - A list of Resource Role CRNs or a single role's CRN.
      - If no CRNs are provided, all Resource Roles are returned.
    type: list
    elements: str
    required: False
    aliases:
      - crn
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Gather information about all Resource Roles
- cloudera.cloud.iam_resource_role_info:

# Gather information about a named Resource Role
- cloudera.cloud.iam_resource_role_info:
    name: crn:altus:iam:us-west-1:altus:resourceRole:ODUser

# Gather information about several named Resource Roles
- cloudera.cloud.iam_resource_role_info:
    name:
      - crn:altus:iam:us-west-1:altus:resourceRole:DWAdmin
      - crn:altus:iam:us-west-1:altus:resourceRole:DWUser
"""

RETURN = r"""
resource_roles:
  description: The information about the named Resource Role or Roles
  type: list
  returned: always
  elements: dict
  contains:
    crn:
      description: The CRN of the resource role.
      returned: on success
      type: str
    rights:
      description: List of rights assigned to the group.
      returned: on success
      type: list
      elements: str
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

PAGE_SIZE = 50


class IAMResourceRoleInfo(CdpModule):
    def __init__(self, module):
        super(IAMResourceRoleInfo, self).__init__(module)

        # Set Variables
        self.name = self._get_param("name")

        # Initialize the return values
        self.info = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.info = self.cdpy.iam.list_resource_roles(self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="list", elements="str", aliases=["crn"]),
        ),
        supports_check_mode=True,
    )

    result = IAMResourceRoleInfo(module)

    output = dict(
        changed=False,
        resource_roles=result.info,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
