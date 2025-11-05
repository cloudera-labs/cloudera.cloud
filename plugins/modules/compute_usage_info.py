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
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from typing import Any

from ansible_collections.cloudera.runtime.plugins.module_utils.common import ServicesModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import AnsibleCdpClient


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
        client = AnsibleCdpClient(
            module=self.module,
            base_url=self.endpoint,
            access_key=self.access_key,
            private_key=self.private_key,
        )

        # TODO error handling for missing 'records' key
        self.records = client.list_compute_usage_records(
            from_timestamp=self.from_timestamp,
            to_timestamp=self.to_timestamp,
        ).get("records", [])


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
