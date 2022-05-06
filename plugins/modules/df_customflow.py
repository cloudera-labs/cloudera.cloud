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
module: df_customflow
short_description: Import or Delete CustomFlows into the DataFlow Catalog
description:
  - Import or Delete CustomFlows into the DataFlow Catalog
author:
  - "Andre Araujo (@asdaraujo)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the CustomFlow to be acted upon.
    type: str
    required: True
  file:
    description:
      - The JSON file containing the CustomFlow definition to be imported.
    type: str
    default: None
    required: True, if state==present. False, otherwise
  description:
    description:
      - The description of the CustomFlow.
    type: str
    default: None
    required: False
  comments:
    description:
      - Comments associated to the initial version of the CustomFlow.
    type: str
    default: None
    required: False
  state:
    description:
      - The declarative state of the CustomFlow
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Import a CustomFlow into the DataFlow Catalog
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    file: /tmp/my-custom-flow.json
    description: My sample CDF flow
    comments: Initial version

# Delete a CustomFlow from the DataFlow Catalog
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    state: absent
'''

RETURN = r'''
---
customflow:
  description: The CustomFlow Definition
  type: dict (or None if state = absent and flow does not exist)
  returned: always
  contains:
    crn:
      description:  
        - The DataFlow CustomFlow's CRN.
        - Use this crn to address this object
      returned: always
      type: str
    name:
      description: The DataFlow CustomFlow's name.
      returned: always
      type: str
    versionCount:
      description: Number of versions contained in this CustomFlow.
      returned: always
      type: int
    createdTimestamp:
      description: The timestamp the entry was created.
      returned: always
      type: int
    modifiedTimestamp:
      description: The timestamp the entry was last modified.
      returned: always
      type: int
    versions:
      description: The list of artifactDetail versions.
      returned: always
      type: list
      elements: dict
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


class DFCustomFlow(CdpModule):
    def __init__(self, module):
        super(DFCustomFlow, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.file = self._get_param('file')
        self.description = self._get_param('description')
        self.comments = self._get_param('comments')
        self.state = self._get_param('state')

        # Initialize return values
        self.flow = None
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.flow = self.cdpy.df.list_flow_definitions(name=self.name)
        if self.flow:
            # return is list with one item if name exists, since name is unique
            self.flow = self.flow[0]
            if self.state == 'present':
                # Flow already exists and should be left alone
                # helpfully return the detailed description
                self.flow = self.cdpy.df.describe_customflow(def_crn=self.flow['crn'])
            elif self.state == 'absent':
                self.changed = True
                if not self.module.check_mode:
                    # Flow exists and should be deleted
                    self.flow = self.cdpy.df.delete_customflow(def_crn=self.flow['crn'])
                else:
                    self.module.log("Check mode enabled, skipping deletion of flow [{}]".format(self.name))
        else:
            if self.state == 'present':
                # Flow should be imported
                self.changed = True
                if not self.module.check_mode:
                    self.flow = self.cdpy.df.import_customflow(
                        def_file=self.file,
                        name=self.name,
                        description=self.description,
                        comments=self.comments
                    )
                else:
                    self.module.log("Check mode enabled, skipping import of flow [{}]".format(self.name))
            if self.state == 'absent':
                # Flow does not exist. Nothing to do.
                self.module.log("Flow [{}] does not exist".format(self.name))


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str'),
            file=dict(required=False, type='str'),
            description=dict(required=False, type='str'),
            comments=dict(required=False, type='str'),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
        ),
        required_if=[
            ('state', 'present', ('file',)),
        ],
        supports_check_mode=True
    )

    result = DFCustomFlow(module)
    output = dict(
        changed=result.changed,
        customflow=result.flow or None,
    )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
