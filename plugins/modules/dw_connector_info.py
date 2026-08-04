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
module: dw_connector_info
short_description: Gather information about CDP Data Warehouse Connectors
description:
    - Gather information about CDP Data Warehouse Connectors
    - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "3.4.0"
options:
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
    type: str
    required: true
    aliases:
      - id
  connector_id:
    description:
      - The ID of the connector to query.
      - Mutually exclusive with O(name).
    type: str
    aliases:
      - connector_identifier
  name:
    description:
      - The name of the connector to query.
      - Mutually exclusive with O(connector_id).
    type: str
attributes:
  check_mode:
    support: full
  diff_mode:
    support: N/A
  platform:
    platforms: all
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List all connectors in a cluster
- cloudera.cloud.dw_connector_info:
    cluster_id: example-cluster-id

# Get a specific connector by ID
- cloudera.cloud.dw_connector_info:
    cluster_id: example-cluster-id
    connector_id: example-connector-id

# Get a specific connector by name
- cloudera.cloud.dw_connector_info:
    cluster_id: example-cluster-id
    name: example-connector-name
"""

RETURN = r"""
connectors:
  description: The information about the connector(s)
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The unique identifier of the connector
      returned: always
      type: str
    name:
      description: The name of the connector
      returned: always
      type: str
    template:
      description: The template of the connector
      returned: always
      type: str
    crn:
      description: The CRN of the connector
      returned: always
      type: str
    description:
      description: User-provided description
      returned: when available
      type: str
    config:
      description: The connector configuration in key-value format
      returned: when available
      type: dict
    createdAt:
      description: The timestamp when the connector was created
      returned: always
      type: int
    createdBy:
      description: The CRN of the user who created the connector
      returned: always
      type: str
    updatedAt:
      description: The timestamp when the connector was last updated
      returned: always
      type: int
    updatedBy:
      description: The CRN of the user who last updated the connector
      returned: always
      type: str
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when debug is true
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when debug is true
  type: list
  elements: str
"""

from typing import Any, Dict, List

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
)


class DwConnectorInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                cluster_id=dict(
                    required=True,
                    type="str",
                    aliases=["id"],
                ),
                connector_id=dict(
                    type="str",
                    aliases=["connector_identifier"],
                ),
                name=dict(type="str"),
            ),
            mutually_exclusive=[["connector_id", "name"]],
            supports_check_mode=True,
        )

        self.cluster_id = self.get_param("cluster_id")
        self.connector_id = self.get_param("connector_id")
        self.name = self.get_param("name")

        self.connectors: List[Connector] = []

    def process(self):
        client = CdpDwClient(api_client=self.api_client)

        if self.connector_id is not None:
            connector = client.get_connector_by_id(self.cluster_id, self.connector_id)
            if connector is not None:
                self.connectors.append(connector)
        elif self.name is not None:
            connector = client.get_connector_by_name(self.cluster_id, self.name)
            if connector is not None:
                self.connectors.append(connector)
        else:
            self.connectors = client.list_connectors(self.cluster_id)


def main():
    result = DwConnectorInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        connectors=[to_dict(c) for c in result.connectors],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
