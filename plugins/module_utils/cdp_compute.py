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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
)


# NOTE: fields holding lists of opaque objects are typed as a bare ``list`` on
# purpose. ``from_dict`` recurses into ``List[X]`` items and fails with an
# IndexError on ``List[Any]`` when an item is a dict; a bare ``list`` is passed
# through unchanged.


@dataclass
class CommonNetwork:
    """Network settings of a compute cluster (API ``CommonNetwork``)."""

    subnets: Union[List[str], None, NULLABLE] = NULLABLE
    podCidr: Union[str, None, NULLABLE] = NULLABLE
    serviceCidr: Union[str, None, NULLABLE] = NULLABLE
    outboundType: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class CommonStatusMessage:
    """Status of a compute cluster as returned by create/delete (``CommonStatusMessage``)."""

    status: Union[str, None, NULLABLE] = NULLABLE
    message: Union[str, None, NULLABLE] = NULLABLE
    cloudProviderDetails: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


@dataclass
class ComputeClusterSummary:
    """A compute cluster as returned by ``listClusters`` (``ListClusterItem``)."""

    clusterCrn: Union[str, None, NULLABLE] = NULLABLE
    clusterId: Union[str, None, NULLABLE] = NULLABLE
    clusterName: Union[str, None, NULLABLE] = NULLABLE
    clusterOwner: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    clusterShape: Union[str, None, NULLABLE] = NULLABLE
    clusterSize: Union[int, None, NULLABLE] = NULLABLE
    clusterStateVersion: Union[int, None, NULLABLE] = NULLABLE
    clusterType: Union[str, None, NULLABLE] = NULLABLE
    computePlatform: Union[str, None, NULLABLE] = NULLABLE
    creationTime: Union[str, None, NULLABLE] = NULLABLE
    deletionTime: Union[str, None, NULLABLE] = NULLABLE
    updateTime: Union[str, None, NULLABLE] = NULLABLE
    account: Union[str, None, NULLABLE] = NULLABLE
    availableUpgrades: Union[list, None, NULLABLE] = NULLABLE
    envCloudProvider: Union[str, None, NULLABLE] = NULLABLE
    envCrn: Union[str, None, NULLABLE] = NULLABLE
    envName: Union[str, None, NULLABLE] = NULLABLE
    imageCatalog: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    isDefault: Union[bool, None, NULLABLE] = NULLABLE
    kubernetesVersion: Union[str, None, NULLABLE] = NULLABLE
    labels: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    message: Union[str, None, NULLABLE] = NULLABLE
    operationItems: Union[list, None, NULLABLE] = NULLABLE
    proxiedServices: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    region: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    storage: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


@dataclass
class ComputeCluster:
    """A compute cluster as returned by ``describeCluster`` (``DescribeClusterResponse``)."""

    clusterCrn: Union[str, None, NULLABLE] = NULLABLE
    clusterId: Union[str, None, NULLABLE] = NULLABLE
    clusterName: Union[str, None, NULLABLE] = NULLABLE
    clusterOwner: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    clusterShape: Union[str, None, NULLABLE] = NULLABLE
    clusterSize: Union[int, None, NULLABLE] = NULLABLE
    clusterStateVersion: Union[int, None, NULLABLE] = NULLABLE
    clusterType: Union[str, None, NULLABLE] = NULLABLE
    computePlatform: Union[str, None, NULLABLE] = NULLABLE
    computePlatformVersion: Union[str, None, NULLABLE] = NULLABLE
    creationTime: Union[str, None, NULLABLE] = NULLABLE
    deletionTime: Union[str, None, NULLABLE] = NULLABLE
    updateTime: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    account: Union[str, None, NULLABLE] = NULLABLE
    apiEndPoint: Union[str, None, NULLABLE] = NULLABLE
    availableUpgrades: Union[list, None, NULLABLE] = NULLABLE
    defaultGatewayHostname: Union[str, None, NULLABLE] = NULLABLE
    eks: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    envCloudProvider: Union[str, None, NULLABLE] = NULLABLE
    envCrn: Union[str, None, NULLABLE] = NULLABLE
    envName: Union[str, None, NULLABLE] = NULLABLE
    failedEvents: Union[list, None, NULLABLE] = NULLABLE
    imageCatalog: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    isClouderaManaged: Union[bool, None, NULLABLE] = NULLABLE
    isDefault: Union[bool, None, NULLABLE] = NULLABLE
    kubernetesVersion: Union[str, None, NULLABLE] = NULLABLE
    labels: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    message: Union[str, None, NULLABLE] = NULLABLE
    nodeImageUpgradeAvailable: Union[bool, None, NULLABLE] = NULLABLE
    nodeImageUpgrades: Union[list, None, NULLABLE] = NULLABLE
    region: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    storage: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    workloads: Union[List[str], None, NULLABLE] = NULLABLE


@dataclass
class ComputeClusterSpec:
    """Desired state for a new externalized compute cluster (``createCluster`` input)."""

    name: Union[str, None, NULLABLE] = NULLABLE
    environment: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    network: Union[CommonNetwork, None, NULLABLE] = NULLABLE
    tags: Union[Dict[str, str], None, NULLABLE] = NULLABLE


@dataclass
class CreateClusterResponse:
    """Response of ``createCluster``."""

    clusterCrn: Union[str, None, NULLABLE] = NULLABLE
    clusterId: Union[str, None, NULLABLE] = NULLABLE
    clusterStatus: Union[CommonStatusMessage, None, NULLABLE] = NULLABLE
    uri: Union[str, None, NULLABLE] = NULLABLE
    validationResponse: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


@dataclass
class DeleteClusterResponse:
    """Response of ``deleteCluster``."""

    clusterStatus: Union[CommonStatusMessage, None, NULLABLE] = NULLABLE
    validationResponse: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


# Cluster status values. Verified against the live API (create -> run -> delete):
#   CREATING -> DEPLOYING_SERVICES -> RUNNING, then DELETING -> DELETED.
# Transitional statuses can carry a non-null "Runtime Status" ``message``; that is
# progress text, not an error. ``DEPLOYMENT_FAILED`` was observed live (reason in
# ``message``, ``failedEvents`` stayed empty); the other FAILED values are assumptions
# as the API does not document the enum. ``describeCluster`` can also briefly return
# ``status: null`` with an ``INTERNAL: ...`` message and then recover; callers must
# treat a null status as "unknown, keep polling".
COMPUTE_CLUSTER_ACTIVE_STATUSES: Set[str] = {"RUNNING"}
COMPUTE_CLUSTER_CREATING_STATUSES: Set[str] = {"CREATING", "DEPLOYING_SERVICES"}
COMPUTE_CLUSTER_TERMINATION_STATUSES: Set[str] = {"DELETING"}
COMPUTE_CLUSTER_DELETED_STATUSES: Set[str] = {"DELETED"}
COMPUTE_CLUSTER_FAILED_STATUSES: Set[str] = {
    "DEPLOYMENT_FAILED",
    "FAILED",
    "CREATE_FAILED",
    "DELETE_FAILED",
}

EXTERNALIZED_SHAPE = "Externalized"


def cluster_to_result(
    cluster: Union[ComputeCluster, ComputeClusterSummary, None],
) -> Dict[str, Any]:
    """Render a cluster dataclass as a snake_case dict (label keys are preserved)."""
    if cluster is None:
        return {}
    return camel_dict_to_snake_dict(to_dict(cluster), ignore_list=("labels",))


class CdpComputeClient:
    """CDP Compute API client."""

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

        Returns the raw (page-merged) API response; use get_all_clusters or
        get_clusters_by_env for typed results.

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

    def describe_cluster(self, cluster_crn: str) -> Optional[ComputeCluster]:
        """
        Describe a compute cluster by CRN.

        A deleted cluster is still returned (with status DELETED).

        Args:
            cluster_crn: The CRN of the compute cluster

        Returns:
            ComputeCluster, or None if the cluster is not found
        """
        response = self.api_client.post(
            "/api/v1/compute/describeCluster",
            data={"clusterCrn": cluster_crn},
            squelch={404: {}},
        )
        if not response:
            return None
        return from_dict(ComputeCluster, response)

    def get_cluster_by_crn(self, cluster_crn: str) -> Optional[ComputeCluster]:
        """
        Get detailed cluster information by CRN.

        Args:
            cluster_crn: The CRN of the compute cluster

        Returns:
            ComputeCluster, or None if not found
        """
        return self.describe_cluster(cluster_crn)

    def get_clusters_by_env(
        self,
        env_name_or_crn: str,
        **kwargs: Any,
    ) -> List[ComputeClusterSummary]:
        """
        List clusters filtered by environment name or CRN.

        Args:
            env_name_or_crn: Environment name or CRN
            **kwargs: Additional filter arguments passed to list_clusters

        Returns:
            List of ComputeClusterSummary
        """
        response = self.list_clusters(env_name_or_crn=env_name_or_crn, **kwargs)
        return [
            from_dict(ComputeClusterSummary, c) for c in response.get("clusters", [])
        ]

    def get_all_clusters(self, **kwargs: Any) -> List[ComputeClusterSummary]:
        """
        List all compute clusters.

        Args:
            **kwargs: Optional filter arguments passed to list_clusters

        Returns:
            List of ComputeClusterSummary
        """
        response = self.list_clusters(**kwargs)
        return [
            from_dict(ComputeClusterSummary, c) for c in response.get("clusters", [])
        ]

    def get_cluster_by_name_and_env(
        self,
        name: str,
        env_name_or_crn: str,
    ) -> Optional[ComputeClusterSummary]:
        """
        Find a user-managed externalized cluster by name within an environment.

        Default clusters, Embedded clusters and DELETED records are never
        returned, so callers cannot accidentally manage them.

        Args:
            name: Cluster name to search for
            env_name_or_crn: Environment name or CRN to filter by

        Returns:
            First matching ComputeClusterSummary, or None if not found
        """
        clusters = self.get_clusters_by_env(
            env_name_or_crn,
            cluster_shape=EXTERNALIZED_SHAPE,
        )
        for cluster in clusters:
            if (
                cluster.clusterName == name
                and cluster.clusterShape == EXTERNALIZED_SHAPE
                and cluster.isDefault is not True
                and cluster.status not in COMPUTE_CLUSTER_DELETED_STATUSES
            ):
                return cluster
        return None

    def get_default_cluster(
        self,
        environment: str,
    ) -> Optional[ComputeClusterSummary]:
        """
        Find the default compute cluster of an environment.

        The server-side ``default`` filter is not trusted on its own: the result
        is filtered client-side to ``isDefault is True`` and a status that is not
        DELETED. An unset (NULLABLE) or null ``isDefault`` is not a default
        cluster, and an unset or null status is not DELETED.

        The API is expected to hold at most one default cluster per environment.
        If several match anyway, the choice is deterministic rather than list
        order: an active (RUNNING) cluster is preferred, then a creating one, then
        any other; ties are broken by the lowest ``clusterCrn``. The ranking is a
        convention of this client, not an API guarantee.

        Args:
            environment: Environment name or CRN

        Returns:
            The default ComputeClusterSummary, or None if there is none
        """
        clusters = self.get_clusters_by_env(environment, default=True)
        candidates = [
            c
            for c in clusters
            if c.isDefault is True and c.status not in COMPUTE_CLUSTER_DELETED_STATUSES
        ]
        if not candidates:
            return None

        def rank(cluster: ComputeClusterSummary) -> Any:
            if cluster.status in COMPUTE_CLUSTER_ACTIVE_STATUSES:
                order = 0
            elif cluster.status in COMPUTE_CLUSTER_CREATING_STATUSES:
                order = 1
            else:
                order = 2
            crn = cluster.clusterCrn
            return (order, crn if isinstance(crn, str) else "")

        return min(candidates, key=rank)

    def wait_for_default_cluster(
        self,
        environment: str,
        timeout: int = 3600,
        delay: int = 15,
    ) -> ComputeCluster:
        """
        Wait for the default compute cluster of an environment to be active.

        Phase 1 polls ``get_default_cluster`` while no default cluster exists
        yet, or while its status is still null/unset (the API can return a
        cluster before it reports a status). Phase 2 hands over to
        ``wait_for_cluster_state`` for the cluster CRN. ``timeout`` covers both
        phases: the handover receives only the time that is left.

        Args:
            environment: Environment name or CRN
            timeout: Maximum seconds for the whole wait, including the wait for
                the cluster to appear
            delay: Polling interval in seconds

        Returns:
            ComputeCluster (from describeCluster) in an active status

        Raises:
            CdpError: On timeout or when the cluster enters a failed status
        """
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for the default compute cluster of "
                    f"environment '{environment}' to appear after {timeout} seconds",
                )

            cluster = self.get_default_cluster(environment)
            if cluster is not None and isinstance(cluster.clusterCrn, str):
                status = cluster.status
                if status in COMPUTE_CLUSTER_FAILED_STATUSES:
                    msg = cluster.message
                    if not isinstance(msg, str):
                        msg = "Unknown error"
                    raise CdpError(
                        f"Default compute cluster entered failed state "
                        f"'{status}': {msg}",
                    )
                if isinstance(status, str):
                    break
            time.sleep(delay)

        remaining = max(0, timeout - (time.time() - start_time))
        return self.wait_for_cluster_state(
            cluster.clusterCrn,
            COMPUTE_CLUSTER_ACTIVE_STATUSES,
            timeout=remaining,
            delay=delay,
        )

    def create_cluster(
        self,
        name: str,
        environment: str,
        description: Optional[str] = None,
        network: Optional[CommonNetwork] = None,
        tags: Optional[Dict[str, str]] = None,
        skip_validation: Optional[bool] = None,
    ) -> CreateClusterResponse:
        """
        Create an externalized compute cluster.

        Args:
            name: Name for the new cluster
            environment: CRN of the CDP environment (the API requires a CRN)
            description: Optional description
            network: Optional CommonNetwork
            tags: Optional map of string tags
            skip_validation: If True, skip pre-flight validation

        Returns:
            CreateClusterResponse
        """
        data: Dict[str, Any] = {
            "name": name,
            "environment": environment,
        }
        if description is not None:
            data["description"] = description
        if network is not None:
            data["network"] = to_dict(network)
        if tags is not None:
            data["tags"] = tags
        if skip_validation is not None:
            data["skipValidation"] = skip_validation

        response = self.api_client.post(
            "/api/v1/compute/createCluster",
            data=data,
        )
        return from_dict(CreateClusterResponse, response)

    def delete_cluster(
        self,
        cluster_crn: str,
        force: Optional[bool] = None,
        skip_validation: Optional[bool] = None,
        skip_workloads_validation: Optional[bool] = None,
    ) -> DeleteClusterResponse:
        """
        Delete an externalized compute cluster.

        Args:
            cluster_crn: CRN of the cluster to delete
            force: If True, force delete even if workloads are running
            skip_validation: If True, skip pre-flight validation
            skip_workloads_validation: If True, skip workload validation checks

        Returns:
            DeleteClusterResponse
        """
        data: Dict[str, Any] = {"clusterCrn": cluster_crn}
        if force is not None:
            data["force"] = force
        if skip_validation is not None:
            data["skipValidation"] = skip_validation
        if skip_workloads_validation is not None:
            data["skipWorkloadsValidation"] = skip_workloads_validation

        response = self.api_client.post(
            "/api/v1/compute/deleteCluster",
            data=data,
        )
        return from_dict(DeleteClusterResponse, response)

    def wait_for_cluster_state(
        self,
        cluster_crn: str,
        target_states: Set[str],
        error_states: Set[str] = COMPUTE_CLUSTER_FAILED_STATUSES,
        timeout: int = 3600,
        delay: int = 15,
    ) -> Optional[ComputeCluster]:
        """
        Wait for a compute cluster to reach one of the target states.

        If the cluster cannot be found, it is treated as gone (returns None)
        only when a deleted status is one of the targets; otherwise polling
        continues, since a freshly created cluster may not be visible yet.

        Args:
            cluster_crn: CRN of the cluster to monitor
            target_states: Acceptable target status strings
            error_states: Statuses treated as non-recoverable failures
            timeout: Maximum seconds to wait before raising CdpError
            delay: Polling interval in seconds

        Returns:
            ComputeCluster when a target state is reached, or None if the
            cluster is gone and a deleted status was a target

        Raises:
            CdpError: On timeout or when the cluster enters an error state
        """
        start_time = time.time()
        waiting_for_delete = bool(set(target_states) & COMPUTE_CLUSTER_DELETED_STATUSES)

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CdpError(
                    f"Timeout waiting for compute cluster to reach {sorted(target_states)} "
                    f"after {timeout} seconds",
                )

            cluster = self.get_cluster_by_crn(cluster_crn)

            if cluster is None:
                if waiting_for_delete:
                    return None
                time.sleep(delay)
                continue

            current_state = cluster.status

            if current_state in target_states:
                return cluster

            if current_state in error_states:
                msg = cluster.message
                if msg is NULLABLE or msg is None:
                    msg = "Unknown error"
                raise CdpError(
                    f"Compute cluster entered failed state '{current_state}': {msg}",
                )

            time.sleep(delay)
