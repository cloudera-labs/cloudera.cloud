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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
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
        except Exception:
            return None
