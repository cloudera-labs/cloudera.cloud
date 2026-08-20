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


from typing import Any, Dict, List, Optional, Tuple
import time
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


def check_service_updates(
    cluster_id: str,
    service_details: Dict[str, Any],
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
        service_details: Current ServiceDescription dict from describe_service
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
    resources = service_details.get("resources", {}) or {}
    all_purpose_resources = resources.get("allPurposeInstanceGroupDetails", {}) or {}
    updates = {}

    if minimum_instances is not None:
        if int(resources.get("min_instances") or 0) != minimum_instances:
            updates["minimum_instances"] = minimum_instances

    if maximum_instances is not None:
        if int(resources.get("max_instances") or 0) != maximum_instances:
            updates["maximum_instances"] = maximum_instances

    if minimum_spot_instances is not None:
        if int(resources.get("min_spot_instances") or 0) != minimum_spot_instances:
            updates["minimum_spot_instances"] = minimum_spot_instances

    if maximum_spot_instances is not None:
        if int(resources.get("max_spot_instances") or 0) != maximum_spot_instances:
            updates["maximum_spot_instances"] = maximum_spot_instances

    if whitelist_ips is not None:
        current_raw = service_details.get("whitelistIps", "") or ""
        current_ips = {ip.strip() for ip in current_raw.split(",") if ip.strip()}
        if current_ips != set(whitelist_ips):
            updates["whitelist_ips"] = whitelist_ips

    if loadbalancer_allowlist is not None:
        current_raw = service_details.get("loadbalancerAllowlist", "") or ""
        current_lb = {ip.strip() for ip in current_raw.split(",") if ip.strip()}
        if current_lb != set(loadbalancer_allowlist):
            updates["loadbalancer_allowlist"] = loadbalancer_allowlist

    if all_purpose_minimum_instances is not None:
        if (
            int(all_purpose_resources.get("min_instances") or 0)
            != all_purpose_minimum_instances
        ):
            updates["all_purpose_minimum_instances"] = all_purpose_minimum_instances

    if all_purpose_maximum_instances is not None:
        if (
            int(all_purpose_resources.get("max_instances") or 0)
            != all_purpose_maximum_instances
        ):
            updates["all_purpose_maximum_instances"] = all_purpose_maximum_instances

    if all_purpose_minimum_spot_instances is not None:
        if (
            int(all_purpose_resources.get("min_spot_instances") or 0)
            != all_purpose_minimum_spot_instances
        ):
            updates["all_purpose_minimum_spot_instances"] = (
                all_purpose_minimum_spot_instances
            )

    if all_purpose_maximum_spot_instances is not None:
        if (
            int(all_purpose_resources.get("max_spot_instances") or 0)
            != all_purpose_maximum_spot_instances
        ):
            updates["all_purpose_maximum_spot_instances"] = (
                all_purpose_maximum_spot_instances
            )

    if updates:
        updates["cluster_id"] = cluster_id
        return updates
    return {}


class CdpDeClient:
    """CDP Data Engineering API client."""

    # Service statuses that indicate a healthy running service (can be disabled)
    REMOVABLE_STATUSES = ["ClusterCreationCompleted"]

    # Service statuses that indicate the service has been fully deleted
    STOPPED_STATUSES = ["ClusterDeletionCompleted"]

    # Service statuses indicating active deletion is in progress
    TERMINATION_STATUSES = ["ClusterDeletionInProgress"]

    # Virtual cluster statuses that indicate the VC is active and can be deleted
    VC_REMOVABLE_STATUSES = {"AppInstalled"}

    # Virtual cluster statuses that indicate the VC has been deleted or is being deleted
    VC_STOPPED_STATUSES = {"AppDeleted", "AppDeletionInProgress"}

    # Service statuses that indicate a non-recoverable failure
    FAILED_STATUSES = {
        "ClusterDNSDeletionFailed",
        "ClusterChartDeletionFailed",
        "ClusterServiceMeshDeletionFailed",
        "ClusterTLSCertDeletionFailed",
        "DBDeletionFailed",
        "FSMountTargetsDeletionFailed",
        "FSDeletionFailed",
        "ClusterNamespaceDeletionFailed",
        "ClusterAccessGroupDeletionFailed",
        "ClusterDeletionFailed",
        "ClusterUpgradeFailed",
    }

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
    ) -> Dict[str, Any]:
        """
        List Data Engineering services.

        Args:
            remove_deleted: Filter out deleted CDE services from the list.
            env_name: Optional environment name to filter services by.

        Returns:
            Dictionary containing:
                - services: List of service summary objects.
        """
        data: Dict[str, Any] = {"removeDeleted": remove_deleted}

        result = self.api_client.post(
            "/api/v1/de/listServices",
            data=data,
            squelch={404: {"services": []}},
        )

        if env_name:
            services = result.get("services", [])
            result["services"] = [
                s for s in services if s.get("environmentName") == env_name
            ]

        return result

    def describe_service(self, cluster_id: str) -> Dict[str, Any]:
        """
        Describe a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            Dictionary containing service details, or empty dict if not found
        """
        return self.api_client.post(
            "/api/v1/de/describeService",
            data={"clusterId": cluster_id},
            squelch={404: {}},
        )

    def get_service_by_name(
        self,
        name: str,
        env_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get service details by service name, optionally filtered by environment.

        Args:
            name: The service name
            env_name: Optional environment name to narrow the search

        Returns:
            Full describe result dict or None if not found
        """
        services = self.list_services(env_name=env_name)
        for service in services.get("services", []):
            if service.get("name") == name:
                cluster_id = service.get("clusterId")
                if cluster_id:
                    result = self.describe_service(cluster_id)
                    if result and result.get("service"):
                        return result
        return None

    def get_service_by_cluster_id(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get service details by cluster ID.

        Args:
            cluster_id: The cluster ID

        Returns:
            Full describe result dict or None if not found
        """
        result = self.describe_service(cluster_id)
        if not result or not result.get("service"):
            return None
        return result

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
    ) -> Dict[str, Any]:
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
            Dictionary containing service details of the created service
        """
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
            data["azureVirtualClusterManagedIdentities"] = azure_virtual_cluster_managed_identities
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

        return self.api_client.post("/api/v1/de/enableService", data=data)

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

    def _get_service_state(
        self,
        cluster_id: str,
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Helper to get the current service status.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            Tuple of (status_string, service_details) or None if service not found
        """
        result = self.describe_service(cluster_id)
        if not result or not result.get("service"):
            # describeService returns 404 while a service is still terminating;
            # fall back to listServices to get the true current state.
            services = self.list_services()
            for svc in services.get("services", []):
                if svc.get("clusterId") == cluster_id:
                    return (svc.get("status"), svc)
            return None
        service = result["service"]
        return (service.get("status"), service)

    def wait_for_service_state(
        self,
        cluster_id: str,
        target_statuses: List[str],
        timeout: int = 7200,
        delay: int = 60,
        force: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a Data Engineering service to reach a target status.

        If target includes a stopped status, automatically initiates disablement
        when the service is in a removable state.

        Args:
            cluster_id: The cluster ID of the service
            target_statuses: List of acceptable target statuses
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds
            force: Whether to force disable (used when targeting stopped statuses)

        Returns:
            Service details dict when target status is reached, or None if service gone

        Raises:
            CdpError: If timeout is reached, service enters a failed status, or
                      disable cannot be initiated from the current status
        """
        start_time = time.time()

        if any(s in self.STOPPED_STATUSES for s in target_statuses):
            result = self._get_service_state(cluster_id)
            if result is None:
                return None

            current_status, service = result

            if current_status in self.REMOVABLE_STATUSES:
                self.disable_service(cluster_id, force=force)
            elif current_status in target_statuses:
                return service
            elif current_status in self.TERMINATION_STATUSES:
                pass  # Already disabling — proceed to wait loop
            else:
                raise CdpError(
                    f"Cannot disable DE service in status '{current_status}'. "
                    f"Service must be in one of {self.REMOVABLE_STATUSES} to be disabled.",
                )

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for DE service to reach {target_statuses} "
                    f"after {timeout} seconds.",
                )

            result = self._get_service_state(cluster_id)

            if result is None:
                # Service no longer visible — treat as successfully stopped
                return None

            current_status, service = result

            if current_status in target_statuses:
                return service

            if current_status in self.FAILED_STATUSES:
                raise CdpError(
                    f"DE service entered failed status '{current_status}'.",
                )

            time.sleep(delay)

    # ========================================================================
    # Virtual Cluster Methods
    # ========================================================================

    def list_virtual_clusters(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        List virtual clusters in a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            List of virtual cluster summary objects
        """
        result = self.api_client.post(
            "/api/v1/de/listVcs",
            data={"clusterId": cluster_id},
            squelch={404: {"vcs": []}},
        )
        return result.get("vcs", [])

    def describe_virtual_cluster(
        self,
        cluster_id: str,
        vc_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Describe a virtual cluster.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID

        Returns:
            Virtual cluster details dict, or None if not found
        """
        result = self.api_client.post(
            "/api/v1/de/describeVc",
            data={"clusterId": cluster_id, "vcId": vc_id},
            squelch={404: None},
        )
        return result.get("vc") if result else None

    def get_virtual_cluster_by_name(
        self,
        cluster_id: str,
        vc_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get virtual cluster details by name.

        Args:
            cluster_id: The cluster ID of the service
            vc_name: The virtual cluster name

        Returns:
            Virtual cluster details dict, or None if not found
        """
        vcs = self.list_virtual_clusters(cluster_id)
        for vc in vcs:
            if vc.get("vcName") == vc_name:
                vc_id = vc.get("vcId")
                if vc_id:
                    return self.describe_virtual_cluster(cluster_id, vc_id)
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
    ) -> Optional[Dict[str, Any]]:
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
            VcDescription dict for the created virtual cluster, or None on failure
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
        return result.get("Vc") if result else None

    def delete_virtual_cluster(
        self,
        cluster_id: str,
        vc_id: str,
    ) -> Dict[str, Any]:
        """
        Delete a virtual cluster.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID

        Returns:
            Dictionary containing deletion status
        """
        return self.api_client.post(
            "/api/v1/de/deleteVc",
            data={"clusterId": cluster_id, "vcId": vc_id},
        )

    def wait_for_vc_state(
        self,
        cluster_id: str,
        vc_id: str,
        target_statuses: List[str],
        timeout: int = 600,
        delay: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a virtual cluster to reach one of the target statuses.

        Args:
            cluster_id: The cluster ID of the service
            vc_id: The virtual cluster ID
            target_statuses: List of acceptable target statuses
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            Virtual cluster details dict when target status is reached,
            or None if the VC is no longer visible (fully deleted)

        Raises:
            CdpError: If timeout is reached before the target status is achieved
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
            if vc.get("status") in target_statuses:
                return vc
            time.sleep(delay)
