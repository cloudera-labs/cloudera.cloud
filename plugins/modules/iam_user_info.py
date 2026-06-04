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
module: iam_user_info
short_description: Gather information about CDP Public IAM users
description:
    - Gather information about CDP Public IAM users
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
options:
  name:
    description:
      - A list of user names or a single user name.
      - If no user name is provided, all users are returned.
      - Mutually exclusive with O(current_user) and O(user_id).
    type: list
    elements: str
    required: False
    aliases:
      - user_name
  current_user:
    description:
      - Flag to retrieve the current authenticated user.
      - Mutually exclusive with O(name) and O(user_id).
    type: bool
    required: False
    default: False
  user_id:
    description:
      - A list of user Ids or a single user Id name/CRN.
      - Mutually exclusive with O(current_user) and O(name).
    type: list
    elements: str
    required: False
  filter:
    description:
      - Key value pair where the key is the field to compare and the value is a regex statement. If there is a match in the regex statment, the user will return.
      - Mutually exclusive with O(current_user) and O(name).
    type: dict
    required: False
  view:
    description:
      - The level of detail returned for each user.
      - V(summary) returns the basic C(User) object fields from the list API.
      - V(full) additionally fetches each user's assigned roles, resource roles, and group memberships.
    type: str
    required: False
    default: full
    choices:
      - summary
      - full
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all Users
- cloudera.cloud.iam_user_info:
    view: summary

# Gather detailed information about a named User
- cloudera.cloud.iam_user_info:
    name: Example

# Gather detailed information specific user Id
- cloudera.cloud.iam_user_info:
    user_id: "11a111a-91f0-4ca2-9262-111aa1111"

# Gather detailed information about more users
- cloudera.cloud.iam_user_info:
    filter:
      workloadUsername: my[0-9]{2}_admin.*?'

# Gather detailed information about the current user
- cloudera.cloud.iam_user_info:
    current_user: true
"""

RETURN = r"""
users:
  description: The information about the current or named User or Users
  type: list
  returned: always
  elements: dict
  contains:
    accountAdmin:
      description: Whether the user is an administrator of their CDP account.
      returned: on success
      type: bool
    creationDate:
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
    firstName:
      description: The user's first name.
      returned: on success
      type: str
    identityProviderCrn:
      description: The identity provider that the user belongs to. It can be "Cloudera-Default", "Cloudera-Administration", or a customer-defined identity provider.
      returned: on success
      type: str
    lastInteractiveLogin:
      description: The date of the user’s last interactive login.
      returned: when supported
      type: str
      sample: 2020-08-04T16:57:37.808000+00:00
    lastName:
      description: The user's last name.
      returned: on success
      type: str
    userId:
      description: The stable, unique identifier of the user.
      returned: on success
      type: str
      sample: f2e7cd8a-4c2d-41b5-92e9-784255c25b7d
    workloadUsername:
      description: The username used in all the workload clusters of the user.
      returned: when supported
      type: str
      sample: u_023
    groups:
      description: List of groups that user is assigned.
      returned: when supported
      type: list
      elements: str
    roles:
      description: List of user assigned roles.
      returned: when supported
      type: list
      elements: str
    resource_roles:
      description: List of resource role assignments associated with the user.
      returned: when supported
      type: list
      elements: dict
      contains:
        resourceCrn:
          description: The CRN of the resource granted the rights of the role.
          returned: when supported
          type: str
        resourceRoleCrn:
          description: The CRN of the resource role.
          returned: when supported
          type: str
    status:
      description: The current status of the user.
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

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class IAMUserInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["user_name"],
                ),
                current_user=dict(
                    required=False,
                    type="bool",
                    default=False,
                ),
                user_id=dict(
                    required=False,
                    type="list",
                    elements="str",
                ),
                filter=dict(
                    required=False,
                    type="dict",
                ),
                view=dict(
                    required=False,
                    type="str",
                    choices=["summary", "full"],
                    default="full",
                ),
            ),
            mutually_exclusive=[
                ["name", "current_user"],
                ["filter", "current_user"],
                ["filter", "name"],
                ["user_id", "name"],
                ["user_id", "current_user"],
            ],
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.current_user = self.get_param("current_user")
        self.user_id = self.get_param("user_id")
        self.filter = self.get_param("filter")
        self.view = self.get_param("view")

        # Initialize the return values
        self.users = []

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    def process(self):
        if self.current_user:
            user = self.client.get_user()
            if user:
                self.users.append(user)

        elif self.user_id:
            result = self.client.list_users(user_ids=self.user_id)
            self.users = result.get("users", [])

        elif self.name:
            result = self.client.list_users()
            user_list = result.get("users", [])
            for user in user_list:
                if user.get("workloadUsername") in self.name:
                    self.users.append(user)

        elif self.filter is not None:
            self.users = self.client.list_users_filtered(self.filter)

        else:
            result = self.client.list_users()
            self.users = result.get("users", [])

        if self.view == "full":
            details = []
            for user in self.users:
                uid = user.get("userId")
                detail = self.client.get_user_details(uid)
                if detail:
                    # Rename resourceAssignments to resource_roles for backward compatibility
                    if "resourceAssignments" in detail:
                        detail["resource_roles"] = detail.pop("resourceAssignments")
                    details.append(detail)
            self.users = details


def main():
    result = IAMUserInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        users=result.users,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
