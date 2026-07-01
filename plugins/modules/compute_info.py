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
    - When O(cluster_crn) is provided, describes that single cluster in detail.
    - When O(environment) is provided, lists all clusters in that environment.
    - When neither is provided, lists all compute clusters.
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
  - cloudera.cloud.cdp_client
attributes:
  check_mode:
    support: full
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
  description: The information about the named Cluster or Clusters.
  returned: always
  type: list
  elements: dict
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
      description: Compute cluster status.
      returned: always
      type: str
    message:
      description: Message with additional details about the cluster status.
      returned: when available
      type: str
    env_crn:
      description: CDP environment CRN.
      returned: always
      type: str
    env_name:
      description: CDP environment name.
      returned: always
      type: str
    env_cloud_provider:
      description: CDP environment cloud provider.
      returned: when available
      type: str
    compute_platform:
      description: Compute cluster platform provider.
      returned: when available
      type: str
    compute_platform_version:
      description: Compute cluster platform version.
      returned: when available
      type: str
    kubernetes_version:
      description: Kubernetes version.
      returned: when available
      type: str
    cluster_type:
      description: Compute cluster type.
      returned: when available
      type: str
    cluster_shape:
      description: The shape of the cluster (Embedded or Externalized).
      returned: when available
      type: str
    cluster_size:
      description: Number of nodes in the cluster.
      returned: when available
      type: int
    is_default:
      description: Whether the cluster is the default cluster for its environment.
      returned: when available
      type: bool
    is_cloudera_managed:
      description: Whether the cluster is Cloudera managed.
      returned: when describe is used
      type: bool
    creation_time:
      description: Compute cluster creation time in ISO format.
      returned: when available
      type: str
    update_time:
      description: Compute cluster update time in ISO format.
      returned: when available
      type: str
    deletion_time:
      description: Compute cluster deletion time in ISO format.
      returned: when available
      type: str
    region:
      description: Region.
      returned: when available
      type: str
    labels:
      description: Map of labels associated with this cluster.
      returned: when available
      type: dict
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
      description: List of available Kubernetes upgrades.
      returned: when available
      type: list
      elements: str
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

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
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
                self.clusters.append(camel_dict_to_snake_dict(cluster))
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

            self.clusters = [camel_dict_to_snake_dict(c) for c in clusters]


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
