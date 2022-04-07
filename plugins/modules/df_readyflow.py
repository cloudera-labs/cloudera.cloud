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
module: df_readyflow
short_description: Import or Delete ReadyFlows from your CDP Tenant
description:
    - Import or Delete ReadyFlows from your CDP Tenant
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the ReadyFlow to be acted upon.
    type: str
    required: True
  state:
    description:
      - The declarative state of the ReadyFlow
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
notes:
  - This feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Import a ReadyFlow into your CDP Tenant
- cloudera.cloud.df_readyflow:
    name: my-readyflow-name

# Delete an added ReadyFlow from your CDP Tenant
- cloudera.cloud.df_readyflow:
    name: my-readyflow-name
    state: absent
'''

RETURN = r'''
---
readyflow:
  description: The ReadyFlow Definition
  type: dict
  returned: always
  contains:
    readyflowCrn:
      description:  
        - The DataFlow readyflow Definition's CRN.
        - Use this readyflowCrn to address this object
      returned: always
      type: str
    readyflow:
      description: The details of the ReadyFlow object
      type: dict
      returned: varies
      contains:
        readyflowCrn:
          description:
            - The general base CRN of this ReadyFlow
            - Different to the unique readyflowCrn containing a UUID4
          returned: always
          type: str
        name:
          description: The DataFlow Flow Definition's name.
          returned: always
          type: str
        author:
          description: Author of the most recent version.
          returned: always
          type: str
        summary:
          description: The ready flow summary (short).
          returned: always
          type: str
        description:
          description: The ready flow description (long).
          returned: always
          type: str
        documentationLink:
          description: A link to the ready flow documentation.
          returned: always
          type: str
        notes:
          description: Optional notes about the ready flow.
          returned: always
          type: str
        source:
          description: The ready flow data source.
          returned: always
          type: str
        sourceDataFormat:
          description: The ready flow data source format.
          returned: always
          type: str
        destination:
          description: The ready flow data destination.
          returned: always
          type: str
        destinationDataFormat:
          description: The ready flow data destination format.
          returned: always
          type: str
        imported:
          description: Whether the ready flow has been imported into the current account.
          returned: always
          type: bool         
        modifiedTimestamp:
          description: The timestamp the entry was last modified.
          returned: always
          type: int
    versions:
      description: The list of artifactDetail versions.
      returned: When imported is True
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
        comments:
          description: Comments about the version.
          returned: always
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


class DFReadyFlow(CdpModule):
    def __init__(self, module):
        super(DFReadyFlow, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.state = self._get_param('state')

        # Initialize internal values
        self.target = None
        self.listing = None

        # Initialize return values
        self.readyflow = None
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.listing = self.cdpy.df.list_readyflows(name=self.name)
        if not self.listing:  # return is list with one item if name exists, as name is unique
            self.module.fail_json(
                msg="ReadyFlow with Name %s is not found" % self.name)
        else:
            self.target = self.listing[0]
            if self.target['imported']:  # field is bool
                if self.state == 'present':
                    # ReadyFlow is imported and should be left alone
                    # helpfully return the detailed description
                    self.readyflow = self.cdpy.df.describe_added_readyflow(
                        def_crn=self.target['importedArtifactCrn']
                    )
                if self.state == 'absent':
                    if not self.module.check_mode:
                        # ReadyFlow is imported and should be deleted
                        self.readyflow = self.cdpy.df.delete_added_readyflow(
                            def_crn=self.target['importedArtifactCrn']
                        )
                        self.changed = True
                    else:
                        self.module.log(
                            "Check mode enabled, skipping deletion of %s" % self.name)
            else:
                if self.state == 'present':
                    # ReadyFlow should be imported
                    if not self.module.check_mode:
                        self.readyflow = self.cdpy.df.import_readyflow(
                            def_crn=self.target['readyflowCrn']
                        )
                        self.changed = True
                    else:
                        self.module.log(
                            "Check mode enabled, skipping import of %s" % self.name)
                if self.state == 'absent':
                    # ReadyFlow is not imported and should stay that way
                    self.module.log(
                        "ReadyFlow already not imported to CDP Tenant %s" % self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str'),
            state=dict(type='str', choices=['present', 'absent'],
                       default='present'),
        ),
        supports_check_mode=True
    )

    result = DFReadyFlow(module)
    output = dict(changed=result.changed, readyflow=result.readyflow)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
