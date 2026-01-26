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

import pytest
from typing import List, Dict, Any

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    filter_subnets_by_expression,
)


# ==================== Test Fixtures ====================


@pytest.fixture
def sample_subnets() -> List[Dict[str, Any]]:
    """
    Sample subnet data representing a typical AWS environment with:
    - Public subnets across 3 AZs
    - Private subnets across 3 AZs
    - Different CIDR ranges
    """
    return [
        {
            "subnetId": "subnet-pub-001",
            "subnetName": "test-pub-subnet-1",
            "availabilityZone": "us-east-1a",
            "cidr": "10.0.1.0/24",
        },
        {
            "subnetId": "subnet-pub-002",
            "subnetName": "test-pub-subnet-2",
            "availabilityZone": "us-east-1b",
            "cidr": "10.0.2.0/24",
        },
        {
            "subnetId": "subnet-pub-003",
            "subnetName": "test-pub-subnet-3",
            "availabilityZone": "us-east-1c",
            "cidr": "10.0.3.0/24",
        },
        {
            "subnetId": "subnet-pvt-001",
            "subnetName": "test-pvt-0-subnet-1",
            "availabilityZone": "us-east-1a",
            "cidr": "10.0.11.0/24",
        },
        {
            "subnetId": "subnet-pvt-002",
            "subnetName": "test-pvt-0-subnet-2",
            "availabilityZone": "us-east-1b",
            "cidr": "10.0.12.0/24",
        },
        {
            "subnetId": "subnet-pvt-003",
            "subnetName": "test-pvt-0-subnet-3",
            "availabilityZone": "us-east-1c",
            "cidr": "10.0.13.0/24",
        },
        {
            "subnetId": "subnet-pvt-alt-001",
            "subnetName": "test-pvt-1-subnet-1",
            "availabilityZone": "us-east-1a",
            "cidr": "10.0.21.0/24",
        },
    ]


# ==================== Real-World Scenario Tests ====================


class TestRealWorldScenarios:
    """Test real-world filtering scenarios like those in df_service.yml."""

    def test_df_service_yml_public_subnet_filtering(self, sample_subnets):
        """
        Test the exact filtering scenario from df_service.yml:
        cluster_subnets_filter: "[?contains(subnetName, 'pub')]"
        loadbalancer_subnets_filter: "[?contains(subnetName, 'pub')]"
        """
        # Legacy JMESPath filter example
        cluster_filter = "[?contains(subnetName, 'pub')]"
        lb_filter = "[?contains(subnetName, 'pub')]"

        cluster_subnets = filter_subnets_by_expression(sample_subnets, cluster_filter)
        lb_subnets = filter_subnets_by_expression(sample_subnets, lb_filter)

        # Both should return the 3 public subnets
        assert len(cluster_subnets) == 3
        assert len(lb_subnets) == 3
        assert cluster_subnets == lb_subnets
        assert all("pub" in subnet_id for subnet_id in cluster_subnets)

    def test_df_service_private_cluster_setup(self, sample_subnets):
        """Test filtering for private cluster setup (private subnets only)."""
        cluster_filter = "[?contains(subnetName, 'pvt-0')]"

        cluster_subnets = filter_subnets_by_expression(sample_subnets, cluster_filter)

        assert len(cluster_subnets) == 3
        assert all("pvt" in subnet_id for subnet_id in cluster_subnets)

    def test_df_service_mixed_setup(self, sample_subnets):
        """Test mixed setup: private cluster with public load balancer."""
        cluster_filter = "[?contains(subnetName, 'pvt-0')]"
        lb_filter = "[?contains(subnetName, 'pub')]"

        cluster_subnets = filter_subnets_by_expression(sample_subnets, cluster_filter)
        lb_subnets = filter_subnets_by_expression(sample_subnets, lb_filter)

        assert len(cluster_subnets) == 3  # Private subnets
        assert len(lb_subnets) == 3  # Public subnets
        assert cluster_subnets != lb_subnets

    def test_multi_az_deployment(self, sample_subnets):
        """Test ensuring subnets span multiple availability zones."""
        pub_subnets = filter_subnets_by_expression(sample_subnets, "pub")

        # Get the subnets from sample_subnets that match the pub_subnets IDs
        filtered_subnets = [s for s in sample_subnets if s["subnetId"] in pub_subnets]

        # Extract unique AZs
        availability_zones = {s["availabilityZone"] for s in filtered_subnets}

        # Should have 3 AZs for high availability
        assert len(availability_zones) == 3
        assert "us-east-1a" in availability_zones
        assert "us-east-1b" in availability_zones
        assert "us-east-1c" in availability_zones

    def test_cidr_range_validation(self, sample_subnets):
        """Test validating subnets belong to specific CIDR range."""
        # Get all subnets in 10.0.0.0/16 range
        filtered = filter_subnets_by_expression(
            sample_subnets, "startswith(cidr, '10.0.')"
        )

        # All sample subnets should be in 10.0.0.0/16
        assert len(filtered) == 7

    def test_combining_multiple_filters(self, sample_subnets):
        """Test combining multiple filters (simulating complex requirements)."""
        # First filter: get public subnets
        pub_subnets = filter_subnets_by_expression(sample_subnets, "pub")

        # Second filter: from public subnets, get those in us-east-1a
        pub_subnet_objects = [s for s in sample_subnets if s["subnetId"] in pub_subnets]
        az_filtered = filter_subnets_by_expression(
            pub_subnet_objects,
            "availabilityZone == 'us-east-1a'",
        )

        # Should get exactly 1 subnet: subnet-pub-001
        assert len(az_filtered) == 1
        assert "subnet-pub-001" in az_filtered
