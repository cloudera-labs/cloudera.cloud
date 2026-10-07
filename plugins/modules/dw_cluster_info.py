#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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
module: dw_cluster_info
short_description: Gather information about CDP Data Warehouse Clusters
description:
    - Gather information about CDP Data Warehouse Clusters.
    - Returns a single cluster when O(cluster_id) is specified, all clusters in an
      environment when O(environment) is specified, or all clusters when neither is
      specified.
    - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Jim Enright (@jenright)"
version_added: "1.0.0"
options:
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
      - Mutually exclusive with O(environment).
    type: str
    aliases:
      - id
  environment:
    description:
      - The name or CRN of the Environment in which to find and describe Data Warehouse Clusters.
      - Mutually exclusive with O(cluster_id).
    type: str
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List information about all Data Warehouse Clusters
- cloudera.cloud.dw_cluster_info:

# Gather information about all Data Warehouse Clusters within an Environment
- cloudera.cloud.dw_cluster_info:
    env: example-environment

# Gather information about an identified Cluster
- cloudera.cloud.dw_cluster_info:
    cluster_id: env-xyzabc
"""

RETURN = r"""
clusters:
  description: The information about the named Cluster or Clusters
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The cluster identifier.
      returned: always
      type: str
    environmentCrn:
      description: The CRN of the cluster's Environment
      returned: always
      type: str
    crn:
      description: The cluster's CRN.
      returned: always
      type: str
    creationDate:
      description: The creation timestamp of the cluster in UTC.
      returned: always
      type: str
    status:
      description: The status of the cluster
      returned: always
      type: str
    creator:
      description: The cluster creator details.
      returned: always
      type: dict
      contains:
        crn:
          description: The Actor CRN.
          type: str
          returned: always
        email:
          description: Email address (users).
          type: str
          returned: when supported
        workloadUsername:
          description: Username (users).
          type: str
          returned: when supported
        machineUsername:
          description: Username (machine users).
          type: str
          returned: when supported
    cloudPlatform:
      description: The cloud platform of the environment that was used to create this cluster.
      returned: always
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

from typing import Any, Dict, List

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    ClusterSummary,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)


class DwClusterInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                cluster_id=dict(type="str", aliases=["id"]),
                environment=dict(type="str", aliases=["env"]),
            ),
            mutually_exclusive=[["cluster_id", "environment"]],
            supports_check_mode=True,
        )

        self.cluster_id = self.get_param("cluster_id")
        self.environment = self.get_param("environment")

        self.clusters: List[ClusterSummary] = []

    def process(self):
        client = CdpDwClient(api_client=self.api_client)

        if self.cluster_id is not None:
            cluster = client.describe_cluster(cluster_id=self.cluster_id)
            if cluster is not None:
                self.clusters = [cluster]
        elif self.environment is not None:
            env_client = CdpEnvClient(api_client=self.api_client)
            if self.environment.startswith("crn:"):
                env_crn = self.environment
            else:
                env_crn = env_client.get_environment_crn(self.environment)
            if env_crn:
                self.clusters = client.list_clusters(env_crn=env_crn)
        else:
            self.clusters = client.list_clusters()


def main():
    result = DwClusterInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        clusters=[to_dict(c) for c in result.clusters],
    )

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
