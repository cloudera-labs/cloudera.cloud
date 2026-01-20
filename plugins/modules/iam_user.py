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
version_added: "3.2.0"
options:
  email:
    description:
      - The email address for the user.
      - Required when creating a new user (C(state=present)).
      - Can be used to identify an existing user for updates or deletion.
      - If both C(email) and C(user_id) are provided, C(email) takes precedence for lookup.
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
      - Groups will be created if they don't exist.
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
      - Flag to replace C(roles) and C(resource_roles) with their specified values.
      - If True, any roles or resource roles not specified will be removed.
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
      - Either C(user_id) or C(email) must be provided.
      - If both C(email) and C(user_id) are provided, C(email) takes precedence for lookup.
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

# Create a user and assign to groups
- cloudera.cloud.iam_user:
    email: user@example.com
    groups:
      - developers
      - admins

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

from typing import Any, Dict

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


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
                            aliases=["resource_crn"],
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
            required_if=[
                ("state", "present", ["email"]),
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
        self.groups = self.get_param("groups")
        self.roles = self.get_param("roles")
        self.resource_roles = self.get_param("resource_roles")
        self.purge = self.get_param("purge")

        # Initialize return values
        self.user = {}
        self.changed = False

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    def process(self):
        existing_user = None

        if self.email:
            existing_user = self.client.get_user_details_by_email(email=self.email)
            if existing_user:
                self.user_id = existing_user.get("userId")
        elif self.user_id:
            existing_user = self.client.get_user_details(user_id=self.user_id)


        if self.state == "absent":
            if existing_user:
                if not self.module.check_mode:
                    self.client.delete_user(user_id=self.user_id)
                self.changed = True

        elif self.state == "present":

            if not existing_user:
                # Default identity_provider_user_id to email if not provided
                idp_user_id = self.identity_provider_user_id or self.email
                
                if not self.module.check_mode:
                    response = self.client.create_user(
                        email=self.email,
                        first_name=self.first_name,
                        groups=self.groups,
                        identity_provider_user_id=idp_user_id,
                        last_name=self.last_name,
                        saml_provider_name=self.saml_provider_name,
                    )
                    self.user = response.get("user", {})
                    existing_user = self.client.get_user_details(
                        user_id=self.user.get("userId")
                    )
                self.changed = True


            if existing_user and not self.module.check_mode:

                if self.groups is not None or self.purge:
                    if self.client.manage_user_groups(
                        user_id=existing_user.get("userId"),
                        current_groups=existing_user.get("groups", []),
                        desired_groups=self.groups or [],
                        purge=self.purge,
                    ):
                        self.changed = True

                if self.roles is not None or self.purge:
                    if self.client.manage_user_roles(
                        user_id=existing_user.get("userId"),
                        current_roles=existing_user.get("roles", []),
                        desired_roles=self.roles or [],
                        purge=self.purge,
                    ):
                        self.changed = True

                if self.resource_roles is not None or self.purge:
                    if self.client.manage_user_resource_roles(
                        user_id=existing_user.get("userId"),
                        current_assignments=existing_user.get(
                            "resourceAssignments",
                            [],
                        ),
                        desired_assignments=(self.resource_roles or []),
                        purge=self.purge,
                    ):
                        self.changed = True

            if existing_user and self.changed and not self.module.check_mode:
                existing_user = self.client.get_user_details(
                    user_id=existing_user.get("userId")
                )

            if existing_user:
                self.user = existing_user

        self.user = camel_dict_to_snake_dict(self.user)


def main():
    result = IAMUser()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        user=result.user,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
