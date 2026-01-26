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
import re

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


def parse_filter_expression(filter_expr: str) -> Dict[str, Any]:
    """
    Parse a filter expression into a structured format.

    Supports multiple filter expression formats:
    1. **JMESPath syntax (legacy)**: "[?contains(subnetName, 'pvt-0')]" - FULLY SUPPORTED
    2. **Simple string pattern**: "pub" or "pvt-0" - matches substring in subnetName
    3. **Filter expressions**:
       - contains(field, 'value') - checks if field contains value
       - field == 'value' - checks if field equals value (exact match)
       - field != 'value' - checks if field does not equal value
       - startswith(field, 'value') - checks if field starts with value

    Args:
        filter_expr: Filter expression string in any supported format

    Returns:
        Dictionary with parsed filter criteria
    """
    # Remove leading/trailing whitespace and array brackets if present
    filter_expr = filter_expr.strip()
    if filter_expr.startswith("[?") and filter_expr.endswith("]"):
        filter_expr = filter_expr[2:-1].strip()

    # Try to parse contains() function
    contains_match = re.match(r"contains\((\w+),\s*['\"](.+?)['\"]\)", filter_expr)
    if contains_match:
        field, value = contains_match.groups()
        return {"type": "contains", "field": field, "value": value}

    # Try to parse startswith() function
    startswith_match = re.match(r"startswith\((\w+),\s*['\"](.+?)['\"]\)", filter_expr)
    if startswith_match:
        field, value = startswith_match.groups()
        return {"type": "startswith", "field": field, "value": value}

    # Try to parse equality (==)
    eq_match = re.match(r"(\w+)\s*==\s*['\"](.+?)['\"]", filter_expr)
    if eq_match:
        field, value = eq_match.groups()
        return {"type": "equals", "field": field, "value": value}

    # Try to parse inequality (!=)
    neq_match = re.match(r"(\w+)\s*!=\s*['\"](.+?)['\"]", filter_expr)
    if neq_match:
        field, value = neq_match.groups()
        return {"type": "not_equals", "field": field, "value": value}

    # Default: treat as simple substring match on subnetName
    return {"type": "contains", "field": "subnetName", "value": filter_expr}


def apply_filter_to_subnet(
    subnet: Dict[str, Any],
    filter_criteria: Dict[str, Any],
) -> bool:
    """
    Apply filter criteria to a single subnet.

    Args:
        subnet: Subnet dictionary with subnetId, subnetName, availabilityZone, cidr
        filter_criteria: Parsed filter criteria from parse_filter_expression()

    Returns:
        True if subnet matches the filter criteria, False otherwise
    """
    filter_type = filter_criteria.get("type")
    field = filter_criteria.get("field")
    value = filter_criteria.get("value")

    # Get the field value from subnet
    field_value = subnet.get(field, "")

    # Apply the appropriate filter operation
    if filter_type == "contains":
        return value.lower() in field_value.lower()
    elif filter_type == "startswith":
        return field_value.lower().startswith(value.lower())
    elif filter_type == "equals":
        return field_value == value
    elif filter_type == "not_equals":
        return field_value != value

    return False


def filter_subnets_by_expression(
    subnets: List[Dict[str, Any]],
    filter_expr: str,
) -> List[str]:
    """
    Filter subnets using a filter expression and return subnet IDs.

    **FULLY BACKWARD COMPATIBLE** with JMESPath syntax from previous versions.
    All existing filter expressions will continue to work without changes.

    Supported filter formats (in order of recommendation):

    1. **Legacy JMESPath syntax (BACKWARD COMPATIBLE)**:
       - "[?contains(subnetName, 'pvt-0')]" - filters subnets with 'pvt-0' in name
       - "[?contains(subnetName, 'pub')]" - filters subnets with 'pub' in name
       - "[?contains(cidr, '10.0')]" - filters subnets with '10.0' in CIDR

    2. **Simple string pattern** (shorthand for subnetName contains):
       - "pvt-0" - matches subnets with 'pvt-0' in subnetName (case-insensitive)
       - "pub" - matches subnets with 'pub' in subnetName (case-insensitive)

    3. **New filter expressions** (optional, for advanced use cases):
       - "contains(subnetName, 'pvt-0')" - same as legacy JMESPath
       - "availabilityZone == 'us-east-1a'" - exact match on availability zone
       - "startswith(cidr, '10.0.')" - checks if CIDR starts with prefix
       - "availabilityZone != 'us-west-2'" - exclude specific zone

    Args:
        subnets: List of subnet dicts with subnetId, subnetName, availabilityZone, cidr
        filter_expr: Filter expression string (any supported format)

    Returns:
        List of subnet IDs that match the filter expression

    Examples:
        >>> # Legacy JMESPath (works exactly as before)
        >>> filter_subnets_by_expression(subnets, "[?contains(subnetName, 'pvt-0')]")
        ['subnet-001', 'subnet-003']

        >>> # Simple pattern (shorthand)
        >>> filter_subnets_by_expression(subnets, "pvt-0")
        ['subnet-001', 'subnet-003']

        >>> # New filter expression (optional)
        >>> filter_subnets_by_expression(subnets, "availabilityZone == 'us-east-1a'")
        ['subnet-001', 'subnet-002']
    """
    if not filter_expr or not subnets:
        return []

    # Parse the filter expression
    filter_criteria = parse_filter_expression(filter_expr)

    # Apply filter to each subnet and collect matching IDs
    filtered_ids = []
    for subnet in subnets:
        if apply_filter_to_subnet(subnet, filter_criteria):
            subnet_id = subnet.get("subnetId")
            if subnet_id:
                filtered_ids.append(subnet_id)

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
