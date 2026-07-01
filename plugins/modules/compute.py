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
module: compute
short_description: Manage the lifecycle of CDP Externalized Compute Clusters
description:
  - Create and delete CDP Externalized Compute Clusters.
  - Use O(state=present) to create a cluster; the module is idempotent if the
    cluster already exists.
  - Use O(state=absent) to delete a cluster; the module is idempotent if the
    cluster does not exist.
  - Default compute clusters (embedded, environment-scoped) are managed through
    environment creation and are out of scope for this module.
  - The module supports check_mode.
author:
    - "Jim Enright (@jimright)"
version_added: "3.6.0"
options:
  name:
    description:
      - Name of the compute cluster.
      - Required when O(state=present).
      - Used together with O(environment) to resolve an existing cluster when
        O(crn) is not provided.
    type: str
    required: false
    aliases:
      - cluster_name
  environment:
    description:
      - CRN of the CDP environment in which to create the cluster.
      - Required when O(state=present).
      - Used together with O(name) to resolve an existing cluster when
        O(crn) is not provided.
    type: str
    required: false
    aliases:
      - env
  crn:
    description:
      - CRN of an existing compute cluster.
      - When provided, used directly to look up or delete the cluster.
      - Required when O(state=absent) and O(name)/O(environment) are not set.
    type: str
    required: false
    aliases:
      - cluster_crn
  description:
    description:
      - Human-readable description for the cluster.
      - Only used when O(state=present) and the cluster does not yet exist.
    type: str
    required: false
  network:
    description:
      - Network configuration for the cluster.
      - Only used when O(state=present) and the cluster does not yet exist.
    type: dict
    required: false
    suboptions:
      subnets:
        description: List of subnet IDs for the cluster nodes.
        type: list
        elements: str
        required: false
      pod_cidr:
        description: CIDR block for pod IP addresses.
        type: str
        required: false
      service_cidr:
        description: CIDR block for service IP addresses.
        type: str
        required: false
      outbound_type:
        description: Outbound connectivity type (e.g. C(loadBalancer), C(userDefinedRouting)).
        type: str
        required: false
  tags:
    description:
      - Map of string key/value tags to apply to the cluster.
      - Only used when O(state=present) and the cluster does not yet exist.
    type: dict
    required: false
  skip_validation:
    description:
      - If C(true), skip pre-flight validation during create or delete.
    type: bool
    required: false
    default: false
  force:
    description:
      - If C(true), force-delete the cluster even if workloads are running.
      - Only relevant when O(state=absent).
    type: bool
    required: false
    default: false
    aliases:
      - force_delete
  skip_workloads_validation:
    description:
      - If C(true), skip workload validation checks during delete.
      - Only relevant when O(state=absent).
    type: bool
    required: false
    default: false
  wait:
    description:
      - If C(true), wait for the cluster to reach a stable state before returning.
      - For O(state=present), waits until the cluster is C(Running).
      - For O(state=absent), waits until the cluster is C(Deleted) or no longer exists.
    type: bool
    required: false
    default: true
  delay:
    description:
      - Polling interval in seconds when O(wait=true).
    type: int
    required: false
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - Maximum time in seconds to wait for the cluster to reach a stable state.
      - Only relevant when O(wait=true).
    type: int
    required: false
    default: 3600
    aliases:
      - polling_timeout
  state:
    description:
      - Desired lifecycle state of the compute cluster.
    type: str
    required: false
    choices:
      - present
      - absent
    default: present
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
attributes:
  check_mode:
    support: full
  platform:
    platforms: all
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create an externalized compute cluster
- cloudera.cloud.compute:
    name: my-compute-cluster
    environment: "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
    state: present

# Create a cluster with custom network settings and tags
- cloudera.cloud.compute:
    name: my-compute-cluster
    environment: "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
    description: "Production compute cluster"
    network:
      pod_cidr: "10.0.0.0/16"
      service_cidr: "10.1.0.0/16"
    tags:
      team: platform
      env: production
    state: present

# Delete a cluster by name and environment (waits for deletion to complete)
- cloudera.cloud.compute:
    name: my-compute-cluster
    environment: "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
    state: absent

# Delete a cluster directly by CRN, force-removing active workloads
- cloudera.cloud.compute:
    crn: "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
    force: true
    state: absent
"""

RETURN = r"""
cluster:
  description: Details of the compute cluster after the operation.
  returned: when O(state=present) or when the cluster still exists after delete
  type: dict
  contains:
    cluster_crn:
      description: Compute cluster CRN.
      returned: always
      type: str
    cluster_id:
      description: Compute cluster ID.
      returned: always
      type: str
    cluster_name:
      description: Compute cluster name.
      returned: always
      type: str
    status:
      description: Current cluster status.
      returned: always
      type: str
    status_message:
      description: Additional message about the cluster status.
      returned: when available
      type: str
    env_crn:
      description: CRN of the CDP environment.
      returned: when available
      type: str
    env_name:
      description: Name of the CDP environment.
      returned: when available
      type: str
    compute_platform:
      description: Underlying compute platform (e.g. C(EKS), C(AKS)).
      returned: when available
      type: str
    kubernetes_version:
      description: Kubernetes version.
      returned: when available
      type: str
    cluster_shape:
      description: Shape of the cluster (C(Externalized) or C(Embedded)).
      returned: when available
      type: str
    is_default:
      description: Whether this is the default cluster for its environment.
      returned: when available
      type: bool
    creation_time:
      description: Cluster creation time in ISO format.
      returned: when available
      type: str
    region:
      description: Cloud region.
      returned: when available
      type: str
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

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
)


def _build_network(
    network_params: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Convert snake_case network suboptions to the API camelCase CommonNetwork dict."""
    if not network_params:
        return None

    result: Dict[str, Any] = {}
    if network_params.get("subnets") is not None:
        result["subnets"] = network_params["subnets"]
    if network_params.get("pod_cidr") is not None:
        result["podCidr"] = network_params["pod_cidr"]
    if network_params.get("service_cidr") is not None:
        result["serviceCidr"] = network_params["service_cidr"]
    if network_params.get("outbound_type") is not None:
        result["outboundType"] = network_params["outbound_type"]

    return result if result else None


class ComputeCluster(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=False, type="str", aliases=["cluster_name"]),
                environment=dict(required=False, type="str", aliases=["env"]),
                crn=dict(required=False, type="str", aliases=["cluster_crn"]),
                description=dict(required=False, type="str"),
                network=dict(
                    required=False,
                    type="dict",
                    options=dict(
                        subnets=dict(required=False, type="list", elements="str"),
                        pod_cidr=dict(required=False, type="str"),
                        service_cidr=dict(required=False, type="str"),
                        outbound_type=dict(required=False, type="str"),
                    ),
                ),
                tags=dict(required=False, type="dict"),
                skip_validation=dict(required=False, type="bool", default=False),
                force=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["force_delete"],
                ),
                skip_workloads_validation=dict(
                    required=False,
                    type="bool",
                    default=False,
                ),
                wait=dict(required=False, type="bool", default=True),
                delay=dict(
                    required=False,
                    type="int",
                    default=15,
                    aliases=["polling_delay"],
                ),
                timeout=dict(
                    required=False,
                    type="int",
                    default=3600,
                    aliases=["polling_timeout"],
                ),
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            supports_check_mode=True,
            required_if=[
                ("state", "present", ("name", "environment")),
                ("state", "absent", ("crn", "name"), False),
            ],
        )

        # Set parameters
        self.name = self.get_param("name")
        self.environment = self.get_param("environment")
        self.cluster_crn = self.get_param("crn")
        self.description = self.get_param("description")
        self.network = self.get_param("network")
        self.tags = self.get_param("tags")
        self.skip_validation = self.get_param("skip_validation")
        self.force = self.get_param("force")
        self.skip_workloads_validation = self.get_param("skip_workloads_validation")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")
        self.state = self.get_param("state")

        # Initialize return values
        self.cluster: Dict[str, Any] = {}
        self.changed = False

    def process(self):
        compute_client = CdpComputeClient(self.api_client)

        # Resolve existing cluster
        existing: Optional[Dict[str, Any]] = None
        if self.cluster_crn:
            existing = compute_client.get_cluster_by_crn(self.cluster_crn)
        elif self.name and self.environment:
            existing = compute_client.get_cluster_by_name_and_env(
                self.name,
                self.environment,
            )

        if self.state == "present":
            if existing:
                # Cluster already exists — idempotent
                self.cluster = camel_dict_to_snake_dict(existing)
            else:
                self.changed = True
                if not self.module.check_mode:
                    result = compute_client.create_cluster(
                        name=self.name,
                        environment=self.environment,
                        description=self.description,
                        network=_build_network(self.network),
                        tags=self.tags,
                        skip_validation=(
                            self.skip_validation if self.skip_validation else None
                        ),
                    )
                    # After create, result contains clusterCrn — describe for full details
                    created_crn = result.get("clusterCrn")

                    if self.wait and created_crn:
                        final = compute_client.wait_for_cluster_state(
                            cluster_crn=created_crn,
                            target_states=CdpComputeClient.ACTIVE_STATES,
                            timeout=self.timeout,
                            delay=self.delay,
                        )
                        self.cluster = (
                            camel_dict_to_snake_dict(final)
                            if final
                            else camel_dict_to_snake_dict(result)
                        )
                    else:
                        self.cluster = camel_dict_to_snake_dict(result)

        elif self.state == "absent":
            if not existing:
                # Cluster doesn't exist — idempotent
                pass
            else:
                self.changed = True
                resolved_crn = self.cluster_crn or existing.get("clusterCrn")

                if not self.module.check_mode:
                    compute_client.delete_cluster(
                        cluster_crn=resolved_crn,
                        force=self.force if self.force else None,
                        skip_validation=(
                            self.skip_validation if self.skip_validation else None
                        ),
                        skip_workloads_validation=(
                            self.skip_workloads_validation
                            if self.skip_workloads_validation
                            else None
                        ),
                    )

                    if self.wait:
                        final = compute_client.wait_for_cluster_state(
                            cluster_crn=resolved_crn,
                            target_states=CdpComputeClient.DELETED_STATES,
                            timeout=self.timeout,
                            delay=self.delay,
                        )
                        self.cluster = camel_dict_to_snake_dict(final) if final else {}


def main():
    result = ComputeCluster()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        cluster=result.cluster,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
