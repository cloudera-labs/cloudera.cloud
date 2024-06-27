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

DOCUMENTATION = """
---
module: env_automated_user_sync_info
short_description: Get the status of the automated CDP Users and Groups synchronization service
description:
  - Get the status of the automated synchronization for users and groups for a given Environment.
  - Requires the C(WORKLOAD_IAM_SYNC) entitlement.
  - The module support check_mode.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  name:
    description:
      - The CDP Environment name or CRN to check.
    aliases:
      - environment
    required: True
    type: str
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Get the status of a sync event (non-WORKLOAD_IAM_SYNC)
- cloudera.cloud.env_automated_user_sync_info:
    name: example-env
"""

RETURN = r"""
sync:
    description: Returns an object describing of the status of the automated User and Group synchronization service.
    returned: success
    type: complex
    contains:
        environmentCrn:
            description: The environment CRN.
            returned: always
            type: str
        lastSyncStatus:
            description: Status of the last automated sync operation for the environment.
            returned: always
            type: dict
            contains:
                status:
                    description: The status of the sync.
                    returned: always
                    type: str
                    sample:
                        - UNKNOWN
                        - SUCCESS
                        - FAILED
                statusMessages:
                    description: Additional detail related to the status.
                    returned: when supported
                    type: list
                    elements: str
                timestamp:
                    description: A datetime stamp of when the sync was processed.
                    returned: always
                    type: str
        syncPendingState:
            description: The state indicating whether the environment is synced or has a sync pending.
            returned: always
            type: str
            sample:
                - UNKNOWN
                - SYNC_PENDING
                - SYNCED
                - SYNC_HALTED
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


class EnvironmentAutomatedUserSyncInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentAutomatedUserSyncInfo, self).__init__(module)

        # Set variables
        self.name = self.module.params["name"]

        # Initialize the return values
        self.sync = {}
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.sync = self.cdpy.environments.get_automated_sync_environment_status(
            self.name
        )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type="str", aliases=["environment"])
        ),
        supports_check_mode=True,
    )

    result = EnvironmentAutomatedUserSyncInfo(module)

    output = dict(
        changed=result.changed,
        sync=result.sync,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
