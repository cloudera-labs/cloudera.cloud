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
from ..module_utils.cdp_common import CdpModule


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: de
short_description: Create or Destroy CDP Data Engineering Workspaces
description:
    - Create or Destroy CDP Data Engineering Workspaces
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Alan Silva (@acsjumpi)"
requirements:
  - cdpy
options:
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''


class DEWorkspace(CdpModule):
    def __init__(self, module):
        super(DEWorkspace, self).__init__(module)

        # Set variablesj
        self.name = self._get_param('name')
        self.env = self._get_param('env')
        self.vcId = self._get_param('vcId')

        self.instance_type = self._get_param('instance_type')
        self.min_instances = self._get_param('min_instances')
        self.max_instances = self._get_param('max_instances')

        # Initialize return values
        self.cluster = {}

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name is not None:
            self.target = self.cdpy.de.describe_vc(cluster_id=self.name, env=self.env)
        else:
            self.target = None
            # If the Service exists
        if self.target is not None:
            # Delete the Workspace
            if self.state == 'absent':
                if self.module.check_mode:
                    self.service.append(self.target)
                else:
                    if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.warn("DE Service not in valid state for Delete operation: %s" % self.target['status'])
                    else:
                        self.cdpy.de.delete_vc(cluster_id=self.env, vc_id=self.vcId)
                    if self.wait:
                        self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_vc,
                            params=dict(cluster_id=self.env, vc_id=self.vcId),
                            field=None, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.cdpy.sdk.sleep(3)  # Wait for consistency sync
                        self.target = self.cdpy.dw.describe_cluster(cluster_id=self.env,vc_id=self.vcId)
                        self.clusters.append(self.target)
                        # Drop Done
            elif self.state == 'present':
            # Being Config check
                self.module.warn("DE Cluster already present and config validation is not implemented")
                if self.wait:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.dw.describe_vc,
                        params=dict(cluster_id=self.env,vc_id=self.vcId),
                        state='Running', delay=self.delay, timeout=self.timeout
                    )
                    self.clusters.append(self.target)
                    # End Config check
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End handling Cluster exists
        else:
            # Begin handling Cluster not found
            if self.state == 'absent':
                self.module.warn("DE CLuster %s already absent in Environment %s" % (self.name, self.env))
            elif self.state == 'present':
                if self.module.check_mode:
                    pass
                else:
                    self.name = self.cdpy.de.create_vc(name=self.name, cluster_id=self.env)
                    if self.wait:
                            self.target = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.describe_vc,
                                params=dict(cluster_id=self.env, vc_id=self.vcId),
                                state='Running', delay=self.delay, timeout=self.timeout
                            )
                    else:
                            self.target = self.cdpy.de.describe_vc(cluster_id=self.env, vc_id=self.vcId)
                            self.clusters.append(self.target)
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['name']),
            env=dict(required=False, type='str', aliases=['environment']),
            vcId=dict(required=false, type='str', aliases['vcId']),
            instance_type=dict(required=false, type='str', aliases['instance_type']),
            min_instances=dict(required=false, type='str', aliases['min_instances']),
            max_instances=dict(required=false, type='str', aliases['max_instances']),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            force=dict(required=False, type='bool', default=False),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        required_one_of=[['name', 'env', 'vcId'], ],
        supports_check_mode=True
    )

    result = DECluster(module)
    output = dict(changed=False, clusters=result.clusters)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
