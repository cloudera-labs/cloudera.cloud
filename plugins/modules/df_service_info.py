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
module: df_service_info
short_description: Gather information about CDP DataFlow Services
description:
    - Gather information about CDP DataFlow Services
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.2.0"
options:
  name:
    description:
      - If a name is provided, that DataFlow Service will be described
      - Must be the string name of the CDP Environment
      - Mutually exclusive with df_crn and env_crn
    type: str
    required: False
  df_crn:
    description:
      - If a df_crn is provided, that DataFlow Service will be described
      - Mutually exclusive with name and env_crn
    type: str
    required: False
  env_crn:
    description:
      - If an env_crn is provided, the DataFlow Service for that Environment will be described
      - Mutually exclusive with name and df_crn
    type: str
    required: False

extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all DataFlow Services
- cloudera.cloud.df_service_info:

# Gather detailed information about a named DataFlow Service using a name
- cloudera.cloud.df_service_info:
    name: example-service

# Gather detailed information about a named DataFlow Service using a Dataflow CRN
- cloudera.cloud.df_service_info:
    df_crn: crn:cdp:df:region:tenant-uuid4:service:service-uuid4

# Gather detailed information about a named DataFlow Service using an Environment CRN
- cloudera.cloud.df_service_info:
    env_crn: crn:cdp:environments:region:tenant-uuid4:environment:environment-uuid4
"""

RETURN = r"""
services:
  description: The information about the named DataFlow Service or DataFlow Services
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description: The DataFlow Service's CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Service's parent environment name.
      returned: always
      type: str
    environmentCrn:
      description: The DataFlow Service's Parent Environment CRN.
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform of the environment.
      returned: always
      type: str
    region:
      description: The region of the environment.
      returned: always
      type: str
    deploymentCount:
      description: The deployment count.
      returned: always
      type: int
    minK8sNodeCount:
      description: The minimum number of Kubernetes nodes that need to be provisioned in the environment.
      returned: always
      type: int
    maxK8sNodeCount:
      description: The maximum number of Kubernetes nodes that the environment may scale up to under high-demand situations.
      returned: always
      type: int
    status:
      description: The status of a DataFlow enabled environment.
      returned: always
      type: dict
      contains:
        state:
          description: The state of the environment.
          returned: always
          type: str
        message:
          description: A status message for the environment.
          returned: always
          type: str
        detailedState:
          description: A detailed state of the environment.
          returned: when available
          type: str
    clusterId:
      description: Cluster id of the environment.
      returned: if enabled
      type: str
    instanceType:
      description: The instance type of the kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: str
    proxyName:
      description: The name of the proxy configuration used by the service.
      returned: when available
      type: str
    enforceProject:
      description: Whether project enforcement is enabled for the service.
      returned: when available
      type: bool
    runningK8sNodeCount:
      description: The number of kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: int
    creatingK8sNodeCount:
      description: The number of kubernetes nodes currently being created by DataFlow for this environment.
      returned: always
      type: int
    terminatingK8sNodeCount:
      description: The number of kubernetes nodes currently being terminated by DataFlow for this environment.
      returned: always
      type: int
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning.
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error.
      returned: always
      type: int
    activeInfoAlertCount:
      description: Current count of active alerts classified as informational.
      returned: always
      type: int
    upgradeDeploymentsNiFiVersion:
      description: The NiFi version used when upgrading deployments.
      returned: when available
      type: str
    validActions:
      description: The list of actions currently valid for the service.
      returned: when available
      type: list
    workloadVersion:
      description: The workload version of the service.
      returned: when available
      type: str
    availableK8sVersionUpgrade:
      description: The Kubernetes version available for upgrade, if any.
      returned: when available
      type: str
    k8sServerVersion:
      description: The Kubernetes server version in use by the service.
      returned: when available
      type: str
    dfLocalUrl:
      description: The URL of the environment local DataFlow application.
      returned: always
      type: str
    clusterSubnets:
      description: The list of subnet IDs used by the Kubernetes cluster.
      returned: when available
      type: list
    loadBalancerSubnets:
      description: The list of subnet IDs used by the load balancer.
      returned: when available
      type: list
    kubeApiAuthorizedIpRanges:
      description: The authorized IP ranges for the Kubernetes API.
      returned: always
      type: list
    loadBalancerAuthorizedIpRanges:
      description: The authorized IP ranges for the load balancer.
      returned: always
      type: list
    podCidr:
      description: The CIDR block used for Kubernetes pods.
      returned: when available
      type: str
    serviceCidr:
      description: The CIDR block used for Kubernetes services.
      returned: when available
      type: str
    privateCluster:
      description: Whether the Kubernetes cluster is private.
      returned: when available
      type: bool
    usePublicLoadBalancer:
      description: Whether a public load balancer is used.
      returned: when available
      type: bool
    userDefinedRouting:
      description: Whether user-defined routing is enabled.
      returned: when available
      type: bool
    tags:
      description: Custom tags applied to the service.
      returned: when available
      type: dict
    encryptionParameters:
      description: The encryption parameters of the service.
      returned: when available
      type: dict
      contains:
        encryptionKeyArn:
          description: The ARN of the encryption key.
          returned: when available
          type: str
        encryptionStrategy:
          description: The encryption strategy used.
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
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    DataFlowServiceStatus,
)


class DFServiceInfo(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=False, type="str"),
                df_crn=dict(required=False, type="str"),
                env_crn=dict(required=False, type="str"),
            ),
            supports_check_mode=True,
            mutually_exclusive=[["name", "df_crn", "env_crn"]],
        )

        # Set parameters
        self.name = self.get_param("name")
        self.df_crn = self.get_param("df_crn")
        self.env_crn = self.get_param("env_crn")

        # Initialize return values
        self.services = []

    def process(self):
        self.df_client = CdpDfClient(self.api_client)

        if self.name:
            service = self.df_client.get_service_by_name(self.name)
            if service:
                self.services.append(to_dict(service))
        elif self.df_crn:
            service = self.df_client.get_service_by_crn(self.df_crn)
            if service:
                self.services.append(to_dict(service))
        elif self.env_crn:
            service = self.df_client.get_service_by_env_crn(self.env_crn)
            if service:
                self.services.append(to_dict(service))
        else:
            summaries = self.df_client.list_services()
            for summary in summaries:
                status = summary.status
                state = (
                    status.state if isinstance(status, DataFlowServiceStatus) else None
                )
                if state in CdpDfClient.DISABLED_STATES:
                    continue
                # describeService can return a server-side 500 for a listed service
                # (e.g. null privateCluster); fall back to the list summary.
                service_details = self.df_client.describe_service(
                    summary.crn,
                    squelch={500: {}},
                )
                if not service_details:
                    self.module.warn(
                        f"Unable to describe DataFlow service '{summary.crn}'; "
                        "returning list summary only.",
                    )
                    service_details = summary
                self.services.append(to_dict(service_details))


def main():
    result = DFServiceInfo()

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
