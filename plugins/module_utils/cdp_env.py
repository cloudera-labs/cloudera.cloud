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
A REST client for the Cloudera on Cloud Platform (CDP) Environments API
"""

from typing import Any, Dict, List, Optional

import jmespath

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


def convert_to_jmespath_query(filter_value: str) -> str:
    """
    Convert a filter value to a JMESPath query.

    If the filter value is already a JMESPath query (starts with '['), return it as-is.
    Otherwise, convert a simple string pattern to a JMESPath query that checks if
    subnetName contains the pattern (case-insensitive).

    Args:
        filter_value: Either a JMESPath query string or a simple pattern string

    Returns:
        A valid JMESPath query string
    """
    # If it already looks like a JMESPath query, return as-is
    if filter_value.startswith("["):
        return filter_value

    # Convert simple string pattern to JMESPath query
    # This maintains backward compatibility for users who just pass "pub" or "pvt"
    return f"[?contains(subnetName, '{filter_value}')]"


def filter_subnets_by_jmespath(
    subnets: List[Dict[str, Any]],
    jmespath_query: str,
) -> List[str]:
    """
    Apply a JMESPath query to an array of subnets and return the IDs of the selected subnets.

    The query must only filter the array, without applying any projection. The query result must also be an
    array of subnet objects.

    Args:
        subnets: An array of subnet objects. Each subnet in the array is an object with the following attributes:
                 subnetId, subnetName, availabilityZone, cidr.
        jmespath_query: JMESPath query to filter the subnet array.
                       Examples:
                       - "[?contains(subnetName, 'pub')]" - filters subnets with 'pub' in the name
                       - "[?contains(subnetName, 'pvt')]" - filters subnets with 'pvt' in the name
                       - "[?availabilityZone=='us-east-1a']" - filters by availability zone

    Returns:
        An array of subnet IDs from the filtered subnets.
    """
    filtered_ids = []

    try:
        # Apply JMESPath query to filter subnets
        filtered_subnets = jmespath.search(jmespath_query, subnets)

        # Extract subnet IDs from filtered results
        if filtered_subnets:
            for subnet in filtered_subnets:
                subnet_id = subnet.get("subnetId")
                if subnet_id:
                    filtered_ids.append(subnet_id)
    except (jmespath.exceptions.JMESPathError, AttributeError, TypeError) as e:
        pass

    return filtered_ids


class CdpEnvClient:
    """CDP Environments API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP Environments client.

        Args:
            api_client: CdpClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def describe_environment(self, environment_name: str) -> Optional[Dict[str, Any]]:
        """
        Describe an environment by name or CRN.

        Args:
            environment_name: Name or CRN of the environment

        Returns:
            Environment details dict, or None if environment doesn't exist
        """
        json_data: Dict[str, Any] = {
            "environmentName": environment_name,
        }

        response = self.api_client.post(
            "/api/v1/environments2/describeEnvironment",
            json_data=json_data,
            squelch={404: None},
        )

        return response.get("environment") if response else None

    def get_environment_subnets(self, environment_name: str) -> List[Dict[str, Any]]:
        """
        Get subnet information for an environment.

        Returns a list of subnets with the following structure:
        - subnetId: The id of the subnet
        - subnetName: The name of the subnet
        - availabilityZone: The availability zone of the subnet
        - cidr: The CIDR IP range of the subnet

        Args:
            environment_name: Name or CRN of the environment

        Returns:
            List of subnet dictionaries with subnetId, subnetName, availabilityZone, and cidr
        """
        env = self.describe_environment(environment_name)
        if not env:
            return []

        # Extract subnets from the network structure
        subnets = []

        # Get subnet metadata which contains the detailed subnet information
        network = env.get("network", {})
        subnet_metadata = network.get("subnetMetadata", {})

        # The subnetMetadata is a map where keys are subnet IDs and values are CloudSubnet objects
        for subnet_id, subnet_info in subnet_metadata.items():
            subnet = {
                "subnetId": subnet_id,
                "subnetName": subnet_info.get("subnetName", ""),
                "availabilityZone": subnet_info.get("availabilityZone", ""),
                "cidr": subnet_info.get("cidr", ""),
            }
            subnets.append(subnet)

        # If no subnet metadata, try to get subnet IDs from the network object
        if not subnets:
            subnet_ids = network.get("subnetIds", [])
            for subnet_id in subnet_ids:
                subnets.append(
                    {
                        "subnetId": subnet_id,
                        "subnetName": "",
                        "availabilityZone": "",
                        "cidr": "",
                    },
                )

        return subnets

    def list_environments(self) -> List[Dict[str, Any]]:
        """
        List all environments.

        Returns:
            List of environment summary dictionaries
        """
        json_data: Dict[str, Any] = {}

        response = self.api_client.post(
            "/api/v1/environments2/listEnvironments",
            json_data=json_data,
        )

        return response.get("environments", []) if response else []

    def get_environment_by_name(
        self,
        environment_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get environment by name (using list and filter).

        Args:
            environment_name: Name of the environment

        Returns:
            Environment dict or None if not found
        """
        environments = self.list_environments()
        for env in environments:
            if env.get("environmentName") == environment_name:
                return env
        return None

    def get_environment_crn(self, environment_name: str) -> Optional[str]:
        """
        Get the CRN for an environment by name.

        Args:
            environment_name: Name of the environment

        Returns:
            Environment CRN or None if not found
        """
        env = self.get_environment_by_name(environment_name)
        return env.get("crn") if env else None

    def filter_subnets_by_name_pattern(
        self,
        subnets: List[Dict[str, Any]],
        pattern: str,
    ) -> List[str]:
        """
        Filter subnets by name pattern and return subnet IDs.

        Args:
            subnets: List of subnet dicts with subnetId, subnetName, availabilityZone, cidr
            pattern: String pattern to search for in subnet names (case-insensitive)

        Returns:
            List of subnet IDs where subnetName contains the pattern
        """
        filtered_ids = []
        pattern_lower = pattern.lower()

        for subnet in subnets:
            subnet_name = subnet.get("subnetName", "")
            if pattern_lower in subnet_name.lower():
                subnet_id = subnet.get("subnetId")
                if subnet_id:
                    filtered_ids.append(subnet_id)

        return filtered_ids

    def filter_subnets_by_az(
        self,
        subnets: List[Dict[str, Any]],
        availability_zone: str,
    ) -> List[str]:
        """
        Filter subnets by availability zone and return subnet IDs.

        Args:
            subnets: List of subnet dicts with subnetId, subnetName, availabilityZone, cidr
            availability_zone: Availability zone to filter by

        Returns:
            List of subnet IDs in the specified availability zone
        """
        filtered_ids = []

        for subnet in subnets:
            if subnet.get("availabilityZone") == availability_zone:
                subnet_id = subnet.get("subnetId")
                if subnet_id:
                    filtered_ids.append(subnet_id)

        return filtered_ids

    def filter_subnets_by_cidr_prefix(
        self,
        subnets: List[Dict[str, Any]],
        cidr_prefix: str,
    ) -> List[str]:
        """
        Filter subnets by CIDR prefix and return subnet IDs.

        Args:
            subnets: List of subnet dicts with subnetId, subnetName, availabilityZone, cidr
            cidr_prefix: CIDR prefix to match (e.g., "10.0.")

        Returns:
            List of subnet IDs where CIDR starts with the prefix
        """
        filtered_ids = []

        for subnet in subnets:
            cidr = subnet.get("cidr", "")
            if cidr.startswith(cidr_prefix):
                subnet_id = subnet.get("subnetId")
                if subnet_id:
                    filtered_ids.append(subnet_id)

        return filtered_ids
