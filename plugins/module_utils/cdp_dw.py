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

"""
A REST client for the Cloudera Data Warehouse (CDW) API
"""

import time

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Union,
)


from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
)


@dataclass
class Connector:
    """CDP Data Warehouse Database Connector."""

    id: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    template: Union[str, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    config: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    createdAt: Union[int, None, NULLABLE] = NULLABLE
    createdBy: Union[str, None, NULLABLE] = NULLABLE
    updatedAt: Union[int, None, NULLABLE] = NULLABLE
    updatedBy: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ConnectorTestJob:
    """CDP Data Warehouse Connector Test Job details."""

    jobId: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    jobStartTime: Union[str, None, NULLABLE] = NULLABLE
    jobFinishTime: Union[str, None, NULLABLE] = NULLABLE
    labels: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    outputLog: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class VirtualWarehouse:
    """CDP Data Warehouse Virtual Warehouse.

    C(associatedConnectors) is stored as the raw API map,
    C(<connectorId>: {name, configId}). Only its key set (the connector ids)
    is meaningful for reconciliation; C(name) and C(configId) are managed by
    the server and are excluded from change detection.
    """

    id: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    vwType: Union[str, None, NULLABLE] = NULLABLE
    dbcId: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    instanceType: Union[str, None, NULLABLE] = NULLABLE
    nodeCount: Union[int, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    creator: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    creationDate: Union[str, None, NULLABLE] = NULLABLE
    configId: Union[str, None, NULLABLE] = NULLABLE
    cdhVersion: Union[str, None, NULLABLE] = NULLABLE
    availabilityZone: Union[str, None, NULLABLE] = NULLABLE
    endpoints: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    tags: Union[List[Any], None, NULLABLE] = NULLABLE
    associatedConnectors: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


@dataclass
class DwSecretProperties:
    """Properties of a CDW secret."""

    azureVaultName: Union[str, None, NULLABLE] = NULLABLE
    cloudProvider: Union[str, None, NULLABLE] = NULLABLE
    version: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class DwSecret:
    """Details of a single CDW secret."""

    secretName: Union[str, None, NULLABLE] = NULLABLE
    secretProviderKey: Union[str, None, NULLABLE] = NULLABLE
    createdBy: Union[str, None, NULLABLE] = NULLABLE
    properties: Union[DwSecretProperties, None, NULLABLE] = NULLABLE


@dataclass
class ActorResponse:
    """Identity details for the creator of a DW cluster."""

    crn: Union[str, None, NULLABLE] = NULLABLE
    email: Union[str, None, NULLABLE] = NULLABLE
    workloadUsername: Union[str, None, NULLABLE] = NULLABLE
    machineUsername: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class AwsOptionsNonTransparentProxyResponse:
    """Non-transparent proxy settings for an AWS DW cluster."""

    use: Union[bool, None, NULLABLE] = NULLABLE
    bypassedDomains: Union[List[str], None, NULLABLE] = NULLABLE


@dataclass
class AwsOptionsResponse:
    """AWS-specific configuration for a DW cluster."""

    lbSubnetIds: Union[List[str], None, NULLABLE] = NULLABLE
    workerSubnetIds: Union[List[str], None, NULLABLE] = NULLABLE
    subnetIds: Union[List[str], None, NULLABLE] = NULLABLE
    customAmiId: Union[str, None, NULLABLE] = NULLABLE
    kmsKey: Union[str, None, NULLABLE] = NULLABLE
    availabilityZones: Union[List[str], None, NULLABLE] = NULLABLE
    reducedPermissionMode: Union[bool, None, NULLABLE] = NULLABLE
    nonTransparentProxy: Union[
        AwsOptionsNonTransparentProxyResponse,
        None,
        NULLABLE,
    ] = NULLABLE


@dataclass
class AzureOptionsResponse:
    """Azure-specific configuration for a DW cluster."""

    subnetId: Union[str, None, NULLABLE] = NULLABLE
    userAssignedManagedIdentity: Union[str, None, NULLABLE] = NULLABLE
    enableAZ: Union[bool, None, NULLABLE] = NULLABLE
    enablePrivateAKS: Union[bool, None, NULLABLE] = NULLABLE
    enablePrivateSQL: Union[bool, None, NULLABLE] = NULLABLE
    logAnalyticsWorkspaceId: Union[str, None, NULLABLE] = NULLABLE
    outboundType: Union[str, None, NULLABLE] = NULLABLE
    privateDNSZoneAKS: Union[str, None, NULLABLE] = NULLABLE
    privateDNSZoneSQL: Union[str, None, NULLABLE] = NULLABLE
    privateSQLSubnetName: Union[str, None, NULLABLE] = NULLABLE
    aksPodCIDR: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ClusterSummary:
    """CDP Data Warehouse cluster summary."""

    id: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    environmentCrn: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    cloudPlatform: Union[str, None, NULLABLE] = NULLABLE
    creationDate: Union[str, None, NULLABLE] = NULLABLE
    creator: Union[ActorResponse, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    version: Union[str, None, NULLABLE] = NULLABLE
    enablePrivateLoadBalancer: Union[bool, None, NULLABLE] = NULLABLE
    enableSpotInstances: Union[bool, None, NULLABLE] = NULLABLE
    useOverlayNetwork: Union[bool, None, NULLABLE] = NULLABLE
    resourcePool: Union[str, None, NULLABLE] = NULLABLE
    whitelistK8sClusterAccessIpCIDRs: Union[str, None, NULLABLE] = NULLABLE
    whitelistWorkloadAccessIpCIDRs: Union[str, None, NULLABLE] = NULLABLE
    awsOptions: Union[AwsOptionsResponse, None, NULLABLE] = NULLABLE
    azureOptions: Union[AzureOptionsResponse, None, NULLABLE] = NULLABLE


DW_CLUSTER_RUNNING_STATUSES: Set[str] = {"Running"}
DW_CLUSTER_FAILED_STATUSES: Set[str] = {"Error", "Failed"}


class CdpDwClient:
    """CDP Data Warehouse API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP Data Warehouse client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def list_connectors(self, cluster_id: str) -> List[Connector]:
        """
        List Database Connectors in a cluster.

        Args:
            cluster_id: The ID of the cluster

        Returns:
            List of Connector dataclass instances
        """
        data = {"clusterId": cluster_id}
        response = self.api_client.post(
            "/api/v1/dw/listConnectors",
            data=data,
            squelch={404: {"connectors": []}},
        )
        return [from_dict(Connector, c) for c in response.get("connectors", [])]

    def get_connector_by_id(
        self,
        cluster_id: str,
        connector_id: str,
    ) -> Optional[Connector]:
        """
        Get connector details by connector ID.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector

        Returns:
            Connector dataclass instance, or None if not found
        """
        for connector in self.list_connectors(cluster_id):
            if connector.id == connector_id:
                return connector
        return None

    def get_connector_by_name(
        self,
        cluster_id: str,
        name: str,
    ) -> Optional[Connector]:
        """
        Get connector details by name.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the connector

        Returns:
            Connector dataclass instance, or None if not found
        """
        for connector in self.list_connectors(cluster_id):
            if connector.name == name:
                return connector
        return None

    def create_connector(
        self,
        cluster_id: str,
        name: str,
        template: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, str]] = None,
    ) -> Connector:
        """
        Create a new Database Connector in a cluster.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the connector
            template: The template of the connector
            description: Optional user-provided description
            config: Optional connector configuration in key-value format

        Returns:
            Connector dataclass instance of the created connector
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "name": name,
            "template": template,
        }
        if description is not None:
            data["description"] = description
        if config is not None:
            data["config"] = config
        response = self.api_client.post(
            "/api/v1/dw/createConnector",
            data=data,
        )
        return from_dict(Connector, response.get("result", {}))

    def update_connector(
        self,
        cluster_id: str,
        connector_id: str,
        name: str,
        description: str,
        template: str,
        config: Dict[str, str],
    ) -> Connector:
        """
        Update a Database Connector in a cluster.

        The API expects the connector's full representation, so every field is
        required; callers pass the connector's existing value for any field they
        are not changing.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to update
            name: The name of the connector
            description: The description of the connector
            template: The template of the connector
            config: The connector configuration in key-value format

        Returns:
            Connector dataclass instance reflecting the updated state
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "connectorId": connector_id,
            "name": name,
            "description": description,
            "template": template,
            "config": config,
        }
        self.api_client.post(
            "/api/v1/dw/updateConnector",
            data=data,
        )
        return self.get_connector_by_id(cluster_id, connector_id)

    def delete_connector(
        self,
        cluster_id: str,
        connector_id: str,
    ) -> None:
        """
        Delete a Database Connector from a cluster.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to delete
        """
        self.api_client.post(
            "/api/v1/dw/deleteConnector",
            data={
                "clusterId": cluster_id,
                "connectorId": connector_id,
            },
            squelch={404: {}},
        )

    def create_connector_test_job(
        self,
        cluster_id: str,
        connector_id: Optional[str] = None,
        connector_name: Optional[str] = None,
        config: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create a test job for a Connector.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to test
            connector_name: The name of the connector to test
            config: Optional key-value configuration overrides

        Returns:
            The ID of the created test job
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}
        if connector_id is not None:
            data["connectorId"] = connector_id
        if connector_name is not None:
            data["connectorName"] = connector_name
        if config is not None:
            data["config"] = config
        response = self.api_client.post(
            "/api/v1/dw/createConnectorTestJob",
            data=data,
        )
        return response.get("jobId", "")

    def list_connector_test_jobs(
        self,
        cluster_id: str,
        job_id: Optional[str] = None,
    ) -> List[ConnectorTestJob]:
        """
        List test jobs for a cluster's connectors.

        Args:
            cluster_id: The ID of the cluster
            job_id: Optional specific job ID to fetch

        Returns:
            List of ConnectorTestJob dataclass instances
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}
        if job_id is not None:
            data["jobId"] = job_id
        response = self.api_client.post(
            "/api/v1/dw/listConnectorTestJobs",
            data=data,
            squelch={404: {"results": []}},
        )
        return [from_dict(ConnectorTestJob, j) for j in response.get("results", [])]

    def list_vws(
        self,
        cluster_id: str,
        name: Optional[str] = None,
    ) -> List[VirtualWarehouse]:
        """
        List Virtual Warehouses in a cluster.

        Args:
            cluster_id: The ID of the cluster
            name: Optional Virtual Warehouse name to filter by (exact match).
                When provided, only the matching entry is marshalled.

        Returns:
            List of VirtualWarehouse dataclass instances
        """
        response = self.api_client.post(
            "/api/v1/dw/listVws",
            data={"clusterId": cluster_id},
            squelch={404: {"vws": []}},
        )
        return [
            from_dict(VirtualWarehouse, vw)
            for vw in response.get("vws", [])
            if name is None or vw.get("name") == name
        ]

    def get_vw_by_id(
        self,
        cluster_id: str,
        vw_id: str,
    ) -> Optional[VirtualWarehouse]:
        """
        Get Virtual Warehouse details by ID.

        Args:
            cluster_id: The ID of the cluster
            vw_id: The ID of the Virtual Warehouse

        Returns:
            VirtualWarehouse dataclass instance, or None if not found
        """
        response = self.api_client.post(
            "/api/v1/dw/describeVw",
            data={"clusterId": cluster_id, "vwId": vw_id},
            squelch={400: None, 404: None},
        )
        if response is None:
            return None
        vw = response.get("vw")
        return from_dict(VirtualWarehouse, vw) if vw else None

    def get_vw_by_name(
        self,
        cluster_id: str,
        name: str,
    ) -> Optional[VirtualWarehouse]:
        """
        Get Virtual Warehouse details by name.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the Virtual Warehouse

        Returns:
            VirtualWarehouse dataclass instance, or None if not found
        """
        vws = self.list_vws(cluster_id, name=name)
        return vws[0] if vws else None

    def create_vw(
        self,
        cluster_id: str,
        dbc_id: str,
        vw_type: str,
        name: str,
        tshirt_size: Optional[str] = None,
        node_count: Optional[int] = None,
        instance_type: Optional[str] = None,
        autoscaling: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        impala_ha: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        enable_unified_analytics: Optional[bool] = None,
        enable_platform_jwt_auth: Optional[bool] = None,
    ) -> Optional[VirtualWarehouse]:
        """
        Create a Virtual Warehouse in a cluster.

        The C(createVw) endpoint returns only the new warehouse id, so this
        method re-describes the warehouse and returns its full representation.

        Args:
            cluster_id: The ID of the cluster
            dbc_id: The ID of the Database Catalog to attach
            vw_type: The type of Virtual Warehouse (hive, impala, trino)
            name: The display name of the Virtual Warehouse
            tshirt_size: Optional deployment T-shirt size
            node_count: Optional node count (forces a custom template)
            instance_type: Optional underlying compute instance type
            autoscaling: Optional autoscaling configuration
            config: Optional service configuration (ServiceConfigReq)
            impala_ha: Optional Impala high-availability settings
            tags: Optional key-value resource tags
            enable_unified_analytics: Optional Unified Analytics flag (Impala)
            enable_platform_jwt_auth: Optional CDP JWT auth flag

        Returns:
            VirtualWarehouse dataclass instance of the created warehouse, or
            None if it cannot yet be described.
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "dbcId": dbc_id,
            "vwType": vw_type,
            "name": name,
        }
        optional = {
            "tShirtSize": tshirt_size,
            "nodeCount": node_count,
            "instanceType": instance_type,
            "autoscaling": autoscaling,
            "config": config,
            "impalaHaSettings": impala_ha,
            "tags": tags,
            "enableUnifiedAnalytics": enable_unified_analytics,
            "platformJwtAuth": enable_platform_jwt_auth,
        }
        data.update({k: v for k, v in optional.items() if v is not None})
        response = self.api_client.post(
            "/api/v1/dw/createVw",
            data=data,
        )
        vw_id = response.get("vwId", "")
        return self.get_vw_by_id(cluster_id, vw_id) if vw_id else None

    def update_vw(
        self,
        cluster_id: str,
        vw_id: str,
        tshirt_size: Optional[str] = None,
        node_count: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        autoscaling: Optional[Dict[str, Any]] = None,
        impala_ha: Optional[Dict[str, Any]] = None,
        associated_connectors: Optional[List[str]] = None,
    ) -> Optional[VirtualWarehouse]:
        """
        Update a Virtual Warehouse.

        C(associated_connectors) is a list of connector ids. The API treats the
        C(associatedConnectors) map as the authoritative (full-sync) set, so the
        map sent here replaces the warehouse's current associations. Only the
        connector id (the map key) is honored on write; C(name) is ignored and
        C(configId) is auto-assigned by the server, so each value is an empty
        object.

        The C(updateVw) endpoint returns only a status message, so this method
        re-describes the warehouse and returns its full representation.

        Args:
            cluster_id: The ID of the cluster
            vw_id: The ID of the Virtual Warehouse to update
            tshirt_size: Optional new deployment T-shirt size
            node_count: Optional new node count
            config: Optional service configuration delta (ServiceConfigReq)
            autoscaling: Optional autoscaling configuration
            impala_ha: Optional Impala high-availability settings
            associated_connectors: Optional full desired set of connector ids

        Returns:
            VirtualWarehouse dataclass instance reflecting the updated state, or
            None if it cannot be described.
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "vwId": vw_id,
        }
        optional: Dict[str, Any] = {
            "tShirtSize": tshirt_size,
            "nodeCount": node_count,
            "config": config,
            "autoscaling": autoscaling,
            "impalaHaSettings": impala_ha,
        }
        data.update({k: v for k, v in optional.items() if v is not None})
        if associated_connectors is not None:
            data["associatedConnectors"] = {
                connector_id: {"name": ""} for connector_id in associated_connectors
            }
        self.api_client.post(
            "/api/v1/dw/updateVw",
            data=data,
        )
        return self.get_vw_by_id(cluster_id, vw_id)

    def delete_vw(
        self,
        cluster_id: str,
        vw_id: str,
    ) -> None:
        """
        Delete a Virtual Warehouse from a cluster.

        Args:
            cluster_id: The ID of the cluster
            vw_id: The ID of the Virtual Warehouse to delete
        """
        self.api_client.post(
            "/api/v1/dw/deleteVw",
            data={
                "clusterId": cluster_id,
                "vwId": vw_id,
            },
            squelch={404: {}},
        )

    def list_secrets(
        self,
        cluster_id: str,
        name: Optional[str] = None,
    ) -> List[DwSecret]:
        """
        List secrets in a CDW cluster.

        Args:
            cluster_id: The ID of the cluster
            name: Optional secret name to filter by (exact match). When provided,
                only the matching entry is marshalled into a DwSecret.

        Returns:
            List of DwSecret dataclass instances
        """
        response = self.api_client.post(
            "/api/v1/dw/listSecrets",
            json_data={"clusterId": cluster_id},
        )
        return [
            from_dict(DwSecret, item)
            for item in response.get("result", [])
            if name is None or item.get("secretName") == name
        ]

    def get_secret(
        self,
        cluster_id: str,
        name: str,
    ) -> Optional[DwSecret]:
        """
        Get a secret by its name.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the secret

        Returns:
            DwSecret dataclass instance, or None if not found
        """
        secrets = self.list_secrets(cluster_id, name=name)
        return secrets[0] if secrets else None

    def create_secret(
        self,
        cluster_id: str,
        secret_name: str,
        secret_value: str,
    ) -> DwSecret:
        """
        Create a secret in a Kubernetes cluster.

        Args:
            cluster_id: The ID of the cluster
            secret_name: The name of the secret
            secret_value: The value (contents) of the secret

        Returns:
            DwSecret dataclass instance of the created secret
        """
        response = self.api_client.post(
            "/api/v1/dw/createSecret",
            data={
                "clusterId": cluster_id,
                "secretName": secret_name,
                "secretValue": secret_value,
            },
        )
        return from_dict(DwSecret, response.get("result", {}))

    def register_secret(
        self,
        cluster_id: str,
        secret_name: str,
        secret_provider_key: str,
        azure_vault_name: Optional[str] = None,
    ) -> DwSecret:
        """
        Register a reference to a secret stored in the cloud provider's vault.

        Unlike C(create_secret) (which stores the secret value in the cluster's
        Kubernetes metadata), this registers metadata that references a secret
        already held in the cloud provider's vault. The two approaches are
        mutually exclusive.

        Args:
            cluster_id: The ID of the cluster
            secret_name: The name of the secret
            secret_provider_key: The key of the secret in the cloud provider's vault
            azure_vault_name: The name of the Azure Key Vault (required for Azure)

        Returns:
            DwSecret dataclass instance of the registered secret
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "secretName": secret_name,
            "secretProviderKey": secret_provider_key,
        }
        if azure_vault_name is not None:
            data["azureVaultName"] = azure_vault_name
        response = self.api_client.post(
            "/api/v1/dw/registerSecret",
            data=data,
        )
        return from_dict(DwSecret, response.get("result", {}))

    def delete_secret(self, cluster_id: str, secret_name: str) -> None:
        """
        Delete a secret from a CDW cluster.

        Args:
            cluster_id: The ID of the cluster
            secret_name: The name of the secret to delete
        """
        self.api_client.post(
            "/api/v1/dw/deleteSecret",
            json_data={
                "clusterId": cluster_id,
                "secretName": secret_name,
            },
            squelch={404: {}},
        )

    # ========================================================================
    # Cluster Methods
    # ========================================================================

    def describe_cluster(self, cluster_id: str) -> Optional[ClusterSummary]:
        """
        Describe a Data Warehouse cluster.

        Args:
            cluster_id: The ID of the cluster

        Returns:
            ClusterSummary dataclass instance, or None if not found
        """
        response = self.api_client.post(
            "/api/v1/dw/describeCluster",
            data={"clusterId": cluster_id},
            squelch={404: None},
        )
        if response is None:
            return None
        cluster = response.get("cluster")
        return from_dict(ClusterSummary, cluster) if cluster else None

    def list_clusters(
        self,
        env_crn: Optional[str] = None,
    ) -> List[ClusterSummary]:
        """
        List Data Warehouse clusters.

        Args:
            env_crn: Optional environment CRN to filter by

        Returns:
            List of ClusterSummary dataclass instances
        """
        data: Dict[str, Any] = {}
        if env_crn is not None:
            data["environmentCrn"] = env_crn
        response = self.api_client.post(
            "/api/v1/dw/listClusters",
            data=data,
            squelch={404: {"clusters": []}},
        )
        return [from_dict(ClusterSummary, c) for c in response.get("clusters", [])]

    def get_cluster_by_name(
        self,
        name: str,
        env_crn: Optional[str] = None,
    ) -> Optional[ClusterSummary]:
        """
        Get a Data Warehouse cluster by name.

        Args:
            name: The cluster name
            env_crn: Optional environment CRN to narrow the search

        Returns:
            ClusterSummary dataclass instance, or None if not found
        """
        clusters = self.list_clusters(env_crn=env_crn)
        for cluster in clusters:
            if cluster.name == name:
                return cluster
        return None

    def create_aws_cluster(
        self,
        env_crn: str,
        use_overlay_network: Optional[bool] = None,
        use_private_load_balancer: Optional[bool] = None,
        use_public_worker_node: Optional[bool] = None,
        lb_subnet_ids: Optional[List[str]] = None,
        worker_subnet_ids: Optional[List[str]] = None,
        custom_subdomain: Optional[str] = None,
        database_backup_retention_period: Optional[int] = None,
        whitelist_workload_access_ip_cidrs: Optional[List[str]] = None,
        whitelist_k8s_cluster_access_ip_cidrs: Optional[List[str]] = None,
        custom_ami_id: Optional[str] = None,
        enable_private_eks: Optional[bool] = None,
        enable_spot_instances: Optional[bool] = None,
        reduced_permission_mode: Optional[bool] = None,
        node_role_cdw_managed_policy_arn: Optional[str] = None,
        custom_registry_options: Optional[Dict[str, Any]] = None,
        non_transparent_proxy: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a Data Warehouse cluster on AWS.

        Args:
            env_crn: The CRN of the environment
            use_overlay_network: Use overlay network
            use_private_load_balancer: Use a private load balancer
            use_public_worker_node: Use public worker nodes
            lb_subnet_ids: Load balancer subnet IDs
            worker_subnet_ids: Worker node subnet IDs
            custom_subdomain: Custom subdomain
            database_backup_retention_period: Database backup retention in days
            whitelist_workload_access_ip_cidrs: Workload access IP CIDRs
            whitelist_k8s_cluster_access_ip_cidrs: K8s cluster access IP CIDRs
            custom_ami_id: Custom AMI ID for cluster nodes
            enable_private_eks: Enable private EKS mode
            enable_spot_instances: Enable spot instances
            reduced_permission_mode: Use reduced IAM permissions
            node_role_cdw_managed_policy_arn: Managed policy ARN for the node role
            custom_registry_options: Custom ACR/ECR registry options
            non_transparent_proxy: Non-transparent proxy settings

        Returns:
            The ID of the created cluster
        """
        data: Dict[str, Any] = {"environmentCrn": env_crn}
        optional = {
            "useOverlayNetwork": use_overlay_network,
            "usePrivateLoadBalancer": use_private_load_balancer,
            "usePublicWorkerNode": use_public_worker_node,
            "lbSubnetIds": lb_subnet_ids,
            "workerSubnetIds": worker_subnet_ids,
            "customSubdomain": custom_subdomain,
            "databaseBackupRetentionPeriod": database_backup_retention_period,
            "whitelistWorkloadAccessIpCIDRs": whitelist_workload_access_ip_cidrs,
            "whitelistK8sClusterAccessIpCIDRs": whitelist_k8s_cluster_access_ip_cidrs,
            "customAmiId": custom_ami_id,
            "enablePrivateEKS": enable_private_eks,
            "enableSpotInstances": enable_spot_instances,
            "reducedPermissionMode": reduced_permission_mode,
            "nodeRoleCDWManagedPolicyArn": node_role_cdw_managed_policy_arn,
            "customRegistryOptions": custom_registry_options,
            "nonTransparentProxy": non_transparent_proxy,
        }
        data.update({k: v for k, v in optional.items() if v is not None})
        response = self.api_client.post(
            "/api/v1/dw/createAwsCluster",
            data=data,
        )
        return response["clusterId"]

    def create_azure_cluster(
        self,
        env_crn: str,
        subnet_name: str,
        user_assigned_managed_identity: str,
        use_overlay_networking: Optional[bool] = None,
        use_internal_load_balancer: Optional[bool] = None,
        enable_az: Optional[bool] = None,
        enable_private_aks: Optional[bool] = None,
        enable_private_sql: Optional[bool] = None,
        enable_spot_instances: Optional[bool] = None,
        log_analytics_workspace_id: Optional[str] = None,
        outbound_type: Optional[str] = None,
        private_dns_zone_aks: Optional[str] = None,
        private_dns_zone_sql: Optional[str] = None,
        private_sql_subnet_name: Optional[str] = None,
        aks_pod_cidr: Optional[str] = None,
        custom_subdomain: Optional[str] = None,
        database_backup_retention_period: Optional[int] = None,
        whitelist_workload_access_ip_cidrs: Optional[List[str]] = None,
        whitelist_k8s_cluster_access_ip_cidrs: Optional[List[str]] = None,
        custom_registry_options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a Data Warehouse cluster on Azure.

        Args:
            env_crn: The CRN of the environment
            subnet_name: Azure subnet name
            user_assigned_managed_identity: AKS managed identity resource ID
            use_overlay_networking: Use overlay networking
            use_internal_load_balancer: Use an internal load balancer
            enable_az: Enable availability zones
            enable_private_aks: Enable private AKS
            enable_private_sql: Enable private SQL
            enable_spot_instances: Enable spot instances
            log_analytics_workspace_id: Log Analytics workspace ID
            outbound_type: Network outbound type
            private_dns_zone_aks: Private DNS zone for AKS
            private_dns_zone_sql: Private DNS zone for SQL
            private_sql_subnet_name: Private SQL subnet name
            aks_pod_cidr: AKS pod CIDR
            custom_subdomain: Custom subdomain
            database_backup_retention_period: Database backup retention in days
            whitelist_workload_access_ip_cidrs: Workload access IP CIDRs
            whitelist_k8s_cluster_access_ip_cidrs: K8s cluster access IP CIDRs
            custom_registry_options: Custom ACR/ECR registry options

        Returns:
            The ID of the created cluster
        """
        data: Dict[str, Any] = {
            "environmentCrn": env_crn,
            "subnetName": subnet_name,
            "userAssignedManagedIdentity": user_assigned_managed_identity,
        }
        optional = {
            "useOverlayNetworking": use_overlay_networking,
            "useInternalLoadBalancer": use_internal_load_balancer,
            "enableAZ": enable_az,
            "enablePrivateAks": enable_private_aks,
            "enablePrivateSQL": enable_private_sql,
            "enableSpotInstances": enable_spot_instances,
            "logAnalyticsWorkspaceId": log_analytics_workspace_id,
            "outboundType": outbound_type,
            "privateDNSZoneAKS": private_dns_zone_aks,
            "privateDNSZoneSQL": private_dns_zone_sql,
            "privateSQLSubnetName": private_sql_subnet_name,
            "aksPodCIDR": aks_pod_cidr,
            "customSubdomain": custom_subdomain,
            "databaseBackupRetentionPeriod": database_backup_retention_period,
            "whitelistWorkloadAccessIpCIDRs": whitelist_workload_access_ip_cidrs,
            "whitelistK8sClusterAccessIpCIDRs": whitelist_k8s_cluster_access_ip_cidrs,
            "customRegistryOptions": custom_registry_options,
        }
        data.update({k: v for k, v in optional.items() if v is not None})
        response = self.api_client.post(
            "/api/v1/dw/createAzureCluster",
            data=data,
        )
        return response["clusterId"]

    def create_private_cluster(
        self,
        env_crn: str,
        storage_class: Optional[str] = None,
        db_client_credentials: Optional[Dict[str, str]] = None,
        custom_kerberos_principal_hostname: Optional[str] = None,
    ) -> str:
        """
        Create a Data Warehouse cluster on Private Cloud.

        Args:
            env_crn: The CRN of the environment
            storage_class: Storage class for the cluster
            db_client_credentials: Dict with 'certificate' and 'privateKey' keys
            custom_kerberos_principal_hostname: Custom Kerberos principal hostname

        Returns:
            The ID of the created cluster
        """
        data: Dict[str, Any] = {"environmentCrn": env_crn}
        optional: Dict[str, Any] = {
            "storageClass": storage_class,
            "dbClientCredentials": db_client_credentials,
            "customKerberosPrincipalHostname": custom_kerberos_principal_hostname,
        }
        data.update({k: v for k, v in optional.items() if v is not None})
        response = self.api_client.post(
            "/api/v1/dw/createPrivateCluster",
            data=data,
        )
        return response["clusterId"]

    def delete_cluster(
        self,
        cluster_id: str,
        force: bool = False,
    ) -> None:
        """
        Delete a Data Warehouse cluster.

        Args:
            cluster_id: The ID of the cluster to delete
            force: Force delete even if errors occur
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}
        if force:
            data["force"] = True
        self.api_client.post(
            "/api/v1/dw/deleteCluster",
            data=data,
            squelch={404: {}},
        )

    def wait_for_cluster_state(
        self,
        cluster_id: str,
        target_statuses: Set[str],
        error_statuses: Set[str] = DW_CLUSTER_FAILED_STATUSES,
        timeout: int = 3600,
        delay: int = 15,
    ) -> Optional[ClusterSummary]:
        """
        Poll a Data Warehouse cluster until it reaches a target status.

        Args:
            cluster_id: The ID of the cluster
            target_statuses: Set of acceptable target statuses
            error_statuses: Statuses treated as non-recoverable failures
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            ClusterSummary when a target status is reached, or None if the
            cluster is no longer visible (fully deleted).

        Raises:
            CdpError: If the timeout is reached or the cluster enters an error
                status.
        """
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for DW cluster to reach {target_statuses} "
                    f"after {timeout} seconds.",
                )

            cluster = self.describe_cluster(cluster_id)

            if cluster is None:
                return None

            current_status = cluster.status

            if current_status in target_statuses:
                return cluster

            if current_status in error_statuses:
                raise CdpError(
                    f"DW cluster entered failed status '{current_status}'.",
                )

            time.sleep(delay)
