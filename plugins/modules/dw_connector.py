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
module: dw_connector
short_description: Create, update, delete, and test CDP Data Warehouse Database Connectors
description:
  - Create, update, and delete CDP Data Warehouse Database Connectors.
  - Supports C(present), C(absent), and C(tested) states.
  - The C(tested) state implies C(present) and always executes a connector test job,
    making it analogous to the C(restarted) state found in other Ansible modules.
  - The module supports check_mode.
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
      - The ID of the connector.
      - When specified, used as the primary lookup key and takes precedence over I(name).
    type: str
    aliases:
      - connector_identifier
  name:
    description:
      - The display name of the connector.
      - Required when I(state) is C(present) or C(tested).
      - Used as the primary lookup key when I(connector_id) is not specified.
      - Must contain only alphanumeric characters (A-Z, a-z, 0-9).
    type: str
  template:
    description:
      - The template of the connector.
      - Required only when creating a new connector; not needed when updating an
        existing one.
      - This field is immutable after creation; the module will fail if the requested
        template differs from the existing connector's template. Delete and recreate
        the connector to change its template.
    type: str
  description:
    description:
      - User-provided description for the connector.
    type: str
  config:
    description:
      - Connector configuration in key-value format.
    type: dict
  state:
    description:
      - The declarative state of the connector.
      - V(present) creates the connector if it does not exist, or updates mutable
        fields if they differ (idempotent).
      - V(absent) deletes the connector if it exists (idempotent).
      - V(tested) implies V(present) and always executes a connector test job,
        setting C(changed=True) regardless of whether the connector was modified.
    type: str
    default: present
    choices:
      - present
      - absent
      - tested
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Create a connector
  cloudera.cloud.dw_connector:
    cluster_id: example-cluster-id
    name: my-iceberg-connector
    template: iceberg
    description: "Iceberg connector for production"
    config:
      connector.name: iceberg
      iceberg.catalog.type: hive_metastore

- name: Ensure a connector exists (idempotent)
  cloudera.cloud.dw_connector:
    cluster_id: example-cluster-id
    name: my-hive-connector
    template: hive
    state: present

- name: Run a connectivity test against an existing connector
  cloudera.cloud.dw_connector:
    cluster_id: example-cluster-id
    name: my-iceberg-connector
    template: iceberg
    state: tested
  register: test_result

- name: Use the test job ID
  ansible.builtin.debug:
    msg: "Test job ID: {{ test_result.test_job.jobId }}"

- name: Delete a connector by name
  cloudera.cloud.dw_connector:
    cluster_id: example-cluster-id
    name: my-iceberg-connector
    state: absent

- name: Delete a connector by ID
  cloudera.cloud.dw_connector:
    cluster_id: example-cluster-id
    connector_id: example-connector-id
    state: absent
"""

RETURN = r"""
connector:
  description: The details about the CDP Data Warehouse Database Connector.
  returned: always
  type: dict
  contains:
    id:
      description: The unique identifier of the connector.
      returned: always
      type: str
    name:
      description: The display name of the connector.
      returned: always
      type: str
    template:
      description: The template of the connector.
      returned: always
      type: str
    crn:
      description: The CRN of the connector.
      returned: always
      type: str
    description:
      description: User-provided description.
      returned: when available
      type: str
    config:
      description: The connector configuration in key-value format.
      returned: when available
      type: dict
    createdAt:
      description: The timestamp when the connector was created.
      returned: always
      type: int
    createdBy:
      description: The CRN of the user who created the connector.
      returned: always
      type: str
    updatedAt:
      description: The timestamp when the connector was last updated.
      returned: always
      type: int
    updatedBy:
      description: The CRN of the user who last updated the connector.
      returned: always
      type: str
test_job:
  description:
    - The details of the connector test job.
    - Only returned when I(state) is C(tested).
  returned: when state is tested
  type: dict
  contains:
    jobId:
      description: The ID of the created test job.
      returned: when not in check mode
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

import re

from dataclasses import replace
from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    ServicesModule,
    diff_dict,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
)


class DwConnector(ServicesModule):
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
                template=dict(type="str"),
                description=dict(type="str"),
                config=dict(type="dict"),
                state=dict(
                    type="str",
                    choices=["present", "absent", "tested"],
                    default="present",
                ),
            ),
            required_if=[
                ("state", "present", ("name",)),
                ("state", "tested", ("name",)),
            ],
            required_one_of=[["name", "connector_id"]],
            supports_check_mode=True,
        )

        self.cluster_id = self.get_param("cluster_id")
        self.connector_id = self.get_param("connector_id")
        self.name = self.get_param("name")
        self.template = self.get_param("template")
        self.description = self.get_param("description")
        self.config = self.get_param("config")
        self.state = self.get_param("state")

        self.connector: Optional[Connector] = None
        self.test_job_id: Optional[str] = None
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

    def process(self):
        # Validate name character set at the system boundary
        if self.name is not None and not re.fullmatch(r"[A-Za-z0-9]+", self.name):
            self.module.fail_json(
                msg=(
                    f"Invalid connector name {self.name!r}. "
                    "Names must contain only alphanumeric characters (A-Z, a-z, 0-9)."
                ),
            )

        client = CdpDwClient(api_client=self.api_client)

        # Look up existing connector
        existing: Optional[Connector] = None
        if self.connector_id is not None:
            existing = client.get_connector_by_id(self.cluster_id, self.connector_id)
        elif self.name is not None:
            existing = client.get_connector_by_name(self.cluster_id, self.name)

        if self.state == "absent":
            if existing is not None:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = to_dict(existing)
                if not self.module.check_mode:
                    client.delete_connector(self.cluster_id, existing.id)
            return

        # present or tested state

        # Validate immutable template field before any mutations
        if (
            existing is not None
            and self.template is not None
            and self.template != existing.template
        ):
            self.module.fail_json(
                msg=(
                    f"The 'template' field is immutable after connector creation. "
                    f"Current: {existing.template!r}, Requested: {self.template!r}. "
                    f"Delete and recreate the connector to change its template."
                ),
            )

        if existing is None:
            # Create — template is required only when creating a new connector
            # (it is immutable thereafter, so updates do not need it supplied).
            if self.template is None:
                self.module.fail_json(
                    msg="Parameter 'template' is required when creating a new connector.",
                )
            self.changed = True
            if self.module._diff:
                desired = Connector(name=self.name, template=self.template)
                if self.description is not None:
                    desired.description = self.description
                if self.config is not None:
                    desired.config = self.config
                self.diff["after"] = to_dict(desired)
            if not self.module.check_mode:
                self.connector = client.create_connector(
                    cluster_id=self.cluster_id,
                    name=self.name,
                    template=self.template,
                    description=self.description,
                    config=self.config,
                )
        else:
            # Build the desired state by copying the existing connector and
            # overriding only the mutable fields the caller supplied (template is
            # immutable). diff_dict() then drives both change detection and the diff.
            desired = replace(
                existing,
                name=self.name if self.name is not None else existing.name,
                description=(
                    self.description
                    if self.description is not None
                    else existing.description
                ),
                config=self.config if self.config is not None else existing.config,
            )

            before, after = diff_dict(existing, desired)

            if before or after:
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = before
                    self.diff["after"] = after
                if not self.module.check_mode:
                    # updateConnector requires the full representation with every
                    # field set. Resolve any unset (NULLABLE) values to serializable
                    # defaults — the existing connector may have no description/config.
                    self.connector = client.update_connector(
                        cluster_id=self.cluster_id,
                        connector_id=existing.id,
                        name=desired.name,
                        description=(
                            desired.description
                            if desired.description is not NULLABLE
                            else None
                        ),
                        template=existing.template,
                        config=(
                            desired.config if desired.config is not NULLABLE else {}
                        ),
                    )

            if not self.changed or self.module.check_mode:
                self.connector = existing

        # Handle tested state: always mutating (analogous to restarted)
        if self.state == "tested":
            self.changed = True
            if not self.module.check_mode:
                connector_id = self.connector.id if self.connector else None
                if connector_id:
                    self.test_job_id = client.create_connector_test_job(
                        cluster_id=self.cluster_id,
                        connector_id=connector_id,
                    )


def main():
    result = DwConnector()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        connector=to_dict(result.connector) if result.connector else {},
    )

    if result.diff["before"] or result.diff["after"]:
        output["diff"] = result.diff

    if result.state == "tested":
        output["test_job"] = {"jobId": result.test_job_id} if result.test_job_id else {}

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
