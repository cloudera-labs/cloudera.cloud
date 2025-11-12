#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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
module: compute_usage_info
short_description: Gather information about compute usage records
description:
  - Gather information about compute usage records for a Cloudera on cloud tenant.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "3.2.0"
options:
  from_timestamp:
    description:
      - The starting timestamp (ISO format) for the search range (inclusive).
    type: str
    required: True
  to_timestamp:
    description:
      - The ending timestamp (ISO format) for the search range (exclusive).
    type: str
    required: True
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Gather information about compute usage records
  cloudera.cloud.compute_usage_info:
    from_timestamp: "2023-01-01T00:00:00Z"
    to_timestamp: "2023-01-31T23:59:59Z"
"""

RETURN = r"""
records:
  description:
    - Returns a list of compute usage records.
    - Each record represents the aggregated hourly usage.
  returned: always
  type: list
  elements: dict
  contains:
    cloud_provider:
      description: The cloud provider for the running cluster.
      returned: when supported
      type: str
      sample: AWS
    cluster_crn:
      description: The cluster CRN.
      returned: when supported
      type: str
    cluster_name:
      description: The cluster name.
      returned: always
      type: str
    cluster_template:
      description: The template used to create the cluster.
      returned: when supported
      type: str
    cluster_type:
      description: The cluster type.
      returned: always
      type: str
      sample: Data Engineering
    environment_crn:
      description: The environment CRN for the cluster.
      returned: always
      type: str
    environment_name:
      description: The environment name for the cluster.
      returned: always
      type: str
    gross_charge:
      description: Number of credits consumed for the compute usage record.
      returned: always
      type: float
    hours:
      description: Total number of hours for which the instances were running.
      returned: always
      type: float
    instance_count:
      description: Total number of instances in use.
      returned: always
      type: int
    instance_type:
      description: The instance type for the cluster.
      returned: always
      type: str
    list_rate:
      description: Rate in credits at which usage is charged for given cluster type, instance type, and cloud provider.
      returned: always
      type: float
    quantity:
      description: Quantity of usage of the cluster.
      returned: always
      type: float
    quantity_type:
      description: Type of usage by the cluster.
      returned: always
      type: float
      sample:
        - INSTANCE_USAGE
        - COMPUTE_USAGE
    service_feature:
      description: The service feature for the cluster.
      returned: when supported
      type: str
    usage_end_timestamp:
      description: Timestamp of end of the usage (ISO format).
      returned: always
      type: str
    usage_start_timestamp:
      description: Timestamp of start of the usage (ISO format).
      returned: always
      type: str
    user_tags:
      description:
        - User-defined tags assigned to the cluster.
        - Returns a JSON-encoded string of key-value pairs.
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

from typing import Any

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_consumption import (
    CdpConsumptionClient,
)


class ConsumptionComputeUsageRecordsInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                to_timestamp=dict(required=True, aliases=["to"]),
                from_timestamp=dict(required=True, aliases=["from"]),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.to_timestamp = self.get_param("to_timestamp")
        self.from_timestamp = self.get_param("from_timestamp")

        # Initialize the return values
        self.records = []

    def process(self):
        client = CdpConsumptionClient(api_client=self.api_client)

        result = client.list_compute_usage_records(
            from_timestamp=self.from_timestamp,
            to_timestamp=self.to_timestamp,
        )

        self.records = [
            camel_dict_to_snake_dict(record) for record in result.get("records", [])
        ]


def main():
    result = ConsumptionComputeUsageRecordsInfo()

    output: dict[str, Any] = dict(
        changed=False,
        records=result.records,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
