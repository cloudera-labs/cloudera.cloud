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
A REST client for the Cloudera Data Warehouse (CDW) API
"""

from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
)


@dataclass
class Connector:
    """CDP Data Warehouse Database Connector."""

    id: Union[str, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
    template: Union[str, None, NULLABLE] = NULLABLE
    crn: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    config: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    createdAt: Union[int, None, NULLABLE] = NULLABLE
    createdBy: Union[str, None, NULLABLE] = NULLABLE
    updatedAt: Union[int, None, NULLABLE] = NULLABLE
    updatedBy: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class ConnectorTestJob:
    """CDP Data Warehouse Connector Test Job details."""

    jobId: Union[str, None, NULLABLE] = NULLABLE
    status: Union[str, None, NULLABLE] = NULLABLE
    jobStartTime: Union[str, None, NULLABLE] = NULLABLE
    jobFinishTime: Union[str, None, NULLABLE] = NULLABLE
    labels: Union[Dict[str, str], None, NULLABLE] = NULLABLE
    outputLog: Union[str, None, NULLABLE] = NULLABLE


class CdpDwClient:
    """CDP Data Warehouse API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP Data Warehouse client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def list_connectors(self, cluster_id: str) -> List[Connector]:
        """
        List Database Connectors in a cluster.

        Args:
            cluster_id: The ID of the cluster

        Returns:
            List of Connector dataclass instances
        """
        data = {"clusterId": cluster_id}
        response = self.api_client.post(
            "/api/v1/dw/listConnectors",
            data=data,
            squelch={404: {"connectors": []}},
        )
        return [from_dict(Connector, c) for c in response.get("connectors", [])]

    def get_connector_by_id(
        self,
        cluster_id: str,
        connector_id: str,
    ) -> Optional[Connector]:
        """
        Get connector details by connector ID.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector

        Returns:
            Connector dataclass instance, or None if not found
        """
        for connector in self.list_connectors(cluster_id):
            if connector.id == connector_id:
                return connector
        return None

    def get_connector_by_name(
        self,
        cluster_id: str,
        name: str,
    ) -> Optional[Connector]:
        """
        Get connector details by name.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the connector

        Returns:
            Connector dataclass instance, or None if not found
        """
        for connector in self.list_connectors(cluster_id):
            if connector.name == name:
                return connector
        return None

    def create_connector(
        self,
        cluster_id: str,
        name: str,
        template: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, str]] = None,
    ) -> Connector:
        """
        Create a new Database Connector in a cluster.

        Args:
            cluster_id: The ID of the cluster
            name: The name of the connector
            template: The template of the connector
            description: Optional user-provided description
            config: Optional connector configuration in key-value format

        Returns:
            Connector dataclass instance of the created connector
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "name": name,
            "template": template,
        }
        if description is not None:
            data["description"] = description
        if config is not None:
            data["config"] = config
        response = self.api_client.post(
            "/api/v1/dw/createConnector",
            data=data,
        )
        return from_dict(Connector, response.get("result", {}))

    def update_connector(
        self,
        cluster_id: str,
        connector_id: str,
        name: str,
        description: str,
        template: str,
        config: Dict[str, str],
    ) -> Connector:
        """
        Update a Database Connector in a cluster.

        The API expects the connector's full representation, so every field is
        required; callers pass the connector's existing value for any field they
        are not changing.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to update
            name: The name of the connector
            description: The description of the connector
            template: The template of the connector
            config: The connector configuration in key-value format

        Returns:
            Connector dataclass instance reflecting the updated state
        """
        data: Dict[str, Any] = {
            "clusterId": cluster_id,
            "connectorId": connector_id,
            "name": name,
            "description": description,
            "template": template,
            "config": config,
        }
        self.api_client.post(
            "/api/v1/dw/updateConnector",
            data=data,
        )
        return self.get_connector_by_id(cluster_id, connector_id)

    def delete_connector(
        self,
        cluster_id: str,
        connector_id: str,
    ) -> None:
        """
        Delete a Database Connector from a cluster.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to delete
        """
        self.api_client.post(
            "/api/v1/dw/deleteConnector",
            data={
                "clusterId": cluster_id,
                "connectorId": connector_id,
            },
            squelch={404: {}},
        )

    def create_connector_test_job(
        self,
        cluster_id: str,
        connector_id: Optional[str] = None,
        connector_name: Optional[str] = None,
        config: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create a test job for a Connector.

        Args:
            cluster_id: The ID of the cluster
            connector_id: The ID of the connector to test
            connector_name: The name of the connector to test
            config: Optional key-value configuration overrides

        Returns:
            The ID of the created test job
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}
        if connector_id is not None:
            data["connectorId"] = connector_id
        if connector_name is not None:
            data["connectorName"] = connector_name
        if config is not None:
            data["config"] = config
        response = self.api_client.post(
            "/api/v1/dw/createConnectorTestJob",
            data=data,
        )
        return response.get("jobId", "")

    def list_connector_test_jobs(
        self,
        cluster_id: str,
        job_id: Optional[str] = None,
    ) -> List[ConnectorTestJob]:
        """
        List test jobs for a cluster's connectors.

        Args:
            cluster_id: The ID of the cluster
            job_id: Optional specific job ID to fetch

        Returns:
            List of ConnectorTestJob dataclass instances
        """
        data: Dict[str, Any] = {"clusterId": cluster_id}
        if job_id is not None:
            data["jobId"] = job_id
        response = self.api_client.post(
            "/api/v1/dw/listConnectorTestJobs",
            data=data,
            squelch={404: {"results": []}},
        )
        return [from_dict(ConnectorTestJob, j) for j in response.get("results", [])]
