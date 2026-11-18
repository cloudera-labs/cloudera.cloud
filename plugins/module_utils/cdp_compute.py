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
A REST client for the Cloudera on Cloud Platform (CDP) Compute API
"""

import time
from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


class CdpComputeClient:
    """CDP Compute API client."""

    # Cluster lifecycle state constants
    ACTIVE_STATES = ["RUNNING"]
    REMOVABLE_STATES = ["RUNNING", "FAILED", "CREATE_FAILED"]
    TERMINATION_STATES = ["DELETING"]
    DELETED_STATES = ["DELETED"]
    FAILED_STATES = ["FAILED", "CREATE_FAILED", "DELETE_FAILED"]

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP Compute client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    # ========================================================================
    # Cluster Management Methods
    # ========================================================================

    @CdpClient.paginated()
    def list_clusters(
        self,
        env_name_or_crn: Optional[str] = None,
        cluster_shape: Optional[str] = None,
        default: Optional[bool] = None,
        include_deleted: Optional[bool] = None,
        status: Optional[str] = None,
        workloads: Optional[str] = None,
        pageToken: Optional[str] = None,
        pageSize: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List all compute clusters, optionally filtered by environment.

        Args:
            env_name_or_crn: Environment name or CRN to filter clusters by
            cluster_shape: Filter between Externalized and Embedded cluster shapes
            default: Only show default clusters
            include_deleted: Include deleted clusters in the response
            status: Cluster status for status filtering
            workloads: Workloads for workload filtering
            pageToken: Pagination token for getting the next page
            pageSize: Number of results per page (1-500, default 100)

        Returns:
            Dictionary containing:
                - clusters: List of ListClusterItem objects
                - nextToken: Token for next page (if available)
                - totalClusters: Total number of clusters
                - totalPages: Total number of pages
        """
        data: Dict[str, Any] = {}
        if env_name_or_crn is not None:
            data["envNameOrCrn"] = env_name_or_crn
        if cluster_shape is not None:
            data["clusterShape"] = cluster_shape
        if default is not None:
            data["default"] = default
        if include_deleted is not None:
            data["includeDeleted"] = include_deleted
        if status is not None:
            data["status"] = status
        if workloads is not None:
            data["workloads"] = workloads
        if pageToken is not None:
            data["startingToken"] = pageToken
        if pageSize is not None:
            data["pageSize"] = pageSize

        return self.api_client.post(
            "/api/v1/compute/listClusters",
            data=data,
            squelch={404: {"clusters": []}},
        )

    def describe_cluster(self, cluster_crn: str) -> Dict[str, Any]:
        """
        Describe a compute cluster by CRN.

        Args:
            cluster_crn: The CRN of the compute cluster

        Returns:
            Dictionary containing DescribeClusterResponse fields, or empty dict if not found
        """
        data = {"clusterCrn": cluster_crn}
        return self.api_client.post(
            "/api/v1/compute/describeCluster",
            data=data,
            squelch={404: {}},
        )

    def get_cluster_by_crn(self, cluster_crn: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed cluster information by CRN.

        Args:
            cluster_crn: The CRN of the compute cluster

        Returns:
            Cluster details dict (DescribeClusterResponse), or None if not found
        """
        response = self.describe_cluster(cluster_crn)
        if not response:
            return None
        return response

    def get_clusters_by_env(
        self,
        env_name_or_crn: str,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        List clusters filtered by environment name or CRN.

        Args:
            env_name_or_crn: Environment name or CRN
            **kwargs: Additional filter arguments passed to list_clusters

        Returns:
            List of ListClusterItem objects
        """
        response = self.list_clusters(env_name_or_crn=env_name_or_crn, **kwargs)
        return response.get("clusters", [])

    def get_all_clusters(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        List all compute clusters.

        Args:
            **kwargs: Optional filter arguments passed to list_clusters

        Returns:
            List of ListClusterItem objects
        """
        response = self.list_clusters(**kwargs)
        return response.get("clusters", [])

    def create_cluster(
        self,
        name: str,
        environment: str,
        description: Optional[str] = None,
        network: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        skip_validation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create an externalized compute cluster.

        Args:
            name: Name for the new cluster
            environment: CRN of the CDP environment
            description: Optional description
            network: Optional CommonNetwork dict (subnets, podCidr, serviceCidr, outboundType)
            tags: Optional map of string tags
            skip_validation: If True, skip pre-flight validation

        Returns:
            Dictionary containing CreateClusterResponse fields:
                - clusterCrn, clusterId, clusterStatus, uri, validationResponse
        """
        data: Dict[str, Any] = {
            "clusterName": name,
            "environmentCrn": environment,
        }
        if description is not None:
            data["description"] = description
        if network is not None:
            data["network"] = network
        if tags is not None:
            data["tags"] = tags
        if skip_validation is not None:
            data["skipValidation"] = skip_validation

        return self.api_client.post(
            "/api/v1/compute/createCluster",
            data=data,
        )

    def delete_cluster(
        self,
        cluster_crn: str,
        force: Optional[bool] = None,
        skip_validation: Optional[bool] = None,
        skip_workloads_validation: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Delete an externalized compute cluster.

        Args:
            cluster_crn: CRN of the cluster to delete
            force: If True, force delete even if workloads are running
            skip_validation: If True, skip pre-flight validation
            skip_workloads_validation: If True, skip workload validation checks

        Returns:
            Dictionary containing DeleteClusterResponse fields:
                - clusterStatus, validationResponse
        """
        data: Dict[str, Any] = {"clusterCrn": cluster_crn}
        if force is not None:
            data["force"] = force
        if skip_validation is not None:
            data["skipValidation"] = skip_validation
        if skip_workloads_validation is not None:
            data["skipWorkloadsValidation"] = skip_workloads_validation

        return self.api_client.post(
            "/api/v1/compute/deleteCluster",
            data=data,
        )

    def get_cluster_by_name_and_env(
        self,
        name: str,
        env_name_or_crn: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find an externalized cluster by name within an environment.

        Calls list_clusters filtered by environment and scans for a matching name.

        Args:
            name: Cluster name to search for
            env_name_or_crn: Environment name or CRN to filter by

        Returns:
            First matching cluster dict, or None if not found
        """
        clusters = self.get_clusters_by_env(env_name_or_crn)
        for cluster in clusters:
            if cluster.get("clusterName") == name:
                return cluster
        return None

    def wait_for_cluster_state(
        self,
        cluster_crn: str,
        target_states: List[str],
        timeout: int = 3600,
        delay: int = 15,
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for a compute cluster to reach one of the target states.

        Args:
            cluster_crn: CRN of the cluster to monitor
            target_states: List of acceptable target state strings
            timeout: Maximum seconds to wait before raising CdpError
            delay: Polling interval in seconds

        Returns:
            Cluster details dict when target state is reached, or None if cluster is gone

        Raises:
            CdpError: If timeout is reached or cluster enters a failed state
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for compute cluster to reach {target_states} "
                    f"after {timeout} seconds",
                )

            cluster = self.get_cluster_by_crn(cluster_crn)

            if cluster is None:
                return None

            current_state = cluster.get("status")

            if current_state in target_states:
                return cluster

            if current_state in self.FAILED_STATES:
                msg = cluster.get("statusMessage", "Unknown error")
                raise CdpError(
                    f"Compute cluster entered failed state '{current_state}': {msg}",
                )

            time.sleep(delay)
