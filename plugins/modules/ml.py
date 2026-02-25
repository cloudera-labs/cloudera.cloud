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
module: ml
short_description: Create or Destroy CDP Machine Learning Workspaces
description:
    - Create or Destroy CDP Machine Learning Workspaces
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Jim Enright (@jenright)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the ML Workspace
    type: str
    required: True
    aliases:
      - workspace
  environment:
    description:
      - The name of the Environment for the ML Workspace
    type: str
    required: True
    aliases:
      - env
  state:
    description:
      - The declarative state of the ML Workspace
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  tls:
    description:
      - The flag to manage TLS for the ML Workspace.
    type: bool
    required: False
    default: True
    aliases:
      - enable_tls
  monitoring:
    description:
      - The flag to manage monitoring for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_monitoring
  governance:
    description:
      - The flag to enable governance by integrating with Cloudera Atlas for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_governance
  metrics:
    description:
      - The flag to enable the exporting of model metrics to a metrics store for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_metrics
  database:
    description:
      - Configuration for exporting model metrics to an existing Postgres database.
    type: dict
    required: False
    suboptions:
      existingDatabaseHost:
        description:
          - The Postgres hostname
        type: str
        required: False
      existingDatabaseName:
        description:
          - The Postgres database name
        type: str
        required: False
      existingDatabasePort:
        description:
          - The Postgres port
        type: str
        required: False
      existingDatabaseUser:
        description:
          - The Postgres user
        type: str
        required: False
      existingDatabasePassword:
        description:
          - The Postgres password
        type: str
        required: False
    aliases:
      - existing_database
      - database_config
  namespace:
    description:
      - The namespace to use for the workspace.
      - Applicable to I(Private Cloud) deployments only.
    type: str
    required: False
  nfs:
    description:
      - An existing NFS mount (hostname and desired path).
      - Applicable to I(Azure) and I(Private Cloud) deployments only.
    type: str
    required: False
    aliases:
      - existing_nfs
  nfs_version:
    description:
      - The NFS Protocol version of the NFS server as declared in C(nfs).
      - Applicable to I(Azure) and I(Private Cloud) deployments only.
    type: str
    required: False
  k8s_request:
    description:
      - Configuration for the Kubernetes provisioning of the ML Workspace.
    type: dict
    required: False
    suboptions:
      environmentName:
        description:
          - The Environment for the ML Workspace
        type: str
        required: True
      instanceGroups:
        description:
          - The instance groups for the ML Workspace provisioning request
        type: list
        elements: dict
        required: True
        suboptions:
          autoscaling:
            description:
              - The autoscaling configuration for the instance group
            type: dict
            required: False
            suboptions:
              enabled:
                description:
                  - The flag enabling autoscaling
                type: bool
                required: False
                default: True
              maxInstance:
                description:
                  - The maximum number of instances
                type: int
                required: True
              minInstance:
                description:
                  - The minimum number of instances
                type: int
                required: True
          ingressRules:
            description:
              - The networking rules for the ingress
            type: list
            elements: str
            required: False
          instanceCount:
            description:
              - The initial number of instances
            type: int
            required: False
            default: 0
          instanceTier:
            description:
              - The provision tier of the instances.
              - For example, C(ON_DEMAND).
            type: str
            required: False
          instanceType:
            description:
              - The cloud provider instance type for the instance.
              - For example, (AWS) C(m5.2xlarge).
            type: str
            required: True
          name:
            description:
              - A unique name of the instance group
            type: str
            required: False
          rootVolume:
            description:
              - Configuration of the root volume for each instance
            type: dict
            required: False
            suboptions:
              size:
                description:
                  - The volume size (in GB)
                type: int
                required: True
      network:
        description:
          - The overlay network for the Container Network Interface (CNI).
          - I(AWS) only.
        type: dict
        required: False
        suboptions:
          plugin:
            description:
              - The identifier for the specific Container Network Interface (CNI) vendor
              - For example, I(calico), I(weave).
            type: str
            required: False
          topology:
            description:
              - The options for overlay topology
            type: dict
            required: False
            suboptions:
              subnets:
                description:
                  - Configuration for the topology subnets
                type: list
                elements: str
                required: False
      tags:
        description:
          - Tags to add to the cloud provider resources
        type: dict
        required: False
        suboptions:
          key:
            description:
              - The key/value pair for the tag
            type: str
            required: False
    aliases:
      - provision_k8s
  loadbalancer_ip_ranges:
    description:
      - List of allowed CIDR blocks for the load balancer.
    type: list
    elements: str
    required: False
    aliases:
      - loadbalancer_access_ips
      - ip_addresses
  public_loadbalancer:
    description:
      - Flag to manage the usage of a public load balancer.
    type: bool
    required: False
    default: False
    aliases:
      - enable_public_loadbalancer
  private_cluster:
    description:
      - Flag to specify if a private K8s cluster should be created.
    type: bool
    required: False
    default: False
    aliases:
      - enable_private_cluster
  k8s_ip_ranges:
    description:
      - List of allowed CIDR blocks to connect to the Kubernetes API server.
    type: list
    elements: str
    required: False
  force:
    description:
      - Flag to force delete a workspace even if errors occur during deletion.
      - Force delete removes the guarantee that the cloud provider resources are destroyed.
      - Applicable to C(state=absent) only.
    type: bool
    required: False
    default: False
    aliases:
      - force_delete
  storage:
    description:
      - Flag to delete the ML Workspace backing storage during delete operations.
      - Applicable to C(state=absent) only.
    type: bool
    required: False
    default: True
    aliases:
      - remove_storage
  yunikorn:
    description:
      - Enable yunikorn scheduling on the ML Workspace.
    type: bool
    required: False
    aliases:
      - enable_yunikorn_scheduling
  enhanced_volume_performance:
    description:
      - Enable Enhanced Performance Mode to maximize throughput and IOPS for root volumes attached to worker nodes.
    type: bool
    required: False
    aliases:
      - enable_enhanced_volume_performance
  global_access_loadbalancer:
    description:
      - Enable global access for the load balancer.
    type: bool
    required: False
    aliases:
      - enable_global_access_loadbalancer
  subdomain:
    description:
      - The static subdomain to be used for the ML Workspace.
    type: str
    required: False
    aliases:
      - static_subdomain
  loadbalancer_subnets:
    description:
      - Subnet ids that will be assigned to the load balancer.
    type: list
    required: False
  resource_pool:
    description:
      - The resource pool configuration for quota management.
    type: dict
    required: False
    suboptions:
      cpu:
        description:
          - The CPU resource pool configuration.
        type: str
        required: True
        aliases:
          - cpu_quota
      gpu:
        description:
          - The GPU resource pool configuration.
        type: str
        required: False
        aliases:
          - gpu_quota
      memory:
        description:
          - The memory resource pool configuration.
        type: str
        required: True
        aliases:
          - memory_quota
  outbound_type:
    description:
      - Outbound type for the ML Workspace.
    type: str
    required: False
    choices:
      - UNKNOWN
      - OUTBOUND_TYPE_UDR
  wait:
    description:
      - Flag to enable internal polling to wait for the ML Workspace to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the ML Workspace to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the ML Workspace to achieve the declared
        state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a ML Workspace with TLS turned off and wait for setup completion
- cloudera.cloud.ml:
    name: ml-example
    env: cdp-env
    tls: false
    wait: true

# Create a ML Workspace (in AWS) with a custom Kubernetes request configuration
- cloudera.cloud.ml:
    name: ml-k8s-example
    env: cdp-env
    k8s_request:
      environmentName: cdp-env
      instanceGroups:
        - name: default_settings
          autoscaling:
            maxInstances: 10
            minInstances: 1
          instanceType: m5.2xlarge
        - name: cpu_settings
          autoscaling:
            maxInstances: 10
            minInstances: 1
          instanceCount: 0
          instanceTier: "ON_DEMAND"
          instanceType: m5.2xlarge
          rootVolume:
            size: 60
        - name: gpu_settings
          autoscaling:
            maxInstances: 1
            minInstances: 0
          instanceCount: 0
          instanceTier: "ON_DEMAND"
          instanceType: "p2.8xlarge"
          rootVolume:
            size: 40
      wait: true

# Remove a ML Workspace, but return immediately
- cloudera.cloud.ml:
    name: ml-example
    env: cdp-env
    state: absent
    wait: false
"""

RETURN = r"""
workspace:
  description: The information about the ML Workspace
  type: dict
  returned: when supported
  contains:
    cloudPlatform:
      description: The cloud platform of the environment that was used to create this workspace.
      returned: always
      type: str
    clusterBaseDomain:
      description: The basedomain of the cluster.
      returned: when supported
      type: str
    creationDate:
      description: Creation date of workspace (date-time).
      returned: always
      type: str
      sample: "2021-05-19T15:35:17.997000+00:00"
    creatorCrn:
      description: The CRN of the creator of the workspace.
      returned: always
      type: str
    crn:
      description: The CRN of the workspace.
      returned: always
      type: str
    endpointPublicAccess:
      description: Flag indicating if the cluster is publicly accessible.
      returned: always
      type: bool
    environmentCrn:
      description: CRN of the environment.
      returned: always
      type: str
    environmentName:
      description: The name of the workspace's environment.
      returned: always
      type: str
    failureMessage:
      description: Failure message from the most recent failure that has occurred during workspace provisioning.
      returned: during failure
      type: str
    filesystemID:
      description: A filesystem ID referencing the filesystem that was created on the cloud provider environment that this workspace uses.
      returned: always
      type: str
    governanceEnabled:
      description: Flag indicating if Cloudera Atlas governance is enabled for the cluster.
      returned: when supported
      type: bool
    healthInfoLists:
      description: The health info information of the workspace.
      type: list
      elements: dict
      contains:
        HealthInfo:
          description: Healthinfo  object  contains  the health information of a resource.
          type: list
          returned: always
          contains:
            details:
              description: The detail of the health info.
              returned: always
              type: list
            isHealthy:
              description: The boolean that indicates the health status.
              returned: always
              type: bool
            message:
              description: The message to show for the health info.
              returned: always
              type: str
            resourceName:
              description: The resource name being checked.
              returned: always
              type: str
            updatedAt:
              description: The unix timestamp for the heartbeat.
              returned: always
              type: str
    httpsEnabled:
      description: Indicates if HTTPS communication was enabled on this workspace when provisioned.
      returned: always
      type: bool
    instanceGroups:
      description: The instance groups details for the cluster.
      returned: always
      type: list
      elements: dict
      contains:
        instanceCount:
          description: The initial number of instance nodes.
          returned: always
          type: int
        instanceGroupName:
          description: The unique name of the instance group.
          returned: always
          type: str
        instanceType:
          description: The cloud provider instance type for the node instances.
          returned: always
          type: str
        instances:
          description: Instances in the instance group.
          returned: always
          type: list
          elements: dict
          contains:
            availabilityZone:
              description: Availability zone of the instance.
              returned: always
              type: str
            instanceId:
              description: Unique instance Id generated by the cloud provider.
              returned: always
              type: str
        maxInstances:
          description: The maximum number of instances that can be deployed to this instance group.
          returned: always
          type: int
        minInstances:
          description: The minimum number of instances that can be deployed to this instance group. If the value is 0, the group might be empty.
          returned: always
          type: int
        tags:
          description: Key/value pairs applied to all applicable resources deployed in cloud provider.
          returned: always
          type: list
          elements: dict
          contains:
            key:
              description: Tag name
              returned: always
              type: str
            value:
              description: Tag value
              returned: always
              type: str
    instanceName:
      description: The name of the workspace.
      returned: always
      type: str
    instanceStatus:
      description: The workspace's current status.
      returned: always
      type: str
    instanceUrl:
      description: URL of the workspace's user interface.
      returned: always
      type: str
    k8sClusterName:
      description: The Kubernetes cluster name.
      returned: always
      type: str
    loadBalancerIPWhitelists:
      description: The whitelist of ips for loadBalancer.
      returned: always
      type: list
    modelMetricsEnabled:
      description: Flag indicating if model metrics export is enabled for the cluster.
      returned: when supported
      type: bool
    monitoringEnabled:
      description: If usage monitoring is enabled or not on this workspace.
      returned: always
      type: bool
    tags:
      description: Tags provided by the user at the time of workspace creation.
      returned: always
      type: list
      elements: dict
      contains:
        key:
          description: Tag name
          returned: always
          type: str
        value:
          description: Tag value
          returned: always
          type: str
    version:
      description: The version of Cloudera Machine Learning that was installed on the workspace.
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

from typing import Any, Dict

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_ml import (
    CdpMlClient,
)


class MLWorkspace(ServicesModule):
    def __init__(self):
        super(MLWorkspace, self).__init__(
            argument_spec=dict(
                name=dict(
                    required=True,
                    type="str",
                    aliases=["workspace", "crn", "workspace_crn"],
                ),
                environment=dict(required=False, type="str", aliases=["env"]),
                tls=dict(
                    required=False,
                    type="bool",
                    default=True,
                    aliases=["enable_tls"],
                ),
                monitoring=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["enable_monitoring"],
                ),
                governance=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["enable_governance"],
                ),
                metrics=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["enable_metrics"],
                ),
                database=dict(
                    required=False,
                    type="dict",
                    options=dict(
                        existingDatabaseHost=dict(required=False, type="str"),
                        existingDatabaseName=dict(required=False, type="str"),
                        existingDatabasePort=dict(required=False, type="str"),
                        existingDatabaseUser=dict(required=False, type="str"),
                        existingDatabasePassword=dict(required=False, type="str"),
                    ),
                    aliases=["existing_database", "database_config"],
                ),
                namespace=dict(required=False, type="str"),
                nfs=dict(required=False, type="str", aliases=["existing_nfs"]),
                nfs_version=dict(required=False, type="str"),
                k8s_request=dict(
                    required=False,
                    type="dict",
                    options=dict(
                        environmentName=dict(required=True, type="str"),
                        instanceGroups=dict(
                            required=True,
                            type="list",
                            elements="dict",
                            options=dict(
                                autoscaling=dict(
                                    required=False,
                                    type="dict",
                                    options=dict(
                                        enabled=dict(
                                            required=False,
                                            type="bool",
                                            default=True,
                                        ),
                                        maxInstances=dict(required=True, type="int"),
                                        minInstances=dict(required=True, type="int"),
                                    ),
                                ),
                                ingressRules=dict(
                                    required=False,
                                    type="list",
                                    elements="str",
                                ),
                                instanceCount=dict(
                                    required=False,
                                    type="int",
                                    default=0,
                                ),
                                instanceTier=dict(required=False, type="str"),
                                instanceType=dict(required=True, type="str"),
                                name=dict(required=False, type="str"),
                                rootVolume=dict(
                                    required=False,
                                    type="dict",
                                    options=dict(size=dict(required=True, type="int")),
                                ),
                            ),
                        ),
                        network=dict(
                            required=False,
                            type="dict",
                            options=dict(
                                plugin=dict(required=False, type="str"),
                                topology=dict(
                                    required=False,
                                    type="dict",
                                    options=dict(
                                        subnets=dict(
                                            required=False,
                                            type="list",
                                            elements="str",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        tags=dict(required=False, type="dict"),
                    ),
                    aliases=["provision_k8s"],
                ),
                loadbalancer_ip_ranges=dict(
                    required=False,
                    type="list",
                    elements="str",
                    aliases=["ip_addresses", "loadbalancer_access_ips"],
                ),
                public_loadbalancer=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["enable_public_loadbalancer"],
                ),
                private_cluster=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["enable_private_cluster"],
                ),
                k8s_ip_ranges=dict(
                    required=False,
                    type="list",
                    elements="str",
                ),
                force=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["force_delete"],
                ),
                storage=dict(
                    required=False,
                    type="bool",
                    default=True,
                    aliases=["remove_storage"],
                ),
                yunikorn=dict(
                    required=False,
                    type="bool",
                    aliases=["enable_yunikorn_scheduling"],
                ),
                enhanced_volume_performance=dict(
                    required=False,
                    type="bool",
                    aliases=["enable_enhanced_volume_performance"],
                ),
                global_access_loadbalancer=dict(
                    required=False,
                    type="bool",
                    aliases=["enable_global_access_loadbalancer"],
                ),
                subdomain=dict(
                    required=False,
                    type="str",
                    aliases=["static_subdomain"],
                ),
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                loadbalancer_subnets=dict(
                    type="list",
                    elements="str",
                    default=None,
                ),
                resource_pool=dict(
                    required=False,
                    type="dict",
                    options=dict(
                        cpu=dict(required=True, type="str", aliases=["cpu_quota"]),
                        gpu=dict(required=False, type="str", aliases=["gpu_quota"]),
                        memory=dict(
                            required=True,
                            type="str",
                            aliases=["memory_quota"],
                        ),
                    ),
                ),
                outbound_type=dict(
                    required=False,
                    type="str",
                    choices=["UNKNOWN", "OUTBOUND_TYPE_UDR"],
                    default=None,
                ),
                wait=dict(required=False, type="bool", default=True),
                delay=dict(
                    required=False,
                    type="int",
                    aliases=["polling_delay"],
                    default=15,
                ),
                timeout=dict(
                    required=False,
                    type="int",
                    aliases=["polling_timeout"],
                    default=3600,
                ),
            ),
            required_if=[
                ("state", "present", ("environment",), False),
            ],
            supports_check_mode=True,
        )

        # Set variables
        self.name = self.get_param("name")
        self.env = self.get_param("environment")

        self.tls = self.get_param("tls")
        self.monitoring = self.get_param("monitoring")
        self.governance = self.get_param("governance")
        self.metrics = self.get_param("metrics")
        self.database = self.get_param("database")
        self.namespace = self.get_param("namespace")
        self.nfs = self.get_param("nfs")
        self.nfs_version = self.get_param("nfs_version")
        self.loadbalancer_ip_ranges = self.get_param("loadbalancer_ip_ranges")
        self.public_loadbalancer = self.get_param("public_loadbalancer")
        self.private_cluster = self.get_param("private_cluster")
        self.k8s_request = self.get_param("k8s_request")
        self.k8s_ip_ranges = self.get_param("k8s_ip_ranges")
        self.force = self.get_param("force")
        self.storage = self.get_param("storage")
        self.enhanced_volume_performance = self.get_param("enhanced_volume_performance")
        self.global_access_loadbalancer = self.get_param("global_access_loadbalancer")
        self.subdomain = self.get_param("subdomain")
        self.loadbalancer_subnets = self.get_param("loadbalancer_subnets")
        self.resource_pool = self.get_param("resource_pool")
        self.outbound_type = self.get_param("outbound_type")

        self.state = self.get_param("state")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")

        # Initialize return values
        self.workspace = {}
        self.changed = False

        # Initialize internal values
        self.target = None

    def process(self):
        client = CdpMlClient(api_client=self.api_client)

        self.target = client.describe_workspace(
            name=self.name,
            env=self.env,
        )

        existing_workspace = self.target.get("workspace")
        # If the Workspace exists
        if existing_workspace is not None:
            # Delete the Workspace
            if self.state == "absent":
                if self.module.check_mode:
                    self.workspace = existing_workspace
                else:
                    if (
                        existing_workspace["instanceStatus"]
                        in CdpMlClient.REMOVABLE_STATES
                    ):
                        client.delete_workspace(
                            workspace_name=self.name,
                            environment_name=self.env,
                            force=self.force,
                            remove_storage=self.storage,
                        )
                        self.changed = True
                    elif (
                        existing_workspace["instanceStatus"]
                        in CdpMlClient.TERMINATION_STATES
                    ):
                        self.module.log(
                            "ML Workspace already performing Delete operation: %s"
                            % existing_workspace["instanceStatus"],
                        )
                    else:
                        self.module.warn(
                            "ML Workspace not in valid state to perform Delete operation: %s"
                            % existing_workspace["instanceStatus"],
                        )
                        if self.wait:
                            self.module.warn(
                                "Waiting for ML Workspace to reach Active state before performing Delete operation",
                            )
                            client.wait_for_workspace_state(
                                self.env,
                                self.name,
                                CdpMlClient.REMOVABLE_STATES,
                                self.delay,
                                self.timeout,
                            )
                            client.delete_workspace(
                                workspace_name=self.name,
                                environment_name=self.env,
                                force=self.force,
                                remove_storage=self.storage,
                            )
                            self.changed = True

                    if self.wait:
                        result = client.wait_for_workspace_state(
                            self.env,
                            self.name,
                            None,
                            self.delay,
                            self.timeout,
                        )
                        # wait_for_workspace_state returns None when workspace is deleted
                        self.workspace = result.get("workspace") if result else None
                    else:
                        self.workspace = existing_workspace
            elif self.state == "present":
                # Check the existing configuration
                self.module.warn(
                    "ML Workspace already present and configuration validation and reconciliation is not supported;"
                    + "to change a ML Workspace, explicitly destroy and recreate the Workspace",
                )
                if self.wait:
                    result = client.wait_for_workspace_state(
                        self.env,
                        self.name,
                        CdpMlClient.READY_STATES,
                        self.delay,
                        self.timeout,
                    )
                    self.workspace = (
                        result.get("workspace") if result else existing_workspace
                    )
                    self.changed = False
                else:
                    self.workspace = existing_workspace
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state,
                )

        # Else if the Workspace does not exist
        else:
            if self.state == "absent":
                self.module.log(
                    "ML Workspace %s already absent in Environment %s"
                    % (self.name, self.env),
                )
            # Create the Workspace
            elif self.state == "present":
                if not self.module.check_mode:
                    # Process k8s_request tags if present
                    k8s_request = self.k8s_request
                    if k8s_request and k8s_request.get("tags") is not None:
                        k8s_request = k8s_request.copy()
                        tag_items = []
                        for k, v in k8s_request["tags"].items():
                            tag_items.append(dict(key=k, value=v))
                        k8s_request["tags"] = tag_items

                    client.create_workspace(
                        workspace_name=self.name,
                        environment_name=self.env,
                        disable_tls=not self.tls,
                        enable_monitoring=self.monitoring,
                        enable_governance=self.governance,
                        enable_model_metrics=self.metrics,
                        existing_database_config=self.database,
                        namespace=self.namespace,
                        existing_nfs=self.nfs,
                        nfs_version=self.nfs_version,
                        load_balancer_ip_whitelists=self.loadbalancer_ip_ranges,
                        authorized_ip_ranges=self.k8s_ip_ranges,
                        use_public_loadbalancer=self.public_loadbalancer,
                        private_cluster=self.private_cluster,
                        provision_k8s_request=k8s_request,
                        enable_enhanced_performance=self.enhanced_volume_performance,
                        enable_global_access_loadbalancer=self.global_access_loadbalancer,
                        static_subdomain=self.subdomain,
                        resource_pool_config=self.resource_pool,
                        outbound_types=self.outbound_type,
                    )
                    self.changed = True
                    if self.wait:
                        result = client.wait_for_workspace_state(
                            self.env,
                            self.name,
                            CdpMlClient.READY_STATES,
                            self.delay,
                            self.timeout,
                        )
                        self.workspace = result.get("workspace") if result else None
                        self.changed = True
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state,
                )


def main():
    result = MLWorkspace()
    output = dict(changed=result.changed, workspace=result.workspace)

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
