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
module: de_info
short_description: Gather information about CDP Data Engineering Services
description:
    - Gather information about CDP Data Engineering Services
author:
  - "Ronald Suplina (@rsuplina)"
  - "Curtis Howard (@curtishoward)"
  - "Alan Silva (@acsjumpi)"
version_added: "1.5.0"
options:
  name:
    description:
      - If a name is provided, that Data Engineering Service will be described
      - Must be the string name of the CDE service
      - Mutually exclusive with cluster_id and env_name
    type: str
    required: False
  cluster_id:
    description:
      - If a cluster_id is provided, that Data Engineering Service will be described
      - Mutually exclusive with name and env_name
    type: str
    required: False
    aliases:
      - id
  env_name:
    description:
      - If an env_name is provided, the Data Engineering Service for that Environment will be described
      - Mutually exclusive with name and cluster_id
    type: str
    required: False
    aliases:
      - environment

extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all Data Engineering Services
- cloudera.cloud.de_info:

# Gather detailed information about a named Data Engineering Service
- cloudera.cloud.de_info:
    name: example-de-service

# Gather detailed information about a Data Engineering Service using a cluster ID
- cloudera.cloud.de_info:
    cluster_id: cluster-12345

# Gather detailed information about a Data Engineering Service using an Environment name
- cloudera.cloud.de_info:
    env_name: my-environment
"""

RETURN = r"""
services:
  description: The information about the named Data Engineering Service or Data Engineering Services
  type: list
  returned: always
  elements: complex
  contains:
    clusterId:
      description: Cluster Id of the CDE Service
      returned: always
      type: str
    name:
      description: Name of the CDE Service
      returned: always
      type: str
    environmentName:
      description: CDP Environment Name
      returned: always
      type: str
    environmentCrn:
      description: CRN of the environment
      returned: when available
      type: str
    status:
      description: Status of the CDE service
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform where the CDE service is enabled
      returned: when available
      type: str
    clusterFqdn:
      description: FQDN of the CDE service
      returned: when available
      type: str
    creatorEmail:
      description: Email address of the creator of the CDE service
      returned: when available
      type: str
    creatorCrn:
      description: CRN of the creator
      returned: when available
      type: str
    enablingTime:
      description: Timestamp of service enabling
      returned: when available
      type: str
    resources:
      description: Resources details of CDE Service
      returned: when available
      type: dict
      contains:
        instance_type:
          description: Instance type of the CDE service
          returned: when available
          type: str
        min_instances:
          description: Minimum Instances for the CDE service
          returned: when available
          type: str
        max_instances:
          description: Maximum instances for the CDE service
          returned: when available
          type: str
        min_spot_instances:
          description: Minimum number of spot instances for the CDE service
          returned: when available
          type: str
        max_spot_instances:
          description: Maximum Number of Spot instances
          returned: when available
          type: str
        initial_instances:
          description: Initial instances for the CDE service
          returned: when available
          type: str
        initial_spot_instances:
          description: Initial Spot Instances for the CDE Service
          returned: when available
          type: str
        root_vol_size:
          description: Root Volume Size
          returned: when available
          type: str
        cpuRequests:
          description: CPU Requests for the entire CDE service quota
          returned: when available
          type: str
        memoryRequests:
          description: Memory requests for the entire CDE service quota
          returned: when available
          type: str
        resourcePool:
          description: Resource Pool for the CDE service
          returned: when available
          type: str
        allPurposeInstanceGroupDetails:
          description: Resource details for the nodes used in All Purpose Virtual Clusters
          returned: when available
          type: dict
    logLocation:
      description: Location for the log files of jobs
      returned: when available
      type: str
    dataLakeFileSystems:
      description: The Data lake file system
      returned: when available
      type: str
    dataLakeAtlasUIEndpoint:
      description: Endpoint of Data Lake Atlas
      returned: when available
      type: str
    whitelistIps:
      description: List of CIDRs that would be allowed to access kubernetes master API server
      returned: when available
      type: str
    loadbalancerAllowlist:
      description: Comma-separated CIDRs that would be allowed to access the load balancer
      returned: when available
      type: str
    publicEndpointEnabled:
      description: If true, the CDE endpoint was created in a publicly accessible subnet
      returned: when available
      type: bool
    workloadAnalyticsEnabled:
      description: If true, diagnostic information about job and query execution is sent to Cloudera Workload Manager
      returned: when available
      type: bool
    privateClusterEnabled:
      description: If true, the CDE service was created with fully private Azure services
      returned: when available
      type: bool
    networkOutboundType:
      description: Network outbound type
      returned: when available
      type: str
    subnets:
      description: List of Subnet IDs of the CDP subnets used by the kubernetes worker node
      returned: when available
      type: str
    ssdUsed:
      description: If true, SSD would have been be used for workload filesystem
      returned: when available
      type: bool
    previousVersionDeployed:
      description: The "true" value indicates that the previous version of the CDE service was requested to be deployed
      returned: when available
      type: bool
    backupLocation:
      description: Base location for the service backup archives
      returned: when available
      type: str
    tenantId:
      description: CDP tenant ID
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

from typing import Any, Dict
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import CdpDeClient


class DEServiceInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=False, type="str"),
                cluster_id=dict(required=False, type="str", aliases=["id"]),
                env_name=dict(required=False, type="str", aliases=["environment"]),
            ),
            supports_check_mode=True,
            mutually_exclusive=[["name", "cluster_id", "env_name"]],
        )

        # Set parameters
        self.name = self.get_param("name")
        self.cluster_id = self.get_param("cluster_id")
        self.env_name = self.get_param("env_name")

        # Initialize return values
        self.services = []

    def process(self):
        self.de_client = CdpDeClient(self.api_client)

        if self.name:
            service = self.de_client.get_service_by_name(self.name)
            if service:
                self.services.append(service.get("service", {}))
        elif self.cluster_id:
            service = self.de_client.get_service_by_cluster_id(self.cluster_id)
            if service:
                self.services.append(service.get("service", {}))
        elif self.env_name:
            env_services = self.de_client.get_service_by_env_name(self.env_name)
            self.services = [s.get("service", {}) for s in env_services]
        else:
            response = self.de_client.list_services()
            for svc in response.get("services", []):
                service_details = self.de_client.describe_service(svc["clusterId"])
                if service_details and service_details.get("service"):
                    self.services.append(service_details.get("service", {}))


def main():
    result = DEServiceInfo()

    output: Dict[str, Any] = dict(
        changed=False,
        services=result.services,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
