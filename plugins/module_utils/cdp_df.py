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
A REST client for the Cloudera on Cloud Platform (CDP) DataFlow API
"""

from typing import Any, Dict, List, Optional, Tuple
import time
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


def check_service_updates(
    service_crn: str,
    service_details: Dict[str, Any],
    min_k8s_node_count: Optional[int] = None,
    max_k8s_node_count: Optional[int] = None,
    kubernetes_ip_cidr_blocks: Optional[List[str]] = None,
    load_balancer_ip_cidr_blocks: Optional[List[str]] = None,
    skip_preflight_checks: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Check if service updates are needed and build update parameters.

    Args:
        service_crn: The CRN of the service to update
        service_details: Current service details from API
        min_k8s_node_count: Desired minimum number of Kubernetes nodes
        max_k8s_node_count: Desired maximum number of Kubernetes nodes
        kubernetes_ip_cidr_blocks: Desired CIDR blocks for Kubernetes API access
        load_balancer_ip_cidr_blocks: Desired CIDR blocks for load balancer access
        skip_preflight_checks: Whether to skip pre-flight checks during update

    Returns:
        Dictionary of update parameters if changes are needed, empty dict otherwise
    """
    update_params = {"service_crn": service_crn}
    changes = []

    param_mappings = [
        (min_k8s_node_count, "minK8sNodeCount", "min_k8s_node_count"),
        (max_k8s_node_count, "maxK8sNodeCount", "max_k8s_node_count"),
    ]

    for desired_value, service_key, api_param in param_mappings:
        current_value = service_details.get(service_key)
        if desired_value is not None and desired_value != current_value:
            update_params[api_param] = desired_value
            changes.append(api_param)

    ip_range_mappings = [
        (
            kubernetes_ip_cidr_blocks,
            "kubeApiAuthorizedIpRanges",
            "kubernetes_ip_cidr_blocks",
        ),
        (
            load_balancer_ip_cidr_blocks,
            "loadBalancerAuthorizedIpRanges",
            "load_balancer_ip_cidr_blocks",
        ),
    ]

    for desired_ranges, service_key, api_param in ip_range_mappings:
        if desired_ranges is not None:
            current_ranges = service_details.get(service_key, [])
            if set(desired_ranges) != set(current_ranges):
                update_params[api_param] = desired_ranges
                changes.append(api_param)

    if skip_preflight_checks:
        update_params["skip_preflight_checks"] = skip_preflight_checks

    if changes:
        if "min_k8s_node_count" not in update_params:
            current_min = service_details.get("minK8sNodeCount")
            if current_min is not None:
                update_params["min_k8s_node_count"] = current_min
        if "max_k8s_node_count" not in update_params:
            current_max = service_details.get("maxK8sNodeCount")
            if current_max is not None:
                update_params["max_k8s_node_count"] = current_max

        return update_params
    else:
        return {}


class CdpDfClient:
    """CDP DataFlow API client."""

    # Service state constants
    FAILED_STATES = ["BAD_HEALTH", "UNKNOWN"]
    REMOVABLE_STATES = [
        "GOOD_HEALTH",
        "CONCERNING_HEALTH",
        "BAD_HEALTH",
        "UNKNOWN",
    ]
    TERMINATION_STATES = ["DISABLING"]
    DISABLED_STATES = ["NOT_ENABLED"]

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP DataFlow client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    # Service state constants
    FAILED_STATES = ["BAD_HEALTH", "UNKNOWN"]
    REMOVABLE_STATES = [
        "GOOD_HEALTH",
        "CONCERNING_HEALTH",
        "BAD_HEALTH",
        "UNKNOWN",
    ]
    TERMINATION_STATES = ["DISABLING"]
    DISABLED_STATES = ["NOT_ENABLED"]

    # ========================================================================
    # Service Management Methods
    # ========================================================================

    @CdpClient.paginated()
    def list_services(
        self,
        search_term: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
        sorts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        List DataFlow services.

        Args:
            search_term: Search term to filter by name
            pageToken: Pagination token for getting the next page
            pageSize: Number of results per page (1-100)
            sorts: Sort criteria

        Returns:
            Dictionary containing:
                - services: List of ServiceSummary objects
                - nextToken: Token for next page (if available)
        """
        data: Dict[str, Any] = {}
        if search_term is not None:
            data["searchTerm"] = search_term
        if pageToken is not None:
            data["startingToken"] = pageToken
        if pageSize is not None:
            data["pageSize"] = pageSize
        if sorts is not None:
            data["sorts"] = sorts

        return self.api_client.post(
            "/api/v1/df/listServices",
            data=data,
            squelch={404: {"services": []}},
        )

    def describe_service(self, crn: str) -> Dict[str, Any]:
        """
        Describe a DataFlow service.

        Args:
            crn: The CRN of the service

        Returns:
            Dictionary containing service details
        """
        data = {"serviceCrn": crn}
        return self.api_client.post(
            "/api/v1/df/describeService",
            data=data,
            squelch={404: {}},
        )

    def get_service_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get service details by environment name.

        Args:
            name: The environment name

        Returns:
            Service details dict, or None if not found or disabled
        """
        services = self.list_services(search_term=name)
        for service in services.get("services", []):
            if service.get("name") == name:
                if service.get("status", {}).get("state") in self.DISABLED_STATES:
                    return None
                return self.describe_service(service.get("crn"))
        return None

    def get_service_by_crn(self, crn: str) -> Optional[Dict[str, Any]]:
        """
        Get service details by service CRN.

        Args:
            crn: The service CRN

        Returns:
            Service details dict, or None if not found or disabled
        """
        services = self.list_services()
        for service in services.get("services", []):
            if service.get("crn") == crn:
                # Skip describe for disabled services (returns 500)
                if service.get("status", {}).get("state") in self.DISABLED_STATES:
                    return None
                return self.describe_service(crn)
        return None

    def get_service_by_env_crn(self, env_crn: str) -> Optional[Dict[str, Any]]:
        """
        Get service details by environment CRN.

        Args:
            env_crn: The environment CRN

        Returns:
            Service details dict, or None if not found or disabled
        """
        services = self.list_services()
        for service in services.get("services", []):
            if service.get("environmentCrn") == env_crn:
                # Skip describe for disabled services (returns 500)
                if service.get("status", {}).get("state") in self.DISABLED_STATES:
                    return None
                return self.describe_service(service.get("crn"))
        return None

    def enable_service(
        self,
        environment_crn: str,
        min_k8s_node_count: Optional[int] = None,
        max_k8s_node_count: Optional[int] = None,
        use_public_load_balancer: Optional[bool] = None,
        kubernetes_ip_cidr_blocks: Optional[List[str]] = None,
        load_balancer_ip_cidr_blocks: Optional[List[str]] = None,
        kubernetes_service_ip_cidr_blocks: Optional[List[str]] = None,
        cluster_subnet_ids: Optional[List[str]] = None,
        load_balancer_subnet_ids: Optional[List[str]] = None,
        persist_public_ip: Optional[bool] = None,
        private_cluster: Optional[bool] = None,
        pod_cidr: Optional[str] = None,
        service_cidr: Optional[str] = None,
        instance_type: Optional[str] = None,
        skip_preflight_checks: Optional[bool] = None,
        user_defined_routing: Optional[bool] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Enable DataFlow service for an environment.

        Args:
            environment_crn: The CRN of the environment
            min_k8s_node_count: Minimum number of Kubernetes nodes
            max_k8s_node_count: Maximum number of Kubernetes nodes
            use_public_load_balancer: Whether to use public load balancer
            kubernetes_ip_cidr_blocks: CIDR blocks for Kubernetes
            load_balancer_ip_cidr_blocks: CIDR blocks for load balancer
            kubernetes_service_ip_cidr_blocks: CIDR blocks for Kubernetes services
            cluster_subnet_ids: Subnet IDs for cluster
            load_balancer_subnet_ids: Subnet IDs for load balancer
            persist_public_ip: Whether to persist public IP
            private_cluster: Whether to create private cluster
            pod_cidr: CIDR range for pod IPs in Kubernetes cluster
            service_cidr: CIDR range for internal Kubernetes services
            instance_type: Custom instance type for Kubernetes nodes
            skip_preflight_checks: Whether to skip pre-flight checks
            user_defined_routing: Whether UDR mode is enabled (Azure AKS)
            tags: Tags to apply to service-related resources

        Returns:
            Dictionary containing service details
        """
        data: Dict[str, Any] = {"environmentCrn": environment_crn}

        if min_k8s_node_count is not None:
            data["minK8sNodeCount"] = min_k8s_node_count
        if max_k8s_node_count is not None:
            data["maxK8sNodeCount"] = max_k8s_node_count
        if use_public_load_balancer is not None:
            data["usePublicLoadBalancer"] = use_public_load_balancer
        if kubernetes_ip_cidr_blocks is not None:
            data["kubeApiAuthorizedIpRanges"] = kubernetes_ip_cidr_blocks
        if load_balancer_ip_cidr_blocks is not None:
            data["loadBalancerAuthorizedIpRanges"] = load_balancer_ip_cidr_blocks
        if kubernetes_service_ip_cidr_blocks is not None:
            data["kubernetesServiceIpCidrBlocks"] = kubernetes_service_ip_cidr_blocks
        if cluster_subnet_ids is not None:
            data["clusterSubnets"] = cluster_subnet_ids
        if load_balancer_subnet_ids is not None:
            data["loadBalancerSubnets"] = load_balancer_subnet_ids
        if persist_public_ip is not None:
            data["persistPublicIp"] = persist_public_ip
        if private_cluster is not None:
            data["privateCluster"] = private_cluster
        if pod_cidr is not None:
            data["podCidr"] = pod_cidr
        if service_cidr is not None:
            data["serviceCidr"] = service_cidr
        if instance_type is not None:
            data["instanceType"] = instance_type
        if skip_preflight_checks is not None:
            data["skipPreflightChecks"] = skip_preflight_checks
        if user_defined_routing is not None:
            data["userDefinedRouting"] = user_defined_routing
        if tags is not None:
            data["tags"] = tags

        return self.api_client.post("/api/v1/df/enableService", data=data)

    def update_service(
        self,
        service_crn: str,
        min_k8s_node_count: Optional[int] = None,
        max_k8s_node_count: Optional[int] = None,
        kubernetes_ip_cidr_blocks: Optional[List[str]] = None,
        load_balancer_ip_cidr_blocks: Optional[List[str]] = None,
        skip_preflight_checks: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update a DataFlow service configuration.

        Args:
            service_crn: The CRN of the service to update
            min_k8s_node_count: Updated minimum number of Kubernetes nodes
            max_k8s_node_count: Updated maximum number of Kubernetes nodes
            kubernetes_ip_cidr_blocks: Updated CIDR blocks for Kubernetes API access
            load_balancer_ip_cidr_blocks: Updated CIDR blocks for load balancer access
            skip_preflight_checks: Whether to skip pre-flight checks during update

        Returns:
            Dictionary containing updated service details

        Note:
            Not all parameters from enable_service are updatable.
            Network configuration (subnets, CIDR ranges, cluster type) typically cannot be changed.
            Only the following parameters can be updated:
            - minK8sNodeCount (required)
            - maxK8sNodeCount (required)
            - kubeApiAuthorizedIpRanges (optional)
            - loadBalancerAuthorizedIpRanges (optional)
            - skipPreflightChecks (optional)
        """
        data: Dict[str, Any] = {"serviceCrn": service_crn}

        # Note: According to API docs, min and max node counts are required for update
        if min_k8s_node_count is not None:
            data["minK8sNodeCount"] = min_k8s_node_count
        if max_k8s_node_count is not None:
            data["maxK8sNodeCount"] = max_k8s_node_count
        if kubernetes_ip_cidr_blocks is not None:
            data["kubeApiAuthorizedIpRanges"] = kubernetes_ip_cidr_blocks
        if load_balancer_ip_cidr_blocks is not None:
            data["loadBalancerAuthorizedIpRanges"] = load_balancer_ip_cidr_blocks
        if skip_preflight_checks is not None:
            data["skipPreflightChecks"] = skip_preflight_checks

        return self.api_client.post("/api/v1/df/updateService", data=data)

    def disable_service(
        self,
        crn: str,
        terminate_deployments: bool = False,
        persist: bool = False,
    ) -> Dict[str, Any]:
        """
        Disable a DataFlow service.

        Args:
            crn: The CRN of the service
            terminate_deployments: Whether to terminate all deployments
            persist: Whether to retain the database records of related entities

        Returns:
            Empty dictionary on success
        """
        data = {
            "serviceCrn": crn,
            "terminateDeployments": terminate_deployments,
            "persist": persist,
        }
        return self.api_client.post("/api/v1/df/disableService", data=data)

    def reset_service(self, crn: str) -> Dict[str, Any]:
        """
        Reset a DataFlow service.

        Resets all references to a service. Only NOT_ENABLED services can be reset.
        Makes no attempt to clean up resources.

        Args:
            crn: The CRN of the service

        Returns:
            Empty dictionary on success
        """
        data = {"serviceCrn": crn}
        return self.api_client.post("/api/v1/df/resetService", data=data)

    def _get_service_state(
        self,
        service_crn: str,
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Helper method to get current service state.

        Args:
            service_crn: The CRN of the service

        Returns:
            Tuple of (state, service_details) or None if service doesn't exist
        """
        service = self.get_service_by_crn(service_crn)
        if not service:
            return None

        service_details = service.get("service", service)

        try:
            current_state = service_details["status"]["state"]
            return (current_state, service_details)
        except (KeyError, TypeError):
            return (None, service_details)

    def wait_for_service_state(
        self,
        service_crn: str,
        target_states: List[str],
        timeout: int = 3600,
        delay: int = 60,
        terminate_deployments: bool = False,
        persist: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a DataFlow service to reach a target state.

        If target state is "NOT_ENABLED", automatically initiates service disablement if needed.

        Args:
            service_crn: The CRN of the service
            target_states: List of acceptable target states
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds
            terminate_deployments: Whether to terminate all deployments (used when disabling)
            persist: Whether to retain database records (used when disabling)

        Returns:
            Service details dict when target state is reached, or None if service is deleted

        Raises:
            CdpError: If timeout is reached or service enters a failed state

        Notes:
            When target_states includes "NOT_ENABLED", the method will:
            1. Check current service state
            2. If in REMOVABLE_STATES (healthy/unhealthy) → Call disable_service API
            3. If already NOT_ENABLED → Return immediately
            4. If already DISABLING → Skip to waiting loop
            5. Otherwise → Raise error (cannot disable from current state)

            Failed states are always: BAD_HEALTH, UNKNOWN
        """

        start_time = time.time()

        # If target is NOT_ENABLED, initiate disablement if needed
        if "NOT_ENABLED" in target_states:
            result = self._get_service_state(service_crn)
            if result is None:
                # Service doesn't exist
                return None

            current_state, service_details = result

            # Define valid state transitions

            # State-based decision for disablement
            if current_state in self.REMOVABLE_STATES:
                # Service is running - initiate disable
                self.disable_service(
                    crn=service_crn,
                    terminate_deployments=terminate_deployments,
                    persist=persist,
                )
            elif current_state in target_states:
                # Already in target state - return immediately
                return service_details
            elif current_state in self.TERMINATION_STATES:
                # Already disabling - proceed to waiting loop
                pass
            else:
                # Cannot disable from this state
                raise CdpError(
                    f"Cannot disable service in state '{current_state}'. ",
                )

        # Wait for target state
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for DataFlow service to reach {target_states} "
                    f"after {timeout} seconds",
                )

            result = self._get_service_state(service_crn)

            # Service no longer exists
            if result is None:
                return None

            current_state, service_details = result

            # Check if in target state
            if current_state in target_states:
                return service_details

            # Check if in failed state
            if current_state in self.FAILED_STATES:
                msg = service_details.get("status", {}).get("message", "Unknown error")
                raise CdpError(
                    f"DataFlow service entered failed state '{current_state}': {msg}",
                )

            time.sleep(delay)

    # ========================================================================
    # Deployment Management Methods
    # ========================================================================

    @CdpClient.paginated()
    def list_deployments(
        self,
        filters: Optional[List[str]] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
        sorts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        List DataFlow deployments.

        Args:
            filters: Filter criteria (see list-filter-options)
            pageToken: Pagination token for getting the next page
            pageSize: Number of results per page (1-100)
            sorts: Sort criteria (updated|name|state|dataSent|dataReceived):(asc|desc)

        Returns:
            Dictionary containing:
                - deployments: List of DeploymentSummary objects
                - nextToken: Token for next page (if available)
        """
        data: Dict[str, Any] = {}
        if filters is not None:
            data["filters"] = filters
        if pageToken is not None:
            data["startingToken"] = pageToken
        if pageSize is not None:
            data["pageSize"] = pageSize
        if sorts is not None:
            data["sorts"] = sorts

        return self.api_client.post(
            "/api/v1/df/listDeployments",
            data=data,
            squelch={404: {"deployments": []}},
        )

    def describe_deployment(self, deployment_crn: str) -> Dict[str, Any]:
        """
        Describe a DataFlow deployment.

        Args:
            deployment_crn: The CRN of the deployment

        Returns:
            Dictionary containing deployment details
        """
        data = {"deploymentCrn": deployment_crn}
        return self.api_client.post(
            "/api/v1/df/describeDeployment",
            data=data,
            squelch={404: {}},
        )

    def get_deployment_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment details by name.

        Args:
            name: The deployment name

        Returns:
            Deployment details dict, or None if not found
        """
        deployments = self.list_deployments()
        for deployment in deployments.get("deployments", []):
            if deployment.get("name") == name:
                return self.describe_deployment(deployment.get("crn"))
        return None

    def get_deployment_by_crn(self, crn: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment details by CRN.

        Args:
            crn: The deployment CRN

        Returns:
            Deployment details dict, or None if not found
        """
        try:
            return self.describe_deployment(crn)
        except CdpError:
            return None

    # ========================================================================
    # ReadyFlow Management Methods
    # ========================================================================

    @CdpClient.paginated()
    def list_readyflows(
        self,
        search_term: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List available ReadyFlows in the catalog.

        Args:
            search_term: Search term to filter ReadyFlows (searches by name)
            pageToken: Pagination token for getting the next page
            pageSize: Number of results per page

        Returns:
            Dictionary containing:
                - readyflows: List of ReadyFlow objects
                - nextToken: Token for next page (if available)
        """
        data: Dict[str, Any] = {}
        if search_term is not None:
            data["searchTerm"] = search_term
        if pageToken is not None:
            data["startingToken"] = pageToken
        if pageSize is not None:
            data["pageSize"] = pageSize

        return self.api_client.post("/api/v1/df/listReadyflows", data=data)

    def describe_readyflow(self, readyflow_crn: str) -> Dict[str, Any]:
        """
        Get details for a specific ReadyFlow.

        Args:
            readyflow_crn: The CRN of the ReadyFlow

        Returns:
            Dictionary containing ReadyFlow details
        """
        data = {"readyflowCrn": readyflow_crn}
        return self.api_client.post("/api/v1/df/describeReadyflow", data=data)

    def describe_added_readyflow(
        self,
        readyflow_crn: str,
    ) -> Dict[str, Any]:
        """
        Get details for a ReadyFlow that has been added to the account.

        Args:
            readyflow_crn: The CRN of the added ReadyFlow

        Returns:
            Dictionary containing added ReadyFlow details including versions
        """
        data = {"readyflowCrn": readyflow_crn}
        return self.api_client.post("/api/v1/df/describeAddedReadyflow", data=data)

    # ========================================================================
    # Flow Definition Methods
    # ========================================================================

    @CdpClient.paginated()
    def list_flow_definitions(
        self,
        search_term: Optional[str] = None,
        collection_crn: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
        sorts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        List custom flow definitions in the catalog.

        Args:
            search_term: Search term to filter by flow name
            collection_crn: Filter by collection CRN
            pageToken: Pagination token for getting the next page
            pageSize: Number of results per page
            sorts: Sort criteria

        Returns:
            Dictionary containing:
                - flows: List of FlowSummary objects
                - nextToken: Token for next page (if available)
        """
        data: Dict[str, Any] = {}
        if search_term is not None:
            data["searchTerm"] = search_term
        if collection_crn is not None:
            data["collectionCrn"] = collection_crn
        if pageToken is not None:
            data["startingToken"] = pageToken
        if pageSize is not None:
            data["pageSize"] = pageSize
        if sorts is not None:
            data["sorts"] = sorts

        return self.api_client.post(
            "/api/v1/df/listFlowDefinitions",
            data=data,
            squelch={404: {"flows": []}},
        )

    def describe_flow(self, flow_crn: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific flow definition.

        Args:
            flow_crn: The CRN of the flow

        Returns:
            Dictionary containing flow details
        """
        data = {"flowCrn": flow_crn}
        return self.api_client.post(
            "/api/v1/df/describeFlow",
            data=data,
            squelch={404: {}},
        )

    def get_flow_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get flow details by name.

        Args:
            name: The flow name

        Returns:
            Flow details dict, or None if not found
        """
        flows = self.list_flow_definitions(search_term=name)
        for flow in flows.get("flows", []):
            if flow.get("name") == name:
                result = self.describe_flow(flow.get("crn"))
                if result:
                    flow_obj = result.get("flow", result)
                    return flow_obj.get("flowDetail", flow_obj)
                return None
        return None

    def get_flow_by_crn(self, crn: str) -> Optional[Dict[str, Any]]:
        """
        Get flow details by CRN.

        Args:
            crn: The flow CRN

        Returns:
            Flow details dict, or None if not found
        """
        try:
            result = self.describe_flow(crn)
            if result:
                flow_obj = result.get("flow", result)
                return flow_obj.get("flowDetail", flow_obj)
            return None
        except Exception:
            return None

    def import_flow_definition(
        self,
        name: str,
        file_content: str,
        description: Optional[str] = None,
        comments: Optional[str] = None,
        collection_crn: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Import a new flow definition.

        This method uses the DataFlow extension format which sends metadata
        as custom headers and the flow definition as the raw request body.

        Args:
            name: The name of the flow
            file_content: The flow definition file content (JSON string)
            description: The description of the flow
            comments: Comments for the initial version
            collection_crn: The CRN of the collection to assign the flow to
            tags: List of tags for the initial flow definition version.
                  Each tag should be a dict with 'tagName' (required) and 'tagColor' (optional)

        Returns:
            Dictionary containing the imported flow details
        """

        data: Dict[str, Any] = {
            "name": name,
            "file": file_content,
        }
        if description is not None:
            data["description"] = description
        if comments is not None:
            data["comments"] = comments
        if collection_crn is not None:
            data["collectionCrn"] = collection_crn
        if tags is not None:
            data["tags"] = tags

        return self.api_client.post(
            "/api/v1/df/importFlowDefinition",
            data=data,
        )

    def import_flow_definition_version(
        self,
        flow_crn: str,
        file_content: str,
        comments: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Import a new flow definition version to an existing flow.

        Args:
            flow_crn: The CRN of the existing flow
            file_content: The flow definition file content (JSON string)
            comments: Comments for the new version
            tags: List of tags for the flow definition version.
                  Each tag should be a dict with 'tagName' (required) and 'tagColor' (optional)

        Returns:
            Dictionary containing the new version details
        """
        data: Dict[str, Any] = {
            "flowCrn": flow_crn,
            "file": file_content,
        }
        if comments is not None:
            data["comments"] = comments
        if tags is not None:
            data["tags"] = tags

        return self.api_client.post(
            "/api/v1/df/importFlowDefinitionVersion",
            data=data,
        )

    def delete_flow(self, flow_crn: str) -> Dict[str, Any]:
        """
        Delete a flow definition.

        Args:
            flow_crn: The CRN of the flow to delete

        Returns:
            Dictionary containing the deleted flow details
        """
        data = {"flowCrn": flow_crn}
        return self.api_client.post("/api/v1/df/deleteFlow", data=data)
