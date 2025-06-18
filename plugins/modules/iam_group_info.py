#!/usr/bin/python
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

DOCUMENTATION = r"""
module: iam_group_info
short_description: Gather information about CDP Public IAM groups
description:
    - Gather information about CDP Public IAM group or groups
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
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
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Gather information about all Groups
- cloudera.cloud.iam_group_info:

# Gather information about a named Group
- cloudera.cloud.iam_group_info:
    name: example-01

# Gather information about several named Groups
- cloudera.cloud.iam_group_info:
    name:
      - example-01
      - example-02
      - example-03
"""

RETURN = r"""
groups:
  description: The information about the named Group or Groups
  type: list
  returned: always
  elements: dict
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
      description: Flag indicating whether group membership is synced when a user logs in. The default is to sync group
        membership.
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class IAMGroupInfo(CdpModule):
    def __init__(self, module):
        super(IAMGroupInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")

        # Initialize the return values
        self.info = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.info = self.cdpy.iam.gather_groups(self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(
                required=False, type="list", elements="str", aliases=["group_name"]
            )
        ),
        supports_check_mode=True,
    )

    result = IAMGroupInfo(module)

    output = dict(
        changed=False,
        groups=result.info,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
