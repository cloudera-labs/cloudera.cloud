#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
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
    - Gathers information about CDP Public IAM role or roles
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
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
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
sdk_out:
  description: Returns the captured API HTTP log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured API HTTP log.
  returned: when supported
  type: list
  elements: str
"""

from typing import Any, Dict

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class IAMRoleInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["crn"],
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")

        # Initialize the return values
        self.roles = []

    def process(self):
        client = CdpIamClient(api_client=self.api_client)
        result = client.list_roles(role_names=self.name)
        self.roles = [
            camel_dict_to_snake_dict(role) for role in result.get("roles", [])
        ]


def main():
    result = IAMRoleInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        roles=result.roles,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
