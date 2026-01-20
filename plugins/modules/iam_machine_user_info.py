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
module: iam_machine_user_info
short_description: Gather information about CDP Public IAM machine users
description:
    - Gather information about CDP Public IAM machine user or machine users
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "3.2.0"
options:
  name:
    description:
      - A list of machine user names or CRNs or a single machine user name/CRN.
      - If no machine user name or CRN is provided, all machine users are returned.
    type: list
    elements: str
    required: False
    aliases:
      - machine_user_name
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

 - name: Gather information about all Machine Users
   cloudera.cloud.iam_machine_user_info:

 - name: Gather information about a named Machine User
   cloudera.cloud.iam_machine_user_info:
     name: example-machine-user-01

 - name: Gather information about several named Machine Users
   cloudera.cloud.iam_machine_user_info:
     name:
       - example-machine-user-01
       - example-machine-user-02
       - example-machine-user-03
"""

RETURN = r"""
machine_users:
  description:
    - Returns a list of machine user records.
    - Each record represents a CDP IAM machine user and its details.
  type: list
  returned: always
  elements: dict
  contains:
    creation_date:
      description: The date when this machine user record was created.
      returned: on success
      type: str
      sample: 2020-07-06T12:24:05.531000+00:00
    crn:
      description: The CRN of the machine user.
      returned: on success
      type: str
    machine_user_name:
      description: The machine user name.
      returned: on success
      type: str
      sample: example-machine-user-01
    status:
      description: The current status of the machine user (ACTIVE or CONTROL_PLANE_LOCKED_OUT).
      returned: when supported
      type: str
      sample: ACTIVE
    workload_password_details:
      description: Information about the workload password for the machine user.
      returned: when supported
      type: dict
    workload_username:
      description: The username used in all the workload clusters of the machine user.
      returned: when supported
      type: str
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


class IAMMachineUserInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["machine_user_name"],
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")

        # Initialize the return values
        self.machine_users = []

    def process(self):
        client = CdpIamClient(api_client=self.api_client)
        result = client.list_machine_users(machine_user_names=self.name)
        self.machine_users = [
            camel_dict_to_snake_dict(machine_user)
            for machine_user in result.get("machineUsers", [])
        ]


def main():
    result = IAMMachineUserInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        machine_users=result.machine_users,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
