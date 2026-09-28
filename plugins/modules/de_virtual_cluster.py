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
module: de_virtual_cluster
short_description: Manage CDP Data Engineering Virtual Clusters
description:
  - Create, update, suspend, resume, or delete CDP Data Engineering Virtual Clusters.
author:
  - "Curtis Howard (@curtishoward)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.5.0"
options:
  name:
    description:
      - The name of the Virtual Cluster.
    type: str
    required: True
  environment:
    description:
      - The CDP environment name of the CDE Service in which to create the Virtual Cluster.
    type: str
    required: True
    aliases:
      - env
  service_name:
    description:
      - The name of the CDE Service in which to create the Virtual Cluster.
    type: str
    required: True
    aliases:
      - cluster_name
  cpu_requests:
    description:
      - CPU requests for autoscaling.
      - Required when O(state=present) and the Virtual Cluster does not yet exist.
    type: str
    required: False
  memory_requests:
    description:
      - Memory requests for autoscaling, for example C(30Gi).
      - Required when O(state=present) and the Virtual Cluster does not yet exist.
    type: str
    required: False
  chart_value_overrides:
    description:
      - Chart overrides for creating the Virtual Cluster.
    type: list
    elements: dict
    required: False
    suboptions:
      chart_name:
        description:
          - Name of the chart to override, for example C(dex-app) or C(dex-base).
        type: str
        required: False
      overrides:
        description:
          - Space-separated key-value pairs for overriding chart values.
        type: str
        required: False
  runtime_spot_component:
    description:
      - Where the Driver and the Executors run, on-demand or spot instances.
    type: str
    required: False
  spark_version:
    description:
      - Spark version for the Virtual Cluster, for example C(SPARK3_5_4).
    type: str
    required: False
  acl_users:
    description:
      - Comma-separated Workload usernames of CDP users to be granted access to the Virtual Cluster.
    type: str
    required: False
  tier:
    description:
      - Tier of the Virtual Cluster, for CDE 1.19.0 and beyond.
      - C(CORE) enables operational batch jobs.
      - C(ALLP) enables both operational batch jobs and interactive sessions.
    type: str
    required: False
    choices:
      - ALLP
      - CORE
    aliases:
      - vc_tier
  spark_os_name:
    description:
      - Spark OS image for the Virtual Cluster.
    type: str
    required: False
    choices:
      - SECURITYHARDENED
      - REDHAT
  session_timeout:
    description:
      - Default session timeout, applicable to the All Purpose (ALLP) virtual cluster tier.
    type: str
    required: False
  spark_configs:
    description:
      - Spark configurations applied to all jobs run in the Virtual Cluster.
    type: dict
    required: False
  full_access_users:
    description:
      - Users granted full access to the Virtual Cluster.
    type: list
    elements: str
    required: False
  full_access_groups:
    description:
      - Groups granted full access to the Virtual Cluster.
    type: list
    elements: str
    required: False
  view_only_users:
    description:
      - Users granted view-only access to the Virtual Cluster.
    type: list
    elements: str
    required: False
  view_only_groups:
    description:
      - Groups granted view-only access to the Virtual Cluster.
    type: list
    elements: str
    required: False
  discard_spark_configs:
    description:
      - Discard the Virtual Cluster's existing Spark configurations instead of merging
        them with O(spark_configs).
    type: bool
    required: False
  enable_compute_override:
    description:
      - Enable compute override for the Virtual Cluster.
    type: bool
    required: False
  state:
    description:
      - The declarative state of the Virtual Cluster.
      - C(suspended) suspends the Virtual Cluster; setting O(state=present) on a
        suspended Virtual Cluster resumes it.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
      - suspended
  wait:
    description:
      - Flag to enable internal polling to wait for the Virtual Cluster to achieve the declared state.
      - If set to C(False), the module will return immediately after initiating the operation.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the
        Virtual Cluster to achieve the declared state.
    type: int
    required: False
    default: 30
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the
        Virtual Cluster to achieve the declared state.
    type: int
    required: False
    default: 600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a Virtual Cluster and wait for it to become active
- cloudera.cloud.de_virtual_cluster:
    name: my-virtual-cluster
    environment: my-cdp-environment
    service_name: my-cde-service
    cpu_requests: "20"
    memory_requests: "80Gi"
    tier: ALLP
    spark_version: SPARK3_5_4
    state: present
    wait: true

# Delete a Virtual Cluster without waiting
- cloudera.cloud.de_virtual_cluster:
    name: my-virtual-cluster
    environment: my-cdp-environment
    service_name: my-cde-service
    state: absent
    wait: false

# Suspend a Virtual Cluster and wait for it to become suspended
- cloudera.cloud.de_virtual_cluster:
    name: my-virtual-cluster
    environment: my-cdp-environment
    service_name: my-cde-service
    state: suspended
    wait: true

# Resume a suspended Virtual Cluster
- cloudera.cloud.de_virtual_cluster:
    name: my-virtual-cluster
    environment: my-cdp-environment
    service_name: my-cde-service
    state: present
    wait: true

# Update the access control and Spark configs of an existing Virtual Cluster
- cloudera.cloud.de_virtual_cluster:
    name: my-virtual-cluster
    environment: my-cdp-environment
    service_name: my-cde-service
    full_access_users:
      - alice
    view_only_groups:
      - viewers
    spark_configs:
      spark.executor.memory: 4g
    state: present
"""

RETURN = r"""
virtual_cluster:
  description: Description of the Virtual Cluster.
  type: dict
  returned: always
  contains:
    vcId:
      description: Virtual Cluster ID.
      returned: always
      type: str
    vcName:
      description: Name of the Virtual Cluster.
      returned: always
      type: str
    clusterId:
      description: Cluster ID of the CDE Service that contains the Virtual Cluster.
      returned: always
      type: str
    status:
      description: Status of the Virtual Cluster.
      returned: always
      type: str
    vcTier:
      description: Tier of the Virtual Cluster (ALLP or CORE).
      returned: when available
      type: str
    sparkVersion:
      description: Spark version for the Virtual Cluster.
      returned: when available
      type: str
    creatorEmail:
      description: Email address of the creator of the Virtual Cluster.
      returned: when available
      type: str
    vcApiUrl:
      description: URL for the Virtual Cluster APIs.
      returned: when available
      type: str
    accessControl:
      description: Access control details for the Virtual Cluster.
      returned: when available
      type: dict
    resources:
      description: Resource details of the Virtual Cluster.
      returned: when available
      type: dict
    sparkConfigs:
      description: Spark configurations applied to all jobs run in the Virtual Cluster.
      returned: when available
      type: dict
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when supported
  type: list
  elements: str
"""

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CDE_VC_REMOVABLE_STATUSES,
    CDE_VC_STOPPED_STATUSES,
    CDE_VC_SUSPENDED_STATUSES,
    CdpDeClient,
    VcDescription,
    check_vc_updates,
)


class DEVirtualCluster(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=True, type="str"),
                environment=dict(required=True, type="str", aliases=["env"]),
                service_name=dict(
                    required=True,
                    type="str",
                    aliases=["cluster_name"],
                ),
                cpu_requests=dict(required=False, type="str"),
                memory_requests=dict(required=False, type="str"),
                chart_value_overrides=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    default=None,
                    options=dict(
                        chart_name=dict(required=False, type="str"),
                        overrides=dict(required=False, type="str"),
                    ),
                ),
                runtime_spot_component=dict(required=False, type="str"),
                spark_version=dict(required=False, type="str"),
                acl_users=dict(required=False, type="str"),
                tier=dict(
                    required=False,
                    type="str",
                    choices=["ALLP", "CORE"],
                    aliases=["vc_tier"],
                ),
                spark_os_name=dict(
                    required=False,
                    type="str",
                    choices=["SECURITYHARDENED", "REDHAT"],
                ),
                session_timeout=dict(required=False, type="str"),
                spark_configs=dict(required=False, type="dict"),
                full_access_users=dict(required=False, type="list", elements="str"),
                full_access_groups=dict(required=False, type="list", elements="str"),
                view_only_users=dict(required=False, type="list", elements="str"),
                view_only_groups=dict(required=False, type="list", elements="str"),
                discard_spark_configs=dict(required=False, type="bool"),
                enable_compute_override=dict(required=False, type="bool"),
                state=dict(
                    type="str",
                    choices=["present", "absent", "suspended"],
                    default="present",
                ),
                wait=dict(required=False, type="bool", default=True),
                delay=dict(
                    required=False,
                    type="int",
                    aliases=["polling_delay"],
                    default=30,
                ),
                timeout=dict(
                    required=False,
                    type="int",
                    aliases=["polling_timeout"],
                    default=600,
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name: str = self.get_param("name")
        self.environment: str = self.get_param("environment")
        self.service_name: str = self.get_param("service_name")
        self.cpu_requests: Optional[str] = self.get_param("cpu_requests")
        self.memory_requests: Optional[str] = self.get_param("memory_requests")
        self.chart_value_overrides: Optional[list] = self.get_param(
            "chart_value_overrides",
        )
        self.runtime_spot_component: Optional[str] = self.get_param(
            "runtime_spot_component",
        )
        self.spark_version: Optional[str] = self.get_param("spark_version")
        self.acl_users: Optional[str] = self.get_param("acl_users")
        self.tier: Optional[str] = self.get_param("tier")
        self.spark_os_name: Optional[str] = self.get_param("spark_os_name")
        self.session_timeout: Optional[str] = self.get_param("session_timeout")
        self.spark_configs: Optional[dict] = self.get_param("spark_configs")
        self.full_access_users: Optional[list] = self.get_param("full_access_users")
        self.full_access_groups: Optional[list] = self.get_param("full_access_groups")
        self.view_only_users: Optional[list] = self.get_param("view_only_users")
        self.view_only_groups: Optional[list] = self.get_param("view_only_groups")
        self.discard_spark_configs: Optional[bool] = self.get_param(
            "discard_spark_configs",
        )
        self.enable_compute_override: Optional[bool] = self.get_param(
            "enable_compute_override",
        )
        self.state: str = self.get_param("state")
        self.wait: bool = self.get_param("wait")
        self.delay: int = self.get_param("delay")
        self.timeout: int = self.get_param("timeout")

        # Initialize DE client
        self.de_client = CdpDeClient(self.api_client)

        # Initialize return values
        self.virtual_cluster: Dict[str, Any] = {}
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

    def process(self):
        cluster_id = self._resolve_cluster_id()

        if cluster_id is None:
            if self.state in ("present", "suspended"):
                self.module.fail_json(
                    msg=f"CDE service '{self.service_name}' not found in environment '{self.environment}'",
                )
            return

        existing = self.de_client.get_virtual_cluster_by_name(cluster_id, self.name)

        if existing is not None and existing.status in CDE_VC_STOPPED_STATUSES:
            existing = None

        if existing is None:
            if self.state == "present":
                self._handle_create(cluster_id)
            elif self.state == "suspended":
                self.module.fail_json(
                    msg=f"Virtual Cluster '{self.name}' not found in CDE service '{self.service_name}'",
                )
            return

        if self.state == "absent":
            self._handle_absent(cluster_id, existing)
        elif self.state == "suspended":
            self._handle_suspend(cluster_id, existing)
        elif self.state == "present":
            if existing.status in CDE_VC_SUSPENDED_STATUSES:
                self._handle_resume(cluster_id, existing)
            else:
                self._handle_update(cluster_id, existing)

    def _resolve_cluster_id(self) -> Optional[str]:
        service = self.de_client.get_service_by_name(
            self.service_name,
            env_name=self.environment,
        )
        return service.clusterId if service else None

    def _handle_absent(self, cluster_id: str, existing: VcDescription) -> None:
        self.changed = True
        self.virtual_cluster = to_dict(existing)
        if self.module._diff:
            self.diff["before"] = to_dict(existing)

        if not self.module.check_mode:
            vc_id = existing.vcId
            self.de_client.delete_virtual_cluster(cluster_id, vc_id)
            if self.wait:
                result = self.de_client.wait_for_vc_state(
                    cluster_id=cluster_id,
                    vc_id=vc_id,
                    target_statuses=CDE_VC_STOPPED_STATUSES,
                    timeout=self.timeout,
                    delay=self.delay,
                )
                self.virtual_cluster = to_dict(result) if result else {}
                if self.module._diff:
                    self.diff["after"] = self.virtual_cluster

    def _handle_suspend(self, cluster_id: str, existing: VcDescription) -> None:
        if existing.status in CDE_VC_SUSPENDED_STATUSES:
            self.virtual_cluster = to_dict(existing)
            return

        self.changed = True
        self.virtual_cluster = to_dict(existing)
        if self.module._diff:
            self.diff["before"] = to_dict(existing)

        if not self.module.check_mode:
            vc_id = existing.vcId
            self.de_client.suspend_virtual_cluster(cluster_id, vc_id)
            if self.wait:
                result = self.de_client.wait_for_vc_state(
                    cluster_id=cluster_id,
                    vc_id=vc_id,
                    target_statuses=CDE_VC_SUSPENDED_STATUSES,
                    timeout=self.timeout,
                    delay=self.delay,
                )
                self.virtual_cluster = to_dict(result) if result else {}
                if self.module._diff:
                    self.diff["after"] = self.virtual_cluster

    def _handle_resume(self, cluster_id: str, existing: VcDescription) -> None:
        self.changed = True
        self.virtual_cluster = to_dict(existing)
        if self.module._diff:
            self.diff["before"] = to_dict(existing)

        if not self.module.check_mode:
            vc_id = existing.vcId
            self.de_client.resume_virtual_cluster(cluster_id, vc_id)
            if self.wait:
                result = self.de_client.wait_for_vc_state(
                    cluster_id=cluster_id,
                    vc_id=vc_id,
                    target_statuses=CDE_VC_REMOVABLE_STATUSES,
                    timeout=self.timeout,
                    delay=self.delay,
                )
                self.virtual_cluster = to_dict(result) if result else {}
                if self.module._diff:
                    self.diff["after"] = self.virtual_cluster

    def _handle_update(self, cluster_id: str, existing: VcDescription) -> None:
        vc_id = existing.vcId
        update_params = check_vc_updates(
            cluster_id=cluster_id,
            vc_id=vc_id,
            vc_details=existing,
            full_access_users=self.full_access_users,
            full_access_groups=self.full_access_groups,
            view_only_users=self.view_only_users,
            view_only_groups=self.view_only_groups,
            spark_configs=self.spark_configs,
        )

        if update_params:
            if self.acl_users is not None:
                update_params["acl_users"] = self.acl_users
            if self.discard_spark_configs is not None:
                update_params["discard_spark_configs"] = self.discard_spark_configs
            if self.enable_compute_override is not None:
                update_params["enable_compute_override"] = self.enable_compute_override

            self.changed = True
            self.virtual_cluster = to_dict(existing)
            if self.module._diff:
                self.diff["before"] = to_dict(existing)
                self.diff["after"] = to_dict(existing)
                self.diff["after"].update(update_params)

            if not self.module.check_mode:
                self.de_client.update_virtual_cluster(**update_params)
                if self.wait:
                    result = self.de_client.wait_for_vc_state(
                        cluster_id=cluster_id,
                        vc_id=vc_id,
                        target_statuses=CDE_VC_REMOVABLE_STATUSES,
                        timeout=self.timeout,
                        delay=self.delay,
                    )
                    if result:
                        self.virtual_cluster = to_dict(result)
                        if self.module._diff:
                            self.diff["after"] = to_dict(result)
        else:
            self.virtual_cluster = to_dict(existing)

    def _handle_create(self, cluster_id: str) -> None:
        missing = [
            param
            for param, value in (
                ("cpu_requests", self.cpu_requests),
                ("memory_requests", self.memory_requests),
            )
            if value is None
        ]
        if missing:
            self.module.fail_json(
                msg=f"state is present but all of the following are missing: {', '.join(missing)}",
            )

        self.changed = True

        if self.module._diff:
            self.diff["after"] = {
                "vcName": self.name,
                "clusterId": cluster_id,
                "status": "AppInstallationInProgress",
            }

        if self.module.check_mode:
            return

        result = self.de_client.create_virtual_cluster(
            name=self.name,
            cluster_id=cluster_id,
            cpu_requests=self.cpu_requests,
            memory_requests=self.memory_requests,
            chart_value_overrides=self.chart_value_overrides,
            runtime_spot_component=self.runtime_spot_component,
            spark_version=self.spark_version,
            acl_users=self.acl_users,
            vc_tier=self.tier,
            spark_os_name=self.spark_os_name,
            session_timeout=self.session_timeout,
            spark_configs=self.spark_configs,
            full_access_users=self.full_access_users,
            full_access_groups=self.full_access_groups,
            view_only_users=self.view_only_users,
            view_only_groups=self.view_only_groups,
        )

        if result:
            self.virtual_cluster = to_dict(result)

            if self.wait and result.vcId:
                wait_result = self.de_client.wait_for_vc_state(
                    cluster_id=cluster_id,
                    vc_id=result.vcId,
                    target_statuses=CDE_VC_REMOVABLE_STATUSES,
                    timeout=self.timeout,
                    delay=self.delay,
                )
                if wait_result:
                    self.virtual_cluster = to_dict(wait_result)

            if self.module._diff:
                self.diff["after"] = self.virtual_cluster


def main():
    result = DEVirtualCluster()
    output = dict(changed=result.changed, virtual_cluster=result.virtual_cluster)

    if result.diff["before"] or result.diff["after"]:
        output["diff"] = result.diff

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
