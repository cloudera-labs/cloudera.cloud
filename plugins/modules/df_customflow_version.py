#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 Cloudera, Inc. All Rights Reserved.
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
module: df_customflow_version
short_description: Import CustomFlow versions into the DataFlow Catalog
description:
    - Import CustomFlow versions into the DataFlow Catalog
author:
  - "Andre Araujo (@asdaraujo)"
requirements:
  - cdpy
options:
  flow_crn:
    description:
      - The name of the CustomFlow into which the version will be imported.
    type: str
    required: True
  file:
    description:
      - The JSON file containing the CustomFlow definition to be imported as a new version.
    type: str
    required: True
  comments:
    description:
      - Comments associated to the version of the CustomFlow being imported.
    type: str
    default: None
    required: False
  state:
    description:
      - The declarative state of the CustomerFlow version
    type: str
    required: False
    default: present
    choices:
      - present
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Import a CustomFlow version into the DataFlow Catalog
- cloudera.cloud.df_customflow_version:
    name: my-customflow-version-name
    file: /tmp/my-custom-flow-v2.json
    comments: Second version
'''

RETURN = r'''
---
customflow_version:
  description: The CustomFlow Version Definition
  type: dict
  returned: always
  contains:
    crn:
      description: The artifact version CRN.
      returned: always
      type: str
    bucketIdentifier:
      description: The bucketIdentifier of the flow.
      returned: always
      type: str
    author:
      description: The author of the artifact.
      returned: always
      type: str
    version:
      description: The version of the artifact.
      returned: always
      type: int
    timestamp:
      description: The timestamp of the artifact.
      returned: always
      type: int
    deploymentCount:
      description: The number of deployments of the artifact.
      returned: always
      type: int
'''


class DFCustomFlowVersion(CdpModule):
    def __init__(self, module):
        super(DFCustomFlowVersion, self).__init__(module)

        # Set variables
        self.flow_crn = self._get_param('flow_crn')
        self.file = self._get_param('file')
        self.comments = self._get_param('comments')
        self.state = self._get_param('state')

        # Initialize return values
        self.flow_version = None
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        flow = self.cdpy.df.describe_customflow(self.flow_crn)
        if not flow:
            self.module.fail_json(msg="Flow definition with crn {} does not exist".format(self.flow_crn))
        else:
            # Only possible state is "present"
            self.changed = True
            if not self.module.check_mode:
                self.flow_version = self.cdpy.df.import_customflow_version(self.flow_crn, self.file, self.comments)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            flow_crn=dict(required=True, type='str'),
            file=dict(required=True, type='str'),
            comments=dict(required=False, type='str'),
            state=dict(type='str', choices=['present'], default='present'),
        ),
        supports_check_mode=True
    )

    result = DFCustomFlowVersion(module)
    output = dict(
        changed=result.changed,
        customflow_version=result.flow_version
    )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
