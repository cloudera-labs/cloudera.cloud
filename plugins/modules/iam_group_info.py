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
module: iam_group_info
short_description: Gather information about CDP Public IAM groups
description:
    - Gather information about CDP Public IAM group or groups
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
options:
  name:
    description:
      - A list of group names or CRNs or a single group name/CRN.
      - If no group name or CRN is provided, all groups are returned.
      - If any parameter group names are not found, no groups are returned.
    type: list
    elements: str
    required: False
    aliases:
      - group_name
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

 - name: Gather information about all Groups
   cloudera.cloud.iam_group_info:

 - name: Gather information about a named Group
   cloudera.cloud.iam_group_info:
     name: example-01

 - name: Gather information about several named Groups
   cloudera.cloud.iam_group_info:
     name:
       - example-01
       - example-02
       - example-03

- cloudera.cloud.iam_group_info:
    name:
      - example-01
      - example-02
      - example-03
"""

RETURN = r"""
groups:
  description:
    - Returns a list of group records.
    - Each record represents a CDP IAM group and its details.
  type: list
  returned: always
  elements: dict
  contains:
    creationDate:
    # creation_date:
      description: The date when this group record was created.
      returned: on success
      type: str
      sample: 2020-07-06T12:24:05.531000+00:00
    crn:
      description: The CRN of the group.
      returned: on success
      type: str
    groupName:
    # group_name:
      description: The group name.
      returned: on success
      type: str
      sample: example-01
    syncMembershipOnUserLogin:
    # sync_membership_on_user_login:
      description: Flag indicating whether group membership is synced when a user logs in. The default is to sync group membership.
      returned: when supported
      type: bool
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

from typing import Any

# from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class IAMGroupInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["group_name"],
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")

        # Initialize the return values
        self.groups = []

    def process(self):
        client = CdpIamClient(api_client=self.api_client)
        result = client.list_groups(group_names=self.name)
        self.groups = result.get("groups", [])


# NOTE: Snake_case conversion deferred until 4.0 to maintain backward compatibility.
# self.groups = [
#     camel_dict_to_snake_dict(group) for group in result.get("groups", [])
# ]


def main():
    result = IAMGroupInfo()

    output: dict[str, Any] = dict(
        changed=False,
        groups=result.groups,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
