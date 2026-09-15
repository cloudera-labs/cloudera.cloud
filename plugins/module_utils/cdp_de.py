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
A REST client for the Cloudera on Cloud Platform (CDP) Data Engineering API
"""

import time
import re

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
)


@dataclass
class AllPurposeInstanceGroupDetails:
    """Resource details of the All Purpose Instance Group of a CDE Service.

    Field names are the snake_case keys returned by the DE API.
    """

    instance_type: Union[str, None, NULLABLE] = NULLABLE
    min_instances: Union[str, None, NULLABLE] = NULLABLE
    max_instances: Union[str, None, NULLABLE] = NULLABLE
    min_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    max_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    initial_instances: Union[str, None, NULLABLE] = NULLABLE
    initial_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    root_vol_size: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ServiceResources:
    """Resource details of a CDE Service.

    Field names are the snake_case keys returned by the DE API, except the
    nested ``allPurposeInstanceGroupDetails`` which is camelCase.
    """

    instance_type: Union[str, None, NULLABLE] = NULLABLE
    min_instances: Union[str, None, NULLABLE] = NULLABLE
    max_instances: Union[str, None, NULLABLE] = NULLABLE
    min_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    max_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    initial_instances: Union[str, None, NULLABLE] = NULLABLE
    initial_spot_instances: Union[str, None, NULLABLE] = NULLABLE
    root_vol_size: Union[str, None, NULLABLE] = NULLABLE
    allPurposeInstanceGroupDetails: Union[
        AllPurposeInstanceGroupDetails,
        None,
        NULLABLE,
    ] = NULLABLE


@dataclass
class ServiceSummary:
    """Summary of a CDE Service as returned by ``listServices``."""

    clusterId: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    environmentName: Union[str, None, NULLABLE] = NULLABLE
    environmentCrn: Union[str, None, NULLABLE] = NULLABLE
    cloudPlatform: Union[str, None, NULLABLE] = NULLABLE
    clusterFqdn: Union[str, None, NULLABLE] = NULLABLE
    creatorEmail: Union[str, None, NULLABLE] = NULLABLE
    creatorCrn: Union[str, None, NULLABLE] = NULLABLE
    enablingTime: Union[str, None, NULLABLE] = NULLABLE
    tenantId: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ServiceDescription:
    """Full description of a CDE Service as returned by ``describeService``."""

    clusterId: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    environmentName: Union[str, None, NULLABLE] = NULLABLE
    environmentCrn: Union[str, None, NULLABLE] = NULLABLE
    cloudPlatform: Union[str, None, NULLABLE] = NULLABLE
    clusterFqdn: Union[str, None, NULLABLE] = NULLABLE
    creatorEmail: Union[str, None, NULLABLE] = NULLABLE
    creatorCrn: Union[str, None, NULLABLE] = NULLABLE
    enablingTime: Union[str, None, NULLABLE] = NULLABLE
    resources: Union[ServiceResources, None, NULLABLE] = NULLABLE
    tenantId: Union[str, None, NULLABLE] = NULLABLE
    logLocation: Union[str, None, NULLABLE] = NULLABLE
    whitelistIps: Union[str, None, NULLABLE] = NULLABLE
    loadbalancerAllowlist: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class VcSummary:
    """Summary of a Virtual Cluster as returned by ``listVcs``."""

    vcId: Union[str, None, NULLABLE] = NULLABLE
    vcName: Union[str, None, NULLABLE] = NULLABLE
    clusterId: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class VcDescription:
    """Full description of a Virtual Cluster as returned by ``describeVc``."""

    vcId: Union[str, None, NULLABLE] = NULLABLE
    vcName: Union[str, None, NULLABLE] = NULLABLE
    clusterId: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    vcTier: Union[str, None, NULLABLE] = NULLABLE
    sparkVersion: Union[str, None, NULLABLE] = NULLABLE
    creatorEmail: Union[str, None, NULLABLE] = NULLABLE
    creatorCrn: Union[str, None, NULLABLE] = NULLABLE
    vcApiUrl: Union[str, None, NULLABLE] = NULLABLE
    accessControl: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    resources: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


def _coerce_int(value: Any) -> int:
    """Coerce a dataclass field to int, treating NULLABLE/None/empty as 0."""
    if value is NULLABLE or value is None or value == "":
        return 0
    return int(value)


def _coerce_str(value: Any) -> str:
    """Coerce a dataclass field to str, treating NULLABLE/None as empty."""
    if value is NULLABLE or value is None:
        return ""
    return value


def check_service_updates(
    cluster_id: str,
    service_details: "ServiceDescription",
    minimum_instances: Optional[int] = None,
    maximum_instances: Optional[int] = None,
    minimum_spot_instances: Optional[int] = None,
    maximum_spot_instances: Optional[int] = None,
    whitelist_ips: Optional[List[str]] = None,
    loadbalancer_allowlist: Optional[List[str]] = None,
    all_purpose_minimum_instances: Optional[int] = None,
    all_purpose_maximum_instances: Optional[int] = None,
    all_purpose_minimum_spot_instances: Optional[int] = None,
    all_purpose_maximum_spot_instances: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Determine if a CDE service requires an update.

    Compares desired configuration against the current service state and returns
    update parameters if any differences are detected.

    Args:
        cluster_id: The cluster ID of the service
        service_details: Current ServiceDescription from describe_service
        minimum_instances: Desired minimum number of instances
        maximum_instances: Desired maximum number of instances
        minimum_spot_instances: Desired minimum number of spot instances
        maximum_spot_instances: Desired maximum number of spot instances
        whitelist_ips: Desired list of CIDRs for Kubernetes API access
        loadbalancer_allowlist: Desired list of CIDRs for load balancer access
        all_purpose_minimum_instances: Desired minimum instances for the All Purpose Instance Group
        all_purpose_maximum_instances: Desired maximum instances for the All Purpose Instance Group
        all_purpose_minimum_spot_instances: Desired minimum spot instances for the All Purpose Instance Group
        all_purpose_maximum_spot_instances: Desired maximum spot instances for the All Purpose Instance Group

    Returns:
        Dict of update parameters including cluster_id if changes detected, else empty dict
    """
    resources = service_details.resources
    if not isinstance(resources, ServiceResources):
        resources = ServiceResources()
    all_purpose_resources = resources.allPurposeInstanceGroupDetails
    if not isinstance(all_purpose_resources, AllPurposeInstanceGroupDetails):
        all_purpose_resources = AllPurposeInstanceGroupDetails()
    updates = {}

    if minimum_instances is not None:
        if _coerce_int(resources.min_instances) != minimum_instances:
            updates["minimum_instances"] = minimum_instances

    if maximum_instances is not None:
        if _coerce_int(resources.max_instances) != maximum_instances:
            updates["maximum_instances"] = maximum_instances

    if minimum_spot_instances is not None:
        if _coerce_int(resources.min_spot_instances) != minimum_spot_instances:
            updates["minimum_spot_instances"] = minimum_spot_instances

    if maximum_spot_instances is not None:
        if _coerce_int(resources.max_spot_instances) != maximum_spot_instances:
            updates["maximum_spot_instances"] = maximum_spot_instances

    if whitelist_ips is not None:
        current_raw = _coerce_str(service_details.whitelistIps)
        current_ips = {ip.strip() for ip in current_raw.split(",") if ip.strip()}
        if current_ips != set(whitelist_ips):
            updates["whitelist_ips"] = whitelist_ips

    if loadbalancer_allowlist is not None:
        current_raw = _coerce_str(service_details.loadbalancerAllowlist)
        current_lb = {ip.strip() for ip in current_raw.split(",") if ip.strip()}
        if current_lb != set(loadbalancer_allowlist):
            updates["loadbalancer_allowlist"] = loadbalancer_allowlist

    if all_purpose_minimum_instances is not None:
        if (
            _coerce_int(all_purpose_resources.min_instances)
            != all_purpose_minimum_instances
        ):
            updates["all_purpose_minimum_instances"] = all_purpose_minimum_instances

    if all_purpose_maximum_instances is not None:
        if (
            _coerce_int(all_purpose_resources.max_instances)
            != all_purpose_maximum_instances
        ):
            updates["all_purpose_maximum_instances"] = all_purpose_maximum_instances

    if all_purpose_minimum_spot_instances is not None:
        if (
            _coerce_int(all_purpose_resources.min_spot_instances)
            != all_purpose_minimum_spot_instances
        ):
            updates["all_purpose_minimum_spot_instances"] = (
                all_purpose_minimum_spot_instances
            )

    if all_purpose_maximum_spot_instances is not None:
        if (
            _coerce_int(all_purpose_resources.max_spot_instances)
            != all_purpose_maximum_spot_instances
        ):
            updates["all_purpose_maximum_spot_instances"] = (
                all_purpose_maximum_spot_instances
            )

    if updates:
        updates["cluster_id"] = cluster_id
        return updates
    return {}


# """Service statuses that indicate a healthy running service (can be disabled)"""
CDE_SERVICE_REMOVABLE_STATUSES = {"ClusterCreationCompleted"}


# """Service statuses that indicate the service has been fully deleted"""
CDE_SERVICE_STOPPED_STATUSES = {"ClusterDeletionCompleted"}


# """Service statuses indicating active deletion is in progress"""
CDE_SERVICE_TERMINATION_STATUSES = {"ClusterDeletionInProgress"}


# """Service statuses that indicate a non-recoverable failure. These are every
# status mapped to the "Failed" external status in the CDP service status
# model, plus ClusterDeleteFromDBFailed (a terminal delete failure). The
# Maintenance/Upgrade/TLSCertRenewal failures are intentionally omitted: they
# map to the "Available" external status, i.e. the service remains usable."""
CDE_SERVICE_FAILED_STATUSES = {
    "ClusterAccessGroupCreationFailed",
    "ClusterAccessGroupDeletionFailed",
    "ClusterChartDeletionFailed",
    "ClusterChartInstallationFailed",
    "ClusterCreationFailed",
    "ClusterDeleteFromDBFailed",
    "ClusterDeletionFailed",
    "ClusterDNSCreationFailed",
    "ClusterDNSDeletionFailed",
    "ClusterIngressCreationFailed",
    "ClusterMonitoringConfigurationFailed",
    "ClusterNamespaceDeletionFailed",
    "ClusterProvisioningFailed",
    "ClusterServiceMeshDeletionFailed",
    "ClusterServiceMeshProvisioningFailed",
    "ClusterTLSCertCreationFailed",
    "ClusterTLSCertDeletionFailed",
    "ClusterUserSyncCheckFailed",
    "DBDeletionFailed",
    "DBProvisioningFailed",
    "FSDeletionFailed",
    "FSMountTargetsCreationFailed",
    "FSMountTargetsDeletionFailed",
    "FSProvisioningFailed",
}


# """Virtual cluster statuses that indicate the VC is active and can be deleted"""
CDE_VC_REMOVABLE_STATUSES = {"AppInstalled"}


# """Virtual cluster statuses that indicate the VC has been deleted"""
CDE_VC_STOPPED_STATUSES = {"AppDeleted", "AppNotDeletedFromDB"}


# """Virtual cluster statuses indicating active deletion is in progress"""
CDE_VC_TERMINATION_STATUSES = {"AppDeletionInitiated"}


# """Virtual cluster statuses that indicate a non-recoverable failure"""
CDE_VC_FAILED_STATUSES = {
    "AppDeletionFailed",
    "AppInstallationFailed",
}


class CdpDeClient:
    """CDP Data Engineering API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP Data Engineering client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    # ========================================================================
    # Service Management Methods
    # ========================================================================

    def list_services(
        self,
        remove_deleted: bool = True,
        env_name: Optional[str] = None,
    ) -> List[ServiceSummary]:
        """
        List Data Engineering services.

        Args:
            remove_deleted: Filter out deleted CDE services from the list.
            env_name: Optional environment name to filter services by.

        Returns:
            List of ServiceSummary objects.
        """
        data: Dict[str, Any] = {"removeDeleted": remove_deleted}

        result = self.api_client.post(
            "/api/v1/de/listServices",
            data=data,
            squelch={404: {"services": []}},
        )

        services = [from_dict(ServiceSummary, s) for s in result.get("services", [])]

        if env_name:
            services = [s for s in services if s.environmentName == env_name]

        return services

    def describe_service(self, cluster_id: str) -> Optional[ServiceDescription]:
        """
        Describe a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            ServiceDescription for the service, or None if not found
        """
        result = self.api_client.post(
            "/api/v1/de/describeService",
            data={"clusterId": cluster_id},
            squelch={404: {}},
        )
        service = result.get("service") if result else None
        return from_dict(ServiceDescription, service) if service else None

    def get_service_by_name(
        self,
        name: str,
        env_name: Optional[str] = None,
    ) -> Optional[ServiceDescription]:
        """
        Get service details by service name, optionally filtered by environment.

        Args:
            name: The service name
            env_name: Optional environment name to narrow the search

        Returns:
            ServiceDescription or None if not found
        """
        services = self.list_services(env_name=env_name)
        for service in services:
            if service.name == name and service.clusterId:
                return self.describe_service(service.clusterId)
        return None

    def enable_service(
        self,
        name: str,
        env: str,
        instance_type: str,
        minimum_instances: int,
        maximum_instances: int,
        minimum_spot_instances: Optional[int] = None,
        maximum_spot_instances: Optional[int] = None,
        enable_public_endpoint: Optional[bool] = None,
        enable_private_network: Optional[bool] = None,
        enable_workload_analytics: Optional[bool] = None,
        initial_instances: Optional[int] = None,
        initial_spot_instances: Optional[int] = None,
        root_volume_size: Optional[int] = None,
        chart_value_overrides: Optional[List[Dict[str, Any]]] = None,
        loadbalancer_allowlist: Optional[List[str]] = None,
        whitelist_ips: Optional[List[str]] = None,
        skip_validation: Optional[bool] = None,
        use_ssd: Optional[bool] = None,
        tags: Optional[Dict[str, str]] = None,
        resource_pool: Optional[str] = None,
        cpu_requests: Optional[str] = None,
        memory_requests: Optional[str] = None,
        gpu_requests: Optional[str] = None,
        subnets: Optional[List[str]] = None,
        network_outbound_type: Optional[str] = None,
        deploy_previous_version: Optional[bool] = None,
        disable_arm64: Optional[bool] = None,
        azure_database_private_dns_zone_id: Optional[str] = None,
        azure_fileshare_private_dns_zone_id: Optional[str] = None,
        azure_service_managed_identity: Optional[str] = None,
        azure_virtual_cluster_managed_identities: Optional[str] = None,
        custom_azure_files_configs: Optional[Dict[str, Any]] = None,
        all_purpose_minimum_instances: Optional[int] = None,
        all_purpose_maximum_instances: Optional[int] = None,
        all_purpose_minimum_spot_instances: Optional[int] = None,
        all_purpose_maximum_spot_instances: Optional[int] = None,
        all_purpose_initial_instances: Optional[int] = None,
        all_purpose_initial_spot_instances: Optional[int] = None,
        all_purpose_instance_type: Optional[str] = None,
        all_purpose_root_volume_size: Optional[int] = None,
    ) -> Optional[ServiceDescription]:
        """
        Enable a Data Engineering service.

        Args:
            name: Name of the CDE service
            env: CDP environment name
            instance_type: Instance type for the cluster nodes
            minimum_instances: Minimum number of instances (required)
            maximum_instances: Maximum number of instances (required)
            minimum_spot_instances: Minimum number of spot instances
            maximum_spot_instances: Maximum number of spot instances
            enable_public_endpoint: Create endpoint in a publicly accessible subnet
            enable_private_network: Create a fully private CDE instance
            enable_workload_analytics: Send diagnostic information to Workload Manager
            initial_instances: Initial instances when service is enabled
            initial_spot_instances: Initial spot instances when service is enabled
            root_volume_size: EBS volume size in GB
            chart_value_overrides: Chart overrides for the service
            loadbalancer_allowlist: CIDRs allowed to access the load balancer
            whitelist_ips: CIDRs allowed to access the Kubernetes master API server
            skip_validation: Skip validation check
            use_ssd: Use instance local storage for workload filesystem
            tags: User defined labels for provisioned cloud resources
            resource_pool: Resource pool (Private Cloud only)
            cpu_requests: CPU request quota (Private Cloud only)
            memory_requests: Memory request quota (Private Cloud only)
            gpu_requests: GPU request quota (Private Cloud only)

        Returns:
            ServiceDescription of the created service, or None if the response
            contained no service details
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9\-\.]+[a-zA-Z0-9]$", name):
            raise ValueError(
                f"Invalid service name: {name}. Must match regex: ^[a-zA-Z][a-zA-Z0-9\-\.]+[a-zA-Z0-9]$",
            )

        data: Dict[str, Any] = {
            "name": name,
            "env": env,
            "instanceType": instance_type,
            "minimumInstances": minimum_instances,
            "maximumInstances": maximum_instances,
        }

        if minimum_spot_instances is not None:
            data["minimumSpotInstances"] = minimum_spot_instances
        if maximum_spot_instances is not None:
            data["maximumSpotInstances"] = maximum_spot_instances
        if enable_public_endpoint is not None:
            data["enablePublicEndpoint"] = enable_public_endpoint
        if enable_private_network is not None:
            data["enablePrivateNetwork"] = enable_private_network
        if enable_workload_analytics is not None:
            data["enableWorkloadAnalytics"] = enable_workload_analytics
        if initial_instances is not None:
            data["initialInstances"] = initial_instances
        if initial_spot_instances is not None:
            data["initialSpotInstances"] = initial_spot_instances
        if root_volume_size is not None:
            data["rootVolumeSize"] = root_volume_size
        if chart_value_overrides is not None:
            data["chartValueOverrides"] = chart_value_overrides
        if loadbalancer_allowlist is not None:
            data["loadbalancerAllowlist"] = loadbalancer_allowlist
        if whitelist_ips is not None:
            data["whitelistIps"] = whitelist_ips
        if skip_validation is not None:
            data["skipValidation"] = skip_validation
        if use_ssd is not None:
            data["useSsd"] = use_ssd
        if tags is not None:
            data["tags"] = tags
        if resource_pool is not None:
            data["resourcePool"] = resource_pool
        if cpu_requests is not None:
            data["cpuRequests"] = cpu_requests
        if memory_requests is not None:
            data["memoryRequests"] = memory_requests
        if gpu_requests is not None:
            data["gpuRequests"] = gpu_requests
        if subnets is not None:
            data["subnets"] = subnets
        if network_outbound_type is not None:
            data["networkOutboundType"] = network_outbound_type
        if deploy_previous_version is not None:
            data["deployPreviousVersion"] = deploy_previous_version
        if disable_arm64 is not None:
            data["disableArm64"] = disable_arm64
        if azure_database_private_dns_zone_id is not None:
            data["azureDatabasePrivateDNSZoneId"] = azure_database_private_dns_zone_id
        if azure_fileshare_private_dns_zone_id is not None:
            data["azureFilesharePrivateDNSZoneId"] = azure_fileshare_private_dns_zone_id
        if azure_service_managed_identity is not None:
            data["azureServiceManagedIdentity"] = azure_service_managed_identity
        if azure_virtual_cluster_managed_identities is not None:
            data["azureVirtualClusterManagedIdentities"] = (
                azure_virtual_cluster_managed_identities
            )
        if custom_azure_files_configs is not None:
            data["customAzureFilesConfigs"] = custom_azure_files_configs
        if all_purpose_minimum_instances is not None:
            data["allPurposeMinimumInstances"] = all_purpose_minimum_instances
        if all_purpose_maximum_instances is not None:
            data["allPurposeMaximumInstances"] = all_purpose_maximum_instances
        if all_purpose_minimum_spot_instances is not None:
            data["allPurposeMinimumSpotInstances"] = all_purpose_minimum_spot_instances
        if all_purpose_maximum_spot_instances is not None:
            data["allPurposeMaximumSpotInstances"] = all_purpose_maximum_spot_instances
        if all_purpose_initial_instances is not None:
            data["allPurposeInitialInstances"] = all_purpose_initial_instances
        if all_purpose_initial_spot_instances is not None:
            data["allPurposeInitialSpotInstances"] = all_purpose_initial_spot_instances
        if all_purpose_instance_type is not None:
            data["allPurposeInstanceType"] = all_purpose_instance_type
        if all_purpose_root_volume_size is not None:
            data["allPurposeRootVolumeSize"] = all_purpose_root_volume_size

        result = self.api_client.post("/api/v1/de/enableService", data=data)
        service = result.get("service") if result else None
        return from_dict(ServiceDescription, service) if service else None

    def disable_service(
        self,
        cluster_id: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Disable a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service
            force: Force disable even if errors occur during deletion

        Returns:
            Dictionary containing deletion status
        """
        return self.api_client.post(
            "/api/v1/de/disableService",
            data={"clusterId": cluster_id, "force": force},
        )

    def update_service(
        self,
        cluster_id: str,
        minimum_instances: Optional[int] = None,
        maximum_instances: Optional[int] = None,
        minimum_spot_instances: Optional[int] = None,
        maximum_spot_instances: Optional[int] = None,
        whitelist_ips: Optional[List[str]] = None,
        loadbalancer_allowlist: Optional[List[str]] = None,
        all_purpose_minimum_instances: Optional[int] = None,
        all_purpose_maximum_instances: Optional[int] = None,
        all_purpose_minimum_spot_instances: Optional[int] = None,
        all_purpose_maximum_spot_instances: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update a Data Engineering service configuration.

        Args:
            cluster_id: The cluster ID of the service to update
            minimum_instances: Updated minimum number of instances
            maximum_instances: Updated maximum number of instances
            minimum_spot_instances: Updated minimum number of spot instances
            maximum_spot_instances: Updated maximum number of spot instances
            whitelist_ips: Updated CIDRs for Kubernetes API access
            loadbalancer_allowlist: Updated CIDRs for load balancer access
            all_purpose_minimum_instances: Updated minimum instances for the All Purpose Instance Group
            all_purpose_maximum_instances: Updated maximum instances for the All Purpose Instance Group
            all_purpose_minimum_spot_instances: Updated minimum spot instances for the All Purpose Instance Group
            all_purpose_maximum_spot_instances: Updated maximum spot instances for the All Purpose Instance Group

        Returns:
            Dictionary containing the update operation status
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}

        if minimum_instances is not None:
            data["minimumInstances"] = minimum_instances
        if maximum_instances is not None:
            data["maximumInstances"] = maximum_instances
        if minimum_spot_instances is not None:
            data["minimumSpotInstances"] = minimum_spot_instances
        if maximum_spot_instances is not None:
            data["maximumSpotInstances"] = maximum_spot_instances
        if whitelist_ips is not None:
            data["whitelistIps"] = whitelist_ips
        if loadbalancer_allowlist is not None:
            data["loadbalancerAllowlist"] = loadbalancer_allowlist
        if all_purpose_minimum_instances is not None:
            data["allPurposeMinimumInstances"] = all_purpose_minimum_instances
        if all_purpose_maximum_instances is not None:
            data["allPurposeMaximumInstances"] = all_purpose_maximum_instances
        if all_purpose_minimum_spot_instances is not None:
            data["allPurposeMinimumSpotInstances"] = all_purpose_minimum_spot_instances
        if all_purpose_maximum_spot_instances is not None:
            data["allPurposeMaximumSpotInstances"] = all_purpose_maximum_spot_instances

        return self.api_client.post("/api/v1/de/updateService", data=data)

    def wait_for_service_state(
        self,
        cluster_id: str,
        target_statuses: Set[str],
        error_statuses: Set[str] = CDE_SERVICE_FAILED_STATUSES,
        timeout: int = 7200,
        delay: int = 60,
    ) -> Optional[ServiceDescription]:
        """
        Poll a Data Engineering service until it reaches a target status.

        This is a pure waiter: it does not initiate any action. The caller is
        responsible for enabling, disabling, or updating the service first; this
        method only observes the result.

        Args:
            cluster_id: The cluster ID of the service
            target_statuses: Set of acceptable target statuses
            error_statuses: Statuses treated as non-recoverable failures.
                Defaults to FAILED_STATUSES.
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            ServiceDescription when a target status is reached, or None if the
            service is no longer visible (fully deleted).

        Raises:
            CdpError: If the timeout is reached or the service enters an error status.
        """
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for DE service to reach {target_statuses} "
                    f"after {timeout} seconds.",
                )

            service = self.describe_service(cluster_id)

            if service is None:
                # Service no longer visible — treat as successfully stopped
                return None

            current_status = service.status

            if current_status in target_statuses:
                return service

            if current_status in error_statuses:
                raise CdpError(
                    f"DE service entered failed status '{current_status}'.",
                )

            time.sleep(delay)

    # ========================================================================
    # Virtual Cluster Methods
    # ========================================================================

    def list_virtual_clusters(self, cluster_id: str) -> List[VcSummary]:
        """
        List virtual clusters in a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            List of VcSummary objects
        """
        result = self.api_client.post(
            "/api/v1/de/listVcs",
            data={"clusterId": cluster_id},
            squelch={404: {"vcs": []}},
        )
        return [from_dict(VcSummary, vc) for vc in result.get("vcs", [])]

    def describe_virtual_cluster(
        self,
        cluster_id: str,
        vc_id: str,
    ) -> Optional[VcDescription]:
        """
        Describe a virtual cluster.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID

        Returns:
            VcDescription, or None if not found
        """
        result = self.api_client.post(
            "/api/v1/de/describeVc",
            data={"clusterId": cluster_id, "vcId": vc_id},
            squelch={404: None},
        )
        vc = result.get("vc") if result else None
        return from_dict(VcDescription, vc) if vc else None

    def get_virtual_cluster_by_name(
        self,
        cluster_id: str,
        vc_name: str,
    ) -> Optional[VcDescription]:
        """
        Get virtual cluster details by name.

        Args:
            cluster_id: The cluster ID of the service
            vc_name: The virtual cluster name

        Returns:
            VcDescription, or None if not found
        """
        vcs = self.list_virtual_clusters(cluster_id)
        for vc in vcs:
            if vc.vcName == vc_name and vc.vcId:
                return self.describe_virtual_cluster(cluster_id, vc.vcId)
        return None

    def create_virtual_cluster(
        self,
        name: str,
        cluster_id: str,
        cpu_requests: str,
        memory_requests: str,
        chart_value_overrides: Optional[List[Dict[str, Any]]] = None,
        runtime_spot_component: Optional[str] = None,
        spark_version: Optional[str] = None,
        acl_users: Optional[str] = None,
        vc_tier: Optional[str] = None,
        spark_os_name: Optional[str] = None,
        session_timeout: Optional[str] = None,
        spark_configs: Optional[Dict[str, str]] = None,
        full_access_users: Optional[List[str]] = None,
        full_access_groups: Optional[List[str]] = None,
        view_only_users: Optional[List[str]] = None,
        view_only_groups: Optional[List[str]] = None,
    ) -> Optional[VcDescription]:
        """
        Create a virtual cluster.

        Args:
            name: Name of the virtual cluster
            cluster_id: Cluster ID of the CDE service
            cpu_requests: CPU requests for autoscaling
            memory_requests: Memory requests for autoscaling (e.g. 30Gi)
            chart_value_overrides: Chart overrides for the virtual cluster
            runtime_spot_component: Where Driver and Executors run (ALL or NONE)
            spark_version: Spark version (e.g. SPARK3, SPARK3_5)
            acl_users: Comma-separated workload usernames granted access
            vc_tier: Virtual cluster tier (ALLP or CORE)
            spark_os_name: Spark OS image (SECURITYHARDENED or REDHAT)
            session_timeout: Default session timeout for ALLP tier
            spark_configs: Spark configs applied to all jobs in the VC
            full_access_users: Users with full access
            full_access_groups: Groups with full access
            view_only_users: Users with view-only access
            view_only_groups: Groups with view-only access

        Returns:
            VcDescription for the created virtual cluster, or None on failure
        """
        data: Dict[str, Any] = {
            "name": name,
            "clusterId": cluster_id,
            "cpuRequests": cpu_requests,
            "memoryRequests": memory_requests,
        }
        if chart_value_overrides is not None:
            data["chartValueOverrides"] = chart_value_overrides
        if runtime_spot_component is not None:
            data["runtimeSpotComponent"] = runtime_spot_component
        if spark_version is not None:
            data["sparkVersion"] = spark_version
        if acl_users is not None:
            data["aclUsers"] = acl_users
        if vc_tier is not None:
            data["vcTier"] = vc_tier
        if spark_os_name is not None:
            data["sparkOSName"] = spark_os_name
        if session_timeout is not None:
            data["sessionTimeout"] = session_timeout
        if spark_configs is not None:
            data["sparkConfigs"] = spark_configs
        if full_access_users is not None:
            data["fullAccessUsers"] = full_access_users
        if full_access_groups is not None:
            data["fullAccessGroups"] = full_access_groups
        if view_only_users is not None:
            data["viewOnlyUsers"] = view_only_users
        if view_only_groups is not None:
            data["viewOnlyGroups"] = view_only_groups

        result = self.api_client.post("/api/v1/de/createVc", data=data)
        vc = result.get("Vc") if result else None
        return from_dict(VcDescription, vc) if vc else None

    def delete_virtual_cluster(
        self,
        cluster_id: str,
        vc_id: str,
    ) -> None:
        """
        Delete a virtual cluster.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID

        Returns:
            None
        """
        return self.api_client.post(
            "/api/v1/de/deleteVc",
            data={"clusterId": cluster_id, "vcId": vc_id},
            squelch={200: None, 404: None},
        )

    def wait_for_vc_state(
        self,
        cluster_id: str,
        vc_id: str,
        target_statuses: Set[str],
        error_statuses: Set[str] = CDE_VC_FAILED_STATUSES,
        timeout: int = 1800,
        delay: int = 30,
    ) -> Optional[VcDescription]:
        """
        Poll a virtual cluster until it reaches one of the target statuses.

        This is a pure waiter: it does not initiate any action. The caller is
        responsible for creating or deleting the virtual cluster first; this
        method only observes the result.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID
            target_statuses: Set of acceptable target statuses
            error_statuses: Statuses treated as non-recoverable failures.
                Defaults to VC_FAILED_STATUSES.
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            VcDescription when a target status is reached, or None if the VC is
            no longer visible (fully deleted).

        Raises:
            CdpError: If the timeout is reached or the VC enters an error status.
        """
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for virtual cluster to reach {target_statuses} "
                    f"after {timeout} seconds.",
                )
            vc = self.describe_virtual_cluster(cluster_id, vc_id)
            if vc is None:
                return None
            if vc.status in target_statuses:
                return vc
            if vc.status in error_statuses:
                raise CdpError(
                    f"Virtual cluster entered failed status '{vc.status}'.",
                )
            time.sleep(delay)
