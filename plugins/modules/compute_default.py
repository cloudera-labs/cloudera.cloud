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
module: compute_default
short_description: Initialize the default compute cluster for a CDP Environment
description:
  - Initializes the default (embedded, environment-scoped) compute cluster for
    a CDP Environment on AWS or Azure.
  - The cloud provider is detected automatically from the environment's
    C(cloudPlatform) field.
  - The module is idempotent. If a default compute cluster already exists for
    the environment, no new initialization is requested and the existing
    cluster is returned. A cluster that is still being created is not
    initialized again; the module waits for it if O(wait=true).
  - If the existing default cluster is in a failed state, the module fails
    and does not retry the initialization.
  - Deletion of default compute clusters is not supported by the CDP API.
    This module only supports O(state=present).
  - The module supports check_mode and diff mode.
  - Check mode never initializes a cluster and never waits.
author:
    - "Jim Enright (@jimright)"
version_added: "3.6.0"
options:
  environment:
    description:
      - Name or CRN of the CDP environment.
      - A CRN is resolved to the environment name, because the CDP
        environments API accepts only a name for this operation.
      - The module fails if the environment does not exist, also in check mode.
    type: str
    required: true
    aliases:
      - env
  private_cluster:
    description:
      - If C(true), the compute cluster will be created as a private cluster.
      - Mutually exclusive with O(kube_api_authorized_ip_ranges).
    type: bool
    required: false
  kube_api_authorized_ip_ranges:
    description:
      - List of CIDR blocks authorized to access the Kubernetes API server.
      - Mutually exclusive with O(private_cluster).
    type: list
    elements: str
    required: false
  worker_node_subnets:
    description:
      - List of subnet IDs to use for Kubernetes worker nodes.
    type: list
    elements: str
    required: false
  outbound_type:
    description:
      - Customize the cluster egress with a defined outbound type in Azure
        Kubernetes Service.
      - Valid values are C(udr) (User-Defined Routing).
      - This parameter applies to Azure environments only. The module fails
        if it is set for an AWS environment, also in check mode.
    type: str
    required: false
    choices:
      - udr
  wait:
    description:
      - If C(true), wait for the default cluster to reach a running state
        before returning.
      - If C(false), return immediately after issuing the initialization
        request with the operation ID.
      - This also applies when a default cluster is already being created, in
        which case the module returns its current summary without waiting.
      - Check mode never waits, even if a default cluster is being created.
    type: bool
    required: false
    default: true
  delay:
    description:
      - The polling interval in seconds while waiting for the cluster to
        reach a running state.
    type: int
    required: false
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The maximum time in seconds to wait for the cluster to reach a
        running state.
    type: int
    required: false
    default: 3600
    aliases:
      - polling_timeout
  state:
    description:
      - Desired state of the default compute cluster.
      - Only C(present) is supported. The CDP API does not provide a delete
        operation for default compute clusters, so there is no C(absent).
      - To delete an externalized cluster use M(cloudera.cloud.compute); it
        refuses to delete a default cluster.
    type: str
    required: false
    choices:
      - present
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

# Initialize the default compute cluster for an AWS environment and wait for it.
# The cloud provider is detected automatically from the environment.
- name: Initialize the default compute cluster
  cloudera.cloud.compute_default:
    environment: my-aws-environment

# Initialize on AWS with specific worker node subnets and API access ranges
- name: Initialize with subnets and authorized IP ranges
  cloudera.cloud.compute_default:
    environment: my-aws-environment
    worker_node_subnets:
      - subnet-0abc123def456789a
      - subnet-0abc123def456789b
    kube_api_authorized_ip_ranges:
      - 10.0.0.0/8

# Initialize as a private cluster on AWS
- name: Initialize a private default compute cluster
  cloudera.cloud.compute_default:
    environment: my-aws-environment
    private_cluster: true

# Initialize on Azure with user-defined routing for egress
- name: Initialize the default compute cluster on Azure
  cloudera.cloud.compute_default:
    environment: my-azure-environment
    outbound_type: udr

# Do not wait; use the returned operation ID
- name: Request the default compute cluster without waiting
  cloudera.cloud.compute_default:
    environment: my-aws-environment
    wait: false
  register: default_cluster

# Identify the environment by CRN
- name: Initialize the default compute cluster by environment CRN
  cloudera.cloud.compute_default:
    environment: crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid
"""

RETURN = r"""
cluster:
  description:
    - Details of the default compute cluster. The fields depend on the path taken.
    - A full cluster description is returned when the default cluster is already
      running, and when the module waited for it (O(wait=true), not in check mode).
      It then holds more fields than are listed here.
    - Only a summary of the cluster, with the fields listed here, is returned
      when a default cluster is still being created and the module did not wait
      (O(wait=false), or check mode).
    - An empty dictionary is returned after an initialization with O(wait=false),
      and in check mode when the cluster would be initialized.
    - If the default cluster is in a failed state the module fails and returns no
      cluster; the failure message is in C(msg).
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
      returned: when available
      type: str
    status:
      description: Current cluster status (for example C(CREATING), C(RUNNING)).
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
    is_default:
      description: Whether this is the default cluster for its environment.
      returned: when available
      type: bool
    creation_time:
      description: Cluster creation time in ISO format.
      returned: when available
      type: str
operation_id:
  description: The ID of the initialization operation.
  returned: when O(wait=false) and a cluster was initialized
  type: str
diff:
  description:
    - The initialization request when run with C(--diff), also in check mode.
    - Both parts are empty if nothing changes.
  returned: always
  type: dict
  contains:
    before:
      description: Always empty; the default cluster did not exist.
      type: dict
    after:
      description:
        - The initialization request.
        - Holds C(environmentName), the environment name (a CRN given in O(environment) is shown as the name),
          and the options that were set, using the API names (for example C(privateCluster),
          C(workerNodeSubnets), C(kubeApiAuthorizedIpRanges), C(outboundType)).
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

from typing import Any, Dict, Optional, Tuple

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_FAILED_STATUSES,
    CdpComputeClient,
    cluster_to_result,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
    ComputeClusterConfig,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)

PLATFORM_AWS = "AWS"
PLATFORM_AZURE = "AZURE"


class ComputeDefaultCluster(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                environment=dict(required=True, type="str", aliases=["env"]),
                private_cluster=dict(required=False, type="bool"),
                kube_api_authorized_ip_ranges=dict(
                    required=False,
                    type="list",
                    elements="str",
                ),
                worker_node_subnets=dict(
                    required=False,
                    type="list",
                    elements="str",
                ),
                outbound_type=dict(
                    required=False,
                    type="str",
                    choices=["udr"],
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
                    choices=["present"],
                    default="present",
                ),
            ),
            supports_check_mode=True,
            mutually_exclusive=[["private_cluster", "kube_api_authorized_ip_ranges"]],
        )

        # Set parameters
        self.environment = self.get_param("environment")
        self.private_cluster = self.get_param("private_cluster")
        self.kube_api_authorized_ip_ranges = self.get_param(
            "kube_api_authorized_ip_ranges",
        )
        self.worker_node_subnets = self.get_param("worker_node_subnets")
        self.outbound_type = self.get_param("outbound_type")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        # Initialize return values
        self.cluster: Dict[str, Any] = {}
        self.operation_id: Optional[str] = None
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}
        self.changed = False

    def _resolve_environment(self, env_client: CdpEnvClient) -> Tuple[str, str]:
        """
        Resolve the environment option (name or CRN) to (name, platform).

        The initialize API takes a name only, so a CRN is resolved to the name.
        Fails for an unknown environment or a platform other than AWS/Azure.
        """
        env = env_client.describe_environment(self.environment)
        if not env:
            self.module.fail_json(msg=f"Environment '{self.environment}' not found")

        name = env.get("environmentName") or self.environment
        platform = str(env.get("cloudPlatform") or "").upper()
        if platform not in (PLATFORM_AWS, PLATFORM_AZURE):
            self.module.fail_json(
                msg=(
                    f"Unsupported cloud platform '{platform}' for environment "
                    f"'{name}'. Only AWS and AZURE are supported."
                ),
            )
        return name, platform

    def _build_config(self) -> ComputeClusterConfig:
        """Build the config from the options; unset options stay NULLABLE."""
        mapping = {
            "private_cluster": "privateCluster",
            "kube_api_authorized_ip_ranges": "kubeApiAuthorizedIpRanges",
            "worker_node_subnets": "workerNodeSubnets",
            "outbound_type": "outboundType",
        }
        values = {
            api_name: getattr(self, option)
            for option, api_name in mapping.items()
            if getattr(self, option) is not None
        }
        return ComputeClusterConfig(**values)

    def process(self):
        env_client = CdpEnvClient(self.api_client)
        client = CdpComputeClient(self.api_client)

        environment, platform = self._resolve_environment(env_client)

        if self.outbound_type is not None and platform == PLATFORM_AWS:
            self.module.fail_json(
                msg=(
                    f"outbound_type is only supported for Azure environments; "
                    f"environment '{environment}' is on AWS"
                ),
            )

        existing = client.get_default_cluster(environment)

        if existing is not None:
            status = existing.status
            if status in COMPUTE_CLUSTER_ACTIVE_STATUSES:
                # Describe for the full result; if the cluster vanished since
                # the list call, report what was listed.
                described = client.describe_cluster(existing.clusterCrn)
                self.cluster = cluster_to_result(described or existing)
                return

            if status in COMPUTE_CLUSTER_FAILED_STATUSES:
                message = existing.message
                if not isinstance(message, str):
                    message = "Unknown error"
                self.module.fail_json(
                    msg=(
                        f"Default compute cluster of environment '{environment}' "
                        f"is in failed state '{status}': {message}"
                    ),
                )

            # In progress: a creating status, or a null/unset/unrecognised one.
            # Never initialize again over an existing default cluster.
            if self.wait and not self.module.check_mode:
                self.cluster = cluster_to_result(
                    client.wait_for_default_cluster(
                        environment,
                        self.timeout,
                        self.delay,
                    ),
                )
            else:
                self.cluster = cluster_to_result(existing)
            return

        # No default cluster: initialize one
        config = self._build_config()

        self.changed = True
        if self.module._diff:
            # The request: the target environment plus the requested config
            self.diff["after"] = {"environmentName": environment, **to_dict(config)}

        if self.module.check_mode:
            return

        if platform == PLATFORM_AWS:
            response = env_client.initialize_aws_compute_cluster(environment, config)
        else:
            response = env_client.initialize_azure_compute_cluster(environment, config)

        operation_id = response.operationId
        self.operation_id = operation_id if isinstance(operation_id, str) else None

        if self.wait:
            self.cluster = cluster_to_result(
                client.wait_for_default_cluster(
                    environment,
                    self.timeout,
                    self.delay,
                ),
            )


def main():
    result = ComputeDefaultCluster()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        cluster=result.cluster,
        diff=result.diff,
    )

    # operation_id is only surfaced when wait=False (per RETURN docs).
    # When wait=True the caller already has the cluster details; the transient
    # operation ID is not useful and is intentionally omitted.
    if not result.wait and result.operation_id is not None:
        output["operation_id"] = result.operation_id

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
