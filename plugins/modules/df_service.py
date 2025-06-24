#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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
version_added: "1.2.0"
requirements:
  - cdpy
  - jmespath
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
      - L(JMESPath,https://jmespath.org/) expression to filter the subnets to be used for the Kubernetes cluster
      - The expression will be applied to the full list of subnets for the specified environment
      - "Each subnet in the list is an object with the following attributes: subnetId, subnetName, availabilityZone, cidr"
      - The filter expression must only filter the list, but not apply any attribute projection
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
      - L(JMESPath,https://jmespath.org/) expression to filter the subnets to be used for the load balancer
      - The expression will be applied to the full list of subnets for the specified environment
      - "Each subnet in the list is an object with the following attributes: subnetId, subnetName, availabilityZone, cidr"
      - The filter expression must only filter the list, but not apply any attribute projection
      - Mutually exclusive with the I(loadbalancer_subnets) option.
    type: str
    required: False
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
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a Dataflow Service
- cloudera.cloud.df_service:
    name: my-service
    nodes_min: 3
    nodes_max: 10
    public_loadbalancer: true
    cluster_subnets_filter: "[?contains(subnetName, 'pvt')]"
    loadbalancer_subnets_filter: "[?contains(subnetName, 'pub')]"
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

import json
import jmespath

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class DFService(CdpModule):
    def __init__(self, module):
        super(DFService, self).__init__(module)

        # Set variables
        self.env_crn = self._get_param("env_crn")
        self.df_crn = self._get_param("df_crn")
        self.nodes_min = self._get_param("nodes_min")
        self.nodes_max = self._get_param("nodes_max")
        self.public_loadbalancer = self._get_param("public_loadbalancer")
        self.private_cluster = self._get_param("private_cluster")
        self.lb_ip_ranges = self._get_param("loadbalancer_ip_ranges")
        self.k8s_ip_ranges = self._get_param("k8s_ip_ranges")
        self.cluster_subnets = self._get_param("cluster_subnets")
        self.cluster_subnets_filter = self._get_param("cluster_subnets_filter")
        self.lb_subnets = self._get_param("loadbalancer_subnets")
        self.lb_subnets_filter = self._get_param("loadbalancer_subnets_filter")
        self.persist = self._get_param("persist")
        self.terminate = self._get_param("terminate")
        self.force = self._get_param("force")
        self.tags = self._get_param("tags")

        self.state = self._get_param("state")
        self.wait = self._get_param("wait")
        self.delay = self._get_param("delay")
        self.timeout = self._get_param("timeout")

        # Initialize return values
        self.service = {}
        self.changed = False

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        original_env_crn = self.env_crn
        if self.env_crn is not None:
            self.env_crn = self.cdpy.environments.resolve_environment_crn(self.env_crn)
        if self.env_crn is not None or self.df_crn is not None:
            self.target = self.cdpy.df.describe_service(
                env_crn=self.env_crn, df_crn=self.df_crn
            )

        if self.target is not None:
            # DF Database Entry exists
            if self.state in ["absent"]:
                if self.module.check_mode:
                    self.service = self.target
                else:
                    self._disable_df()
            elif self.state in ["present"]:
                self.module.warn(
                    "Dataflow Service already enabled and configuration validation and reconciliation is not "
                    "supported; to change a Dataflow Service, explicitly disable and recreate the Service or "
                    "use the UI"
                )
                if self.wait:
                    self.service = self._wait_for_enabled()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state
                )
        else:
            # Environment does not have DF database entry, and probably doesn't exist
            if self.state in ["absent"]:
                self.module.log(
                    "Dataflow Service already disabled in CDP Environment %s"
                    % self.env_crn
                )
            elif self.state in ["present"]:
                if self.env_crn is None:
                    self.module.fail_json(
                        msg="Could not retrieve CRN for CDP Environment %s"
                        % original_env_crn
                    )
                else:
                    # create DF Service
                    if self.cluster_subnets_filter or self.lb_subnets_filter:
                        try:
                            env_info = self.cdpy.environments.describe_environment(
                                self.env_crn
                            )
                            subnet_metadata = list(
                                env_info["network"]["subnetMetadata"].values()
                            )
                        except Exception:
                            subnet_metadata = []
                        if not subnet_metadata:
                            self.module.fail_json(
                                msg="Could not retrieve subnet metadata for CDP Environment %s"
                                % self.env_crn
                            )

                        if self.cluster_subnets_filter:
                            self.cluster_subnets = self._filter_subnets(
                                self.cluster_subnets_filter, subnet_metadata
                            )
                            self.module.warn(
                                "Found the following cluster subnets: %s"
                                % ", ".join(self.cluster_subnets)
                            )
                        if self.lb_subnets_filter:
                            self.lb_subnets = self._filter_subnets(
                                self.lb_subnets_filter, subnet_metadata
                            )
                            self.module.warn(
                                "Found the following load balancer subnets: %s"
                                % ", ".join(self.lb_subnets)
                            )

                    if not self.module.check_mode:
                        self.service = self.cdpy.df.enable_service(
                            env_crn=self.env_crn,
                            min_nodes=self.nodes_min,
                            max_nodes=self.nodes_max,
                            enable_public_ip=self.public_loadbalancer,
                            private_cluster=self.private_cluster,
                            lb_ips=self.lb_ip_ranges,
                            kube_ips=self.k8s_ip_ranges,
                            # tags=self.tags,  # Currently overstrict blocking of values
                            cluster_subnets=self.cluster_subnets,
                            lb_subnets=self.lb_subnets,
                        )
                        self.changed = True
                        if self.wait:
                            self.service = self._wait_for_enabled()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state
                )

    def _wait_for_enabled(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.df.describe_service,
            params=dict(env_crn=self.env_crn),
            field=["status", "state"],
            state=self.cdpy.sdk.STARTED_STATES,
            delay=self.delay,
            timeout=self.timeout,
        )

    def _filter_subnets(self, query, subnets):
        """Apply a JMESPath to an array of subnets and return the id of the selected subnets.
        The query must only filter the array, without applying any projection. The query result must also be an
        array of subnet objects.

        :param query: JMESpath query to filter the subnet array.
        :param subnets: An array of subnet objects. Each subnet in the array is an object with the following attributes:
        subnetId, subnetName, availabilityZone, cidr.
        :return: An array of subnet ids.
        """
        filtered_subnets = []
        try:
            filtered_subnets = jmespath.search(query, subnets)
        except Exception:
            self.module.fail_json(
                msg="The specified subnet filter is an invalid JMESPath expression: "
                % query
            )
        try:
            return [s["subnetId"] for s in filtered_subnets]
        except Exception:
            self.module.fail_json(
                msg='The subnet filter "%s" should return an array of subnet objects '
                "but instead returned this: %s" % (query, json.dumps(filtered_subnets))
            )

    def _disable_df(self):
        # Attempt clean Disable, which also ensures we have tried at least once before we do a forced removal
        if self.target["status"]["state"] in self.cdpy.sdk.REMOVABLE_STATES:
            self.service = self.cdpy.df.disable_service(
                df_crn=self.df_crn, persist=self.persist, terminate=self.terminate
            )
            self.changed = True
        elif self.target["status"]["state"] in self.cdpy.sdk.TERMINATION_STATES:
            self.module.warn(
                "DataFlow Service is already Disabling, skipping termination request"
            )
            pass
        else:
            self.module.warn(
                "Attempting to disable DataFlow Service but state %s not in Removable States %s"
                % (self.target["status"]["state"], self.cdpy.sdk.REMOVABLE_STATES)
            )
        if self.wait:
            # Wait for Clean Disable, if possible
            self.service = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.df.describe_service,
                params=dict(df_crn=self.df_crn),
                field=["status", "state"],
                state=self.cdpy.sdk.STOPPED_STATES
                + self.cdpy.sdk.REMOVABLE_STATES
                + [None],
                delay=self.delay,
                timeout=self.timeout,
                ignore_failures=True,
            )
        else:
            self.service = self.cdpy.df.describe_service(df_crn=self.df_crn)
        # Check disable result against need for further forced delete action, in case it didn't work first time around
        if self.service is not None:
            if self.service["status"]["state"] in self.cdpy.sdk.REMOVABLE_STATES:
                if self.force:
                    self.service = self.cdpy.df.reset_service(df_crn=self.df_crn)
                    self.changed = True
                else:
                    self.module.fail_json(
                        msg="DF Service Disable failed and Force delete not requested"
                    )
            if self.wait:
                self.service = self.cdpy.sdk.wait_for_state(
                    describe_func=self.cdpy.df.describe_service,
                    params=dict(df_crn=self.df_crn),
                    field=None,  # This time we require removal or declare failure
                    delay=self.delay,
                    timeout=self.timeout,
                )
            else:
                self.service = self.cdpy.df.describe_service(df_crn=self.df_crn)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            env_crn=dict(type="str", aliases=["name"]),
            df_crn=dict(type="str"),
            nodes_min=dict(type="int", default=3, aliases=["min_k8s_node_count"]),
            nodes_max=dict(type="int", default=3, aliases=["max_k8s_node_count"]),
            public_loadbalancer=dict(
                type="bool", default=False, aliases=["use_public_load_balancer"]
            ),
            private_cluster=dict(
                type="bool", default=False, aliases=["enable_private_cluster"]
            ),
            loadbalancer_ip_ranges=dict(type="list", elements="str", default=None),
            k8s_ip_ranges=dict(type="list", elements="str", default=None),
            cluster_subnets=dict(type="list", elements="str", default=None),
            cluster_subnets_filter=dict(type="str", default=None),
            loadbalancer_subnets=dict(type="list", elements="str", default=None),
            loadbalancer_subnets_filter=dict(type="str", default=None),
            persist=dict(type="bool", default=False),
            terminate=dict(type="bool", default=False),
            tags=dict(required=False, type="dict", default=None),
            state=dict(type="str", choices=["present", "absent"], default="present"),
            force=dict(type="bool", default=False, aliases=["force_delete"]),
            wait=dict(type="bool", default=True),
            delay=dict(type="int", aliases=["polling_delay"], default=15),
            timeout=dict(type="int", aliases=["polling_timeout"], default=3600),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("env_crn",), False),
            ("state", "absent", ("df_crn",), False),
        ],
        mutually_exclusive=[
            ("cluster_subnets", "cluster_subnets_filter"),
            ("loadbalancer_subnets", "loadbalancer_subnets_filter"),
        ],
    )

    result = DFService(module)
    output = dict(changed=result.changed, service=result.service)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
