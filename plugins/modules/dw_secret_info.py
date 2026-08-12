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
---
module: dw_secret_info
short_description: Gather information about CDP Data Warehouse secrets
description:
  - Gather information about CDW (Cloudera Data Warehouse) secrets in a cluster.
  - Optionally filter by secret name (exact match).
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
version_added: "3.4.0"
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
options:
  cluster_id:
    description:
      - The ID of the CDW cluster.
    type: str
    required: true
    aliases:
      - id
  name:
    description:
      - The name of the secret to retrieve.
      - Filters results to the secret whose C(secretName) exactly matches this value.
    type: str
    required: false
    aliases:
      - secret_name
attributes:
  check_mode:
    support: full
  diff_mode:
    support: N/A
  platform:
    platforms: all
"""

EXAMPLES = r"""
- name: List all secrets in a CDW cluster
  cloudera.cloud.dw_secret_info:
    cluster_id: "env-abc123"

- name: Retrieve a specific secret by name
  cloudera.cloud.dw_secret_info:
    cluster_id: "env-abc123"
    name: "my-secret"

- name: List secrets using cluster ID alias
  cloudera.cloud.dw_secret_info:
    id: "env-abc123"
    secret_name: "my-db-password"
"""

RETURN = r"""
secrets:
  description: A list of CDW secrets.
  returned: always
  type: list
  elements: dict
  contains:
    secretName:
      description: The user-facing name of the secret.
      type: str
      returned: when available
    secretProviderKey:
      description: The provider key name associated with the secret.
      type: str
      returned: when available
    createdBy:
      description: The CRN of the user who created the secret.
      type: str
      returned: when available
    properties:
      description: The properties of the secret.
      type: dict
      returned: when available
      contains:
        azureVaultName:
          description: The name of the Azure Key Vault.
          type: str
          returned: when available
        cloudProvider:
          description: The cloud provider associated with the secret.
          type: str
          returned: when available
        version:
          description: The version of the secret.
          type: str
          returned: when available
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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    DwSecret,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)


class DwSecretInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                cluster_id=dict(required=True, type="str", aliases=["id"]),
                name=dict(required=False, type="str", aliases=["secret_name"]),
            ),
            supports_check_mode=True,
        )
        self.cluster_id = self.get_param("cluster_id")
        self.name = self.get_param("name")

        self.secrets: List[DwSecret] = []

    def process(self):
        client = CdpDwClient(api_client=self.api_client)
        secrets = client.list_secrets(self.cluster_id)

        if self.name is not None:
            secrets = [s for s in secrets if s.secretName == self.name]

        self.secrets = secrets


def main():
    result = DwSecretInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        secrets=[to_dict(s) for s in result.secrets],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
