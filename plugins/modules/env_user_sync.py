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
module: env_user_sync
short_description: Sync CDP Users and Groups to Environments
description:
  - Synchronize users and groups with one or more CDP environments.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
options:
  name:
    description:
      - A single Environment or list of Environments that will sync all CDP Users and Groups.
      - If not present, all Environments will be synced.
      - Mutually exclusive with I(current_user).
    aliases:
      - environment
    required: False
    type: list
    elements: str
  current_user:
    description:
      - Sync the current CDP user as defined by the C(CDP_PROFILE) with all environments.
      - Mutually exclusive with I(name).
    aliases:
      - user
    required: False
    type: bool
  wait:
    description:
      - Flag to enable internal polling to wait for the user sync operation to complete.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the sync operation to complete.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the sync operation to complete.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
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

# Sync a CDP Environment
- cloudera.cloud.env_user_sync:
    name: example-environment

# Sync multiple CDP Environments
- cloudera.cloud.env_user_sync:
    name:
      - example-environment
      - another-environment

# Sync the current CDP User
- cloudera.cloud.env_user_sync:
    current_user: true
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
            description: UUID of the request for this operation.
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


class EnvironmentUserSync(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["environment"],
                ),
                current_user=dict(
                    required=False,
                    type="bool",
                    aliases=["user"],
                ),
                wait=dict(required=False, type="bool", default=True),
                delay=dict(
                    required=False,
                    type="int",
                    aliases=["polling_delay"],
                    default=15,
                ),
                timeout=dict(
                    required=False,
                    type="int",
                    aliases=["polling_timeout"],
                    default=3600,
                ),
            ),
            mutually_exclusive=[["name", "current_user"]],
            supports_check_mode=True,
        )

        self.name = self.get_param("name")
        self.current_user = self.get_param("current_user")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        self.sync: Optional[SyncStatus] = None
        self.changed = False

    def process(self):
        if self.module.check_mode:
            return

        client = CdpEnvClient(api_client=self.api_client)

        if self.current_user:
            resp = client.sync_user()
        else:
            resp = client.sync_all_users(self.name)

        self.changed = True

        if self.wait:
            self.sync = client.wait_for_sync(
                operation_id=resp.operationId,
                timeout=self.timeout,
                delay=self.delay,
            )
        else:
            self.sync = resp


def main():
    result = EnvironmentUserSync()

    output: Dict[str, Any] = dict(
        changed=result.changed,
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
