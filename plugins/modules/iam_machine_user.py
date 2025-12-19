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
module: iam_machine_user
short_description: Create, update, or destroy CDP IAM machine users
description:
    - Create, update, and destroy Cloudera Data Platform IAM machine users.
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "3.2.0"
options:
  name:
    description:
      - The name of the machine user.
      - The name must be unique, must have a maximum of 128 characters, and must contain only alphanumeric
            characters, "-", and "_".
      - Names are case-sensitive.
    type: str
    required: True
    aliases:
      - machine_user_name
  purge:
    description:
      - Flag to replace C(roles) and C(resource_roles) with their specified values.
    type: bool
    required: False
    default: False
  resource_roles:
    description:
      - A list of resource role assignments.
    type: list
    required: False
    elements: dict
    suboptions:
      resource:
        description:
          - The resource CRN for the rights assignment.
        type: str
        required: True
        aliases:
          - resource_crn
      role:
        description:
          - The resource role CRN to be assigned.
        type: str
        required: True
        aliases:
          - resource_role_crn
  roles:
    description:
      - A single role or list of roles assigned to the machine user.
      - The role must be identified by its full CRN.
    type: list
    elements: str
    required: False
  state:
    description:
      - The state of the machine user.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a machine user
- cloudera.cloud.iam_machine_user:
    name: my-machine-user

# Delete a machine user
- cloudera.cloud.iam_machine_user:
    state: absent
    name: my-machine-user

# Assign roles to a machine user
- cloudera.cloud.iam_machine_user:
    name: my-machine-user
    roles:
      - crn:cdp:iam:us-west-1:altus:role:PowerUser

# Assign resource roles to a machine user
- cloudera.cloud.iam_machine_user:
    name: my-machine-user
    resource_roles:
      - resource: crn:cdp:environments:us-west-1:altus:environment:dev-env
        role: crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser

# Replace resource roles for a machine user
- cloudera.cloud.iam_machine_user:
    name: my-machine-user
    resource_roles:
      - resource: crn:cdp:environments:us-west-1:altus:environment:prod-env
        role: crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentAdmin
    purge: true
"""

RETURN = r"""
machine_user:
  description: The information about the Machine User
  type: dict
  returned: always
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
      sample: my-machine-user
    status:
      description: The status of the machine user.
      returned: on success
      type: str
      sample: ACTIVE
    workload_username:
      description: The username used in all the workload clusters of the machine user.
      returned: on success
      type: str
    roles:
      description: List of Role CRNs assigned to the machine user.
      returned: on success
      type: list
      elements: str
    resource_assignments:
      description: List of Resource-to-Role assignments that are associated with the machine user.
      returned: on success
      type: list
      elements: dict
      contains:
        resource_crn:
          description: The CRN of the resource granted the rights of the role.
          returned: on success
          type: str
        resource_role_crn:
          description: The CRN of the resource role.
          returned: on success
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

from typing import Any

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class IAMMachineUser(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                name=dict(required=True, type="str", aliases=["machine_user_name"]),
                roles=dict(required=False, type="list", elements="str"),
                resource_roles=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        resource=dict(
                            required=True,
                            type="str",
                            aliases=["resource_crn"],
                        ),
                        role=dict(
                            required=True,
                            type="str",
                            aliases=["resource_role_crn"],
                        ),
                    ),
                ),
                purge=dict(required=False, type="bool", default=False),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.state = self.get_param("state")
        self.name = self.get_param("name")
        self.roles = self.get_param("roles")
        self.resource_roles = self.get_param("resource_roles")
        self.purge = self.get_param("purge")

        # Initialize return values
        self.machine_user = {}
        self.changed = False

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    def process(self):
        current_machine_user = self.client.get_machine_user_details(
            machine_user_name=self.name,
        )

        if self.state == "absent":
            if current_machine_user:
                if not self.module.check_mode:
                    self.client.delete_machine_user(machine_user_name=self.name)
                self.changed = True

        if self.state == "present":
            if not current_machine_user:
                if not self.module.check_mode:
                    response = self.client.create_machine_user(
                        machine_user_name=self.name,
                    )
                    self.machine_user = response.get("machineUser", {})
                    current_machine_user = self.client.get_machine_user_details(
                        machine_user_name=self.name,
                    )
                self.changed = True

            if not self.module.check_mode and current_machine_user:

                if self.roles is not None or self.purge:
                    if self.client.manage_machine_user_roles(
                        machine_user_name=self.name,
                        current_roles=current_machine_user.get("roles", []),
                        desired_roles=self.roles or [],
                        purge=self.purge,
                    ):
                        self.changed = True

                if self.resource_roles is not None or self.purge:
                    if self.client.manage_machine_user_resource_roles(
                        machine_user_name=self.name,
                        current_assignments=current_machine_user.get(
                            "resourceAssignments",
                            [],
                        ),
                        desired_assignments=(self.resource_roles or []),
                        purge=self.purge,
                    ):
                        self.changed = True

            if self.changed and not self.module.check_mode:
                self.machine_user = self.client.get_machine_user_details(
                    machine_user_name=self.name,
                )
            else:
                self.machine_user = current_machine_user

        self.machine_user = camel_dict_to_snake_dict(self.machine_user)


def main():
    result = IAMMachineUser()

    output: dict[str, Any] = dict(
        changed=result.changed,
        machine_user=result.machine_user,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
