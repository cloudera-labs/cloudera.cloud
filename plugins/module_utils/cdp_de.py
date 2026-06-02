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
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)


class CdpDeClient:
    """CDP Data Engineering API client."""

    # Service statuses that cannot be described (deletion/upgrade failures)
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
                Defaults to True to only show active services.
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
            filtered_services = [
                s for s in services if s.get("environmentName") == env_name
            ]
            result["services"] = filtered_services

        return result

    def describe_service(self, cluster_id: str) -> Dict[str, Any]:
        """
        Describe a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            Dictionary containing service details, or empty dict if not found or in invalid state

        Note:
            Returns empty dict for 404 errors.
        """
        data = {"clusterId": cluster_id}
        return self.api_client.post(
            "/api/v1/de/describeService",
            data=data,
            squelch={404: {}},
        )

    def get_service_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get service details by service name.

        Args:
            name: The service name

        Returns:
            Service details dict, or empty dict if not found
        """
        services = self.list_services()
        for service in services.get("services", []):
            if service.get("name") == name:
                cluster_id = service.get("clusterId")
                if cluster_id:
                    result = self.describe_service(cluster_id)
                    if result and result.get("service"):
                        return result
        return {}

    def get_service_by_cluster_id(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get service details by cluster ID.

        Args:
            cluster_id: The cluster ID

        Returns:
            Service details dict, or empty dict if not found
        """
        result = self.describe_service(cluster_id)

        if not result or not result.get("service"):
            return {}

        return result

    def list_virtual_clusters(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        List virtual clusters in a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            List of virtual cluster summary objects
        """
        data = {"clusterId": cluster_id}
        result = self.api_client.post(
            "/api/v1/de/listVcs",
            data=data,
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
        data = {"clusterId": cluster_id, "vcId": vc_id}
        result = self.api_client.post(
            "/api/v1/de/describeVc",
            data=data,
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
