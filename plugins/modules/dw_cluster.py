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
module: dw_cluster
short_description: Create or delete CDP Data Warehouse clusters
description:
    - Create or delete CDP Data Warehouse clusters.
    - Cluster creation uses provider-specific endpoints (AWS, Azure, Private Cloud),
      determined automatically from the environment or explicitly via O(cloud_platform).
    - Reconciliation of existing clusters is not yet implemented; the module warns
      when O(state=present) targets an existing cluster.
    - The module supports C(check_mode) and C(diff_mode).
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
  - "Webster Mudge (@wmudge)"
  - "Jim Enright (@jenright)"
version_added: "1.0.0"
options:
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
      - Required if O(state=absent) and O(env) is not specified.
    type: str
    aliases:
      - id
      - name
  cloud_platform:
    description:
      - The cloud provider platform for cluster creation.
      - When set to V(auto) (the default), the module describes the target environment
        and reads its C(cloudPlatform) field to determine which provider-specific
        create endpoint to call.
      - Set explicitly to V(AWS), V(AZURE), or V(PRIVATE) to skip the environment
        describe and use the specified platform directly.
      - Only used when O(state=present) and the cluster does not yet exist.
    type: str
    default: auto
    choices:
      - auto
      - AWS
      - AZURE
      - PRIVATE
    aliases:
      - cloud
      - csp
      - platform
  custom_subdomain:
    description:
      - Custom environment subdomain.
      - Overrides the environment subdomain using a customized domain.
    type: str
  database_backup_retention_period:
    description:
      - PostgreSQL server backup retention days.
    type: int
  env:
    description:
      - The name or CRN of the target environment.
      - Required if O(state=present).
      - Required if O(state=absent) and O(cluster_id) is not specified.
    type: str
    aliases:
      - environment
      - env_crn
  overlay:
    description:
      - Flag to use private IP addresses for Pods within the cluster.
      - Otherwise, use IP addresses within the VPC.
    type: bool
    default: False
  private_load_balancer:
    description: Flag to set up a load balancer for private subnets.
    type: bool
    default: False
  public_worker_node:
    description: Set up public facing worker nodes (AWS only).
    type: bool
  aws:
    description:
      - Options for activating an AWS CDW Cluster.
    type: dict
    required: False
    suboptions:
      lb_subnets:
        description:
          - List of AWS Subnet IDs where the cluster load balancer should be deployed.
        type: list
        elements: str
      worker_subnets:
        description:
          - List of AWS Subnet IDs where the cluster worker nodes should be deployed.
        type: list
        elements: str
      custom_ami_id:
        description:
          - Custom AMI ID for the cluster nodes.
        type: str
      enable_private_eks:
        description:
          - Set up AWS EKS cluster in private-only mode with restricted access.
        type: bool
      enable_spot_instances:
        description:
          - Enable Spot instances for Virtual warehouses.
          - Cannot be updated after creation.
        type: bool
      reduced_permission_mode:
        description:
          - Activate the environment with fewer than half of the standard required IAM permissions.
        type: bool
      node_role_cdw_managed_policy_arn:
        description:
          - Managed Policy ARN to attach to the Node Instance Role.
        type: str
      custom_registry_options:
        description:
          - Options for a custom ECR registry.
        type: dict
        suboptions:
          registry_type:
            description:
              - Custom registry type.
            type: str
            choices:
              - ACR
              - ECR
          repository_url:
            description:
              - URL of the custom image repository.
            type: str
      non_transparent_proxy:
        description:
          - Non-transparent proxy settings for the AWS cluster.
          - See U(https://docs.cloudera.com/data-warehouse/cloud/aws-environments/topics/dw-aws-use-non-transparent-proxy.html).
        type: dict
        suboptions:
          use:
            description:
              - Switch using the default non-transparent proxy on or off.
            type: bool
          bypassed_domains:
            description:
              - Domains where the proxy is bypassed.
            type: list
            elements: str
  aws_lb_subnets:
    description:
      - List of zero or more AWS Subnet IDs where the cluster load balancer should be deployed.
      - Deprecated in favor of O(aws.lb_subnets).
    type: list
    elements: str
    aliases:
      - aws_public_subnets
  aws_worker_subnets:
    description:
      - List of zero or more AWS Subnet IDs where the cluster worker nodes should be deployed.
      - Deprecated in favor of O(aws.worker_subnets).
    type: list
    elements: str
    aliases:
      - aws_private_subnets
  azure:
    description:
      - Options for activating an Azure CDW Cluster.
    type: dict
    required: False
    suboptions:
      subnet:
        description:
          - The Azure Subnet Name.
          - Required if O(state=present) and the O(env) is deployed to Azure.
        type: str
      enable_az:
        description:
          - Flag to enable Availability Zone mode.
        type: bool
      managed_identity:
        description:
          - Resource ID of the managed identity used by AKS.
          - Required if O(state=present) and the O(env) is deployed to Azure.
        type: str
      enable_private_aks:
        description:
          - Flag to enable Azure Private AKS mode.
        type: bool
      enable_private_sql:
        description:
          - Flag to enable private SQL for the cluster deployment.
        type: bool
      enable_spot_instances:
        description:
          - Flag to enable spot instances for Virtual warehouses.
        type: bool
      log_analytics_workspace_id:
        description:
          - Workspace ID for Azure log analytics.
          - Used to monitor the Azure Kubernetes Service (AKS) cluster.
        type: str
      network_outbound_type:
        description:
          - Network outbound type.
          - This setting controls the egress traffic for cluster nodes in Azure Kubernetes Service.
        type: str
        choices:
          - LoadBalancer
          - UserAssignedNATGateway
          - UserDefinedRouting
      aks_private_dns_zone:
        description:
          - ID for the private DNS zone used by AKS.
        type: str
      private_dns_zone_sql:
        description:
          - ID for the private DNS zone used by SQL.
        type: str
      private_sql_subnet_name:
        description:
          - Name of the subnet used for private SQL.
        type: str
      aks_pod_cidr:
        description:
          - CIDR range for AKS pods.
        type: str
      custom_registry_options:
        description:
          - Options for a custom ACR registry.
        type: dict
        suboptions:
          registry_type:
            description:
              - Custom registry type.
            type: str
            choices:
              - ACR
              - ECR
          repository_url:
            description:
              - URL of the custom image repository.
            type: str
      compute_instance_types:
        description:
          - Deprecated. This parameter has no effect and will be removed in a future release.
        type: list
        elements: str
  private_cloud:
    description:
      - Options for activating an On Premise CDW Cluster.
    type: dict
    required: False
    suboptions:
      storage_class:
        description:
          - The storage class for the Local Storage Operator.
        type: str
      db_client_certificate:
        description:
          - TLS client certificate contents.
          - Used for the mutual TLS connections between the Database Catalog and the metastore database.
        type: str
      db_client_key:
        description:
          - TLS client private key contents.
          - Used for the mutual TLS connections between the Database Catalog and the metastore database.
        type: str
      custom_kerberos_principal_hostname:
        description:
          - Custom Kerberos principal hostname for the cluster.
        type: str
  reserved_compute_nodes:
    description:
      - Deprecated. This parameter has no effect and will be removed in a future release.
    type: int
  reserved_shared_services_nodes:
    description:
      - Deprecated. This parameter has no effect and will be removed in a future release.
    type: int
  resource_pool:
    description:
      - Deprecated. This parameter has no effect and will be removed in a future release.
    type: str
  state:
    description: The state of the Data Warehouse Cluster.
    type: str
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.
      - If set to C(false), the module will return immediately.
    type: bool
    default: True
  whitelist_workload_access_ip_cidrs:
    description: The IP ranges authorized to connect for workload access.
    type: list
    elements: str
    required: False
    aliases:
      - loadbalancer_ip_ranges
      - workload_ip_ranges
  whitelist_k8s_cluster_access_ip_cidrs:
    description: The IP ranges authorized to connect to the Kubernetes API server.
    type: list
    elements: str
    required: False
    aliases:
      - k8s_ip_ranges
  force:
    description:
      - Flag to enable force deletion of the Data Warehouse Cluster.
      - This will not destroy the underlying cloud provider assets.
    type: bool
    default: False
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Request AWS Cluster creation (auto-detect platform from environment)
- cloudera.cloud.dw_cluster:
    env: my-environment
    aws:
      lb_subnets:
        - subnet-id-1
        - subnet-id-2
      worker_subnets:
        - subnet-id-3
        - subnet-id-4

# Request AWS Cluster creation with explicit platform
- cloudera.cloud.dw_cluster:
    env: my-environment
    cloud_platform: AWS
    aws:
      lb_subnets:
        - subnet-id-1
      worker_subnets:
        - subnet-id-2
      enable_private_eks: true
      custom_ami_id: ami-0123456789abcdef0

# Request Azure Cluster creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    azure:
      subnet: my-subnet-name
      enable_az: true
      managed_identity: my-aks-managed-identity

# Request Private Cloud Cluster creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    private_cloud:
      storage_class: my-storage-class

# Delete a Data Warehouse Cluster by ID
- cloudera.cloud.dw_cluster:
    state: absent
    cluster_id: my-id

# Delete the Data Warehouse Cluster within the Environment
- cloudera.cloud.dw_cluster:
    state: absent
    env: crn:cdp:environments...

# Force delete a Data Warehouse Cluster
- cloudera.cloud.dw_cluster:
    state: absent
    cluster_id: my-id
    force: true
"""

RETURN = r"""
cluster:
  description: Details for the Data Warehouse cluster.
  type: dict
  contains:
    id:
      description: The cluster identifier.
      returned: always
      type: str
    environmentCrn:
      description: The CRN of the cluster's Environment.
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
      description: The status of the cluster.
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

import time

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    ClusterSummary,
    DW_CLUSTER_RUNNING_STATUSES,
    DW_CLUSTER_FAILED_STATUSES,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)


DW_CLUSTER_REMOVABLE_STATUSES = {
    "Running",
    "Error",
    "Failed",
    "Stopped",
    "Deleting",
}


class DwCluster(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                cluster_id=dict(type="str", aliases=["id", "name"]),
                cloud_platform=dict(
                    type="str",
                    default="auto",
                    choices=["auto", "AWS", "AZURE", "PRIVATE"],
                    aliases=["cloud", "csp", "platform"],
                ),
                custom_subdomain=dict(type="str"),
                database_backup_retention_period=dict(type="int"),
                env=dict(type="str", aliases=["environment", "env_crn"]),
                overlay=dict(type="bool", default=False),
                private_load_balancer=dict(type="bool", default=False),
                public_worker_node=dict(type="bool"),
                aws=dict(
                    type="dict",
                    options=dict(
                        lb_subnets=dict(type="list", elements="str"),
                        worker_subnets=dict(type="list", elements="str"),
                        custom_ami_id=dict(type="str"),
                        enable_private_eks=dict(type="bool"),
                        enable_spot_instances=dict(type="bool"),
                        reduced_permission_mode=dict(type="bool"),
                        node_role_cdw_managed_policy_arn=dict(type="str"),
                        custom_registry_options=dict(
                            type="dict",
                            options=dict(
                                registry_type=dict(
                                    type="str",
                                    choices=["ACR", "ECR"],
                                ),
                                repository_url=dict(type="str"),
                            ),
                        ),
                        non_transparent_proxy=dict(
                            type="dict",
                            options=dict(
                                use=dict(type="bool"),
                                bypassed_domains=dict(
                                    type="list",
                                    elements="str",
                                ),
                            ),
                        ),
                    ),
                ),
                aws_lb_subnets=dict(
                    type="list",
                    elements="str",
                    aliases=["aws_public_subnets"],
                    removed_in_version="4.0.0",
                    removed_from_collection="cloudera.cloud",
                ),
                aws_worker_subnets=dict(
                    type="list",
                    elements="str",
                    aliases=["aws_private_subnets"],
                    removed_in_version="4.0.0",
                    removed_from_collection="cloudera.cloud",
                ),
                azure=dict(
                    type="dict",
                    options=dict(
                        subnet=dict(type="str"),
                        enable_az=dict(type="bool"),
                        managed_identity=dict(type="str"),
                        enable_private_aks=dict(type="bool"),
                        enable_private_sql=dict(type="bool"),
                        enable_spot_instances=dict(type="bool"),
                        log_analytics_workspace_id=dict(type="str"),
                        network_outbound_type=dict(
                            type="str",
                            choices=[
                                "LoadBalancer",
                                "UserAssignedNATGateway",
                                "UserDefinedRouting",
                            ],
                        ),
                        aks_private_dns_zone=dict(type="str"),
                        custom_registry_options=dict(
                            type="dict",
                            options=dict(
                                registry_type=dict(
                                    type="str",
                                    choices=["ACR", "ECR"],
                                ),
                                repository_url=dict(type="str"),
                            ),
                        ),
                        compute_instance_types=dict(
                            type="list",
                            elements="str",
                            removed_in_version="4.0.0",
                            removed_from_collection="cloudera.cloud",
                        ),
                        private_dns_zone_sql=dict(type="str"),
                        private_sql_subnet_name=dict(type="str"),
                        aks_pod_cidr=dict(type="str"),
                    ),
                ),
                private_cloud=dict(
                    type="dict",
                    options=dict(
                        storage_class=dict(type="str"),
                        db_client_certificate=dict(type="str"),
                        db_client_key=dict(type="str"),
                        custom_kerberos_principal_hostname=dict(type="str"),
                    ),
                    required_together=[
                        ["db_client_certificate", "db_client_key"],
                    ],
                ),
                reserved_compute_nodes=dict(
                    type="int",
                    removed_in_version="4.0.0",
                    removed_from_collection="cloudera.cloud",
                ),
                reserved_shared_services_nodes=dict(
                    type="int",
                    removed_in_version="4.0.0",
                    removed_from_collection="cloudera.cloud",
                ),
                resource_pool=dict(
                    type="str",
                    removed_in_version="4.0.0",
                    removed_from_collection="cloudera.cloud",
                ),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                force=dict(type="bool", default=False),
                wait=dict(type="bool", default=True),
                whitelist_workload_access_ip_cidrs=dict(
                    type="list",
                    elements="str",
                    default=None,
                    aliases=["loadbalancer_ip_ranges", "workload_ip_ranges"],
                ),
                whitelist_k8s_cluster_access_ip_cidrs=dict(
                    type="list",
                    elements="str",
                    default=None,
                    aliases=["k8s_ip_ranges"],
                ),
                delay=dict(type="int", aliases=["polling_delay"], default=15),
                timeout=dict(type="int", aliases=["polling_timeout"], default=3600),
            ),
            required_if=[
                ["state", "absent", ["cluster_id", "env"], True],
                ["state", "present", ["env"]],
            ],
            supports_check_mode=True,
        )

        self.cluster_id = self.get_param("cluster_id")
        self.cloud_platform = self.get_param("cloud_platform")
        self.custom_subdomain = self.get_param("custom_subdomain")
        self.database_backup_retention_period = self.get_param(
            "database_backup_retention_period",
        )
        self.env = self.get_param("env")
        self.overlay = self.get_param("overlay")
        self.private_load_balancer = self.get_param("private_load_balancer")
        self.public_worker_node = self.get_param("public_worker_node")
        self.force = self.get_param("force")
        self.state = self.get_param("state")
        self.wait = self.get_param("wait")
        self.delay = self.get_param("delay")
        self.timeout = self.get_param("timeout")
        self.whitelist_workload_access_ip_cidrs = self.get_param(
            "whitelist_workload_access_ip_cidrs",
        )
        self.whitelist_k8s_cluster_access_ip_cidrs = self.get_param(
            "whitelist_k8s_cluster_access_ip_cidrs",
        )

        # AWS nested parameters
        aws_opts = self.get_param("aws") or {}
        self.aws_lb_subnets_nested = aws_opts.get("lb_subnets")
        self.aws_worker_subnets_nested = aws_opts.get("worker_subnets")
        self.aws_custom_ami_id = aws_opts.get("custom_ami_id")
        self.aws_enable_private_eks = aws_opts.get("enable_private_eks")
        self.aws_enable_spot_instances = aws_opts.get("enable_spot_instances")
        self.aws_reduced_permission_mode = aws_opts.get("reduced_permission_mode")
        self.aws_node_role_cdw_managed_policy_arn = aws_opts.get(
            "node_role_cdw_managed_policy_arn",
        )
        self.aws_custom_registry_options = self._build_custom_registry_options(
            aws_opts.get("custom_registry_options"),
        )
        self.aws_non_transparent_proxy = self._build_non_transparent_proxy(
            aws_opts.get("non_transparent_proxy"),
        )

        # Deprecated top-level AWS parameters
        self.aws_lb_subnets_top = self.get_param("aws_lb_subnets")
        self.aws_worker_subnets_top = self.get_param("aws_worker_subnets")

        # Azure nested parameters
        azure_opts = self.get_param("azure") or {}
        self.az_subnet = azure_opts.get("subnet")
        self.az_enable_az = azure_opts.get("enable_az")
        self.az_managed_identity = azure_opts.get("managed_identity")
        self.az_enable_private_aks = azure_opts.get("enable_private_aks")
        self.az_enable_private_sql = azure_opts.get("enable_private_sql")
        self.az_enable_spot_instances = azure_opts.get("enable_spot_instances")
        self.az_log_analytics_workspace_id = azure_opts.get(
            "log_analytics_workspace_id",
        )
        self.az_network_outbound_type = azure_opts.get("network_outbound_type")
        self.az_aks_private_dns_zone = azure_opts.get("aks_private_dns_zone")
        self.az_private_dns_zone_sql = azure_opts.get("private_dns_zone_sql")
        self.az_private_sql_subnet_name = azure_opts.get("private_sql_subnet_name")
        self.az_aks_pod_cidr = azure_opts.get("aks_pod_cidr")
        self.az_custom_registry_options = self._build_custom_registry_options(
            azure_opts.get("custom_registry_options"),
        )

        # Private Cloud nested parameters
        pvc_opts = self.get_param("private_cloud") or {}
        self.pvc_storage_class = pvc_opts.get("storage_class")
        self.pvc_db_client_cert = pvc_opts.get("db_client_certificate")
        self.pvc_db_client_key = pvc_opts.get("db_client_key")
        self.pvc_custom_kerberos_principal_hostname = pvc_opts.get(
            "custom_kerberos_principal_hostname",
        )

        # Initialize return values
        self.cluster: Optional[ClusterSummary] = None
        self.changed = False
        self.diff: Dict[str, Any] = {"before": {}, "after": {}}

    @staticmethod
    def _build_custom_registry_options(opts):
        """Build the API-level customRegistryOptions dict from module params."""
        if opts is None:
            return None
        result = {}
        if opts.get("registry_type") is not None:
            result["registryType"] = opts["registry_type"]
        if opts.get("repository_url") is not None:
            result["repositoryUrl"] = opts["repository_url"]
        return result or None

    @staticmethod
    def _build_non_transparent_proxy(opts):
        """Build the API-level nonTransparentProxy dict from module params."""
        if opts is None:
            return None
        result = {}
        if opts.get("use") is not None:
            result["use"] = opts["use"]
        if opts.get("bypassed_domains") is not None:
            result["bypassedDomains"] = opts["bypassed_domains"]
        return result or None

    def _resolve_aws_subnets(self):
        """Resolve overlapping top-level and nested AWS subnet parameters."""
        lb_subnets = self._resolve_deprecated_param(
            "aws_lb_subnets",
            self.aws_lb_subnets_top,
            "aws.lb_subnets",
            self.aws_lb_subnets_nested,
        )
        worker_subnets = self._resolve_deprecated_param(
            "aws_worker_subnets",
            self.aws_worker_subnets_top,
            "aws.worker_subnets",
            self.aws_worker_subnets_nested,
        )
        return lb_subnets, worker_subnets

    def _resolve_deprecated_param(
        self,
        old_name: str,
        old_value,
        new_name: str,
        new_value,
    ):
        """Resolve a deprecated top-level param vs its nested replacement.

        Returns the effective value. Fails if both are provided with different
        values.
        """
        if new_value is not None and old_value is not None:
            if new_value != old_value:
                self.module.fail_json(
                    msg=(
                        f"Conflicting values for '{old_name}' and '{new_name}'. "
                        f"Use '{new_name}' only; '{old_name}' is deprecated."
                    ),
                )
            return new_value
        if new_value is not None:
            return new_value
        if old_value is not None:
            self.module.deprecate(
                msg=(
                    f"The '{old_name}' parameter is deprecated. "
                    f"Use '{new_name}' instead."
                ),
                version="4.0.0",
                collection_name="cloudera.cloud",
            )
            return old_value
        return None

    def _resolve_cloud_platform(self, env_client: CdpEnvClient) -> str:
        """Determine the cloud platform for cluster creation."""
        if self.cloud_platform != "auto":
            return self.cloud_platform

        env = env_client.describe_environment(self.env)
        if env is None:
            self.module.fail_json(
                msg=(
                    f"Could not describe environment '{self.env}' to determine "
                    f"cloud platform. Set 'cloud_platform' explicitly to "
                    f"AWS, AZURE, or PRIVATE."
                ),
            )

        platform = env.get("cloudPlatform", "")
        if platform == "AWS":
            return "AWS"
        if platform == "AZURE":
            return "AZURE"
        return "PRIVATE"

    def _resolve_env_crn(self, env_client: CdpEnvClient) -> Optional[str]:
        """Resolve environment name or CRN to a CRN."""
        if self.env is None:
            return None
        if self.env.startswith("crn:"):
            return self.env
        return env_client.get_environment_crn(self.env)

    def process(self):
        client = CdpDwClient(api_client=self.api_client)
        env_client = CdpEnvClient(api_client=self.api_client)

        env_crn = self._resolve_env_crn(env_client)

        # Look up existing cluster
        target: Optional[ClusterSummary] = None
        target_id: Optional[str] = self.cluster_id

        if target_id is not None:
            target = client.describe_cluster(cluster_id=target_id)
        elif env_crn is not None:
            listing = client.list_clusters(env_crn=env_crn)
            if len(listing) == 1:
                target_id = listing[0].id
                target = client.describe_cluster(cluster_id=target_id)
            elif len(listing) > 1:
                self.module.fail_json(
                    msg=(
                        f"Received multiple (i.e. ambiguous) Clusters "
                        f"in Environment {self.env}"
                    ),
                )

        if target is not None:
            if self.state == "absent":
                self.changed = True
                if self.module._diff:
                    self.diff["before"] = to_dict(target)

                if not self.module.check_mode:
                    if target.status not in DW_CLUSTER_REMOVABLE_STATUSES:
                        self.module.warn(
                            f"Cluster is not in a valid state for Delete "
                            f"operations: {target.status}",
                        )
                    else:
                        client.delete_cluster(
                            cluster_id=target_id,
                            force=self.force,
                        )

                    if self.wait:
                        client.wait_for_cluster_state(
                            cluster_id=target_id,
                            target_statuses=set(),
                            error_statuses=DW_CLUSTER_FAILED_STATUSES,
                            timeout=self.timeout,
                            delay=self.delay,
                        )
                    else:
                        time.sleep(self.delay)
                        self.cluster = client.describe_cluster(
                            cluster_id=target_id,
                        )

            elif self.state == "present":
                self.module.warn(
                    "Cluster is already present and reconciliation is not yet "
                    "implemented",
                )
                if self.wait:
                    target = client.wait_for_cluster_state(
                        cluster_id=target_id,
                        target_statuses=DW_CLUSTER_RUNNING_STATUSES,
                        error_statuses=DW_CLUSTER_FAILED_STATUSES,
                        timeout=self.timeout,
                        delay=self.delay,
                    )
                self.cluster = target
        else:
            if self.state == "absent":
                self.module.warn(
                    f"Cluster {self.cluster_id} already absent in "
                    f"Environment {self.env}",
                )
            elif self.state == "present":
                self.changed = True

                if env_crn is None:
                    self.module.fail_json(
                        msg=(
                            f"Could not retrieve CRN for CDP " f"Environment {self.env}"
                        ),
                    )

                platform = self._resolve_cloud_platform(env_client)

                if self.module._diff:
                    self.diff["after"] = {
                        "environmentCrn": env_crn,
                        "cloudPlatform": platform,
                    }

                if not self.module.check_mode:
                    cluster_id = self._dispatch_create(client, env_crn, platform)

                    if self.wait:
                        self.cluster = client.wait_for_cluster_state(
                            cluster_id=cluster_id,
                            target_statuses=DW_CLUSTER_RUNNING_STATUSES,
                            error_statuses=DW_CLUSTER_FAILED_STATUSES,
                            timeout=self.timeout,
                            delay=self.delay,
                        )
                    else:
                        self.cluster = client.describe_cluster(
                            cluster_id=cluster_id,
                        )

    def _dispatch_create(
        self,
        client: CdpDwClient,
        env_crn: str,
        platform: str,
    ) -> str:
        """Dispatch to the correct provider-specific create method."""
        if platform == "AWS":
            return self._create_aws_cluster(client, env_crn)
        elif platform == "AZURE":
            return self._create_azure_cluster(client, env_crn)
        else:
            return self._create_private_cluster(client, env_crn)

    def _create_aws_cluster(self, client: CdpDwClient, env_crn: str) -> str:
        lb_subnets, worker_subnets = self._resolve_aws_subnets()
        return client.create_aws_cluster(
            env_crn=env_crn,
            use_overlay_network=self.overlay if self.overlay else None,
            use_private_load_balancer=(
                self.private_load_balancer if self.private_load_balancer else None
            ),
            use_public_worker_node=self.public_worker_node,
            lb_subnet_ids=lb_subnets,
            worker_subnet_ids=worker_subnets,
            custom_subdomain=self.custom_subdomain,
            database_backup_retention_period=self.database_backup_retention_period,
            whitelist_workload_access_ip_cidrs=self.whitelist_workload_access_ip_cidrs,
            whitelist_k8s_cluster_access_ip_cidrs=self.whitelist_k8s_cluster_access_ip_cidrs,
            custom_ami_id=self.aws_custom_ami_id,
            enable_private_eks=self.aws_enable_private_eks,
            enable_spot_instances=self.aws_enable_spot_instances,
            reduced_permission_mode=self.aws_reduced_permission_mode,
            node_role_cdw_managed_policy_arn=self.aws_node_role_cdw_managed_policy_arn,
            custom_registry_options=self.aws_custom_registry_options,
            non_transparent_proxy=self.aws_non_transparent_proxy,
        )

    def _create_azure_cluster(self, client: CdpDwClient, env_crn: str) -> str:
        return client.create_azure_cluster(
            env_crn=env_crn,
            subnet_name=self.az_subnet,
            user_assigned_managed_identity=self.az_managed_identity,
            use_overlay_networking=self.overlay if self.overlay else None,
            use_internal_load_balancer=(
                self.private_load_balancer if self.private_load_balancer else None
            ),
            enable_az=self.az_enable_az,
            enable_private_aks=self.az_enable_private_aks,
            enable_private_sql=self.az_enable_private_sql,
            enable_spot_instances=self.az_enable_spot_instances,
            log_analytics_workspace_id=self.az_log_analytics_workspace_id,
            outbound_type=self.az_network_outbound_type,
            private_dns_zone_aks=self.az_aks_private_dns_zone,
            private_dns_zone_sql=self.az_private_dns_zone_sql,
            private_sql_subnet_name=self.az_private_sql_subnet_name,
            aks_pod_cidr=self.az_aks_pod_cidr,
            custom_subdomain=self.custom_subdomain,
            database_backup_retention_period=self.database_backup_retention_period,
            whitelist_workload_access_ip_cidrs=self.whitelist_workload_access_ip_cidrs,
            whitelist_k8s_cluster_access_ip_cidrs=self.whitelist_k8s_cluster_access_ip_cidrs,
            custom_registry_options=self.az_custom_registry_options,
        )

    def _create_private_cluster(self, client: CdpDwClient, env_crn: str) -> str:
        db_client_credentials = None
        if self.pvc_db_client_cert is not None and self.pvc_db_client_key is not None:
            db_client_credentials = {
                "certificate": self.pvc_db_client_cert,
                "privateKey": self.pvc_db_client_key,
            }
        return client.create_private_cluster(
            env_crn=env_crn,
            storage_class=self.pvc_storage_class,
            db_client_credentials=db_client_credentials,
            custom_kerberos_principal_hostname=self.pvc_custom_kerberos_principal_hostname,
        )


def main():
    result = DwCluster()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        cluster=to_dict(result.cluster) if result.cluster else {},
    )

    if result.diff["before"] or result.diff["after"]:
        output["diff"] = result.diff

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
