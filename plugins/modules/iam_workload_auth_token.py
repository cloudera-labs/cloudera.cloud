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
module: iam_workload_auth_token
short_description: Generate authentication token for CDP workload APIs
description:
    - Generates an authentication token which is required for sending requests to workload APIs.
    - The token can be used to authenticate API calls to workload services like Data Engineering (DE), DataFlow (DF), or Operational Database (OPDB).
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "3.2.0"
options:
  workload_name:
    description:
      - The workload name for which to generate the authentication token.
      - Must be one of DE (Data Engineering), DF (DataFlow), or OPDB (Operational Database).
    type: str
    required: True
    choices:
      - DE
      - DF
      - OPDB
    aliases:
      - workload
  environment_crn:
    description:
      - The environment CRN, required by DF workloads.
      - This should be the CRN of the CDP environment where the DataFlow service is running.
    type: str
    required: False
    aliases:
      - env_crn
  exclude_groups:
    description:
      - Whether to exclude the 'groups' claim from the token.
    type: bool
    required: False
    default: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Generate workload auth token for Data Engineering
  cloudera.cloud.iam_workload_auth_token:
    workload_name: DE

- name: Generate workload auth token for Operational Database
  cloudera.cloud.iam_workload_auth_token:
    workload_name: OPDB

- name: Generate workload auth token for DataFlow with environment
  cloudera.cloud.iam_workload_auth_token:
    workload_name: DF
    environment_crn: crn:cdp:environments:us-west-1:123456-8867-4357-8524-123465:environment:61eb5b97-226a-4be7-b56e-78d4e5d8c7e3
"""

RETURN = r"""
workload_auth_token:
  description: The information about the generated workload authentication token
  type: dict
  returned: always
  contains:
    token:
      description: The authentication token to use for workload API calls.
      type: str
      returned: on success
      sample: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    endpoint_url:
      description: The workload endpoint URL where the token should be used.
      type: str
      returned: when workload_name is DF
      sample: "https://service.us-west-1.workload.cloudera.site/api"
    expire_at:
      description: The date and time when the token will expire.
      type: str
      returned: on success
      sample: "2026-01-22T14:30:00.000Z"
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

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)

class IAMWorkloadAuthToken(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                workload_name=dict(
                    required=True,
                    type="str",
                    choices=["DE", "DF", "OPDB"],
                    aliases=["workload"],
                ),
                environment_crn=dict(
                    required=False,
                    type="str",
                    aliases=["env_crn"],
                ),
                exclude_groups=dict(
                    required=False,
                    type="bool",
                    default=False,
                ),
            ),
            required_if=[
                ("workload_name", "DF", ("environment_crn",)),
            ],
            supports_check_mode=False,
        )

        # Set parameters
        self.workload_name = self.get_param("workload_name")
        self.environment_crn = self.get_param("environment_crn")
        self.exclude_groups = self.get_param("exclude_groups")

        # Initialize the return values
        self.workload_auth_token = {}

        # Initialize client
        self.client = CdpIamClient(api_client=self.api_client)

    def process(self):
        result = self.client.generate_workload_auth_token(
            workload_name=self.workload_name,
            environment_crn=self.environment_crn,
            exclude_groups=self.exclude_groups,
        )

        self.workload_auth_token = camel_dict_to_snake_dict(result)


def main():
    result = IAMWorkloadAuthToken()

    output: Dict[str, Any] = dict(
        changed=True,
        workload_auth_token=result.workload_auth_token,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
