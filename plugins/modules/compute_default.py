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
    the environment it returns the existing cluster details without making any
    API calls.
  - Deletion of default compute clusters is not supported by the CDP API.
    This module only supports O(state=present).
  - The module supports check_mode.
author:
    - "Jim Enright (@jimright)"
version_added: "3.6.0"
options:
  environment:
    description:
      - The name of the CDP environment.
      - The environment name (not CRN) is required; the CDP environments API
        accepts only an environment name for this operation.
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
      - This parameter applies to Azure environments only and is ignored
        for AWS environments.
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
        operation for default compute clusters.
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
  platform:
    platforms: all
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Initialize the default compute cluster for an AWS environment
# The cloud provider is detected automatically from the environment
- cloudera.cloud.compute_default:
    environment: my-aws-environment
    state: present

# Initialize with specific worker node subnets on AWS
- cloudera.cloud.compute_default:
    environment: my-aws-environment
    worker_node_subnets:
      - subnet-0abc123def456789a
      - subnet-0abc123def456789b
    state: present

# Initialize as a private cluster on AWS
- cloudera.cloud.compute_default:
    environment: my-aws-environment
    private_cluster: true
    state: present

# Initialize the default compute cluster for an Azure environment with UDR egress
- cloudera.cloud.compute_default:
    environment: my-azure-environment
    outbound_type: udr
    state: present
"""

RETURN = r"""
cluster:
  description: Details of the default compute cluster after initialization.
  returned: when O(wait=true) and cluster is running
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
  returned: when O(wait=false) and the cluster was initialized
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

import time
from typing import Any, Dict, List, Optional

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpError,
)


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
        self.changed = False

    def process(self):
        compute_client = CdpComputeClient(self.api_client)
        env_client = CdpEnvClient(self.api_client)

        # Resolve the environment to detect cloud platform
        env_summary = env_client.get_environment_by_name(self.environment)
        if env_summary is None:
            self.module.fail_json(
                msg=f"Environment '{self.environment}' not found.",
            )

        cloud_platform = env_summary.get("cloudPlatform", "").upper()
        if cloud_platform not in ("AWS", "AZURE"):
            self.module.fail_json(
                msg=(
                    f"Unsupported cloud platform '{cloud_platform}' for environment "
                    f"'{self.environment}'. Only AWS and AZURE are supported."
                ),
            )

        # Check for an existing default cluster in this environment
        existing_clusters = compute_client.get_clusters_by_env(
            self.environment,
            default=True,
        )
        active_existing = [
            c
            for c in existing_clusters
            if c.get("status") in CdpComputeClient.ACTIVE_STATES
        ]

        if active_existing:
            # Default cluster already exists — idempotent
            self.cluster = camel_dict_to_snake_dict(active_existing[0])
            return

        # No active default cluster — initialize one
        self.changed = True

        if not self.module.check_mode:
            if cloud_platform == "AWS":
                response = env_client.initialize_aws_compute_cluster(
                    environment_name=self.environment,
                    private_cluster=self.private_cluster,
                    kube_api_authorized_ip_ranges=self.kube_api_authorized_ip_ranges,
                    worker_node_subnets=self.worker_node_subnets,
                )
            else:
                # AZURE — outbound_type only applies to Azure; not passed for AWS
                response = env_client.initialize_azure_compute_cluster(
                    environment_name=self.environment,
                    private_cluster=self.private_cluster,
                    kube_api_authorized_ip_ranges=self.kube_api_authorized_ip_ranges,
                    worker_node_subnets=self.worker_node_subnets,
                    outbound_type=self.outbound_type,
                )

            self.operation_id = response.get("operationId")

            if self.wait:
                self.cluster = self._wait_for_default_cluster(compute_client)
            # wait=False: cluster and operation_id both returned via main()

    def _wait_for_default_cluster(
        self,
        compute_client: CdpComputeClient,
    ) -> Dict[str, Any]:
        """
        Poll list_clusters(default=True) until a cluster in ACTIVE_STATES appears.

        No CRN is returned by the initialize API so we cannot use
        wait_for_cluster_state directly. Instead we poll the list endpoint.
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise CdpError(
                    f"Timeout waiting for default compute cluster in environment "
                    f"'{self.environment}' to reach a running state after "
                    f"{self.timeout} seconds",
                )

            clusters = compute_client.get_clusters_by_env(
                self.environment,
                default=True,
            )

            for cluster in clusters:
                current_state = cluster.get("status")

                if current_state in CdpComputeClient.ACTIVE_STATES:
                    return camel_dict_to_snake_dict(cluster)

                if current_state in CdpComputeClient.FAILED_STATES:
                    msg = cluster.get("statusMessage", "Unknown error")
                    raise CdpError(
                        f"Default compute cluster entered failed state "
                        f"'{current_state}': {msg}",
                    )

            time.sleep(self.delay)


def main():
    result = ComputeDefaultCluster()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        cluster=result.cluster,
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
