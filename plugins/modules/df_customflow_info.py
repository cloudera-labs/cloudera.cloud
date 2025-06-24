#!/usr/bin/python
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

DOCUMENTATION = r"""
module: df_customflow_info
short_description: Gather information about CDP DataFlow CustomFlow Definitions
description:
    - Gather information about CDP DataFlow CustomFlow Definitions
author:
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.6.0"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that DataFlow Flow Definition will be described
    type: str
    required: False
  include_details:
    description:
      - If set to false, only a summary of each flow is returned
    type: bool
    required: False
    default: True
notes:
  - The feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List summary information about all Custom DataFlow Flow Definitions
- cloudera.cloud.df_customflow_info:

# Gather summary information about a specific DataFlow Flow Definition using a name
- cloudera.cloud.df_customflow_info:
    name: my-flow-name
    include_details: False
"""

RETURN = r"""
flows:
  description: The listing of CustomFlow Definitions in the DataFlow Catalog in this CDP Tenant
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description:  The DataFlow Flow Definition's CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Flow Definition's name.
      returned: always
      type: str
    modifiedTimestamp:
      description: The timestamp the entry was last modified.
      returned: always
      type: int
    versionCount:
      description: The number of versions uploaded to the catalog.
      returned: always
      type: str
    artifactType:
      description: The type of artifact
      type: str
      returned: when include_details is False
    createdTimestamp:
      description: The created timestamp.
      returned: when include_details is True
      type: int
    author:
      description: Author of the most recent version.
      returned: when include_details is True
      type: str
    description:
      description: The artifact description.
      returned: when include_details is True
      type: str
    versions:
      description: The list of artifactDetail versions.
      returned: when include_details is True
      type: list
      contains:
        crn:
          description: The flow version CRN.
          returned: when include_details is True
          type: str
        bucketIdentifier:
          description: The bucketIdentifier of the flow.
          returned: when include_details is True
          type: str
        author:
          description: The author of the flow.
          returned: when include_details is True
          type: str
        version:
          description: The version of the flow.
          returned: when include_details is True
          type: int
        timestamp:
          description: The timestamp of the flow.
          returned: when include_details is True
          type: int
        deploymentCount:
          description: The number of deployments of the flow.
          returned: when include_details is True
          type: int
        comments:
          description: Comments about the flow.
          returned: when include_details is True
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class DFCustomFlowInfo(CdpModule):
    def __init__(self, module):
        super(DFCustomFlowInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.include_details = self._get_param("include_details")

        # Initialize internal values
        self.listing = []

        # Initialize return values
        self.flows = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.listing = self.cdpy.df.list_flow_definitions(name=self.name)
        if self.include_details:
            self.flows = [
                self.cdpy.df.describe_customflow(x["crn"])
                for x in self.listing
                if x["artifactType"] == "flow"  # ReadyFlow have different fields
            ]
        else:
            self.flows = self.listing


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str"),
            include_details=dict(required=False, type="bool", default=True),
        ),
        supports_check_mode=True,
    )

    result = DFCustomFlowInfo(module)
    output = dict(changed=False, flows=result.flows)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
