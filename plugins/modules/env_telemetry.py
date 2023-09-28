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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: env_telemetry
short_description: Set CDP environment telemetry
description:
    - Set a CDP environment deployment log collection and workload analytics.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The targeted environment.
    type: str
    required: True
    aliases:
      - environment
  workload_analytics:
    description:
      - A flag to specify the availability of the environment's workload analytics.
    type: bool
    required: False
    aliases:
      - analytics
  logs_collection:
    description:
      - A flag to specify the availability of the environment's deployment log collection.
    type: bool
    required: False
    aliases:
      - report_deployment_logs
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Turn off both workload analytics and log collection
- cloudera.cloud.env_telemetry:
    name: the-environment
    workload_analytics: no
    logs_collection: no
'''

RETURN = r'''
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


class EnvironmentTelemetry(CdpModule):
    def __init__(self, module):
        super(EnvironmentTelemetry, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.workload_analytics = self._get_param('workload_analytics')
        self.logs_collection = self._get_param('logs_collection')

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if not self.module.check_mode:
            self.cdpy.environments.set_telemetry(
                name=self.name,
                workload_analytics=self.workload_analytics,
                logs_collection=self.logs_collection)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['environment']),
            workload_analytics=dict(required=False, type='bool', aliases=['analytics']),
            logs_collection=dict(required=False, type='bool', aliases=['logs', 'report_deployment_logs'])
        ),
        supports_check_mode=True
    )

    result = EnvironmentTelemetry(module)
    output = dict(changed=True)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
