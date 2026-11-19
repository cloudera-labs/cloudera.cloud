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
  - Default compute clusters and embedded clusters are out of scope; the module
    fails rather than delete a cluster it does not manage.
  - A compute cluster cannot be updated through this module. If the cluster
    already exists, differing O(description), O(network) or O(tags) are ignored
    with a warning.
  - The module supports check_mode and diff mode.
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
      - Name or CRN of the CDP environment in which to create the cluster.
      - A name is resolved to the environment CRN.
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
      - Must refer to an externalized, non-default cluster.
      - Required when O(state=absent) and O(name)/O(environment) are not set.
    type: str
    required: false
    aliases:
      - cluster_crn
  description:
    description:
      - Human-readable description for the cluster.
      - Only used when O(state=present) and the cluster does not yet exist.
      - If the cluster exists with a different description, a warning is issued
        and the description is not changed (the description is not updatable).
    type: str
    required: false
  network:
    description:
      - Network configuration for the cluster.
      - Only used when O(state=present) and the cluster does not yet exist.
      - If the cluster exists, O(network.subnets) and O(network.service_cidr) are compared
        with the existing cluster (EKS only) and a warning is issued if they differ.
        O(network.pod_cidr) and O(network.outbound_type) are not returned by the API, so
        a warning is issued that they could not be verified.
      - The network of an existing cluster is never changed.
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
      - If the cluster exists, the tags are compared with the labels of the existing cluster
        (extra labels on the cluster are ignored) and a warning is issued if they differ.
      - The tags of an existing cluster are never changed.
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
      - For O(state=present), waits until the cluster is C(RUNNING).
      - For O(state=absent), waits until the cluster is C(DELETED) or no longer exists.
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

# Create an externalized compute cluster, identifying the environment by name
- cloudera.cloud.compute:
    name: my-compute-cluster
    environment: my-environment
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
  description:
    - Details of the compute cluster after the operation.
    - After O(state=absent) with O(wait=true) this is the final C(DELETED) record,
      or an empty dictionary if the cluster is no longer visible or did not exist.
    - In check mode this is the planned (for create) or current (for delete) cluster.
  returned: always
  type: dict
  contains:
    cluster_crn:
      description: Compute cluster CRN.
      returned: when available
      type: str
    cluster_id:
      description: Compute cluster ID.
      returned: when available
      type: str
    cluster_name:
      description: Compute cluster name.
      returned: always
      type: str
    status:
      description: Current cluster status (for example C(CREATING), C(RUNNING), C(DELETED)).
      returned: when available
      type: str
    message:
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
      description: Underlying compute platform (for example C(EKS), C(AKS)).
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
    cluster_state_version:
      description: State version of the cluster.
      returned: when available
      type: int
    creation_time:
      description: Cluster creation time in ISO format.
      returned: when available
      type: str
    region:
      description: Cloud region.
      returned: when available
      type: str
diff:
  description: Before and after state of the cluster when run with C(--diff).
  returned: always
  type: dict
  contains:
    before:
      description: The cluster as it was before the change; empty on create.
      type: dict
    after:
      description: The requested cluster; empty on delete.
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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_DELETED_STATUSES,
    EXTERNALIZED_SHAPE,
    CdpComputeClient,
    CommonNetwork,
    CommonStatusMessage,
    ComputeCluster,
    ComputeClusterSpec,
    cluster_to_result,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    ServicesModule,
    to_dict,
)


def _build_network(
    network_params: Optional[Dict[str, Any]],
) -> Optional[CommonNetwork]:
    """Convert snake_case network suboptions to a CommonNetwork, or None if empty."""
    if not network_params:
        return None

    mapping = {
        "subnets": "subnets",
        "pod_cidr": "podCidr",
        "service_cidr": "serviceCidr",
        "outbound_type": "outboundType",
    }
    values = {
        api_name: network_params[option]
        for option, api_name in mapping.items()
        if network_params.get(option) is not None
    }
    return CommonNetwork(**values) if values else None


class ComputeClusterModule(ServicesModule):
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
                ("state", "absent", ("crn", "name"), True),
            ],
            required_by={"name": ("environment",)},
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
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}
        self._environment_crn_cache: Optional[str] = None

    def _environment_crn(self) -> Optional[str]:
        """
        Resolve the environment option (name or CRN) to a CRN.

        Returns None when an environment name is unknown and state=absent
        (no clusters can exist in it); fails when state=present.
        """
        if self._environment_crn_cache is None and self.environment:
            if self.environment.startswith("crn:"):
                self._environment_crn_cache = self.environment
            else:
                env = CdpEnvClient(self.api_client).describe_environment(
                    self.environment,
                )
                self._environment_crn_cache = env.get("crn") if env else None
                if self._environment_crn_cache is None and self.state == "present":
                    self.module.fail_json(
                        msg=f"Environment '{self.environment}' not found",
                    )
        return self._environment_crn_cache

    def _ensure_managed(self, cluster: ComputeCluster) -> None:
        """Refuse to manage default or embedded clusters."""
        if cluster.isDefault is True or cluster.clusterShape != EXTERNALIZED_SHAPE:
            self.module.fail_json(
                msg=(
                    f"Compute cluster '{cluster.clusterCrn}' is a default or "
                    f"embedded cluster and cannot be managed by this module"
                ),
            )

    def _find_existing(self, client: CdpComputeClient) -> Optional[ComputeCluster]:
        """Return the existing, live externalized cluster, or None."""
        if self.cluster_crn:
            cluster = client.get_cluster_by_crn(self.cluster_crn)
            if cluster is None:
                return None
            self._ensure_managed(cluster)
            if cluster.status in COMPUTE_CLUSTER_DELETED_STATUSES:
                return None
            return cluster

        env_crn = self._environment_crn()
        if env_crn is None:
            return None

        found = client.get_cluster_by_name_and_env(self.name, env_crn)
        return client.get_cluster_by_crn(found.clusterCrn) if found else None

    def _warn_unreconciled(self, existing: ComputeCluster) -> None:
        """
        Warn about options that differ from, and cannot be applied to, an existing cluster.

        Where each option is read back from ``describeCluster`` (verified live):
        ``description`` -> ``description``; ``tags`` -> ``labels``;
        ``network.subnets`` / ``network.service_cidr`` -> ``eks.subnets`` /
        ``eks.serviceCidr``. ``pod_cidr`` and ``outbound_type`` are not returned.
        """
        differing = []
        unverifiable = []

        if self.description is not None and existing.description != self.description:
            differing.append("description")

        if self.tags:
            labels = existing.labels if isinstance(existing.labels, dict) else {}
            if any(labels.get(k) != str(v) for k, v in self.tags.items()):
                differing.append("tags")

        if self.network:
            eks = existing.eks if isinstance(existing.eks, dict) else {}
            network_differs = False
            network_unverifiable = False
            for option, eks_key in (
                ("subnets", "subnets"),
                ("service_cidr", "serviceCidr"),
            ):
                wanted = self.network.get(option)
                if wanted is None:
                    continue
                actual = eks.get(eks_key)
                if actual is None:
                    network_unverifiable = True
                elif option == "subnets":
                    network_differs |= set(wanted) != set(actual)
                else:
                    network_differs |= wanted != actual
            if any(
                self.network.get(o) is not None for o in ("pod_cidr", "outbound_type")
            ):
                network_unverifiable = True
            if network_differs:
                differing.append("network")
            elif network_unverifiable:
                unverifiable.append("network")

        if differing:
            self.module.warn(
                f"Compute cluster '{existing.clusterName}' already exists; "
                f"{', '.join(differing)} differ from the existing cluster, cannot be "
                f"changed on an existing cluster and will be ignored",
            )
        if unverifiable:
            self.module.warn(
                f"Compute cluster '{existing.clusterName}' already exists; "
                f"{', '.join(unverifiable)} could not be verified against the existing "
                f"cluster and will be ignored",
            )

    def _create(self, client: CdpComputeClient) -> None:
        env_crn = self._environment_crn()
        network = _build_network(self.network)

        incoming = ComputeClusterSpec(name=self.name, environment=env_crn)
        if self.description is not None:
            incoming.description = self.description
        if network is not None:
            incoming.network = network
        if self.tags is not None:
            incoming.tags = self.tags

        self.changed = True
        if self.module._diff:
            self.diff["after"] = to_dict(incoming)

        if self.module.check_mode:
            planned = ComputeCluster(clusterName=self.name, envCrn=env_crn)
            if self.description is not None:
                planned.description = self.description
            self.cluster = cluster_to_result(planned)
            return

        response = client.create_cluster(
            name=self.name,
            environment=env_crn,
            description=self.description,
            network=network,
            tags=self.tags,
            skip_validation=self.skip_validation or None,
        )
        created_crn = (
            response.clusterCrn if response.clusterCrn is not NULLABLE else None
        )

        final: Optional[ComputeCluster] = None
        if created_crn:
            if self.wait:
                final = client.wait_for_cluster_state(
                    cluster_crn=created_crn,
                    target_states=COMPUTE_CLUSTER_ACTIVE_STATUSES,
                    timeout=self.timeout,
                    delay=self.delay,
                )
            else:
                final = client.get_cluster_by_crn(created_crn)

        if final is None:
            # Not yet describable: fall back to what createCluster returned
            status = (
                response.clusterStatus.status
                if isinstance(response.clusterStatus, CommonStatusMessage)
                else NULLABLE
            )
            final = ComputeCluster(
                clusterCrn=response.clusterCrn,
                clusterId=response.clusterId,
                clusterName=self.name,
                envCrn=env_crn,
                status=status,
            )
        self.cluster = cluster_to_result(final)

    def _delete(self, client: CdpComputeClient, existing: ComputeCluster) -> None:
        self.changed = True
        if self.module._diff:
            self.diff["before"] = to_dict(existing)

        self.cluster = cluster_to_result(existing)
        if self.module.check_mode:
            return

        client.delete_cluster(
            cluster_crn=existing.clusterCrn,
            force=self.force or None,
            skip_validation=self.skip_validation or None,
            skip_workloads_validation=self.skip_workloads_validation or None,
        )

        if self.wait:
            final = client.wait_for_cluster_state(
                cluster_crn=existing.clusterCrn,
                target_states=COMPUTE_CLUSTER_DELETED_STATUSES,
                timeout=self.timeout,
                delay=self.delay,
            )
            self.cluster = cluster_to_result(final)

    def process(self):
        client = CdpComputeClient(self.api_client)
        existing = self._find_existing(client)

        if self.state == "present":
            if existing:
                self._warn_unreconciled(existing)
                self.cluster = cluster_to_result(existing)
            else:
                self._create(client)
        elif existing:
            self._delete(client, existing)


def main():
    result = ComputeClusterModule()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        cluster=result.cluster,
        diff=result.diff,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
