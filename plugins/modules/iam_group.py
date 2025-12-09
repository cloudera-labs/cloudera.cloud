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
module: iam_group
short_description: Create, update, or destroy CDP IAM Groups
description:
    - Create, update, and destroy CDP IAM Groups.
    - A group is a named collection of users and machine users.
    - Roles and resource roles can be assigned to a group impacting all members of the group.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
options:
  name:
    description:
      - The name of the group.
      - The name must be unique, must have a maximum of 32 characters, and must contain only alphanumeric
            characters, "-", and "_".
      - The first character of the name must be alphabetic or an underscore.
      - Names are are not case-sensitive.
      - The group named "administrators" is reserved.
    type: str
    required: True
    aliases:
      - group_name
  purge:
    description:
      - Flag to replace C(roles), C(users), and C(resource_roles) with their specified values.
    type: bool
    required: False
    default: False
    aliases:
      - replace
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
          - resourceCrn
          - resource_crn
      role:
        description:
          - The resource role CRN to be assigned.
        type: str
        required: True
        aliases:
          - resourceRoleCrn
          - resource_role_crn
  roles:
    description:
      - A single role or list of roles assigned to the group.
      - The role must be identified by its full CRN.
    type: list
    elements: str
    required: False
  state:
    description:
      - The state of the group.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  sync:
    description:
      - Whether group membership is synced when a user logs in.
      - The default is to sync group membership.
    type: bool
    required: False
    default: True
    aliases:
      - sync_membership
      - sync_on_login
      - sync_membership_on_user_login
  users:
    description:
      - A single user or list of users assigned to the group.
      - Users can be regular users or machine users.
      - The user can be either the name or CRN.
    type: list
    elements: str
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a group
- cloudera.cloud.iam_group:
    name: group-example

# Create a group with membership sync disabled
- cloudera.cloud.iam_group:
    state: present
    name: group-example
    sync: false

# Delete a group
- cloudera.cloud.iam_group:
    state: absent
    name: group-example

# Assign users to a group
- cloudera.cloud.iam_group:
    name: group-example
    users:
      - user-a
      - user-b

# Assign roles to a group
- cloudera.cloud.iam_group:
    name: group-example
    roles:
      - role-a
      - role-b

# Replace resource roles a group
- cloudera.cloud.iam_group:
    name: group-example
    resource_roles:
      - role-c
      - role-d
    purge: true
"""

RETURN = r"""
group:
  description: The information about the Group
  type: dict
  returned: always
  contains:
    creationDate:
      description: The date when this group record was created.
      returned: on success
      type: str
      sample: 2020-07-06T12:24:05.531000+00:00
    crn:
      description: The CRN of the group.
      returned: on success
      type: str
    groupName:
      description: The group name.
      returned: on success
      type: str
      sample: example-01
    members:
      description: List of member CRNs (users and machine users) which are members of the group.
      returned: on success
      type: list
      elements: str
    roles:
      description: List of Role CRNs assigned to the group.
      returned: on success
      type: list
      elements: str
    resourceAssignments:
      description: List of Resource-to-Role assignments that are associated with the group.
      returned: on success
      type: list
      elements: dict
      contains:
        resourceCrn:
          description: The CRN of the resource granted the rights of the role.
          returned: on success
          type: str
        resourceRoleCrn:
          description: The CRN of the resource role.
          returned: on success
          type: str
    syncMembershipOnUserLogin:
      description: Flag indicating whether group membership is synced when a user logs in. The default is to sync
        group membership.
      returned: when supported
      type: bool
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

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class IAMGroup(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                name=dict(required=True, type="str", aliases=["group_name"]),
                sync=dict(
                    required=False,
                    type="bool",
                    default=True,
                    aliases=["sync_membership", "sync_membership_on_user_login"],
                ),
                users=dict(required=False, type="list", elements="str"),
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
        self.sync = self.get_param("sync")
        self.users = self.get_param("users")
        self.roles = self.get_param("roles")
        self.resource_roles = self.get_param("resource_roles")
        self.purge = self.get_param("purge")

        # Initialize return values
        self.group = {}
        self.changed = False

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    def process(self):
        current_group = self.client.get_group_details(group_name=self.name)

        # Delete
        if self.state == "absent":
            if current_group:
                if not self.module.check_mode:
                    self.client.delete_group(group_name=self.name)
                self.changed = True
        
        if self.state == "present":
            # Create
            if not current_group:
              if self.module.check_mode:
                  self.group = {"groupName": self.name}
              else:
                  response = self.client.create_group(
                      group_name=self.name,
                      sync_membership_on_user_login=self.sync,
                  )
                  self.group = response.get("group", {})
              self.changed = True
              current_group = self.client.get_group_details(group_name=self.name)

            # Reconcile
            if not self.module.check_mode and current_group:

                if self.sync != current_group.get("syncMembershipOnUserLogin"):
                    self.client.update_group(
                        group_name=self.name,
                        sync_membership_on_user_login=self.sync,
                    )
                    self.changed = True

                if self.users is not None or self.purge:
                    if self.client.manage_group_users(
                        group_name=self.name,
                        current_members=current_group.get("members", []),
                        desired_users=self.users if self.users is not None else [],
                        purge=self.purge,
                    ):
                        self.changed = True

                if self.roles is not None or self.purge:
                    if self.client.manage_group_roles(
                        group_name=self.name,
                        current_roles=current_group.get("roles", []),
                        desired_roles=self.roles if self.roles is not None else [],
                        purge=self.purge,
                    ):
                        self.changed = True

                if self.resource_roles is not None or self.purge:
                    if self.client.manage_group_resource_roles(
                        group_name=self.name,
                        current_assignments=current_group.get("resourceAssignments", []),
                        desired_assignments=(
                            self.resource_roles if self.resource_roles is not None else []
                        ),
                        purge=self.purge,
                    ):
                        self.changed = True

            if self.changed and not self.module.check_mode:
                self.group = self.client.get_group_details(group_name=self.name)
            else:
                self.group = current_group


def main():
    result = IAMGroup()

    output: dict[str, Any] = dict(
        changed=result.changed,
        group=result.group,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
