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
module: iam_group
short_description: Create, update, or destroy CDP IAM Groups
description:
    - Create, update, and destroy CDP IAM Groups.
    - A group is a named collection of users and machine users.
    - Roles and resource roles can be assigned to a group impacting all members of the group.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
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
      role:
        description:
          - The resource role CRN to be assigned.
        type: str
        required: True
        aliases:
          - resourceRoleCrn
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
  users:
    description:
      - A single user or list of users assigned to the group.
      - The user can be either the name or CRN.
    type: list
    elements: str
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
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
    sync: no

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
    purge: yes
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
    users:
      description: List of User CRNs which are members of the group.
      returned: on success
      type: list
      elements: str
    roles:
      description: List of Role CRNs assigned to the group.
      returned: on success
      type: list
      elements: str
    resource_roles:
      description: List of Resource-to-Role assignments, by CRN, that are associated with the group.
      returned: on success
      type: list
      elements: dict
      contains:
        resourceCrn:
          description: The CRN of the resource granted the rights of the role.
          returned: on success
          type: str
        resourceRoleCrn:
          description: The CRN of the CDP Role.
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


class IAMGroup(CdpModule):
    def __init__(self, module):
        super(IAMGroup, self).__init__(module)

        # Set Variables
        self.state = self._get_param("state")
        self.name = self._get_param("name")
        self.sync = self._get_param("sync")
        self.users = self._get_param("users")
        self.roles = self._get_param("roles")
        self.resource_roles = self._get_param("resource_roles")
        self.purge = self._get_param("purge")

        # Initialize the return values
        self.info = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self._retrieve_group()
        if existing is None:
            if self.state == "present":
                self.changed = True
                self.cdpy.iam.create_group(self.name, self.sync)
                if self.users:
                    for user in self.users:
                        self.cdpy.iam.add_group_user(self.name, user)
                if self.roles:
                    for role in self.roles:
                        self.cdpy.iam.assign_group_role(self.name, role)
                if self.resource_roles:
                    for assignment in self.resource_roles:
                        self.cdpy.iam.assign_group_resource_role(
                            self.name, assignment["resource"], assignment["role"]
                        )
                self.info = self._retrieve_group()
        else:
            if self.state == "present":
                if (
                    self.sync is not None
                    and existing["syncMembershipOnUserLogin"] != self.sync
                ):
                    self.changed = True
                    self.cdpy.iam.update_group(self.name, self.sync)

                if self.users is not None:
                    # If an empty user list, don't normalize
                    normalized_users = (
                        self.cdpy.iam.gather_users(self.users) if self.users else list()
                    )
                    new_users = [
                        user
                        for user in normalized_users
                        if user not in existing["users"]
                    ]
                    for user in new_users:
                        self.changed = True
                        self.cdpy.iam.add_group_user(self.name, user)
                    if self.purge:
                        stale_users = [
                            user
                            for user in existing["users"]
                            if user not in normalized_users
                        ]
                        for user in stale_users:
                            self.changed = True
                            self.cdpy.iam.remove_group_user(self.name, user)

                if self.roles is not None:
                    new_roles = [
                        role for role in self.roles if role not in existing["roles"]
                    ]
                    for role in new_roles:
                        self.changed = True
                        self.cdpy.iam.assign_group_role(self.name, role)
                    if self.purge:
                        stale_roles = [
                            role for role in existing["roles"] if role not in self.roles
                        ]
                        for role in stale_roles:
                            self.changed = True
                            self.cdpy.iam.unassign_group_role(self.name, role)

                if self.resource_roles is not None:
                    new_assignments = self._new_assignments(existing["resource_roles"])
                    for assignment in new_assignments:
                        self.changed = True
                        self.cdpy.iam.assign_group_resource_role(
                            self.name, assignment["resource"], assignment["role"]
                        )
                    if self.purge:
                        stale_assignments = self._stale_assignments(
                            existing["resource_roles"]
                        )
                        for assignment in stale_assignments:
                            self.changed = True
                            self.cdpy.iam.unassign_group_resource_role(
                                self.name, assignment["resource"], assignment["role"]
                            )

                if self.changed:
                    self.info = self._retrieve_group()
                else:
                    self.info = existing

            elif self.state == "absent":
                self.changed = True
                self.cdpy.iam.delete_group(self.name)

    def _retrieve_group(self):
        # TODO: What does gather_groups need?
        group_list = self.cdpy.iam.gather_groups(self.name)
        if group_list:
            return group_list[0]
        else:
            return None

    def _new_assignments(self, existing_assignments):
        new_assignments = []
        resource_dict = dict()
        for existing in existing_assignments:
            if existing["resourceCrn"] in resource_dict:
                resource_dict[existing["resourceCrn"]].add(existing["resourceRoleCrn"])
            else:
                resource_dict[existing["resourceCrn"]] = {existing["resourceRoleCrn"]}
        for assignment in self.resource_roles:
            if (
                assignment["resource"] not in resource_dict
                or assignment["role"] not in resource_dict[assignment["resource"]]
            ):
                new_assignments.append(assignment)
        return new_assignments

    def _stale_assignments(self, existing_assignments):
        stale_assignments = []
        resource_dict = dict()
        for assignment in self.resource_roles:
            if assignment["resource"] in resource_dict:
                resource_dict[assignment["resource"]].add(assignment["role"])
            else:
                resource_dict[assignment["resource"]] = {assignment["role"]}
        for existing in existing_assignments:
            if (
                existing["resourceCrn"] not in resource_dict
                or existing["resourceRoleCrn"]
                not in resource_dict[existing["resourceCrn"]]
            ):
                stale_assignments.append(existing)
        return stale_assignments


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
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
                aliases=["sync_membership", "sync_on_login"],
            ),
            users=dict(required=False, type="list", elements="str"),
            roles=dict(required=False, type="list", elements="str"),
            resource_roles=dict(
                required=False,
                type="list",
                elements="dict",
                options=dict(
                    resource=dict(required=True, type="str", aliases=["resourceCrn"]),
                    role=dict(required=True, type="str", aliases=["resourceRoleCrn"]),
                ),
                aliases=["assignments"],
            ),
            purge=dict(required=False, type="bool", default=False, aliases=["replace"]),
        ),
        supports_check_mode=True,
    )

    result = IAMGroup(module)

    output = dict(
        changed=result.changed,
        group=result.info,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
