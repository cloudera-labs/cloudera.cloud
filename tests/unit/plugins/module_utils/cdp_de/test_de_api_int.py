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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import CdpDeClient

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def de_client(test_cdp_client) -> CdpDeClient:
    """Fixture to provide a Data Engineering client for tests."""
    return CdpDeClient(api_client=test_cdp_client)


@pytest.fixture
def valid_de_service(de_client):
    """
    Fixture to find a valid, describable Data Engineering service for testing.

    Returns a service summary dict from list_services that can be described.
    Skips test if no valid services are found.
    """
    services = de_client.list_services().get("services", [])

    if not services:
        pytest.skip("No Data Engineering services available for testing")

    # Find a service that can be described successfully (skip failed states)
    for svc in services:
        if svc.get("status") in CdpDeClient.FAILED_STATUSES:
            continue

        cluster_id = svc.get("clusterId")
        if cluster_id:
            details = de_client.describe_service(cluster_id)
            if details and details.get("service"):
                return svc

    pytest.skip("No describable Data Engineering services available for testing")


@pytest.fixture
def valid_virtual_cluster(de_client, valid_de_service):
    """
    Fixture to find a valid virtual cluster for testing.

    Returns a virtual cluster summary dict from list_virtual_clusters.
    Skips test if no virtual clusters are found.
    """
    cluster_id = valid_de_service.get("clusterId")
    vcs = de_client.list_virtual_clusters(cluster_id)

    if not vcs:
        pytest.skip("No virtual clusters available for testing")

    # Find a virtual cluster that can be described successfully
    for vc in vcs:
        vc_id = vc.get("vcId")
        if vc_id:
            details = de_client.describe_virtual_cluster(cluster_id, vc_id)
            if details:
                return vc

    pytest.skip("No describable virtual clusters available for testing")


class TestCdpDeClientIntegration:
    """Integration tests for CdpDeClient using real CDP API."""

    def test_list_services(self, de_client):
        """Test listing Data Engineering services."""
        response = de_client.list_services()

        # Validate response structure
        assert "services" in response
        assert isinstance(response["services"], list)

        # If services exist, validate their structure
        if response["services"]:
            service = response["services"][0]
            assert "clusterId" in service
            assert "name" in service
            assert "environmentName" in service

    def test_list_services_include_deleted(self, de_client):
        """Test listing Data Engineering services including deleted ones."""
        response = de_client.list_services(remove_deleted=False)

        # Validate response structure
        assert "services" in response
        assert isinstance(response["services"], list)

    def test_describe_service(self, de_client, valid_de_service):
        """Test describing a Data Engineering service."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.describe_service(cluster_id)

        # Validate response structure
        assert response is not None
        assert "service" in response
        service = response["service"]

        # Validate service details
        assert service["clusterId"] == cluster_id
        assert "name" in service
        assert "environmentName" in service
        assert "status" in service

    def test_describe_nonexistent_service(self, de_client):
        """Test describing a service that doesn't exist."""
        response = de_client.describe_service("nonexistent-cluster-12345")

        # Should return empty dict for 404 or 500 errors
        assert response == {}

    def test_get_service_by_name(self, de_client, valid_de_service):
        """Test getting service details by name."""
        service_name = valid_de_service.get("name")

        response = de_client.get_service_by_name(service_name)

        # Validate response
        assert response is not None
        assert "service" in response
        assert response["service"]["name"] == service_name
        assert "clusterId" in response["service"]

    def test_get_service_by_name_not_found(self, de_client):
        """Test getting service by name when it doesn't exist."""
        response = de_client.get_service_by_name("nonexistent-service-12345")

        # Should return None when service not found
        assert response is None

    def test_get_service_by_cluster_id(self, de_client, valid_de_service):
        """Test getting service details by cluster ID."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.get_service_by_cluster_id(cluster_id)

        # Validate response
        assert response is not None
        assert "service" in response
        assert response["service"]["clusterId"] == cluster_id
        assert "name" in response["service"]

    def test_get_service_by_cluster_id_not_found(self, de_client):
        """Test getting service by cluster ID when it doesn't exist."""
        response = de_client.get_service_by_cluster_id("nonexistent-cluster-12345")

        # Should return None when service not found
        assert response is None

    def test_list_virtual_clusters(self, de_client, valid_de_service):
        """Test listing virtual clusters in a service."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.list_virtual_clusters(cluster_id)

        # Validate response structure
        assert isinstance(response, list)

        # If virtual clusters exist, validate their structure
        if response:
            vc = response[0]
            assert "vcId" in vc
            assert "vcName" in vc
            assert "clusterId" in vc

    def test_list_virtual_clusters_nonexistent_service(self, de_client):
        """Test listing virtual clusters for a service that doesn't exist."""
        response = de_client.list_virtual_clusters("nonexistent-cluster-12345")

        # Should return empty list for 404 error
        assert isinstance(response, list)
        assert len(response) == 0

    def test_describe_virtual_cluster(
        self,
        de_client,
        valid_de_service,
        valid_virtual_cluster,
    ):
        """Test describing a virtual cluster."""
        cluster_id = valid_de_service.get("clusterId")
        vc_id = valid_virtual_cluster.get("vcId")

        response = de_client.describe_virtual_cluster(cluster_id, vc_id)

        # Validate response
        assert response is not None
        assert response["vcId"] == vc_id
        assert "vcName" in response
        assert "clusterId" in response
        assert response["clusterId"] == cluster_id

    def test_describe_virtual_cluster_not_found(self, de_client, valid_de_service):
        """Test describing a virtual cluster that doesn't exist."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.describe_virtual_cluster(
            cluster_id,
            "nonexistent-vc-12345",
        )

        # Should return None for 404 error
        assert response is None

    def test_get_virtual_cluster_by_name(
        self,
        de_client,
        valid_de_service,
        valid_virtual_cluster,
    ):
        """Test getting virtual cluster details by name."""
        cluster_id = valid_de_service.get("clusterId")
        vc_name = valid_virtual_cluster.get("vcName")

        response = de_client.get_virtual_cluster_by_name(cluster_id, vc_name)

        # Validate response
        assert response is not None
        assert response["vcName"] == vc_name
        assert "vcId" in response
        assert "clusterId" in response

    def test_get_virtual_cluster_by_name_not_found(self, de_client, valid_de_service):
        """Test getting virtual cluster by name when it doesn't exist."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.get_virtual_cluster_by_name(
            cluster_id,
            "nonexistent-vc-12345",
        )

        # Should return None when virtual cluster not found
        assert response is None

    def test_service_details_completeness(self, de_client, valid_de_service):
        """Test that describe_service returns all expected fields."""
        cluster_id = valid_de_service.get("clusterId")

        response = de_client.describe_service(cluster_id)

        # Validate response has service details
        assert "service" in response
        service = response["service"]

        # Check for expected core fields (should always be present)
        expected_fields = ["clusterId", "name", "environmentName", "status"]
        for field in expected_fields:
            assert field in service, f"Missing expected field: {field}"

        # Check for common optional fields (may or may not be present)
        optional_fields = [
            "environmentCrn",
            "cloudPlatform",
            "clusterFqdn",
            "creatorEmail",
            "creatorCrn",
            "resources",
        ]
        for field in optional_fields:
            if field in service:
                # If present, verify it's not None
                assert service[field] is not None, f"Field {field} is None"
