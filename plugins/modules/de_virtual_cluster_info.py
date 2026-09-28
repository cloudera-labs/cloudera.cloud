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
module: de_virtual_cluster_info
short_description: Gather information about CDP Data Engineering Virtual Clusters
description:
    - Gather information about CDP Data Engineering Virtual Clusters
author:
  - "Curtis Howard (@curtishoward)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.5.0"
options:
  name:
    description:
      - If a name is provided, that Virtual Cluster will be described (if it exists).
      - Note that Virtual Cluster names are unique within a given CDE Service.
    type: str
    required: False
  environment:
    description:
      - The CDP environment name of the CDE Service containing the Virtual Cluster(s).
    type: str
    required: True
    aliases:
      - env
  service_name:
    description:
      - The name of the CDE Service containing the Virtual Cluster(s).
    type: str
    required: True
    aliases:
      - cluster_name

extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: List basic information about all Virtual Clusters within a CDE Service
  cloudera.cloud.de_virtual_cluster_info:
    environment: my-environment
    service_name: my-cde-service

- name: Gather detailed information about a named Virtual Cluster
  cloudera.cloud.de_virtual_cluster_info:
    environment: my-environment
    service_name: my-cde-service
    name: my-virtual-cluster
"""

RETURN = r"""
virtual_clusters:
  description: The information about the named Virtual Cluster or Virtual Clusters.
  type: list
  returned: always
  elements: complex
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

from typing import Any, Dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
)


class DEVirtualClusterInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=False, type="str"),
                environment=dict(required=True, type="str", aliases=["env"]),
                service_name=dict(
                    required=True,
                    type="str",
                    aliases=["cluster_name"],
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.environment = self.get_param("environment")
        self.service_name = self.get_param("service_name")

        # Initialize return values
        self.virtual_clusters = []

    def process(self):
        self.de_client = CdpDeClient(self.api_client)

        service = self.de_client.get_service_by_name(
            self.service_name,
            env_name=self.environment,
        )
        if service is None:
            return

        cluster_id = service.clusterId

        if self.name:
            vc = self.de_client.get_virtual_cluster_by_name(cluster_id, self.name)
            if vc:
                self.virtual_clusters.append(to_dict(vc))
        else:
            for summary in self.de_client.list_virtual_clusters(cluster_id):
                if summary.vcId:
                    vc = self.de_client.describe_virtual_cluster(
                        cluster_id,
                        summary.vcId,
                    )
                    if vc:
                        self.virtual_clusters.append(to_dict(vc))


def main():
    result = DEVirtualClusterInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        virtual_clusters=result.virtual_clusters,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
