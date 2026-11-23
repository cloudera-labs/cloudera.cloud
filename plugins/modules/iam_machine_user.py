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
      - Flag to replace O(roles) and O(resource_roles) with their specified values.
      - If True, any roles or resource roles not specified will be removed.
      - Only applies to an attribute (O(roles), O(resource_roles)) when that attribute is also specified; an omitted attribute is never purged.
    type: bool
    required: False
    default: False
  resource_roles:
    description:
      - A list of resource role assignments.
      - If not specified, the machine user's existing resource role assignments are left untouched, regardless of O(purge).
      - If specified, assignments are reconciled against this list; with O(purge=True), assignments not in this list are removed.
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
      - If not specified, the machine user's existing role assignments are left untouched, regardless of O(purge).
      - If specified, roles are reconciled against this list; with O(purge=True), roles not in this list are removed.
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

# Remove every role from a machine user (an explicit empty list with purge)
- cloudera.cloud.iam_machine_user:
    name: my-machine-user
    roles: []
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
    workload_password_details:
      description: Details about the workload password of the machine user.
      returned: on success
      type: dict
      contains:
        is_password_set:
          description: Whether a workload password has been set.
          returned: on success
          type: bool
        password_expiration_date:
          description: The date when the workload password expires.
          returned: when set
          type: str
        password_min_lifetime_date:
          description: The date until which the workload password cannot be changed again.
          returned: when set
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

from dataclasses import replace
from typing import Any, Dict, List, Optional, Set, Tuple

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    ServicesModule,
    diff_dict,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
    MachineUserDetails,
    ResourceAssignment,
)


def _coerce_list(value: Any) -> List[Any]:
    """Treat an unset (NULLABLE) or null list field as empty."""
    return [] if value is NULLABLE or value is None else value


def _assignment_pairs(
    assignments: Optional[List[ResourceAssignment]],
) -> Set[Tuple[Any, Any]]:
    return {(a.resourceCrn, a.resourceRoleCrn) for a in assignments or []}


def _assignments_from_pairs(pairs: Set[Tuple[Any, Any]]) -> List[ResourceAssignment]:
    return [
        ResourceAssignment(resourceCrn=resource, resourceRoleCrn=role)
        for resource, role in sorted(pairs)
    ]


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
        self.roles: Optional[List[str]] = self.get_param("roles")
        self.purge = self.get_param("purge")

        resource_roles = self.get_param("resource_roles")
        self.resource_roles: Optional[List[ResourceAssignment]] = (
            [
                ResourceAssignment(
                    resourceCrn=item["resource"],
                    resourceRoleCrn=item["role"],
                )
                for item in resource_roles
            ]
            if resource_roles is not None
            else None
        )

        # Initialize return values
        self.machine_user: Dict[str, Any] = {}
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    @property
    def _manages_roles(self) -> bool:
        return self.roles is not None

    @property
    def _manages_resource_roles(self) -> bool:
        return self.resource_roles is not None

    def _expected_new_machine_user(self) -> MachineUserDetails:
        """The machine user as requested by the task, for the 'after' side of a create diff."""
        expected = MachineUserDetails(machineUserName=self.name)
        if self.roles is not None:
            expected.roles = self.roles
        if self.resource_roles is not None:
            expected.resourceAssignments = self.resource_roles
        return expected

    def _plan_update(
        self,
        existing: MachineUserDetails,
    ) -> Tuple[MachineUserDetails, MachineUserDetails]:
        """
        Build comparable (current, desired) views of an existing machine user.

        Lists are sorted so ordering differences never register as changes, and
        an attribute the task does not specify is left identical on both sides.
        """
        current_roles = _coerce_list(existing.roles)
        current_pairs = _assignment_pairs(_coerce_list(existing.resourceAssignments))

        current = replace(
            existing,
            roles=sorted(current_roles),
            resourceAssignments=_assignments_from_pairs(current_pairs),
        )
        desired = replace(current)

        if self._manages_roles:
            wanted_roles = set(self.roles or [])
            desired.roles = sorted(
                wanted_roles if self.purge else set(current_roles) | wanted_roles,
            )

        if self._manages_resource_roles:
            wanted_pairs = _assignment_pairs(self.resource_roles)
            desired.resourceAssignments = _assignments_from_pairs(
                wanted_pairs if self.purge else current_pairs | wanted_pairs,
            )

        return current, desired

    def _apply(self, machine_user: MachineUserDetails) -> bool:
        """Reconcile roles and resource roles. Returns True if anything changed."""
        changed = False

        if self._manages_roles:
            if self.client.manage_machine_user_roles(
                machine_user_name=self.name,
                current_roles=_coerce_list(machine_user.roles),
                desired_roles=self.roles or [],
                purge=self.purge,
            ):
                changed = True

        if self._manages_resource_roles:
            if self.client.manage_machine_user_resource_roles(
                machine_user_name=self.name,
                current_assignments=_coerce_list(machine_user.resourceAssignments),
                desired_assignments=self.resource_roles or [],
                purge=self.purge,
            ):
                changed = True

        return changed

    def process(self):
        existing = self.client.get_machine_user_details(machine_user_name=self.name)
        final: Optional[MachineUserDetails] = None

        if self.state == "absent":
            if existing:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = camel_dict_to_snake_dict(to_dict(existing))
                if self.module.check_mode:
                    final = existing
                else:
                    self.client.delete_machine_user(machine_user_name=self.name)

        elif not existing:
            self.changed = True
            if self.module._diff:
                self.diff["after"] = camel_dict_to_snake_dict(
                    to_dict(self._expected_new_machine_user()),
                )
            if not self.module.check_mode:
                self.client.create_machine_user(machine_user_name=self.name)
                details = self.client.get_machine_user_details(
                    machine_user_name=self.name,
                )
                self._apply(details)
                final = self.client.get_machine_user_details(
                    machine_user_name=self.name,
                )

        else:
            current, desired = self._plan_update(existing)
            before, after = diff_dict(current, desired)

            if before or after:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = camel_dict_to_snake_dict(before)
                    self.diff["after"] = camel_dict_to_snake_dict(after)

            final = existing
            if not self.module.check_mode:
                if self._apply(existing):
                    self.changed = True
                if self.changed:
                    final = self.client.get_machine_user_details(
                        machine_user_name=self.name,
                    )

        if final:
            self.machine_user = camel_dict_to_snake_dict(to_dict(final))


def main():
    result = IAMMachineUser()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        machine_user=result.machine_user,
    )

    if result.diff["before"] or result.diff["after"]:
        output.update(diff=result.diff)

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
