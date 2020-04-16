#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Cloudera, Inc. All Rights Reserved.
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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
module: env_user_sync
short_description: Sync CDP Users and Groups to Environments
description:
  - Synchronize users and groups with one or more CDP environments.
  - The module support check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
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
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the datalake to achieve the declared 
            state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the datalake to achieve the declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
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
    current_user: yes
'''

RETURN = r'''
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
'''


class EnvironmentUserSync(CdpModule):
    def __init__(self, module):
        super(EnvironmentUserSync, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.current_user = self._get_param('current_user')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize the return values
        self.sync = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if not self.module.check_mode:
            if self.current_user:
                resp = self.cdpy.environments.sync_current_user()
            else:
                resp = self.cdpy.environments.sync_users(self.name)
            self.changed = True
            if self.wait:
                self.sync = self.cdpy.sdk.wait_for_state(
                    describe_func=self.cdpy.environments.get_sync_status,
                    params=dict(operation=resp['operationId']),
                    state='COMPLETED',
                    delay=self.delay,
                    timeout=self.timeout
                )
            else:
                self.sync = resp


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='list', aliases=['environment']),
            current_user=dict(required=False, type='bool', aliases=['user']),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        mutually_exclusive=(
            ['name', 'current_user']
        ),
        supports_check_mode=True
    )

    result = EnvironmentUserSync(module)

    output = dict(
        changed=result.changed,
        sync=result.sync,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
