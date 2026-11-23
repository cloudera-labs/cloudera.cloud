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
module: iam_user
short_description: Create, update, or remove CDP IAM Users
description:
    - Create, update, and remove Cloudera Data Platform IAM Users.
    - Manage user role and resource role assignments.
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "3.3.0"
options:
  email:
    description:
      - The email address for the user.
      - Required only when creating a new user (O(state=present) and the user does not yet exist).
      - Can be used to identify an existing user for updates or deletion.
      - If both O(email) and O(user_id) are provided, O(email) takes precedence for lookup.
    type: str
    required: False
  first_name:
    description:
      - The user's first name.
    type: str
    required: False
  groups:
    description:
      - List of groups the user belongs to.
      - Groups must already exist before adding users to them.
      - Use the M(cloudera.cloud.iam_group) module to create groups first.
      - If not specified, the user's existing group memberships are left untouched, regardless of O(purge).
      - If specified, group memberships are reconciled against this list; with O(purge=True), memberships not in this list are removed.
    type: list
    elements: str
    required: False
  identity_provider_user_id:
    description:
      - The identity provider user ID for the user.
      - This ID must match the NameId attribute value in the SAML response.
      - If not provided, defaults to the email address (common for most SAML providers).
      - Only used when creating a new user.
    type: str
    required: False
    aliases:
      - idp_user_id
  last_name:
    description:
      - The user's last name.
    type: str
    required: False
  purge:
    description:
      - Flag to replace O(roles), O(resource_roles), and O(groups) with their specified values.
      - If True, any roles, resource roles, or groups not specified will be removed.
      - Only applies to an attribute (O(roles), O(resource_roles), O(groups)) when that attribute is also specified; an omitted attribute is never purged.
    type: bool
    required: False
    default: False
  resource_roles:
    description:
      - A list of resource role assignments.
      - If not specified, the user's existing resource role assignments are left untouched, regardless of O(purge).
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
      - A single role or list of roles assigned to the user.
      - The role must be identified by its full CRN.
      - If not specified, the user's existing role assignments are left untouched, regardless of O(purge).
      - If specified, roles are reconciled against this list; with O(purge=True), roles not in this list are removed.
    type: list
    elements: str
    required: False
  saml_provider_name:
    description:
      - The name or CRN of the SAML provider the user will use for login.
      - If not provided, the default identity provider will be used automatically.
    type: str
    required: False
    aliases:
      - saml_provider
  workload_password:
    description:
      - The workload password for the user.
      - This will be the user's password in all Environments they have access to.
      - The password plaintext is not stored.
      - Only applicable when creating or updating a user (O(state=present)).
      - This parameter is optional and only set if provided.
      - When provided for an existing user, the password is reset on every run and the task always reports a change, because the current password cannot be read back for comparison.
    type: str
    required: False
    aliases:
      - password
  state:
    description:
      - The state of the user.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  user_id:
    description:
      - The user ID or CRN of the user to manage.
      - Can be used to identify an existing user for updates or deletion.
      - Either O(user_id) or O(email) must be provided.
      - If both O(email) and O(user_id) are provided, O(email) takes precedence for lookup.
    type: str
    required: False
    aliases:
      - user
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a user (identity_provider_user_id defaults to email)
- cloudera.cloud.iam_user:
    email: user@example.com
    first_name: John
    last_name: Doe
    saml_provider_name: my-saml-provider

# Create a user with explicit identity provider user ID
- cloudera.cloud.iam_user:
    email: user@example.com
    identity_provider_user_id: user123
    first_name: John
    last_name: Doe
    saml_provider_name: my-saml-provider

# Create a user and assign to existing groups (groups must exist first)
- cloudera.cloud.iam_user:
    email: user@example.com
    groups:
      - developers
      - admins

# Create a user with a workload password
- cloudera.cloud.iam_user:
    email: user@example.com
    first_name: John
    last_name: Doe
    workload_password: "MySecurePassword123!"
    saml_provider_name: my-saml-provider

# Reset the workload password of an existing user (email is not required)
- cloudera.cloud.iam_user:
    user_id: user001
    workload_password: "MyNewSecurePassword123!"

# Delete a user by user_id
- cloudera.cloud.iam_user:
    state: absent
    user_id: crn:cdp:iam:us-west-1:altus:user:example-user-id

# Delete a user by email
- cloudera.cloud.iam_user:
    state: absent
    email: user@example.com

# Assign roles to an existing user
- cloudera.cloud.iam_user:
    user_id: user@example.com
    roles:
      - crn:cdp:iam:us-west-1:altus:role:PowerUser

# Assign resource roles to a user
- cloudera.cloud.iam_user:
    user_id: user@example.com
    resource_roles:
      - resource: crn:cdp:environments:us-west-1:altus:environment:dev-env
        role: crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentUser

# Replace resource roles for a user
- cloudera.cloud.iam_user:
    user_id: user@example.com
    resource_roles:
      - resource: crn:cdp:environments:us-west-1:altus:environment:prod-env
        role: crn:cdp:iam:us-west-1:altus:resourceRole:EnvironmentAdmin
    purge: true

"""

RETURN = r"""
user:
  description: The information about the User
  type: dict
  returned: always
  contains:
    creation_date:
      description: The date when this user record was created.
      returned: on success
      type: str
      sample: 2020-07-06T12:24:05.531000+00:00
    crn:
      description: The CRN of the user.
      returned: on success
      type: str
    email:
      description: The user's email address.
      returned: on success
      type: str
      sample: user@example.com
    first_name:
      description: The user's first name.
      returned: on success
      type: str
    last_name:
      description: The user's last name.
      returned: on success
      type: str
    status:
      description: The status of the user.
      returned: on success
      type: str
      sample: ACTIVE
    workload_username:
      description: The username used in all the workload clusters of the user.
      returned: on success
      type: str
    groups:
      description: List of Group CRNs the user belongs to.
      returned: on success
      type: list
      elements: str
    roles:
      description: List of Role CRNs assigned to the user.
      returned: on success
      type: list
      elements: str
    resource_assignments:
      description: List of Resource-to-Role assignments that are associated with the user.
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
    ResourceAssignment,
    UserDetails,
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


class IAMUser(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                user_id=dict(required=False, type="str", aliases=["user"]),
                email=dict(required=False, type="str"),
                identity_provider_user_id=dict(
                    required=False,
                    type="str",
                    aliases=["idp_user_id"],
                ),
                first_name=dict(required=False, type="str"),
                last_name=dict(required=False, type="str"),
                saml_provider_name=dict(
                    required=False,
                    type="str",
                    aliases=["saml_provider"],
                ),
                workload_password=dict(
                    required=False,
                    type="str",
                    no_log=True,
                    aliases=["password"],
                ),
                groups=dict(required=False, type="list", elements="str"),
                roles=dict(required=False, type="list", elements="str"),
                resource_roles=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        resource=dict(
                            required=True,
                            type="str",
                            aliases=["resource_crn", "resourceCrn"],
                        ),
                        role=dict(
                            required=True,
                            type="str",
                            aliases=["resource_role_crn", "resourceRoleCrn"],
                        ),
                    ),
                ),
                purge=dict(required=False, type="bool", default=False),
            ),
            required_one_of=[
                ["user_id", "email"],
            ],
            supports_check_mode=True,
        )

        # Set parameters
        self.state = self.get_param("state")
        self.user_id = self.get_param("user_id")
        self.email = self.get_param("email")
        self.identity_provider_user_id = self.get_param("identity_provider_user_id")
        self.first_name = self.get_param("first_name")
        self.last_name = self.get_param("last_name")
        self.saml_provider_name = self.get_param("saml_provider_name")
        self.workload_password = self.get_param("workload_password")
        self.groups: Optional[List[str]] = self.get_param("groups")
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
        self.user: Dict[str, Any] = {}
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

    def _find_existing_user(self) -> Optional[UserDetails]:
        if self.email:
            return self.client.get_user_details_by_email(email=self.email)
        return self.client.get_user_details(user_id=self.user_id)

    def _expected_new_user(self) -> UserDetails:
        """The user as requested by the task, for the 'after' side of a create diff."""
        expected = UserDetails(email=self.email)
        if self.first_name is not None:
            expected.firstName = self.first_name
        if self.last_name is not None:
            expected.lastName = self.last_name
        if self.groups is not None:
            expected.groups = self.groups
        if self.roles is not None:
            expected.roles = self.roles
        if self.resource_roles is not None:
            expected.resourceAssignments = self.resource_roles
        return expected

    def _plan_update(self, existing: UserDetails) -> Tuple[UserDetails, UserDetails]:
        """
        Build comparable (current, desired) views of an existing user.

        Lists are sorted so ordering differences never register as changes, and
        group CRNs are resolved to names (the form in which groups are requested)
        whenever groups are managed by the task.
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

        if self.groups is not None:
            current_names = set(
                self.client.get_group_names(_coerce_list(existing.groups)),
            )
            wanted_names = set(self.groups)
            current.groups = sorted(current_names)
            desired.groups = sorted(
                wanted_names if self.purge else current_names | wanted_names,
            )

        return current, desired

    def _apply(self, user: UserDetails) -> bool:
        """Reconcile groups, roles, resource roles and workload password. Returns True if anything changed."""
        changed = False

        if self.groups is not None:
            if self.client.manage_user_groups(
                user_id=user.userId,
                current_groups=_coerce_list(user.groups),
                desired_groups=self.groups,
                purge=self.purge,
            ):
                changed = True

        if self._manages_roles:
            if self.client.manage_user_roles(
                user_id=user.userId,
                current_roles=_coerce_list(user.roles),
                desired_roles=self.roles or [],
                purge=self.purge,
            ):
                changed = True

        if self._manages_resource_roles:
            if self.client.manage_user_resource_roles(
                user_id=user.userId,
                current_assignments=_coerce_list(user.resourceAssignments),
                desired_assignments=self.resource_roles or [],
                purge=self.purge,
            ):
                changed = True

        if self.workload_password is not None:
            self.client.set_workload_password(
                password=self.workload_password,
                actor_crn=user.crn,
            )
            changed = True

        return changed

    def process(self):
        existing = self._find_existing_user()
        final: Optional[UserDetails] = None

        if self.state == "absent":
            if existing:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = camel_dict_to_snake_dict(to_dict(existing))
                if not self.module.check_mode:
                    self.client.delete_user(user_id=existing.userId)

        elif not existing:
            if not self.email:
                self.module.fail_json(
                    msg=f"email is required to create a new user; no existing user found for user_id '{self.user_id}'",
                )
            self.changed = True
            if self.module._diff:
                self.diff["after"] = camel_dict_to_snake_dict(
                    to_dict(self._expected_new_user()),
                )
            if not self.module.check_mode:
                created = self.client.create_user(
                    email=self.email,
                    first_name=self.first_name,
                    identity_provider_user_id=self.identity_provider_user_id
                    or self.email,
                    last_name=self.last_name,
                    saml_provider_name=self.saml_provider_name,
                )
                details = self.client.get_user_details(user_id=created.userId)
                self._apply(details)
                final = self.client.get_user_details(user_id=created.userId)

        else:
            current, desired = self._plan_update(existing)
            before, after = diff_dict(current, desired)

            if before or after or self.workload_password is not None:
                self.changed = True
                if self.module._diff and (before or after):
                    self.diff["before"] = camel_dict_to_snake_dict(before)
                    self.diff["after"] = camel_dict_to_snake_dict(after)

            final = existing
            if not self.module.check_mode:
                if self._apply(existing):
                    self.changed = True
                if self.changed:
                    final = self.client.get_user_details(user_id=existing.userId)

        if final:
            self.user = camel_dict_to_snake_dict(to_dict(final))


def main():
    result = IAMUser()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        user=result.user,
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
