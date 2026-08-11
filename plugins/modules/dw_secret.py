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
module: dw_secret
short_description: Create, register, and delete CDP Data Warehouse secrets
description:
  - Manage secrets for a CDP Data Warehouse (CDW) cluster.
  - A secret is provisioned by one of two mutually exclusive approaches.
  - Creation stores the secret value in the cluster's Kubernetes metadata via O(secret_value).
  - Registration references a secret already held in the cloud provider's vault via O(secret_provider_key).
  - Secrets are immutable; an existing secret is left unchanged. To alter one, delete it and provision it again.
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
  name:
    description:
      - The name of the secret.
    type: str
    required: true
    aliases:
      - secret_name
  secret_value:
    description:
      - The value (contents) of the secret to store in the cluster's Kubernetes
        metadata.
      - Selects the creation approach and is mutually exclusive with
        O(secret_provider_key).
      - Required for O(state=present) if O(secret_provider_key) is not set.
    type: str
  secret_provider_key:
    description:
      - The key of a secret already stored in the cloud provider's vault.
      - Selects the registration approach and is mutually exclusive with
        O(secret_value).
      - Required for O(state=present) if O(secret_value) is not set.
    type: str
    aliases:
      - provider_key
  azure_vault_name:
    description:
      - The name of the Azure Key Vault holding the secret.
      - Only used with O(secret_provider_key) when registering an Azure secret.
    type: str
  state:
    description:
      - The declarative state of the secret.
      - V(present) provisions the secret if it does not exist (idempotent);
        existing secrets are left unchanged because secrets are immutable.
      - V(absent) deletes the secret if it exists (idempotent).
    type: str
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  platform:
    platforms: all
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Create a Kubernetes-stored secret
  cloudera.cloud.dw_secret:
    cluster_id: example-cluster-id
    name: mydbpassword
    secret_value: "{{ vaulted_db_password }}"
    state: present

- name: Register a secret from an Azure Key Vault
  cloudera.cloud.dw_secret:
    cluster_id: example-cluster-id
    name: myregisteredsecret
    secret_provider_key: my-provider-key
    azure_vault_name: my-key-vault
    state: present

- name: Register a secret from a cloud provider vault (non-Azure)
  cloudera.cloud.dw_secret:
    cluster_id: example-cluster-id
    name: awssecret
    secret_provider_key: "arn:aws:secretsmanager:us-west-2:1234567890:secret:my-secret"

- name: Delete a secret
  cloudera.cloud.dw_secret:
    cluster_id: example-cluster-id
    name: mydbpassword
    state: absent
"""

RETURN = r"""
secret:
  description: The details of the CDP Data Warehouse secret.
  returned: always
  type: dict
  contains:
    secretName:
      description: The user-facing name of the secret.
      returned: when available
      type: str
    secretProviderKey:
      description: The provider key name associated with the secret.
      returned: when available
      type: str
    createdBy:
      description: The CRN of the user who created the secret.
      returned: when available
      type: str
    properties:
      description: The properties of the secret.
      returned: when available
      type: dict
      contains:
        azureVaultName:
          description: The name of the Azure Key Vault.
          returned: when available
          type: str
        cloudProvider:
          description: The cloud provider associated with the secret.
          returned: when available
          type: str
        version:
          description: The version of the secret.
          returned: when available
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    DwSecret,
    DwSecretProperties,
)


class DwSecretModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                cluster_id=dict(
                    required=True,
                    type="str",
                    aliases=["id"],
                ),
                name=dict(
                    required=True,
                    type="str",
                    aliases=["secret_name"],
                ),
                secret_value=dict(type="str", no_log=True),
                secret_provider_key=dict(
                    type="str",
                    aliases=["provider_key"],
                ),
                azure_vault_name=dict(type="str"),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            mutually_exclusive=[
                ["secret_value", "secret_provider_key"],
            ],
            required_if=[
                # For present, exactly one provisioning approach must be supplied.
                ("state", "present", ("secret_value", "secret_provider_key"), True),
            ],
            required_by={
                "azure_vault_name": ["secret_provider_key"],
            },
            supports_check_mode=True,
        )

        self.cluster_id = self.get_param("cluster_id")
        self.name = self.get_param("name")
        self.secret_value = self.get_param("secret_value")
        self.secret_provider_key = self.get_param("secret_provider_key")
        self.azure_vault_name = self.get_param("azure_vault_name")
        self.state = self.get_param("state")

        self.secret: Optional[DwSecret] = None
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

    def process(self):
        client = CdpDwClient(api_client=self.api_client)

        existing = client.get_secret(self.cluster_id, self.name)

        if self.state == "absent":
            if existing is not None:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = to_dict(existing)
                if not self.module.check_mode:
                    client.delete_secret(self.cluster_id, self.name)
            return

        # state == "present"
        if existing is not None:
            # Secrets are immutable; leave an existing secret unchanged.
            self.secret = existing
            return

        # Provision a new secret: create (Kubernetes) or register (provider vault).
        self.changed = True

        if self.secret_value is not None:
            intended = DwSecret(secretName=self.name)
        else:
            intended = DwSecret(
                secretName=self.name,
                secretProviderKey=self.secret_provider_key,
            )
            if self.azure_vault_name is not None:
                intended.properties = DwSecretProperties(
                    azureVaultName=self.azure_vault_name,
                )

        if self.module._diff:
            self.diff["after"] = to_dict(intended)

        if self.module.check_mode:
            self.secret = intended
        elif self.secret_value is not None:
            self.secret = client.create_secret(
                cluster_id=self.cluster_id,
                secret_name=self.name,
                secret_value=self.secret_value,
            )
        else:
            self.secret = client.register_secret(
                cluster_id=self.cluster_id,
                secret_name=self.name,
                secret_provider_key=self.secret_provider_key,
                azure_vault_name=self.azure_vault_name,
            )


def main():
    result = DwSecretModule()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        secret=to_dict(result.secret) if result.secret else {},
    )

    if result.diff["before"] or result.diff["after"]:
        output["diff"] = result.diff

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
