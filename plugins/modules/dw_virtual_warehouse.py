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
module: dw_virtual_warehouse
short_description: Create, manage, and destroy CDP Data Warehouse Virtual Warehouses
description:
  - Create, reconcile, and delete a CDP Data Warehouse (CDW) Virtual Warehouse.
  - Supports C(hive), C(impala), and C(trino) Virtual Warehouses.
  - Trino connector association is declarative and full-sync; the supplied set of
    connector ids becomes the warehouse's complete association set. Connectors
    not listed are detached. At this time, an empty set is a no-op and emits a warning.
  - Reconciliation of an existing warehouse is limited to the following fields -
    O(node_count) and O(connectors). Other creation options - O(tshirt_size),
    O(autoscaling), O(common_configs) - are applied at creation time and are not reconciled.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "3.4.0"
options:
  warehouse_id:
    description:
      - The identifier of the Virtual Warehouse.
      - Required if O(state=absent).
      - Used as the primary lookup key; takes precedence over O(name).
    type: str
    aliases:
      - vw_id
      - id
  cluster_id:
    description:
      - The identifier of the parent Data Warehouse Cluster of the Virtual Warehouse.
    type: str
    required: true
  catalog_id:
    description:
      - The identifier of the parent Database Catalog attached to the Virtual Warehouse.
      - Required if O(state=present).
    type: str
    aliases:
      - dbc_id
  type:
    description:
      - The type of Virtual Warehouse.
      - Required if O(state=present).
    type: str
    choices:
      - hive
      - impala
      - trino
  name:
    description:
      - The name of the Virtual Warehouse.
      - Required if O(state=present).
      - Used as the lookup key when O(warehouse_id) is not specified.
    type: str
  tshirt_size:
    description:
      - The name of deployment T-shirt size, i.e. the deployment template, to use.
      - Applied at creation only; not reconciled on an existing warehouse.
    type: str
    choices:
      - xsmall
      - small
      - medium
      - large
    aliases:
      - template
  node_count:
    description:
      - The number of nodes (compute cluster size) for the Virtual Warehouse.
      - Reconciled on an existing warehouse.
    type: int
  instance_type:
    description:
      - The underlying compute instance type for the Virtual Warehouse.
      - Applied at creation only.
    type: str
  connectors:
    description:
      - The complete, desired set of Database Connector C(identifiers) to associate
        with the Virtual Warehouse.
      - Only valid for C(trino) Virtual Warehouses.
      - Full-sync semantics; connectors not listed are detached. An empty list
        is a no-op (does not yet detach all connectors) and emits a warning.
    type: list
    elements: str
  autoscaling:
    description:
      - Auto-scaling configuration for the Virtual Warehouse.
      - Applied at creation only; not reconciled.
    type: dict
    suboptions:
      min_nodes:
        description: The minimum number of available nodes for autoscaling.
        type: int
      max_nodes:
        description: The maximum number of available nodes for autoscaling.
        type: int
      auto_suspend_timeout_seconds:
        description: Auto suspend threshold for the Virtual Warehouse.
        type: int
      disable_auto_suspend:
        description: Turn off auto suspend for the Virtual Warehouse.
        type: bool
      hive_desired_free_capacity:
        description:
          - Desired free capacity for Hive Virtual Warehouses.
          - Either O(autoscaling.hive_scale_wait_time_seconds) or
            O(autoscaling.hive_desired_free_capacity) can be provided.
        type: int
      hive_scale_wait_time_seconds:
        description:
          - Wait time before a scale event happens for Hive Virtual Warehouses.
          - Either O(autoscaling.hive_scale_wait_time_seconds) or
            O(autoscaling.hive_desired_free_capacity) can be provided.
        type: int
      impala_scale_down_delay_seconds:
        description: Scale down threshold in seconds for Impala Virtual Warehouses.
        type: int
      impala_scale_up_delay_seconds:
        description: Scale up threshold in seconds for Impala Virtual Warehouses.
        type: int
      pod_config_name:
        description: Name of the pod configuration.
        type: str
  common_configs:
    description:
      - Configurations that are applied to every application in the Virtual
        Warehouse service.
      - Applied at creation only.
    type: dict
    suboptions:
      configBlocks:
        description: List of I(ConfigBlocks) for the application.
        type: list
        elements: dict
        suboptions:
          id:
            description:
              - ID of the ConfigBlock.
              - Unique within an I(ApplicationConfig).
            type: str
          format:
            description: Format of the ConfigBlock.
            type: str
            choices:
              - HADOOP_XML
              - PROPERTIES
              - TEXT
              - JSON
              - BINARY
              - ENV
              - FLAGFILE
          content:
            description: Contents of the ConfigBlock.
            type: dict
            suboptions:
              keyValues:
                description: Key-value type configuration.
                type: dict
              text:
                description: Text type configuration.
                type: str
              json:
                description: JSON type configuration.
                type: str
  application_configs:
    description:
      - Configurations that are applied to specific applications in the Virtual
        Warehouse service.
      - Applied at creation only.
    type: dict
  impala_ha:
    description:
      - High Availability settings for an Impala Virtual Warehouse.
      - Applied at creation only.
    type: dict
    suboptions:
      enable_catalog_high_availability:
        description: Enables a backup instance for Impala catalog for high availability.
        type: bool
      enable_shutdown_of_coordinator:
        description:
          - Enables a shutdown of the coordinator.
          - If Unified Analytics is enabled, this setting is explicitly disabled
            and should not be provided.
        type: bool
      high_availability_mode:
        description: Set High Availability mode.
        type: str
        choices:
          - ACTIVE_PASSIVE
          - ACTIVE_ACTIVE
          - DISABLED
      num_of_active_coordinators:
        description: The number of active coordinators.
        type: int
      shutdown_of_coordinator_delay_seconds:
        description: Delay in seconds before the shutdown of coordinator event happens.
        type: int
  ldap_groups:
    description:
      - LDAP group names enabled for authentication to the Virtual Warehouse.
      - Applied at creation only.
    type: list
    elements: str
  enable_sso:
    description:
      - Flag to enable Single Sign-On (SSO) for the Virtual Warehouse.
      - Applied at creation only.
    type: bool
  enable_unified_analytics:
    description:
      - Flag to enable Unified Analytics for the Virtual Warehouse.
      - Only valid for Impala Virtual Warehouses.
      - Applied at creation only.
    type: bool
  enable_platform_jwt_auth:
    description:
      - Flag to configure the Virtual Warehouse to support JWTs issued by the CDP
        JWT token provider.
      - Applied at creation only.
    type: bool
  tags:
    description:
      - Key-value tags associated with the Virtual Warehouse cloud provider resources.
      - Applied at creation only.
    type: dict
  state:
    description:
      - The declarative state of the Virtual Warehouse.
      - V(present) creates the warehouse if it does not exist, and reconciles
        O(node_count) and O(connectors) if it does.
      - V(absent) deletes the warehouse if it exists (idempotent).
    type: str
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Virtual Warehouse to
        achieve the declared state.
      - If set to V(false), the module returns immediately.
    type: bool
    default: true
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the
        Virtual Warehouse to achieve the declared state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the
        Virtual Warehouse to achieve the declared state.
    type: int
    default: 3600
    aliases:
      - polling_timeout
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

- name: Create a Hive Virtual Warehouse
  cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    catalog_id: example-catalog-id
    name: example-hive-vw
    type: hive
    tshirt_size: xsmall

- name: Create a Trino Virtual Warehouse and associate connectors
  cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    catalog_id: example-catalog-id
    name: example-trino-vw
    type: trino
    connectors:
      - connector-1783687110-gwv6
      - connector-1783688742-pqgw

- name: Reconcile the connector set (full-sync) and resize an existing warehouse
  cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    catalog_id: example-catalog-id
    name: example-trino-vw
    type: trino
    node_count: 5
    connectors:
      - connector-1783687110-gwv6

- name: Delete a Virtual Warehouse
  cloudera.cloud.dw_virtual_warehouse:
    cluster_id: example-cluster-id
    warehouse_id: example-trino-vw-id
    state: absent
"""

RETURN = r"""
virtual_warehouse:
  description: The details about the CDP Data Warehouse Virtual Warehouse.
  returned: always
  type: dict
  contains:
    id:
      description: The identifier of the Virtual Warehouse.
      returned: always
      type: str
    name:
      description: The name of the Virtual Warehouse.
      returned: always
      type: str
    vwType:
      description: The Virtual Warehouse type.
      returned: always
      type: str
    dbcId:
      description: The Database Catalog ID associated with the Virtual Warehouse.
      returned: when available
      type: str
    status:
      description: The status of the Virtual Warehouse.
      returned: when available
      type: str
    instanceType:
      description: The underlying compute instance type.
      returned: when available
      type: str
    nodeCount:
      description: The node count (compute cluster size) of the Virtual Warehouse.
      returned: when available
      type: int
    creator:
      description: Details about the Virtual Warehouse creator.
      returned: when available
      type: dict
    creationDate:
      description: The creation time of the Virtual Warehouse in UTC.
      returned: when available
      type: str
    configId:
      description: The identifier of the Virtual Warehouse configuration.
      returned: when available
      type: str
    tags:
      description: Custom tags applied to the Virtual Warehouse.
      returned: when available
      type: list
      elements: dict
    associatedConnectors:
      description:
        - The connectors associated with the Virtual Warehouse, keyed by
          connector id.
      returned: when available
      type: dict
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

import time

from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    VirtualWarehouse,
)


# Virtual Warehouse lifecycle status groupings
ENABLED_STATES = frozenset({"Running", "Created", "Stopped"})
FAILED_STATES = frozenset({"Failed", "Error"})


class DwVirtualWarehouse(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                warehouse_id=dict(type="str", aliases=["vw_id", "id"]),
                cluster_id=dict(required=True, type="str"),
                catalog_id=dict(type="str", aliases=["dbc_id"]),
                type=dict(type="str", choices=["hive", "impala", "trino"]),
                name=dict(type="str"),
                tshirt_size=dict(
                    type="str",
                    choices=["xsmall", "small", "medium", "large"],
                    aliases=["template"],
                ),
                node_count=dict(type="int"),
                instance_type=dict(type="str"),
                connectors=dict(type="list", elements="str"),
                autoscaling=dict(
                    type="dict",
                    options=dict(
                        min_nodes=dict(type="int"),
                        max_nodes=dict(type="int"),
                        auto_suspend_timeout_seconds=dict(type="int"),
                        disable_auto_suspend=dict(type="bool"),
                        hive_desired_free_capacity=dict(type="int"),
                        hive_scale_wait_time_seconds=dict(type="int"),
                        impala_scale_down_delay_seconds=dict(type="int"),
                        impala_scale_up_delay_seconds=dict(type="int"),
                        pod_config_name=dict(type="str"),
                    ),
                ),
                common_configs=dict(
                    type="dict",
                    options=dict(
                        configBlocks=dict(
                            type="list",
                            elements="dict",
                            options=dict(
                                id=dict(type="str"),
                                format=dict(
                                    type="str",
                                    choices=[
                                        "HADOOP_XML",
                                        "PROPERTIES",
                                        "TEXT",
                                        "JSON",
                                        "BINARY",
                                        "ENV",
                                        "FLAGFILE",
                                    ],
                                ),
                                content=dict(
                                    type="dict",
                                    options=dict(
                                        keyValues=dict(type="dict"),
                                        text=dict(type="str"),
                                        json=dict(type="json"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                application_configs=dict(type="dict"),
                impala_ha=dict(
                    type="dict",
                    options=dict(
                        enable_catalog_high_availability=dict(type="bool"),
                        enable_shutdown_of_coordinator=dict(type="bool"),
                        high_availability_mode=dict(
                            type="str",
                            choices=["ACTIVE_PASSIVE", "ACTIVE_ACTIVE", "DISABLED"],
                        ),
                        num_of_active_coordinators=dict(type="int"),
                        shutdown_of_coordinator_delay_seconds=dict(type="int"),
                    ),
                ),
                ldap_groups=dict(type="list", elements="str"),
                enable_sso=dict(type="bool"),
                enable_unified_analytics=dict(type="bool"),
                enable_platform_jwt_auth=dict(type="bool"),
                tags=dict(type="dict"),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                wait=dict(type="bool", default=True),
                delay=dict(type="int", default=15, aliases=["polling_delay"]),
                timeout=dict(type="int", default=3600, aliases=["polling_timeout"]),
            ),
            required_if=[
                ("state", "absent", ("warehouse_id",)),
                ("state", "present", ("catalog_id", "type", "name")),
            ],
            supports_check_mode=True,
        )

        self.warehouse_id = self.get_param("warehouse_id")
        self.cluster_id = self.get_param("cluster_id")
        self.catalog_id = self.get_param("catalog_id")
        self.type = self.get_param("type")
        self.name = self.get_param("name")
        self.tshirt_size = self.get_param("tshirt_size")
        self.node_count = self.get_param("node_count")
        self.instance_type = self.get_param("instance_type")
        self.connectors = self.get_param("connectors")
        self.autoscaling = self.get_param("autoscaling")
        self.common_configs = self.get_param("common_configs")
        self.application_configs = self.get_param("application_configs")
        self.impala_ha = self.get_param("impala_ha")
        self.ldap_groups = self.get_param("ldap_groups")
        self.enable_sso = self.get_param("enable_sso")
        self.enable_unified_analytics = self.get_param("enable_unified_analytics")
        self.enable_platform_jwt_auth = self.get_param("enable_platform_jwt_auth")
        self.tags = self.get_param("tags")
        self.state = self.get_param("state")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        self.virtual_warehouse: Dict[str, Any] = {}
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

    def process(self):
        client = CdpDwClient(api_client=self.api_client)

        # Connector association is a Trino-only capability.
        if (
            self.connectors is not None
            and self.type is not None
            and self.type != "trino"
        ):
            self.module.fail_json(
                msg=(
                    "The 'connectors' parameter is only valid for Trino Virtual "
                    f"Warehouses; got type={self.type!r}."
                ),
            )

        existing = self._find_existing(client)

        if self.state == "absent":
            self._handle_absent(client, existing)
            return

        # state == "present"
        if existing is None:
            self._handle_create(client)
        else:
            self._handle_reconcile(client, existing)

    def _find_existing(self, client) -> Optional[VirtualWarehouse]:
        if self.warehouse_id is not None:
            return client.get_vw_by_id(self.cluster_id, self.warehouse_id)
        if self.name is not None:
            return client.get_vw_by_name(self.cluster_id, self.name)
        return None

    def _handle_absent(self, client, existing) -> None:
        if existing is None:
            return
        self.changed = True
        if self.module._diff:
            self.diff["before"] = to_dict(existing)
        if not self.module.check_mode:
            client.delete_vw(self.cluster_id, existing.id)
            if self.wait:
                self._wait_for_absence(client, existing.id)

    def _handle_create(self, client) -> None:
        self.changed = True

        desired_connectors = self._desired_connector_ids()

        if self.module._diff:
            after: Dict[str, Any] = {
                "name": self.name,
                "vwType": self.type,
                "dbcId": self.catalog_id,
            }
            if self.node_count is not None:
                after["nodeCount"] = self.node_count
            if desired_connectors is not None:
                after["associatedConnectors"] = sorted(desired_connectors)
            self.diff["after"] = after

        if self.module.check_mode:
            return

        created = client.create_vw(
            cluster_id=self.cluster_id,
            dbc_id=self.catalog_id,
            vw_type=self.type,
            name=self.name,
            tshirt_size=self.tshirt_size,
            node_count=self.node_count,
            instance_type=self.instance_type,
            autoscaling=self.autoscaling,
            config=self._build_service_config(),
            impala_ha=self.impala_ha,
            tags=self.tags,
            enable_unified_analytics=self.enable_unified_analytics,
            enable_platform_jwt_auth=self.enable_platform_jwt_auth,
        )
        if created is None:
            self.module.fail_json(
                msg="Virtual Warehouse creation did not return a warehouse.",
            )

        vw_id = created.id
        current = created
        if self.wait:
            current = self._wait_for_presence(client, vw_id)

        # Step 2: associate connectors (Trino two-step) once the warehouse exists.
        if desired_connectors:
            current = client.update_vw(
                cluster_id=self.cluster_id,
                vw_id=vw_id,
                associated_connectors=sorted(desired_connectors),
            )
            if self.wait:
                current = self._wait_for_presence(client, vw_id)

        self.virtual_warehouse = to_dict(current) if current else {}

    def _handle_reconcile(self, client, existing) -> None:
        node_changed = (
            self.node_count is not None and self.node_count != existing.nodeCount
        )

        current_connector_ids = set(
            (
                existing.associatedConnectors.keys()
                if isinstance(existing.associatedConnectors, dict)
                else []
            ),
        )
        desired_connectors = self._desired_connector_ids()
        connectors_changed = (
            desired_connectors is not None
            and set(desired_connectors) != current_connector_ids
        )

        if node_changed or connectors_changed:
            self.changed = True
            if self.module._diff:
                before: Dict[str, Any] = {}
                after: Dict[str, Any] = {}
                if node_changed:
                    before["nodeCount"] = existing.nodeCount
                    after["nodeCount"] = self.node_count
                if connectors_changed:
                    before["associatedConnectors"] = sorted(current_connector_ids)
                    after["associatedConnectors"] = sorted(desired_connectors)
                self.diff["before"] = before
                self.diff["after"] = after

            if not self.module.check_mode:
                updated = client.update_vw(
                    cluster_id=self.cluster_id,
                    vw_id=existing.id,
                    node_count=self.node_count if node_changed else None,
                    associated_connectors=(
                        sorted(desired_connectors) if connectors_changed else None
                    ),
                )
                if self.wait:
                    updated = self._wait_for_presence(client, existing.id)
                self.virtual_warehouse = to_dict(updated) if updated else {}
                return

        # No change, or check_mode: report the existing representation.
        self.virtual_warehouse = to_dict(existing)

    def _desired_connector_ids(self) -> Optional[List[str]]:
        """Resolve the desired connector id set, warning on the empty (no-op) case.

        Returns None when connectors are unmanaged (parameter omitted). An empty
        desired set cannot be applied (the API will not detach all connectors),
        so it is treated as unmanaged after warning.
        """
        if self.connectors is None:
            return None
        if len(self.connectors) == 0:
            self.module.warn(
                "An empty 'connectors' set cannot detach all connectors; "
                "the connector association is left unchanged.",
            )
            return None
        return self.connectors

    def _build_service_config(self) -> Optional[Dict[str, Any]]:
        """Assemble the ServiceConfigReq payload from the discrete config params."""
        config: Dict[str, Any] = {}
        if self.common_configs is not None:
            config["commonConfigs"] = self.common_configs
        if self.application_configs is not None:
            config["applicationConfigs"] = self.application_configs
        if self.ldap_groups is not None:
            config["ldapGroups"] = self.ldap_groups
        if self.enable_sso is not None:
            config["enableSSO"] = self.enable_sso
        return config or None

    def _wait_for_presence(self, client, vw_id):
        """Poll until the Virtual Warehouse reaches a running state or fails.

        Returns the settled VirtualWarehouse so callers avoid an extra describe.
        """
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            vw = client.get_vw_by_id(self.cluster_id, vw_id)
            status = vw.status if vw is not None else None
            if status in ENABLED_STATES:
                return vw
            if status in FAILED_STATES:
                self.module.fail_json(
                    msg=f"Virtual Warehouse {vw_id} entered a failed state: {status}",
                )
            time.sleep(self.delay)
        self.module.fail_json(
            msg=f"Timed out waiting for Virtual Warehouse {vw_id} to reach a running state.",
        )

    def _wait_for_absence(self, client, vw_id) -> None:
        """Poll until the Virtual Warehouse no longer exists."""
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            if client.get_vw_by_id(self.cluster_id, vw_id) is None:
                return
            time.sleep(self.delay)
        self.module.fail_json(
            msg=f"Timed out waiting for Virtual Warehouse {vw_id} to be deleted.",
        )


def main():
    result = DwVirtualWarehouse()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        virtual_warehouse=result.virtual_warehouse,
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
