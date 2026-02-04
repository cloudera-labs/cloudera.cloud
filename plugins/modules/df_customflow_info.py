#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
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
short_description: Gather information about CDP DataFlow Custom Flow Definitions
description:
    - Gather information about CDP DataFlow Custom Flow Definitions
    - Custom flows are user-created flow definitions uploaded to the DataFlow catalog
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.6.0"
options:
  search_term:
    description:
      - If a search term is provided, flows matching this term will be returned
      - Searches by flow name
    type: str
    required: False
    aliases:
      - name
  include_details:
    description:
      - If set to false, only a summary of each flow is returned
      - If set to true, detailed information including versions is returned
    type: bool
    required: False
    default: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all DataFlow Custom Flows (summary only)
- cloudera.cloud.df_customflow_info:

# Search for flows matching a name (summary only)
- cloudera.cloud.df_customflow_info:
    search_term: my-custom-flow

# Search for flows matching a name with detailed information
- cloudera.cloud.df_customflow_info:
    search_term: my-custom-flow
    include_details: true

# Using the 'name' alias (backward compatibility)
- cloudera.cloud.df_customflow_info:
    name: my-custom-flow
"""

RETURN = r"""
flows:
  description: The information about the named DataFlow Custom Flow or DataFlow Custom Flows
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description: The artifact CRN
      returned: always
      type: str
    name:
      description: The artifact name
      returned: always
      type: str
    artifactType:
      description: The type of artifact
      returned: always
      type: str
    versionCount:
      description: The number of versions uploaded to the catalog
      returned: always
      type: int
    modifiedTimestamp:
      description: The modified timestamp (milliseconds since epoch)
      returned: when available
      type: int
    collectionCrn:
      description: The collection CRN
      returned: when available
      type: str
    collectionName:
      description: The collection name
      returned: when available
      type: str
    createdTimestamp:
      description: The created timestamp (milliseconds since epoch)
      returned: when include_details is True
      type: int
    author:
      description: Author of the most recent version
      returned: when include_details is True
      type: str
    description:
      description: The artifact description
      returned: when include_details is True
      type: str
    versions:
      description: The list of flow versions
      returned: when include_details is True
      type: list
      elements: dict
      contains:
        crn:
          description: The flow version CRN
          returned: always
          type: str
        bucketIdentifier:
          description: The bucketIdentifier of the flow
          returned: when available
          type: str
        author:
          description: The author of the flow
          returned: when available
          type: str
        version:
          description: The version of the flow
          returned: when available
          type: int
        timestamp:
          description: The timestamp of the flow (milliseconds since epoch)
          returned: when available
          type: int
        deploymentCount:
          description: The number of deployments of the flow
          returned: when available
          type: int
        draftCount:
          description: The number of draft flows associated with the version
          returned: when available
          type: int
        tags:
          description: The list of tags associated with the flow version
          returned: when available
          type: list
          elements: dict
          contains:
            tagName:
              description: The name of the version tag
              returned: always
              type: str
            tagColor:
              description: The color of the version tag
              returned: when available
              type: str
        comments:
          description: Comments about the flow
          returned: when available
          type: str
sdk_out:
  description: Returns the captured API HTTP log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured API HTTP log.
  returned: when supported
  type: list
  elements: str
"""

from typing import Any, Dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
)


class DFCustomFlowInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                search_term=dict(required=False, type="str", aliases=["name"]),
                include_details=dict(required=False, type="bool", default=False),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.search_term = self.get_param("search_term")
        self.include_details = self.get_param("include_details")

        # Initialize return values
        self.flows = []

    def process(self):
        client = CdpDfClient(api_client=self.api_client)

        response = client.list_flow_definitions(search_term=self.search_term)
        flows = response.get("flows", [])

        if self.include_details:
            for flow_details in flows:
                if flow_details.get("artifactType") == "flow":
                    flow_detail = client.describe_flow(flow_details["crn"])
                    if flow_detail:
                        self.flows.append(flow_detail.get("flowDetail", flow_details))
                else:
                    self.flows.append(flow_details)
        else:
            self.flows = flows


def main():
    result = DFCustomFlowInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        flows=result.flows,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
