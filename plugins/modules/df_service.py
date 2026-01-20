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
module: df_service
short_description: Enable or Disable CDP DataFlow Services
description:
    - Enable or Disable CDP DataFlow Services
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.2.0"
options:
  env_crn:
    description:
      - The CRN of the CDP Environment to host the Dataflow Service
      - The environment name can also be provided, instead of the CRN
      - Required when I(state=present)
    type: str
    aliases:
      - name
  df_crn:
    description:
      - The CRN of the DataFlow Service, if available
      - Required when I(state=absent)
    type: str
  state:
    description:
      - The declarative state of the Dataflow Service
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  nodes_min:
    description: The minimum number of kubernetes nodes needed for the environment.
      Note that the lowest minimum is 3 nodes.
    type: int
    default: 3
    required: False
    aliases:
      - min_k8s_node_count
  nodes_max:
    description: The maximum number of  kubernetes  nodes that environment may scale up under high-demand situations.
    type: int
    default: 3
    required: False
    aliases:
      - max_k8s_node_count
  public_loadbalancer:
    description: Indicates whether or not to use a public load balancer when deploying dependencies stack.
    type: bool
    required: False
    aliases:
      - use_public_load_balancer
  private_cluster:
    description:
      - Flag to specify if a private K8s cluster should be created.
    type: bool
    required: False
    default: False
    aliases:
      - enable_private_cluster
  loadbalancer_ip_ranges:
    description: The IP ranges authorized to connect to the load balancer
    type: list
    required: False
  k8s_ip_ranges:
    description: The IP ranges authorized to connect to the Kubernetes API server
    type: list
    required: False
  cluster_subnets:
    description:
      - Subnet ids that will be assigned to the Kubernetes cluster
      - Mutually exclusive with the I(cluster_subnets_filter) option
    type: list
    required: False
  cluster_subnets_filter:
    description:
      - Filter expression to select subnets for the Kubernetes cluster
      - Can be either a simple string pattern or a JMESPath query
      - "Simple pattern: Just provide a string (e.g., 'pub', 'pvt') to match subnets containing that text in their name"
      - "JMESPath query: Provide a full JMESPath expression (e.g., \"[?contains(subnetName, 'pub')]\") for advanced filtering"
      - "The filter operates on subnet objects with attributes: subnetId, subnetName, availabilityZone, cidr"
      - Mutually exclusive with the I(cluster_subnets) option.
    type: str
    required: False
  loadbalancer_subnets:
    description:
      - Subnet ids that will be assigned to the load balancer
      - Mutually exclusive with the I(loadbalancer_subnets_filter) option
    type: list
    required: False
  loadbalancer_subnets_filter:
    description:
      - Filter expression to select subnets for the load balancer
      - Can be either a simple string pattern or a JMESPath query
      - "Simple pattern: Just provide a string (e.g., 'pub', 'pvt') to match subnets containing that text in their name"
      - "JMESPath query: Provide a full JMESPath expression (e.g., \"[?contains(subnetName, 'pub')]\") for advanced filtering"
      - "The filter operates on subnet objects with attributes: subnetId, subnetName, availabilityZone, cidr"
      - Mutually exclusive with the I(loadbalancer_subnets) option.
    type: str
    required: False
  pod_cidr:
    description:
      - CIDR range from which to assign IPs to pods in the Kubernetes cluster
      - Must be a valid CIDR block (e.g., "10.200.0.0/16")
    type: str
    required: False
  service_cidr:
    description:
      - CIDR range from which to assign IPs to internal services in the Kubernetes cluster
      - Must be a valid CIDR block (e.g., "10.201.0.0/16")
    type: str
    required: False
  instance_type:
    description:
      - Indicates custom instance type to be used for Kubernetes nodes
      - Cloud provider specific (e.g., "m5.2xlarge" for AWS, "Standard_D8s_v3" for Azure)
    type: str
    required: False
  skip_preflight_checks:
    description:
      - Indicates whether to skip pre-flight checks during service enablement
      - Use with caution - skipping checks may result in deployment failures
    type: bool
    required: False
    default: False
  user_defined_routing:
    description:
      - Indicates whether User Defined Routing (UDR) mode is enabled for AKS clusters
      - Azure-specific option for controlling network routing behavior
    type: bool
    required: False
    default: False
  persist:
    description: Whether or not to retain the database records of related entities during removal.
    type: bool
    required: False
    default: False
  terminate:
    description: Whether or  not to terminate all deployments associated with this DataFlow service
    type: bool
    required: False
    default: False
  force:
    description: Flag to indicate if the DataFlow deletion should be forced.
    type: bool
    required: False
    default: False
    aliases:
      - force_delete
  tags:
    description: Tags to apply to the DataFlow Service
    type: dict
    required: False
  wait:
    description:
      - Flag to enable internal polling to wait for the Dataflow Service to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Dataflow Service to achieve the
        declared state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Dataflow Service to achieve the
        declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
notes:
  - This feature this module is for is in Technical Preview
  - "When updating an existing service, only the following parameters can be changed: nodes_min/nodes_max (both required together), k8s_ip_ranges, loadbalancer_ip_ranges, skip_preflight_checks"
  - Network configuration (subnets, pod_cidr, service_cidr, cluster type) cannot be updated after creation
  - To change immutable parameters, you must disable and recreate the service
  - When I(state=absent) and I(force=true), if service is in NOT_ENABLED state, resetService API is used
  - resetService only works on NOT_ENABLED services and does not clean up cloud resources
  - Use I(force=true) with caution as manual resource cleanup may be required
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a Dataflow Service with simple string pattern filters
- cloudera.cloud.df_service:
    name: my-service
    nodes_min: 3
    nodes_max: 10
    public_loadbalancer: true
    cluster_subnets_filter: "pvt"  # Simple pattern - matches subnets with 'pvt' in name
    loadbalancer_subnets_filter: "pub"  # Simple pattern - matches subnets with 'pub' in name
    k8s_ip_ranges: ['192.168.0.1/24']
    state: present
    wait: true

# Create a Dataflow Service with JMESPath filter expressions
- cloudera.cloud.df_service:
    name: my-service
    nodes_min: 3
    nodes_max: 10
    public_loadbalancer: true
    cluster_subnets_filter: "[?contains(subnetName, 'pvt')]"  # JMESPath query
    loadbalancer_subnets_filter: "[?contains(subnetName, 'pub')]"  # JMESPath query
    k8s_ip_ranges: ['192.168.0.1/24']
    state: present
    wait: true

# Remove a Dataflow Service with Async wait
- cloudera.cloud.df_service:
    name: my-service
    persist: false
    state: absent
    wait: true
  async: 3600
  poll: 0
  register: __my_teardown_request
"""

RETURN = r"""
services:
  description: The information about the named DataFlow Service or DataFlow Services
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description:  The DataFlow Service's parent environment CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Service's parent environment name.
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
      type: str
    minK8sNodeCount:
      description: The  minimum number of Kubernetes nodes that need to be provisioned in the environment.
      returned: always
      type: int
    maxK8sNodeCount:
      description:  The maximum number of kubernetes nodes that environment may scale up under high-demand situations.
      returned: always
      type: str
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
    k8sNodeCount:
      description: The number of kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: int
    instanceType:
      description: The instance type of the kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: str
    dfLocalUrl:
      description: The URL of the environment local DataFlow application.
      returned: always
      type: str
    authorizedIpRanges:
      description: The authorized IP Ranges.
      returned: always
      type: list
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning.
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error.
      returned: always
      type: int
    clusterId:
      description: Cluster id of the environment.
      returned: if enabled
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

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    check_service_updates,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
    filter_subnets_by_jmespath,
    convert_to_jmespath_query,
)


class DFService(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                env_crn=dict(type="str", aliases=["name"]),
                df_crn=dict(type="str"),
                nodes_min=dict(type="int", default=3, aliases=["min_k8s_node_count"]),
                nodes_max=dict(type="int", default=3, aliases=["max_k8s_node_count"]),
                public_loadbalancer=dict(
                    type="bool",
                    default=False,
                    aliases=["use_public_load_balancer"],
                ),
                private_cluster=dict(
                    type="bool",
                    default=False,
                    aliases=["enable_private_cluster"],
                ),
                loadbalancer_ip_ranges=dict(type="list", elements="str", default=None),
                k8s_ip_ranges=dict(type="list", elements="str", default=None),
                cluster_subnets=dict(type="list", elements="str", default=None),
                cluster_subnets_filter=dict(type="str", default=None),
                loadbalancer_subnets=dict(type="list", elements="str", default=None),
                loadbalancer_subnets_filter=dict(type="str", default=None),
                pod_cidr=dict(type="str", default=None),
                service_cidr=dict(type="str", default=None),
                instance_type=dict(type="str", default=None),
                skip_preflight_checks=dict(type="bool", default=False),
                persist=dict(type="bool", default=False),
                terminate=dict(type="bool", default=False),
                force=dict(type="bool", default=False),
                tags=dict(required=False, type="dict", default=None),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                wait=dict(type="bool", default=True),
                delay=dict(type="int", aliases=["polling_delay"], default=15),
                timeout=dict(type="int", aliases=["polling_timeout"], default=3600),
                user_defined_routing=dict(type="bool", default=False),
            ),
            supports_check_mode=True,
            required_if=[
                ("state", "absent", ("df_crn",), False),
            ],
            mutually_exclusive=[
                ("cluster_subnets", "cluster_subnets_filter"),
                ("loadbalancer_subnets", "loadbalancer_subnets_filter"),
            ],
        )

        # Set parameters
        self.env_crn = self.get_param("env_crn")
        self.df_crn = self.get_param("df_crn")
        self.state = self.get_param("state")
        self.nodes_min = self.get_param("nodes_min")
        self.nodes_max = self.get_param("nodes_max")
        self.private_cluster = self.get_param("private_cluster")
        self.loadbalancer_ip_ranges = self.get_param("loadbalancer_ip_ranges")
        self.k8s_ip_ranges = self.get_param("k8s_ip_ranges")
        self.cluster_subnets = self.get_param("cluster_subnets")
        self.cluster_subnets_filter = self.get_param("cluster_subnets_filter")
        self.loadbalancer_subnets = self.get_param("loadbalancer_subnets")
        self.loadbalancer_subnets_filter = self.get_param("loadbalancer_subnets_filter")
        self.pod_cidr = self.get_param("pod_cidr")
        self.service_cidr = self.get_param("service_cidr")
        self.instance_type = self.get_param("instance_type")
        self.persist = self.get_param("persist")
        self.terminate = self.get_param("terminate")
        self.skip_preflight_checks = self.get_param("skip_preflight_checks")
        self.force = self.get_param("force")
        self.tags = self.get_param("tags")
        self.user_defined_routing = self.get_param("user_defined_routing")
        self.public_loadbalancer = self.get_param("public_loadbalancer")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        # Initialize DF client
        self.df_client = CdpDfClient(self.api_client)

        # Initialize Environment client (for listing environments and subnet filtering)
        self.env_client = CdpEnvClient(self.api_client)

        # Initialize return values
        self.service = {}
        self.changed = False

    def process(self):
        existing_service = None
        if self.df_crn:
            existing_service = self.df_client.get_service_by_crn(self.df_crn)
        elif self.env_crn:
            existing_service = self.df_client.get_service_by_env_crn(self.env_crn)

        if existing_service:
            existing_service = existing_service.get("service", existing_service)

            if not self.df_crn:
                self.df_crn = existing_service.get("crn")

            if self.state == "absent":
                current_state = existing_service.get("status", {}).get("state")
                self.changed = True

                if not self.module.check_mode:
                    if self.force and current_state in CdpDfClient.DISABLED_STATES:
                        self.df_client.reset_service(crn=self.df_crn)

                    elif current_state not in CdpDfClient.DISABLED_STATES:
                        if self.wait:
                            self.df_client.wait_for_service_state(
                                service_crn=self.df_crn,
                                target_states=CdpDfClient.DISABLED_STATES,
                                timeout=self.timeout,
                                delay=self.delay,
                                terminate_deployments=self.terminate,
                                persist=self.persist,
                            )
                        else:
                            self.df_client.disable_service(
                                crn=self.df_crn,
                                terminate_deployments=self.terminate,
                                persist=self.persist,
                            )

            elif self.state == "present":

                update_params = check_service_updates(
                    service_crn=self.df_crn,
                    service_details=existing_service,
                    min_k8s_node_count=self.nodes_min,
                    max_k8s_node_count=self.nodes_max,
                    kubernetes_ip_cidr_blocks=self.k8s_ip_ranges,
                    load_balancer_ip_cidr_blocks=self.loadbalancer_ip_ranges,
                    skip_preflight_checks=self.skip_preflight_checks,
                )

                if update_params:
                    self.changed = True
                    self.service = existing_service

                    if not self.module.check_mode:
                        result = self.df_client.update_service(**update_params)
                        self.service = result.get("service", result)

                        if self.wait:
                            self.service = self.df_client.wait_for_service_state(
                                service_crn=self.df_crn,
                                target_states=["GOOD_HEALTH"],
                                timeout=self.timeout,
                                delay=self.delay,
                            )
                else:
                    self.service = existing_service
        else:
            # Service doesn't exist (or is already disabled)
            if self.state == "present":
                # Apply subnet filtering if filter parameters are provided
                if self.cluster_subnets_filter or self.loadbalancer_subnets_filter:
                    subnets = self.env_client.get_environment_subnets(self.env_crn)

                    if self.cluster_subnets_filter:
                        query = convert_to_jmespath_query(
                            self.cluster_subnets_filter,
                        )
                        self.cluster_subnets = filter_subnets_by_jmespath(
                            subnets,
                            query,
                        )

                    if self.loadbalancer_subnets_filter:
                        query = convert_to_jmespath_query(
                            self.loadbalancer_subnets_filter,
                        )
                        self.loadbalancer_subnets = filter_subnets_by_jmespath(
                            subnets,
                            query,
                        )

                if not self.module.check_mode:
                    result = self.df_client.enable_service(
                        environment_crn=self.env_crn,
                        min_k8s_node_count=self.nodes_min,
                        max_k8s_node_count=self.nodes_max,
                        use_public_load_balancer=self.public_loadbalancer,
                        private_cluster=self.private_cluster,
                        load_balancer_ip_cidr_blocks=self.loadbalancer_ip_ranges,
                        kubernetes_ip_cidr_blocks=self.k8s_ip_ranges,
                        cluster_subnet_ids=self.cluster_subnets,
                        load_balancer_subnet_ids=self.loadbalancer_subnets,
                        pod_cidr=self.pod_cidr,
                        service_cidr=self.service_cidr,
                        instance_type=self.instance_type,
                        skip_preflight_checks=self.skip_preflight_checks,
                        user_defined_routing=self.user_defined_routing,
                        tags=self.tags,
                    )
                    self.service = result.get("service", result)
                    self.changed = True

                    if self.wait:
                        service_crn = self.service.get("crn")
                        if service_crn:
                            self.service = self.df_client.wait_for_service_state(
                                service_crn=service_crn,
                                target_states=["GOOD_HEALTH"],
                                timeout=self.timeout,
                                delay=self.delay,
                            )


def main():
    result = DFService()
    output = dict(changed=result.changed, service=result.service)

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
