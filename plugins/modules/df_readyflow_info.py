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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: df_readyflow_info
short_description: Gather information about CDP DataFlow ReadyFlow Definitions
description:
    - Gather information about CDP DataFlow ReadyFlow Definitions
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that DataFlow ReadyFlow Definition will be described
    type: str
    required: False
  include_details:
    description:
      - If set to false, only a summary of each ReadyFlow Definition is returned
    type: bool
    required: False
    default: True

notes:
  - This feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List summary information about all Custom DataFlow ReadyFlow Definitions
- cloudera.cloud.df_readyflow_info:

# Gather summary information about a specific DataFlow Flow Definition using a name
- cloudera.cloud.df_readyflow_info:
    name: my-flow-name
"""

RETURN = r"""
---
flows:
  description: The listing of ReadyFlow Definitions in the DataFlow Catalog in this CDP Tenant
  type: list
  returned: always
  elements: complex
  contains:
    addedReadyflowCrn:
      description:
        - The CRN of this readyflow when it is imported to the CDP Tenant
        - Use this readyflowCrn to address this object when doing deployments
      returned: when readyflow imported is True
      type: str
    readyflow:
      description: The details of the ReadyFlow object
      type: dict
      returned: always
      elements: complex
      contains:
        readyflowCrn:
          description:
            - The CRN of this readyflow in the Control Plane
            - Different to the addedReadyflowCrn of the imported readyflow within the CDP Tenant
            - Use this readyflowCrn when importing the object to your CDP Tenant
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
"""


class DFReadyFlowInfo(CdpModule):
    def __init__(self, module):
        super(DFReadyFlowInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")

        # Initialize internal values
        self.listing = []

        # Initialize return values
        self.flows = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.listing = self.cdpy.df.list_readyflows(name=self.name)
        if self.listing:
            self.flows = []
            for this_readyflow in self.listing:
                if this_readyflow["imported"]:
                    self.flows.append(
                        self.cdpy.df.describe_added_readyflow(
                            def_crn=this_readyflow["importedArtifactCrn"]
                        )
                    )
                else:
                    self.flows.append(
                        self.cdpy.df.describe_readyflow(
                            def_crn=this_readyflow["readyflowCrn"]
                        )
                    )
        else:
            self.flows = self.listing


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str"),
        ),
        supports_check_mode=True,
    )

    result = DFReadyFlowInfo(module)
    output = dict(changed=False, flows=result.flows)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
