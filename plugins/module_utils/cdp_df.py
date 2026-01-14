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

from typing import Any, Dict, List, Optional
import time
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


class CdpDfClient:
    """CDP DataFlow API client."""

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

    def check_service_updates(
        self,
        service_crn: str,
        service_details: Dict[str, Any],
        min_k8s_node_count: Optional[int] = None,
        max_k8s_node_count: Optional[int] = None,
        kubernetes_ip_cidr_blocks: Optional[List[str]] = None,
        load_balancer_ip_cidr_blocks: Optional[List[str]] = None,
        skip_preflight_checks: Optional[bool] = None,
    ) -> tuple[bool, Dict[str, Any]]:
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
            Tuple of (update_needed, update_params)
        """
        update_params = {"service_crn": service_crn}
        changes = []

        # Define updatable scalar parameters with their mappings
        param_mappings = [
            (min_k8s_node_count, "minK8sNodeCount", "min_k8s_node_count"),
            (max_k8s_node_count, "maxK8sNodeCount", "max_k8s_node_count"),
        ]

        # Check scalar parameters
        for desired_value, service_key, api_param in param_mappings:
            current_value = service_details.get(service_key)
            if desired_value is not None and desired_value != current_value:
                update_params[api_param] = desired_value
                changes.append(api_param)

        # Check IP range list parameters (order-independent comparison)
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

        # Include skip_preflight_checks if set
        if skip_preflight_checks:
            update_params["skip_preflight_checks"] = skip_preflight_checks

        # Ensure both node counts are present (API requirement)
        if changes:
            if "min_k8s_node_count" not in update_params:
                current_min = service_details.get("minK8sNodeCount")
                if current_min is not None:
                    update_params["min_k8s_node_count"] = current_min
            if "max_k8s_node_count" not in update_params:
                current_max = service_details.get("maxK8sNodeCount")
                if current_max is not None:
                    update_params["max_k8s_node_count"] = current_max

        return bool(changes), update_params

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

    def wait_for_service_state(
        self,
        service_crn: str,
        target_states: List[str],
        failed_states: Optional[List[str]] = None,
        timeout: int = 3600,
        delay: int = 60,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a DataFlow service to reach a target state.

        Args:
            service_crn: The CRN of the service
            target_states: List of acceptable target states
            failed_states: List of states that indicate failure (optional)
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            Service details dict when target state is reached, or None if service is deleted

        Raises:
            CdpError: If timeout is reached or service enters a failed state
        """

        failed_states = failed_states or ["BAD_HEALTH", "UNKNOWN"]
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for DataFlow service to reach {target_states} after {timeout} seconds",
                )

            service = self.get_service_by_crn(service_crn)

            if service is None:
                return None

            # Handle response structure - could be {"service": {...}} or direct service object
            if "service" in service:
                service_details = service["service"]
            else:
                service_details = service

            # Get current state - use dict access instead of .get() to avoid issues
            try:
                current_state = service_details["status"]["state"]
            except (KeyError, TypeError) as e:
                import sys

                print(
                    f"Warning: Could not find state in service response. Error: {e}",
                    file=sys.stderr,
                )
                print(f"Service details type: {type(service_details)}", file=sys.stderr)
                print(f"Service details: {service_details}", file=sys.stderr)
                current_state = None

            # Check if in target state
            if current_state in target_states:
                return service_details

            # Check if in failed state
            if current_state in failed_states:
                msg = service_details.get("status", {}).get("message", "Unknown error")
                raise CdpError(
                    f"DataFlow service entered failed state '{current_state}': {msg}",
                )

            time.sleep(delay)

    def disable_service_and_wait(
        self,
        service_crn: str,
        terminate_deployments: bool = False,
        persist: bool = False,
        timeout: int = 3600,
        delay: int = 60,
    ) -> Optional[Dict[str, Any]]:
        """
        Disable a DataFlow service and wait for completion.

        Args:
            service_crn: The CRN of the service
            terminate_deployments: Whether to terminate all deployments
            persist: Whether to retain the database records of related entities
            timeout: Maximum time to wait in seconds
            delay: Polling interval in seconds

        Returns:
            Service details dict in final state, or None if deleted

        Raises:
            CdpError: If service is in unexpected state or timeout occurs
        """

        # Get current service state
        service = self.get_service_by_crn(service_crn)
        if not service or "service" not in service:
            return None

        service_details = service["service"]
        try:
            current_state = service_details["status"]["state"]
        except (KeyError, TypeError):
            current_state = None

        REMOVABLE_STATES = ["GOOD_HEALTH", "CONCERNING_HEALTH", "BAD_HEALTH", "UNKNOWN"]
        TERMINATION_STATES = ["DISABLING"]
        STOPPED_STATES = ["NOT_ENABLED"]

        # Attempt to disable if in removable state
        if current_state in REMOVABLE_STATES:
            self.disable_service(
                crn=service_crn,
                terminate_deployments=terminate_deployments,
                persist=persist,
            )
        elif current_state in STOPPED_STATES:
            # Already stopped
            return service_details
        elif current_state not in TERMINATION_STATES:
            raise CdpError(
                f"Cannot disable service in state '{current_state}'. Expected one of {REMOVABLE_STATES}",
            )

        # Wait for service to be disabled or deleted
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise CdpError(
                    f"Timeout waiting for DataFlow service to disable after {timeout} seconds",
                )

            service = self.get_service_by_crn(service_crn)

            # Service no longer exists - success!
            if service is None:
                return None

            if "service" in service:
                service_details = service["service"]
                try:
                    current_state = service_details["status"]["state"]
                except (KeyError, TypeError):
                    current_state = None

                # Check if in stopped state
                if current_state in STOPPED_STATES:
                    return service_details

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
