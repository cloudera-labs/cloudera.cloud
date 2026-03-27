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

    def list_services(self, remove_deleted: bool = True) -> Dict[str, Any]:
        """
        List Data Engineering services.

        Args:
            remove_deleted: Filter out deleted CDE services from the list.
                Defaults to True to only show active services.

        Returns:
            Dictionary containing:
                - services: List of ServiceSummary objects
        """
        data: Dict[str, Any] = {"removeDeleted": remove_deleted}

        return self.api_client.post(
            "/api/v1/de/listServices",
            data=data,
            squelch={404: {"services": []}},
        )

    def describe_service(self, cluster_id: str) -> Dict[str, Any]:
        """
        Describe a Data Engineering service.

        Args:
            cluster_id: The cluster ID of the service

        Returns:
            Dictionary containing service details, or empty dict if not found or in invalid state

        Note:
            Returns empty dict for both 404 (not found) and 500 (invalid state) errors.
        """
        data = {"clusterId": cluster_id}
        return self.api_client.post(
            "/api/v1/de/describeService",
            data=data,
            squelch={404: {}, 500: {}},
        )

    def get_service_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get service details by service name.

        Args:
            name: The service name

        Returns:
            Service details dict, or None if not found
        """
        services = self.list_services()
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
            Service details dict, or None if not found
        """
        result = self.describe_service(cluster_id)

        if not result or not result.get("service"):
            return None

        return result

    def get_service_by_env_name(self, env_name: str) -> List[Dict[str, Any]]:
        """
        Get all active service details for an environment.

        Note: Unlike DataFlow, Data Engineering supports multiple services per environment.

        Args:
            env_name: The environment name

        Returns:
            List of active service details dicts (can be empty if none found)
        """
        services = self.list_services()
        results = []
        for service in services.get("services", []):
            if service.get("environmentName") == env_name:
                cluster_id = service.get("clusterId")
                if cluster_id:
                    service_details = self.describe_service(cluster_id)
                    if service_details and service_details.get("service"):
                        results.append(service_details)
        return results

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
