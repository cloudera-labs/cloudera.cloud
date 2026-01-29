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
module: df_readyflow_info
short_description: Gather information about CDP DataFlow ReadyFlow Definitions
description:
    - Gather information about CDP DataFlow ReadyFlow Definitions
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.6.0"
options:
  search_term:
    description:
      - Search term to filter ReadyFlows (matches name, summary, or other fields)
      - If no search_term is provided, all ReadyFlows are returned
    type: str
    required: False
    aliases:
      - name
notes:
  - This feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Gather information about all DataFlow ReadyFlows
   cloudera.cloud.df_readyflow_info:

- name: Gather information about ReadyFlows matching a search term
  cloudera.cloud.df_readyflow_info:
    search_term: "Kafka"

- name: Gather information about a specific DataFlow ReadyFlow
  cloudera.cloud.df_readyflow_info:
    name: "Kafka to S3 Avro"
"""

RETURN = r"""
readyflows:
  description: Returns a list of ReadyFlow details from the DataFlow catalog
  type: list
  returned: always
  elements: dict
  contains:
    readyflowCrn:
      description: The CRN of the ReadyFlow
      returned: always
      type: str
    name:
      description: The ReadyFlow name
      returned: always
      type: str
    author:
      description: The author of the most recent version
      returned: always
      type: str
    summary:
      description: The ReadyFlow summary (short description)
      returned: when supported
      type: str
    description:
      description: The ReadyFlow description (long description)
      returned: when supported
      type: str
    source:
      description: The ReadyFlow data source
      returned: when supported
      type: str
    sourceDataFormat:
      description: The ReadyFlow data source format
      returned: when supported
      type: str
    destination:
      description: The ReadyFlow data destination
      returned: when supported
      type: str
    destinationDataFormat:
      description: The ReadyFlow data destination format
      returned: when supported
      type: str
    documentationLink:
      description: A link to the ReadyFlow documentation
      returned: when supported
      type: str
    imported:
      description: Whether the ReadyFlow has been imported into the current account
      returned: when supported
      type: bool
    modifiedTimestamp:
      description: The modified timestamp
      returned: when supported
      type: int
    notes:
      description: Optional notes about the ReadyFlow
      returned: when supported
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


class DFReadyFlowInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                search_term=dict(required=False, type="str", aliases=["name"]),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.search_term = self.get_param("search_term")

        # Initialize DF client
        self.client = CdpDfClient(api_client=self.api_client)

        # Initialize return values
        self.readyflows = []

    def process(self):
        result = self.client.list_readyflows(search_term=self.search_term)
        readyflow_list = result.get("readyflows", [])

        for readyflow in readyflow_list:
            details = self.client.describe_readyflow(
                readyflow_crn=readyflow["readyflowCrn"],
            )
            readyflow_detail = details.get("readyflowDetail", details)
            self.readyflows.append(readyflow_detail)


def main():
    result = DFReadyFlowInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        readyflows=result.readyflows,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
