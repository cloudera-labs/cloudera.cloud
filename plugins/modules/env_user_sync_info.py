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
module: env_user_sync_info
short_description: Get the status of a CDP Users and Groups sync
description:
  - Get the status of a synchronization event for users and groups with one or more CDP environments.
  - The module support check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Daniel Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - The C(operations id) for a User and Group sync event or the C(operations CRN) for the event if the C(WORKLOAD_IAM_SYNC) entitlement is enabled
    aliases:
      - operations_id
      - operations_crn
    required: True
    type: str
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Get the status of a sync event (non-WORKLOAD_IAM_SYNC)
- cloudera.cloud.env_user_sync_info:
    name: 0e9bc67a-b308-4275-935c-b8c764dc13be
"""

RETURN = r"""
sync:
    description: Returns an object describing of the status of the User and Group sync event.
    returned: success
    type: complex
    contains:
        endTime:
            description: Sync operation end timestamp (epoch seconds).
            returned: when supported
            type: str
            sample: 1602080301000
        error:
            description: Error message for general failure of sync operation.
            returned: when supported
            type: str
        failure:
            description: List of sync operation details for all failed environments.
            returned: when supported
            type: list
            elements: dict
            contains:
                environmentCrn:
                    description: The environment CRN.
                    returned: always
                    type: str
                message:
                    description: Details on the failure.
                    returned: when supported
                    type: str
        operationId:
            description: UUID (or CRN, if running with the C(WORKLOAD_IAM_SYNC) entitlement) of the request for this operation.
            returned: always
            type: str
            sample: 0e9bc67a-b308-4275-935c-b8c764dc13be
        operationType:
            description: The operation type.
            returned: when supported
            type: str
            sample: USER_SYNC
        startTime:
            description: Sync operation start timestamp (epoch seconds).
            returned: when supported
            type: str
            sample: 1602080301000
        status:
            description: Status of this operation.
            returned: when supported
            type: str
            sample:
                - NEVER_RUN
                - REQUESTED
                - REJECTED
                - RUNNING
                - COMPLETED
                - FAILED
                - TIMEDOUT
        success:
            description: List of sync operation details for all succeeded environments.
            returned: when supported
            type: list
            elements: dict
            contains:
                environmentCrn:
                    description: The environment CRN.
                    returned: always
                    type: str
                message:
                    description: Details on the success.
                    returned: when supported
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class EnvironmentUserSyncInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentUserSyncInfo, self).__init__(module)

        # Set variables
        self.name = self.module.params["name"]

        # Initialize the return values
        self.sync = {}
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.sync = self.cdpy.environments.get_sync_status(self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(
                required=True,
                type="str",
                aliases=["operation_id", "operation_crn"],
            ),
        ),
        supports_check_mode=True,
    )

    result = EnvironmentUserSyncInfo(module)

    output = dict(
        changed=result.changed,
        sync=result.sync,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
