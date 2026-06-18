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
    Dict,
    List,
    Optional,
    Union
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
)


@dataclass
class Connector:
    """CDP Data Warehouse Database Connector."""

    id: Union[str, None, type] = NULLABLE
    name: Union[str, None, type] = NULLABLE
    template: Union[str, None, type] = NULLABLE
    crn: Union[str, None, type] = NULLABLE
    description: Union[str, None, type] = NULLABLE
    config: Union[Dict[str, str], None, type] = NULLABLE
    createdAt: Union[int, None, type] = NULLABLE
    createdBy: Union[str, None, type] = NULLABLE
    updatedAt: Union[int, None, type] = NULLABLE
    updatedBy: Union[str, None, type] = NULLABLE


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
        return [
            from_dict(Connector, c) for c in response.get("connectors", [])
        ]

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
