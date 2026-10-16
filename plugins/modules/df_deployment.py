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
module: df_deployment
short_description: Manage CDP DataFlow Deployments
description:
    - Create, update, or terminate CDP DataFlow Deployments
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.6.0"
options:
  name:
    description:
      - The name of the deployment
      - Required when I(state=present)
    type: str
    required: False
  deployment_crn:
    description:
      - The CRN of the deployment
      - Required when I(state=absent) unless I(name) is provided
    type: str
    required: False
    aliases:
      - dep_crn
  env_crn:
    description:
      - The CRN of the CDP Environment where the DataFlow service is enabled
      - Required when I(state=present)
      - Required when I(state=absent) for workload authentication
      - The environment name can also be provided instead of the CRN
    type: str
    required: False
    aliases:
      - environment_crn
  service_crn:
    description:
      - The CRN of the DataFlow service
      - Required when I(state=present) if I(df_name) is not provided
      - Either I(service_crn) or I(df_name) must be provided to identify the DataFlow service
    type: str
    required: False
    aliases:
      - df_crn
  df_name:
    description:
      - The name of the DataFlow service (environment name)
      - Required when I(state=present) if I(service_crn) is not provided
      - Will be used to look up the service CRN
    type: str
    required: False
  flow_version_crn:
    description:
      - The CRN of the flow version to deploy
      - Required when I(state=present)
    type: str
    required: False
  deployment_request_crn:
    description:
      - The CRN of the deployment request
      - If not provided, it will be automatically generated via initiateDeployment API
      - Normally you don't need to provide this - it's generated automatically
    type: str
    required: False
  configuration_version:
    description:
      - The version of the deployment configuration
      - Required for create and update operations
    type: int
    required: False
    default: 0
  cluster_size:
    description:
      - The size of the cluster for the deployment
    type: str
    choices:
      - EXTRA_SMALL
      - SMALL
      - MEDIUM
      - LARGE
    required: False
    aliases:
      - size
  static_node_count:
    description:
      - The static number of nodes when autoscaling is disabled
    type: int
    required: False
    default: 1
  autoscaling_enabled:
    description:
      - Whether to enable autoscaling
    type: bool
    required: False
    default: False
    aliases:
      - autoscale
  autoscale_min_nodes:
    description:
      - The minimum number of nodes when autoscaling is enabled
    type: int
    required: False
    default: 1
    aliases:
      - autoscale_nodes_min
  autoscale_max_nodes:
    description:
      - The maximum number of nodes when autoscaling is enabled
    type: int
    required: False
    default: 3
    aliases:
      - autoscale_nodes_max
  flow_metrics_scaling_enabled:
    description:
      - Whether to enable flow metrics for scaling
    type: bool
    required: False
    default: False
  cfm_nifi_version:
    description:
      - The CFM NiFi version for the deployment
    type: str
    required: False
    aliases:
      - nifi_ver
  autostart_flow:
    description:
      - Whether to automatically start the flow after deployment
    type: bool
    required: False
    default: True
  parameter_groups:
    description:
      - Flow parameter groups configuration
    type: list
    elements: dict
    required: False
  kpis:
    description:
      - Configured KPIs for the deployment
    type: list
    elements: dict
    required: False
  inbound_hostname:
    description:
      - FQDN for inbound connections
    type: str
    required: False
  listen_components:
    description:
      - Listen components port and protocol configuration
    type: list
    elements: dict
    required: False
  inbound_connection_authorized_ip_ranges:
    description:
      - Authorized IP ranges for inbound connections
    type: list
    elements: str
    required: False
  node_storage_profile_name:
    description:
      - Node storage profile name
    type: str
    required: False
  project_crn:
    description:
      - The CRN of the project
    type: str
    required: False
  custom_nar_configuration_crn:
    description:
      - Custom NAR configuration CRN
    type: str
    required: False
  custom_python_configuration_crn:
    description:
      - Custom Python configuration CRN
    type: str
    required: False
  asset_update_request_crn:
    description:
      - Asset update request CRN for updates
    type: str
    required: False
  state:
    description:
      - The declarative state of the deployment
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the deployment to achieve the declared state
      - If set to FALSE, the module will return immediately
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while waiting for state changes
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while waiting for state changes
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
notes:
  - This module requires an enabled DataFlow service
  - The deployment_request_crn is automatically generated if not provided
  - The module will automatically call initiateDeployment API before creating the deployment
  - "When updating an existing deployment, only the following parameters can be changed: cluster_size, static_node_count, autoscaling_enabled, autoscale_min_nodes, autoscale_max_nodes, flow_metrics_scaling_enabled, parameter_groups, kpis"
  - To update flow version or other immutable parameters, you must terminate and recreate the deployment
  - Updates require the configuration_version parameter to match the current deployment configuration version
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a deployment with minimal parameters (using environment CRN)
- cloudera.cloud.df_deployment:
    name: my-deployment
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    flow_version_crn: crn:cdp:df:us-west-1:tenant:flow-version:67890
    configuration_version: 0
    cluster_size: SMALL
    static_node_count: 1
    autostart_flow: true
    state: present

# Create a deployment using service name instead of env_crn
- cloudera.cloud.df_deployment:
    name: my-deployment
    df_name: my-dataflow-service
    flow_version_crn: crn:cdp:df:us-west-1:tenant:flow-version:67890
    configuration_version: 0
    cluster_size: SMALL
    state: present

# Create a deployment with autoscaling
- cloudera.cloud.df_deployment:
    name: my-autoscaling-deployment
    service_crn: crn:cdp:df:us-west-1:tenant:service:12345
    flow_version_crn: crn:cdp:df:us-west-1:tenant:flow-version:67890
    configuration_version: 0
    cluster_size: MEDIUM
    autoscaling_enabled: true
    autoscale_min_nodes: 2
    autoscale_max_nodes: 10
    flow_metrics_scaling_enabled: true
    state: present

# Create a deployment with parameters and KPIs
- cloudera.cloud.df_deployment:
    name: my-configured-deployment
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    flow_version_crn: crn:cdp:df:us-west-1:tenant:flow-version:67890
    configuration_version: 0
    cluster_size: LARGE
    parameter_groups:
      - name: "parameters"
        parameters:
          - name: "brokers"
            value: "kafka-broker:9092"
          - name: "topic"
            value: "my-topic"
    kpis:
      - metricId: "bytes_received"
        alert:
          thresholdMoreThan:
            unitId: "bytes"
            value: 1000000
    state: present

# Update an existing deployment (scale up nodes)
- cloudera.cloud.df_deployment:
    name: my-deployment
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    configuration_version: 1
    autoscaling_enabled: true
    autoscale_min_nodes: 3
    autoscale_max_nodes: 15
    flow_metrics_scaling_enabled: true
    state: present
    wait: true

# Update deployment parameters
- cloudera.cloud.df_deployment:
    deployment_crn: crn:cdp:df:us-west-1:tenant:deployment:12345
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    configuration_version: 2
    parameter_groups:
      - name: "parameters"
        parameters:
          - name: "brokers"
            value: "new-kafka-broker:9092"
          - name: "topic"
            value: "new-topic"
    state: present

# Terminate a deployment by CRN
- cloudera.cloud.df_deployment:
    deployment_crn: crn:cdp:df:us-west-1:tenant:deployment:12345
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    state: absent
    wait: true

# Terminate a deployment by name
- cloudera.cloud.df_deployment:
    name: my-deployment
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    state: absent
    wait: true

# Terminate a deployment without waiting
- cloudera.cloud.df_deployment:
    deployment_crn: crn:cdp:df:us-west-1:tenant:deployment:12345
    env_crn: crn:cdp:environments:us-west-1:tenant:environment:12345
    state: absent
    wait: false
"""

RETURN = r"""
deployment:
  description: The deployment information
  type: dict
  returned: always
  contains:
    crn:
      description: The CRN of the deployment
      returned: always
      type: str
    name:
      description: The name of the deployment
      returned: always
      type: str
    status:
      description: The workflow status of the deployment
      returned: always
      type: dict
      contains:
        state:
          description: The state that the deployment is currently in
          returned: always
          type: str
        detailedState:
          description: The detailed deployment state
          returned: always
          type: str
        message:
          description: Detail message relating to the current status of the deployment
          returned: when available
          type: str
    service:
      description: Simple information about the DataFlow service of the deployment
      returned: always
      type: dict
      contains:
        crn:
          description: The CRN of the DataFlow service
          returned: always
          type: str
        name:
          description: The name of the DataFlow service
          returned: always
          type: str
        cloudProvider:
          description: The cloud platform of the DataFlow service
          returned: always
          type: str
        region:
          description: The region of the DataFlow service
          returned: always
          type: str
        environmentCrn:
          description: CRN of the associated CDP environment
          returned: always
          type: str
    updated:
      description: Timestamp of the last time the deployment was modified
      returned: when available
      type: int
    clusterSize:
      description: The size of the cluster for the deployment
      returned: when available
      type: str
    flowVersionCrn:
      description: The deployment's current flow version CRN
      returned: when available
      type: str
    flowCrn:
      description: The deployment's current flow CRN
      returned: when available
      type: str
    flowName:
      description: The name of the flow
      returned: when available
      type: str
    flowVersion:
      description: The version of the flow
      returned: when available
      type: int
    nifiUrl:
      description: The URL to open the deployed flow in NiFi
      returned: when available
      type: str
    dfxLocalUrl:
      description: Base URL to the CDF Local instance running this deployment
      returned: when available
      type: str
    currentNodeCount:
      description: The current node count
      returned: when available
      type: int
    staticNodeCount:
      description: The static number of nodes of the deployment
      returned: when available
      type: int
    autoscalingEnabled:
      description: Whether or not autoscaling is enabled for this deployment
      returned: always
      type: bool
    autoscaleMinNodes:
      description: The minimum number of nodes that the deployment will allocate when autoscaling is enabled
      returned: when available
      type: int
    autoscaleMaxNodes:
      description: The maximum number of nodes that the deployment can scale up to when autoscaling is enabled
      returned: when available
      type: int
    flowMetricsScalingEnabled:
      description: Whether or not flow metrics scaling is enabled for this deployment
      returned: always
      type: bool
    configurationVersion:
      description: The current version of the deployment's configuration
      returned: always
      type: int
    cfmNifiVersion:
      description: The CFM NiFi version associated with the deployment
      returned: when available
      type: str
    deployedByName:
      description: The name of the person who deployed the first flow
      returned: when available
      type: str
    activeInfoAlertCount:
      description: Current count of active alerts classified as an info
      returned: always
      type: int
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error
      returned: always
      type: int
sdk_out:
  description: Returns the captured CDP SDK log
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log
  returned: when supported
  type: list
  elements: str
"""

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    DataFlowModule,
    build_deployment_update_params,
    check_deployment_updates,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


class DFDeployment(DataFlowModule, ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(type="str"),
                deployment_crn=dict(type="str", aliases=["dep_crn"]),
                env_crn=dict(type="str", aliases=["environment_crn"]),
                service_crn=dict(type="str", aliases=["df_crn"]),
                df_name=dict(type="str"),
                flow_version_crn=dict(type="str"),
                deployment_request_crn=dict(type="str"),
                configuration_version=dict(type="int", default=0),
                cluster_size=dict(
                    type="str",
                    choices=["EXTRA_SMALL", "SMALL", "MEDIUM", "LARGE"],
                    aliases=["size"],
                ),
                static_node_count=dict(type="int", default=1),
                autoscaling_enabled=dict(
                    type="bool",
                    default=False,
                    aliases=["autoscale"],
                ),
                autoscale_min_nodes=dict(
                    type="int",
                    default=1,
                    aliases=["autoscale_nodes_min"],
                ),
                autoscale_max_nodes=dict(
                    type="int",
                    default=3,
                    aliases=["autoscale_nodes_max"],
                ),
                flow_metrics_scaling_enabled=dict(type="bool", default=False),
                cfm_nifi_version=dict(type="str", aliases=["nifi_ver"]),
                autostart_flow=dict(type="bool", default=True),
                parameter_groups=dict(type="list", elements="dict"),
                kpis=dict(type="list", elements="dict"),
                inbound_hostname=dict(type="str"),
                listen_components=dict(type="list", elements="dict"),
                inbound_connection_authorized_ip_ranges=dict(
                    type="list",
                    elements="str",
                ),
                node_storage_profile_name=dict(type="str"),
                project_crn=dict(type="str"),
                custom_nar_configuration_crn=dict(type="str"),
                custom_python_configuration_crn=dict(type="str"),
                asset_update_request_crn=dict(type="str"),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                wait=dict(type="bool", default=True),
                delay=dict(type="int", aliases=["polling_delay"], default=15),
                timeout=dict(type="int", aliases=["polling_timeout"], default=3600),
            ),
            supports_check_mode=True,
            required_if=[
                ("state", "present", ("name", "flow_version_crn"), True),
                ("state", "absent", ("env_crn",)),
            ],
            required_one_of=[
                ("service_crn", "df_name", "env_crn"),
            ],
            mutually_exclusive=[
                ("service_crn", "df_name"),
            ],
        )

        # Set parameters
        self.name = self.get_param("name")
        self.deployment_crn = self.get_param("deployment_crn")
        self.env_crn = self.get_param("env_crn")
        self.service_crn = self.get_param("service_crn")
        self.df_name = self.get_param("df_name")
        self.flow_version_crn = self.get_param("flow_version_crn")
        self.deployment_request_crn = self.get_param("deployment_request_crn")
        self.configuration_version = self.get_param("configuration_version")
        self.cluster_size = self.get_param("cluster_size")
        self.static_node_count = self.get_param("static_node_count")
        self.autoscaling_enabled = self.get_param("autoscaling_enabled")
        self.autoscale_min_nodes = self.get_param("autoscale_min_nodes")
        self.autoscale_max_nodes = self.get_param("autoscale_max_nodes")
        self.flow_metrics_scaling_enabled = self.get_param(
            "flow_metrics_scaling_enabled",
        )
        self.cfm_nifi_version = self.get_param("cfm_nifi_version")
        self.autostart_flow = self.get_param("autostart_flow")
        self.parameter_groups = self.get_param("parameter_groups")
        self.kpis = self.get_param("kpis")
        self.inbound_hostname = self.get_param("inbound_hostname")
        self.listen_components = self.get_param("listen_components")
        self.inbound_connection_authorized_ip_ranges = self.get_param(
            "inbound_connection_authorized_ip_ranges",
        )
        self.node_storage_profile_name = self.get_param("node_storage_profile_name")
        self.project_crn = self.get_param("project_crn")
        self.custom_nar_configuration_crn = self.get_param(
            "custom_nar_configuration_crn",
        )
        self.custom_python_configuration_crn = self.get_param(
            "custom_python_configuration_crn",
        )
        self.asset_update_request_crn = self.get_param("asset_update_request_crn")
        self.state = self.get_param("state")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        # Initialize DF client
        self.df_client = CdpDfClient(self.api_client)

        # Initialize Environment client
        self.env_client = CdpEnvClient(self.api_client)

        # Initialize IAM client (for workload token generation)
        self.iam_client = CdpIamClient(self.api_client)

        # Initialize return values
        self.deployment = {}
        self.changed = False

    def process(self):

        existing_deployment = None
        if self.deployment_crn:
            existing_deployment = self.df_client.get_deployment_by_crn(
                self.deployment_crn,
            )
        elif self.name:
            existing_deployment = self.df_client.get_deployment_by_name(self.name)
            if existing_deployment:
                self.deployment_crn = existing_deployment.get("deployment", {}).get(
                    "crn",
                )

        if self.env_crn:
            env = self.env_client.describe_environment(self.env_crn)
            if env:
                self.env_crn = env.get("crn")
            else:
                self.module.fail_json(msg=f"Environment not found: {self.env_crn}")

        if not self.service_crn:
            if self.df_name:
                service = self.df_client.get_service_by_name(self.df_name)
                if service:
                    self.service_crn = service.get("crn")
                else:
                    self.module.fail_json(
                        msg=f"DataFlow service not found: {self.df_name}",
                    )
            elif self.env_crn:
                service = self.df_client.get_service_by_env_crn(self.env_crn)
                if service:
                    self.service_crn = service.get("service", {}).get("crn")
                else:
                    self.module.fail_json(
                        msg=f"DataFlow service is not enabled for environment: {self.env_crn}",
                    )

        if self.state == "present":
            if existing_deployment:
                deployment_data = existing_deployment.get(
                    "deployment",
                    existing_deployment,
                )

                check_params = build_deployment_update_params(
                    module=self.module,
                    deployment_crn=self.deployment_crn,
                    environment_crn=self.env_crn,
                    deployment_details=deployment_data,
                    configuration_version=self.configuration_version,
                )

                update_params = check_deployment_updates(**check_params)

                if update_params:
                    self.changed = True
                    self.deployment = deployment_data

                    if not self.module.check_mode:
                        workload_client = self.df_client.create_workload_client(
                            iam_client=self.iam_client,
                            environment_crn=self.env_crn,
                        )

                        result = self.df_client.update_deployment(
                            workload_client=workload_client,
                            **update_params,
                        )

                        # Extract deployment from result
                        deployment_config = result.get("deploymentConfiguration", {})
                        self.deployment = deployment_config.get(
                            "deployment",
                            deployment_config,
                        )

                        if self.wait:
                            result = self.df_client.wait_for_deployment_state(
                                target_states=["GOOD_HEALTH"],
                                deployment_crn=self.deployment_crn,
                                timeout=self.timeout,
                                delay=self.delay,
                            )
                            self.deployment = result.get("deployment", {})
                else:
                    self.deployment = deployment_data
                    self.changed = False
            else:
                if not self.module.check_mode:
                    initiate_result = self.df_client.initiate_deployment(
                        service_crn=self.service_crn,
                        flow_version_crn=self.flow_version_crn,
                    )
                    self.deployment_request_crn = initiate_result.get(
                        "deploymentRequestCrn",
                    )

                    workload_client = self.df_client.create_workload_client(
                        iam_client=self.iam_client,
                        environment_crn=self.env_crn,
                    )

                    result = self.df_client.create_deployment(
                        workload_client=workload_client,
                        environment_crn=self.env_crn,
                        deployment_request_crn=self.deployment_request_crn,
                        name=self.name,
                        configuration_version=self.configuration_version,
                        cluster_size=self.cluster_size,
                        static_node_count=self.static_node_count,
                        auto_scaling_enabled=self.autoscaling_enabled,
                        auto_scale_min_nodes=self.autoscale_min_nodes,
                        auto_scale_max_nodes=self.autoscale_max_nodes,
                        flow_metrics_scaling_enabled=self.flow_metrics_scaling_enabled,
                        cfm_nifi_version=self.cfm_nifi_version,
                        auto_start_flow=self.autostart_flow,
                        parameter_groups=self.parameter_groups,
                        kpis=self.kpis,
                        inbound_hostname=self.inbound_hostname,
                        listen_components=self.listen_components,
                        inbound_connection_authorized_ip_ranges=self.inbound_connection_authorized_ip_ranges,
                        node_storage_profile_name=self.node_storage_profile_name,
                        project_crn=self.project_crn,
                        custom_nar_configuration_crn=self.custom_nar_configuration_crn,
                        custom_python_configuration_crn=self.custom_python_configuration_crn,
                    )
                    self.deployment = result.get("deployment", {})

                    # Wait for deployment to be ready if requested
                    if self.wait:
                        result = self.df_client.wait_for_deployment_state(
                            target_states=["GOOD_HEALTH"],
                            deployment_crn=self.deployment["crn"],
                            timeout=self.timeout,
                            delay=self.delay,
                        )
                        self.deployment = result.get("deployment", {})

                self.changed = True

        elif self.state == "absent":
            if existing_deployment:
                if not self.module.check_mode:
                    workload_client = self.df_client.create_workload_client(
                        iam_client=self.iam_client,
                        environment_crn=self.env_crn,
                    )

                    self.df_client.terminate_deployment(
                        workload_client=workload_client,
                        deployment_crn=self.deployment_crn,
                        environment_crn=self.env_crn,
                    )

                    # Wait for termination if requested
                    if self.wait:
                        self.df_client.wait_for_deployment_state(
                            target_states=["DELETED", "NOT_FOUND"],
                            deployment_crn=self.deployment_crn,
                            timeout=self.timeout,
                            delay=self.delay,
                        )

                self.changed = True


def main():
    result = DFDeployment()
    output = dict(changed=result.changed, deployment=result.deployment)

    if result.debug_log:
        output.update(
            sdk_out=result.debug_log,
            sdk_out_lines=result.debug_log.splitlines(),
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
