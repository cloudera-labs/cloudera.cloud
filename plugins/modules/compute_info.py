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
module: compute_info
short_description: Gather information about CDP Compute Clusters
description:
    - Gather information about CDP Compute Clusters.
    - When O(crn) is provided, describes that single cluster in detail.
    - When O(environment) is provided, lists all clusters in that environment.
    - When neither is provided, lists all compute clusters.
    - Clusters listed by environment or without a filter are summaries and carry fewer
      fields than a cluster described by O(crn).
    - The module supports check_mode.
author:
    - "Jim Enright (@jimright)"
version_added: "3.6.0"
options:
  crn:
    description:
      - The CRN of the compute cluster to describe.
      - Mutually exclusive with O(environment).
    type: str
    required: false
    aliases:
      - cluster_crn
  environment:
    description:
      - The name or CRN of the CDP Environment used to filter clusters.
      - Mutually exclusive with O(crn).
    type: str
    required: false
    aliases:
      - env
  cluster_shape:
    description:
      - Filter clusters by shape.
      - Only used when O(crn) is not specified.
    type: str
    required: false
    choices:
      - Externalized
      - Embedded
    aliases:
      - shape
  default:
    description:
      - If C(true), only return the default cluster(s).
      - Only used when O(crn) is not specified.
    type: bool
    required: false
    aliases:
      - default_cluster
  include_deleted:
    description:
      - If C(true), include deleted clusters in the results.
      - Only used when O(crn) is not specified.
    type: bool
    required: false
    default: false
  status:
    description:
      - Filter clusters by status string.
      - Only used when O(crn) is not specified.
    type: str
    required: false
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.cloud.cdp_client
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  platform:
    platforms: all
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List all compute clusters
- cloudera.cloud.compute_info:

# List all compute clusters in a specific environment
- cloudera.cloud.compute_info:
    environment: my-environment

# Describe a specific compute cluster by CRN
- cloudera.cloud.compute_info:
    crn: "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"

# List only default clusters
- cloudera.cloud.compute_info:
    default: true

# List clusters including deleted ones
- cloudera.cloud.compute_info:
    include_deleted: true
"""

RETURN = r"""
clusters:
  description:
    - The information about the named cluster or clusters.
    - Fields that the API did not return are omitted.
  returned: always
  type: list
  elements: dict
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
      description: Compute cluster status (for example C(CREATING), C(RUNNING), C(DELETED)).
      returned: when available
      type: str
    message:
      description: Message with additional details about the cluster status.
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
    cluster_type:
      description: Cluster type (for example C(Shared) or C(Dedicated)).
      returned: when available
      type: str
    cluster_size:
      description: Cluster size.
      returned: when available
      type: int
    cluster_state_version:
      description: State version of the cluster.
      returned: when available
      type: int
    compute_platform:
      description: Underlying compute platform (for example C(EKS), C(AKS)).
      returned: when available
      type: str
    kubernetes_version:
      description: Kubernetes version.
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
    env_cloud_provider:
      description: Cloud provider of the CDP environment.
      returned: when available
      type: str
    region:
      description: Cloud region.
      returned: when available
      type: str
    creation_time:
      description: Cluster creation time in ISO format.
      returned: when available
      type: str
    update_time:
      description: Time of the last cluster update in ISO format.
      returned: when available
      type: str
    deletion_time:
      description: Cluster deletion time in ISO format.
      returned: when available
      type: str
    labels:
      description: Labels on the cluster. Keys are returned as provided.
      returned: when available
      type: dict
    workloads:
      description: Workloads running on the cluster.
      returned: when described by O(crn)
      type: list
      elements: str
    is_cloudera_managed:
      description: Whether the cluster is managed by Cloudera.
      returned: when described by O(crn)
      type: bool
    api_end_point:
      description: Kubernetes API endpoint of the cluster.
      returned: when described by O(crn)
      type: str
    cluster_owner:
      description: Cluster owner details.
      returned: when available
      type: dict
      contains:
        account_id:
          description: Owner's account ID.
          type: str
          returned: when available
        crn:
          description: Owner's actor CRN.
          type: str
          returned: when available
        email:
          description: Owner's email.
          type: str
          returned: when available
        first_name:
          description: Owner's first name.
          type: str
          returned: when available
        last_name:
          description: Owner's last name.
          type: str
          returned: when available
        user_id:
          description: Owner's user ID.
          type: str
          returned: when available
    available_upgrades:
      description: Available Kubernetes upgrades.
      returned: when available
      type: list
      elements: raw
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

from typing import Any, Dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
    cluster_to_result,
)


class ComputeClusterInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                crn=dict(required=False, type="str", aliases=["cluster_crn"]),
                environment=dict(
                    required=False,
                    type="str",
                    aliases=["env"],
                ),
                cluster_shape=dict(
                    required=False,
                    type="str",
                    choices=["Externalized", "Embedded"],
                    aliases=["shape"],
                ),
                default=dict(required=False, type="bool", aliases=["default_cluster"]),
                include_deleted=dict(required=False, type="bool", default=False),
                status=dict(required=False, type="str"),
            ),
            supports_check_mode=True,
            mutually_exclusive=[["crn", "environment"]],
        )

        # Set parameters
        self.cluster_crn = self.get_param("crn")
        self.env_name_or_crn = self.get_param("environment")
        self.cluster_shape = self.get_param("cluster_shape")
        self.default_only = self.get_param("default")
        self.include_deleted = self.get_param("include_deleted")
        self.status = self.get_param("status")

        # Initialize return values
        self.clusters = []

    def process(self):
        compute_client = CdpComputeClient(self.api_client)

        if self.cluster_crn:
            cluster = compute_client.get_cluster_by_crn(self.cluster_crn)
            if cluster:
                self.clusters.append(cluster_to_result(cluster))
        else:
            filter_kwargs: Dict[str, Any] = {}
            if self.cluster_shape is not None:
                filter_kwargs["cluster_shape"] = self.cluster_shape
            if self.default_only is not None:
                filter_kwargs["default"] = self.default_only
            if self.include_deleted is not None:
                filter_kwargs["include_deleted"] = self.include_deleted
            if self.status is not None:
                filter_kwargs["status"] = self.status

            if self.env_name_or_crn:
                clusters = compute_client.get_clusters_by_env(
                    self.env_name_or_crn,
                    **filter_kwargs,
                )
            else:
                clusters = compute_client.get_all_clusters(**filter_kwargs)

            self.clusters = [cluster_to_result(c) for c in clusters]


def main():
    result = ComputeClusterInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        clusters=result.clusters,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
