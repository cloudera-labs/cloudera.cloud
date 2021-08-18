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
module: de_info
short_description: Gather information about CDP DE Workspaces
description:
    - Gather information about CDP DE Workspaces
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Alan Silva (@acsjumpi)"
requirements:
  - cdpy
options:
  id:
    description:
      - If a name is provided, that Data Warehouse Cluster will be described.
      - environment must be provided if using name to retrieve a Cluster
    type: str
    required: False
    aliases:
      - name
  environment:
    description:
      - The name of the Environment in which to find and describe the Data Warehouse Clusters.
      - Required with name to retrieve a Cluster
    type: str
    required: False
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

class DEInfo(CdpModule):
    def __init__(self, module):
        super(DEInfo, self).__init__(module)

        # Set variables
        self.id = self._get_param('name')
        self.env = self._get_param('environment')

        # Initialize return values
        self.cluster = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.id is not None:  # Note that both None and '' will trigger this
            cluster_single = self.cdpy.de.describe_vc(name=self.id, env=self.env)
            if cluster_single is not None:
                self.cluster.append(cluster_single)
        else:
            self.cluster = self.cdpy.de.list_vcs(self.id)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            id=dict(required=False, type='str', aliases=['workspace']),
            env=dict(required=False, type='str', aliases=['env']),
        ),
        supports_check_mode=True,
    )

    result = DEInfo(module)
    output = dict(changed=False, service=result.service)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
