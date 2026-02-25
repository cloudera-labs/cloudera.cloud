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
A REST client for the Cloudera on Cloud Platform (CDP) AI API
"""

import time

from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


class CdpMlClient:
    """CDP AI API client."""

    # Service State contents
    FAILED_STATES = ["installation:failed"]
    CREATION_STATES = ["provision:started", "installation:started"]
    READY_STATES = ["installation:finished", "modify:finished"]
    TERMINATION_STATES = ["deprovision:started"]
    REMOVABLE_STATES = [
        "installation:failed",
        "modify:finished",
        "installation:finished",
    ]

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP AI client.

        Args:
            api_client: RestClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def list_workspaces(
        self,
        env: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List ML Workspaces in the Tenant.

        Args:
            env: Optional environment name to filter workspaces by.

        Returns:
            List of workspaces in the tenant, optionally filtered by environment.
        """

        resp = self.api_client.post(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )

        if env:
            workspaces = resp.get("workspaces", [])
            resp["workspaces"] = [x for x in workspaces if env == x["environmentName"]]

        return resp

    def describe_workspace(
        self,
        env: Optional[str] = None,
        name: Optional[str] = None,
        crn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Describe a single ML Workspace.

        Args:
            env: Optional environment name.
            name: Optional workspace name.
            crn: Optional workspace CRN. If provided, env and name are ignored.

        Returns:
            Workspace details dictionary.
        """

        json_data: Dict[str, Any] = {}

        if crn is not None:
            json_data["workspaceCrn"] = crn
        else:
            if env is not None:
                json_data["environmentName"] = env
            if name is not None:
                json_data["workspaceName"] = name

        return self.api_client.post(
            "/api/v1/ml/describeWorkspace",
            json_data=json_data,
            squelch={
                404: {},
                500: {},
            },
        )

    def describe_all_workspaces(
        self,
        env: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Describe all ML Workspaces in the Tenant, optionally filtered by environment.

        Args:
            env: Optional environment name to filter workspaces by.

        Returns:
            List of workspace details for all workspaces in the tenant.
        """
        ws_list = self.list_workspaces(env)
        resp = []

        for ws in ws_list.get("workspaces", []):
            ws_desc = self.describe_workspace(crn=ws["crn"])
            if ws_desc is not None:
                resp.append(ws_desc.get("workspace", {}))
        return resp

    def create_workspace(
        self,
        workspace_name: str,
        environment_name: str,
        disable_tls: Optional[bool] = None,
        enable_monitoring: Optional[bool] = None,
        enable_governance: Optional[bool] = None,
        enable_model_metrics: Optional[bool] = None,
        existing_database_config: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        existing_nfs: Optional[str] = None,
        nfs_version: Optional[str] = None,
        load_balancer_ip_whitelists: Optional[List[str]] = None,
        use_public_loadbalancer: Optional[bool] = None,
        private_cluster: Optional[bool] = None,
        provision_k8s_request: Optional[Dict[str, Any]] = None,
        authorized_ip_ranges: Optional[List[str]] = None,
        whitelist_authorized_ip_ranges: Optional[bool] = None,
        enable_yunikorn: Optional[bool] = None,
        enable_enhanced_performance: Optional[bool] = None,
        enable_global_access_loadbalancer: Optional[bool] = None,
        static_subdomain: Optional[str] = None,
        subnets_for_load_balancers: Optional[List[str]] = None,
        resource_pool_config: Optional[Dict[str, Any]] = None,
        outbound_types: Optional[List[str]] = None,
        skip_validation: Optional[bool] = None,
        cdsw_migration_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new ML Workspace.

        Args:
            workspace_name: The name of the workspace to create.
            environment_name: The environment for the workspace to create.
            disable_tls: The boolean flag to disable TLS setup for workbench.
            enable_monitoring: The boolean flag to enable monitoring.
            enable_governance: Enables Cloudera AI governance by integrating with Cloudera Atlas.
            enable_model_metrics: Enables the model metrics service for exporting metrics.
            existing_database_config: Optional configurations for an existing Postgres.
            namespace: The namespace of the workspace (Private Cloud only).
            existing_nfs: Optionally use an existing NFS (Azure and Private Cloud only).
            nfs_version: The NFS Protocol version (Azure and Private Cloud only).
            load_balancer_ip_whitelists: The whitelist of IPs for load balancer.
            use_public_loadbalancer: The boolean flag to request public load balancer.
            private_cluster: Whether to create a private cluster.
            provision_k8s_request: The request for Kubernetes workspace provision.
            authorized_ip_ranges: The whitelist of CIDR blocks which can access the API server.
            whitelist_authorized_ip_ranges: Whether to whitelist only authorized IP ranges or all public IPs.
            enable_yunikorn: The boolean flag to enable yunikorn scheduling.
            enable_enhanced_performance: Enable Enhanced Performance Mode for root volumes.
            enable_global_access_loadbalancer: Enable global access to the load balancer.
            static_subdomain: The static subdomain to be used for the workspace.
            subnets_for_load_balancers: The list of subnets used for the load balancer.
            resource_pool_config: The resource pool configuration for quota management.
            outbound_types: Outbound Types provided for the workspace.
            skip_validation: Skip pre-flight validations if requested.
            cdsw_migration_mode: Toggle for cdsw migration preflight validation.

        Returns:
            Response containing the created workspace details.
        """
        json_data: Dict[str, Any] = {
            "workspaceName": workspace_name,
            "environmentName": environment_name,
        }

        # Map of parameter names to API field names
        optional_params = {
            "disableTLS": disable_tls,
            "enableMonitoring": enable_monitoring,
            "enableGovernance": enable_governance,
            "enableModelMetrics": enable_model_metrics,
            "existingDatabaseConfig": existing_database_config,
            "namespace": namespace,
            "existingNFS": existing_nfs,
            "nfsVersion": nfs_version,
            "loadBalancerIPWhitelists": load_balancer_ip_whitelists,
            "usePublicLoadBalancer": use_public_loadbalancer,
            "privateCluster": private_cluster,
            "provisionK8sRequest": provision_k8s_request,
            "authorizedIPRanges": authorized_ip_ranges,
            "whitelistAuthorizedIPRanges": whitelist_authorized_ip_ranges,
            "enableYunikorn": enable_yunikorn,
            "enableEnhancedPerformance": enable_enhanced_performance,
            "enableGlobalAccessLoadBalancer": enable_global_access_loadbalancer,
            "staticSubdomain": static_subdomain,
            "subnetsForLoadBalancers": subnets_for_load_balancers,
            "resourcePoolConfig": resource_pool_config,
            "outboundTypes": outbound_types,
            "skipValidation": skip_validation,
            "cdswMigrationMode": cdsw_migration_mode,
        }

        # Add only non-None optional parameters
        json_data.update({k: v for k, v in optional_params.items() if v is not None})

        return self.api_client.post(
            "/api/v1/ml/createWorkspace",
            json_data=json_data,
            squelch={},
        )

    def delete_workspace(
        self,
        force: bool,
        workspace_name: Optional[str] = None,
        environment_name: Optional[str] = None,
        workspace_crn: Optional[str] = None,
        remove_storage: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Delete an ML Workspace.

        Args:
            force: Force delete a workbench even if errors occur during deletion.
            workspace_name: The name of the workbench to delete.
            environment_name: The environment for the workbench to delete.
            workspace_crn: The CRN of the workbench to delete. If provided, workspace_name and environment_name are ignored.
            remove_storage: Whether to remove the backing workbench filesystem storage during delete.

        Returns:
            Response from the delete operation.
        """
        json_data: Dict[str, Any] = {
            "force": force,
        }

        # Map of parameter names to API field names
        optional_params = {
            "workspaceName": workspace_name,
            "environmentName": environment_name,
            "workspaceCrn": workspace_crn,
            "removeStorage": remove_storage,
        }

        # Add only non-None optional parameters
        json_data.update({k: v for k, v in optional_params.items() if v is not None})

        return self.api_client.post(
            "/api/v1/ml/deleteWorkspace",
            json_data=json_data,
            squelch={},
        )

    def wait_for_workspace_state(
        self,
        environment: str,
        workspace_name: str,
        target_states: Optional[List[str]] = None,
        delay: int = 30,  # Changed from poll_interval to match ml.py usage
        timeout: int = 3600,
        ignore_failures: bool = False,
    ) -> Dict[str, Any]:
        """
        Wait for an ML Workspace to reach one of the target states or be deleted.

        Args:
            environment: The environment of the workspace to monitor.
            workspace_name: The name of the workspace to monitor.
            target_states: List of desired target states to wait for. If None, waits for workspace deletion.
            delay: Time between status checks in seconds.
            timeout: Maximum time to wait in seconds.
            ignore_failures: If True, ignore failed states and continue waiting.

        Returns:
            The final workspace details once a target state is reached, or empty dict if deleted.

        Raises:
            CdpError: If workspace enters a failed state (when ignore_failures=False) or timeout occurs.
        """

        start_time = time.time()

        # Wait for target state(s) to be reached, polling at the specified interval
        while True:
            workspace = self.describe_workspace(env=environment, name=workspace_name)

            # Check if workspace has been deleted (None or empty response)
            if workspace is None or workspace.get("workspace") is None:
                if target_states is None:
                    # Deletion was expected - successfully deleted
                    return {}
                else:
                    # Workspace doesn't exist yet (post-creation lag) or was deleted unexpectedly
                    # Continue polling to allow for API lag where workspace isn't visible yet
                    if time.time() - start_time > timeout:
                        raise CdpError(
                            f"Timeout waiting for workspace {workspace_name} in environment {environment} to appear. "
                            f"The workspace may not have been created successfully.",
                        )
                    time.sleep(delay)
                    continue

            current_state = workspace.get("workspace", {}).get("instanceStatus")

            # Check if in target state
            if target_states is not None and current_state in target_states:
                return workspace

            # Check if in failed state
            if not ignore_failures and current_state in self.FAILED_STATES:
                msg = workspace.get("workspace", {}).get(
                    "failureMessage",
                    "Unknown failure",
                )
                raise CdpError(
                    f"Workspace {workspace_name} in environment {environment} entered failed state '{current_state}': {msg}.",
                )

            if time.time() - start_time > timeout:
                if target_states is None:
                    raise CdpError(
                        f"Timeout waiting for workspace {workspace_name} in environment {environment} to be deleted after {timeout} seconds. "
                        f"Current state: {current_state}",
                    )
                else:
                    raise CdpError(
                        f"Timeout waiting for workspace {workspace_name} in environment {environment} to reach states {target_states} after {timeout} seconds. "
                        f"Current state: {current_state}",
                    )

            time.sleep(delay)
