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
---
module: env_user_sync_info
short_description: Get the status of a CDP Users and Groups sync
description:
  - Get the status of a synchronization event for users and groups with one or more CDP environments.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Daniel Chaffelson (@chaffelson)"
  - "Jim Enright (@jimright)"
version_added: "1.0.0"
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
options:
  name:
    description:
      - The C(operation id) for a User and Group sync event or the C(operation CRN) for the event if the C(WORKLOAD_IAM_SYNC) entitlement is enabled.
    aliases:
      - operation_id
      - operation_crn
    required: True
    type: str
attributes:
  check_mode:
    support: full
  diff_mode:
    support: N/A
  platform:
    platforms: all
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
    SyncStatus,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)


class EnvironmentUserSyncInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=True,
                    type="str",
                    aliases=["operation_id", "operation_crn"],
                ),
            ),
            supports_check_mode=True,
        )

        self.name = self.get_param("name")
        self.sync: Optional[SyncStatus] = None

    def process(self):
        client = CdpEnvClient(api_client=self.api_client)
        self.sync = client.get_sync_status(self.name)


def main():
    result = EnvironmentUserSyncInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        sync=to_dict(result.sync) if result.sync else {},
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
