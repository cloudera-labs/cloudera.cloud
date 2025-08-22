#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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
module: iam_role_info
short_description: Gather information about CDP Public IAM roles
description:
    - Gathers information about  CDP Public IAM role or roles
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "3.0.0"
options:
  name:
    description:
      - A list of Role CRNs or a single role's CRN.
      - If no CRNs are provided, all Roles are returned.
    type: list
    elements: str
    required: False
    aliases:
      - crn
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Retrieve the details about all roles
  cloudera.cloud.iam_role_info:

- name: Gather information about a specific role
  cloudera.cloud.iam_role_info:
    name: crn:iam:us-east-1:cm:role:ClassicClustersCreator

- name: Gather information about specific roles
  cloudera.cloud.iam_role_info:
    name:
      - crn:iam:us-east-1:cm:role:ClassicClustersCreator
      - crn:iam:us-east-1:cm:role:DFCatalogAdmin
"""

RETURN = r"""
roles:
  description: Retrieve details about selected IAM Role or Roles
  type: list
  returned: always
  elements: dict
  contains:
    crn:
      description: The CRN of the IAM role.
      returned: always
      type: str
    policies:
      description: List of policy rights assigned to the role.
      returned: always
      type: list
      elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class IAMRoleInfo(CdpModule):
    def __init__(self, module):
        super(IAMRoleInfo, self).__init__(module)

        # Set Variables
        self.name = self._get_param("name")

        # Initialize the return values
        self.role_info = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.role_info = self.cdpy.iam.list_roles(self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="list", elements="str", aliases=["crn"]),
        ),
        supports_check_mode=True,
    )

    result = IAMRoleInfo(module)

    output = dict(
        changed=False,
        roles=result.role_info,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
