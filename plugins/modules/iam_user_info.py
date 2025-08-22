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
      - Mutually exclusive with C(current_user) and C(user_id).
    type: list
    elements: str
    required: False
    aliases:
      - user_name
  current_user:
    description:
      - Flag to use the current user login.
      - Mutually exclusive with C(name) and C(user_id).
    type: bool
    required: False
    default: False
  user_id:
    description:
      - A list of user Ids or a single user Id name/CRN.
      - Mutually exclusive with C(current_user) and C(name).
    type: list
    elements: str
    required: False
  filter:
    description:
      - Key value pair where the key is the field to compare and the value is a regex statement. If there is a match in the regex statment, the user will return.
      - Mutually exclusive with current user and name
    type: dict
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
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
    name: ["user1", "user2"]

# Gather detailed information about a named User
- cloudera.cdp.iam_user_info:
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
    roles:
      description: List of user assigned roles.
      returned: when supported
      type: list
    resource_roles:
      description: List of user assigned resource roles.
      returned: when supported
      type: list
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

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class IAMUserInfo(CdpModule):
    def __init__(self, module):
        super(IAMUserInfo, self).__init__(module)

        # Set Variables
        self.name = self._get_param("name")
        self.current = self._get_param("current_user", False)
        self.filter = self._get_param("filter")
        self.user_id = self._get_param("user_id")
        self.view = self._get_param("view")

        # Initialize filter if set
        self.compiled_filter = self.compile_filters()

        # Initialize the return values
        self.info = []

        # Execute logic process
        self.process()

    def compile_filters(self):
        compiled_filters = {}

        # Check if filter set
        if self.filter is None:
            return None

        # Compile all regex
        for key in self.filter.keys():
            compiled_filters[key] = re.compile(self.filter[key])

        return compiled_filters

    def get_detailed_user_info(self, user):
        user["groups"] = self.cdpy.iam.list_groups_for_user(user["userId"])
        user["roles"] = self.cdpy.iam.list_user_assigned_roles(user["userId"])
        user["resource_roles"] = self.cdpy.iam.list_user_assigned_resource_roles(
            user["userId"],
        )
        return user

    def apply_filters(self):
        filtered_users = []
        # Iterate users
        for userData in self.cdpy.iam.list_users():
            # Iterate Filters. Must match all
            for filter_key, regx_expr in self.compiled_filter.items():
                key_val = userData.get(filter_key)
                if key_val and re.search(regx_expr, key_val):
                    continue  # Filter matches, continue to next filter
                else:
                    break  # No match, skip to next user
            else:
                # All filters matched, add user to filtered_users
                filtered_users.append(userData)
        return filtered_users

    def process(self):

        if self.current:
            self.info = [self.cdpy.iam.get_user()]

        elif self.user_id:
            self.info = self.cdpy.iam.list_users(self.user_id)

        elif self.name:
            user_list = self.cdpy.iam.list_users()
            for user in user_list:
                if user["workloadUsername"] in self.name:
                    self.info.append(user)

        elif self.filter is not None:
            self.info = self.apply_filters()

        if self.view == "full":
            for user in self.info:
                self.get_detailed_user_info(user)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="list", aliases=["user_name"]),
            user_id=dict(required=False, type="list", aliases=["id"]),
            current_user=dict(required=False, type="bool"),
            filter=dict(required=False, type="dict"),
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

    result = IAMUserInfo(module)

    output = dict(
        changed=False,
        users=result.info,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
