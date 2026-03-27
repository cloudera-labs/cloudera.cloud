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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "cluster-abc123"
SERVICE_NAME = "test-service"
ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
VC_ID = "vc-xyz789"
VC_NAME = "test-virtual-cluster"


class TestCdpDeClient:
    """Unit tests for CdpDeClient service management methods."""

    def test_list_services_default(self, mocker):
        """Test listing all active Data Engineering services (default behavior)."""

        # Mock response data
        mock_response = {
            "services": [
                {
                    "clusterId": "cluster-123",
                    "name": "service-1",
                    "environmentName": "env-1",
                    "status": "ClusterCreationCompleted",
                },
                {
                    "clusterId": "cluster-456",
                    "name": "service-2",
                    "environmentName": "env-2",
                    "status": "ClusterCreationCompleted",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.list_services()

        # Validate the response
        assert "services" in response
        assert len(response["services"]) == 2
        assert response["services"][0]["clusterId"] == "cluster-123"
        assert response["services"][1]["name"] == "service-2"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/listServices",
            data={"removeDeleted": True},
            squelch={404: {"services": []}},
        )

    def test_list_services_include_deleted(self, mocker):
        """Test listing all Data Engineering services including deleted ones."""

        # Mock response data
        mock_response = {
            "services": [
                {
                    "clusterId": "cluster-123",
                    "name": "service-1",
                    "status": "ClusterCreationCompleted",
                },
                {
                    "clusterId": "cluster-deleted",
                    "name": "service-deleted",
                    "status": "ClusterDeletionCompleted",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.list_services(remove_deleted=False)

        # Validate the response
        assert "services" in response
        assert len(response["services"]) == 2
        assert response["services"][1]["status"] == "ClusterDeletionCompleted"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/listServices",
            data={"removeDeleted": False},
            squelch={404: {"services": []}},
        )

    def test_list_services_not_found(self, mocker):
        """Test listing services when none exist (404 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"services": []}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.list_services()

        # Validate the response - should return empty list on 404
        assert "services" in response
        assert len(response["services"]) == 0

    def test_describe_service(self, mocker):
        """Test describing a Data Engineering service."""

        # Mock response data
        mock_response = {
            "service": {
                "clusterId": CLUSTER_ID,
                "name": SERVICE_NAME,
                "environmentName": ENV_NAME,
                "environmentCrn": ENV_CRN,
                "status": "ClusterCreationCompleted",
                "cloudPlatform": "AWS",
                "clusterFqdn": "test.cloudera.com",
                "resources": {
                    "instance_type": "m5.2xlarge",
                    "min_instances": "1",
                    "max_instances": "10",
                },
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_service(CLUSTER_ID)

        # Validate the response
        assert "service" in response
        assert response["service"]["clusterId"] == CLUSTER_ID
        assert response["service"]["name"] == SERVICE_NAME
        assert response["service"]["environmentName"] == ENV_NAME
        assert response["service"]["resources"]["instance_type"] == "m5.2xlarge"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/describeService",
            data={"clusterId": CLUSTER_ID},
            squelch={404: {}, 500: {}},
        )

    def test_describe_service_not_found(self, mocker):
        """Test describing a service that doesn't exist (404 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_service("nonexistent-cluster")

        # Validate the response - should return empty dict on 404
        assert response == {}

    def test_describe_service_invalid_state(self, mocker):
        """Test describing a service in invalid state (500 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_service(CLUSTER_ID)

        # Validate the response - should return empty dict on 500
        assert response == {}

    def test_get_service_by_name(self, mocker):
        """Test getting service details by name."""

        # Mock list_services response
        list_mock = {
            "services": [
                {
                    "clusterId": CLUSTER_ID,
                    "name": SERVICE_NAME,
                    "environmentName": ENV_NAME,
                },
                {
                    "clusterId": "cluster-other",
                    "name": "other-service",
                    "environmentName": "other-env",
                },
            ],
        }

        # Mock describe_service response
        describe_mock = {
            "service": {
                "clusterId": CLUSTER_ID,
                "name": SERVICE_NAME,
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        # Test getting service by name
        response = client.get_service_by_name(SERVICE_NAME)

        # Validate the response
        assert response is not None
        assert response["service"]["name"] == SERVICE_NAME
        assert response["service"]["clusterId"] == CLUSTER_ID

        # Verify the methods were called
        client.list_services.assert_called_once()
        client.describe_service.assert_called_once_with(CLUSTER_ID)

    def test_get_service_by_name_not_found(self, mocker):
        """Test getting service by name when it doesn't exist."""

        # Mock list_services response
        list_mock = {
            "services": [
                {
                    "clusterId": "cluster-other",
                    "name": "other-service",
                    "environmentName": "other-env",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_services", return_value=list_mock)

        # Test getting service by name
        response = client.get_service_by_name("nonexistent-service")

        # Validate the response
        assert response is None

        # Verify the methods were called
        client.list_services.assert_called_once()

    def test_get_service_by_cluster_id(self, mocker):
        """Test getting service details by cluster ID."""

        # Mock describe_service response
        describe_mock = {
            "service": {
                "clusterId": CLUSTER_ID,
                "name": SERVICE_NAME,
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the describe_service method
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        # Test getting service by cluster ID
        response = client.get_service_by_cluster_id(CLUSTER_ID)

        # Validate the response
        assert response is not None
        assert response["service"]["clusterId"] == CLUSTER_ID
        assert response["service"]["name"] == SERVICE_NAME

        # Verify the method was called
        client.describe_service.assert_called_once_with(CLUSTER_ID)

    def test_get_service_by_cluster_id_not_found(self, mocker):
        """Test getting service by cluster ID when it doesn't exist."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the describe_service method to return empty dict
        mocker.patch.object(client, "describe_service", return_value={})

        # Test getting service by cluster ID
        response = client.get_service_by_cluster_id("nonexistent-cluster")

        # Validate the response
        assert response is None

    def test_get_service_by_env_name(self, mocker):
        """Test getting all services for an environment."""

        # Mock list_services response with multiple services in same env
        list_mock = {
            "services": [
                {
                    "clusterId": "cluster-123",
                    "name": "service-1",
                    "environmentName": ENV_NAME,
                },
                {
                    "clusterId": "cluster-456",
                    "name": "service-2",
                    "environmentName": ENV_NAME,
                },
                {
                    "clusterId": "cluster-other",
                    "name": "other-service",
                    "environmentName": "other-env",
                },
            ],
        }

        # Mock describe_service responses
        describe_mock_1 = {
            "service": {
                "clusterId": "cluster-123",
                "name": "service-1",
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        }
        describe_mock_2 = {
            "service": {
                "clusterId": "cluster-456",
                "name": "service-2",
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(
            client,
            "describe_service",
            side_effect=[describe_mock_1, describe_mock_2],
        )

        # Test getting services by environment name
        response = client.get_service_by_env_name(ENV_NAME)

        # Validate the response - should return list with 2 services
        assert len(response) == 2
        assert response[0]["service"]["clusterId"] == "cluster-123"
        assert response[1]["service"]["clusterId"] == "cluster-456"
        assert all(s["service"]["environmentName"] == ENV_NAME for s in response)

        # Verify the methods were called
        client.list_services.assert_called_once()
        assert client.describe_service.call_count == 2

    def test_get_service_by_env_name_not_found(self, mocker):
        """Test getting services by environment name when none exist."""

        # Mock list_services response
        list_mock = {
            "services": [
                {
                    "clusterId": "cluster-other",
                    "name": "other-service",
                    "environmentName": "other-env",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_services", return_value=list_mock)

        # Test getting services by environment name
        response = client.get_service_by_env_name("nonexistent-env")

        # Validate the response - should return empty list
        assert response == []

        # Verify the methods were called
        client.list_services.assert_called_once()

    def test_list_virtual_clusters(self, mocker):
        """Test listing virtual clusters in a service."""

        # Mock response data
        mock_response = {
            "vcs": [
                {
                    "vcId": "vc-123",
                    "vcName": "vc-1",
                    "clusterId": CLUSTER_ID,
                    "status": "ClusterCreationCompleted",
                },
                {
                    "vcId": "vc-456",
                    "vcName": "vc-2",
                    "clusterId": CLUSTER_ID,
                    "status": "ClusterCreationCompleted",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.list_virtual_clusters(CLUSTER_ID)

        # Validate the response
        assert isinstance(response, list)
        assert len(response) == 2
        assert response[0]["vcId"] == "vc-123"
        assert response[1]["vcName"] == "vc-2"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/listVcs",
            data={"clusterId": CLUSTER_ID},
            squelch={404: {"vcs": []}},
        )

    def test_list_virtual_clusters_not_found(self, mocker):
        """Test listing virtual clusters when none exist (404 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"vcs": []}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.list_virtual_clusters(CLUSTER_ID)

        # Validate the response - should return empty list on 404
        assert isinstance(response, list)
        assert len(response) == 0

    def test_describe_virtual_cluster(self, mocker):
        """Test describing a virtual cluster."""

        # Mock response data
        mock_response = {
            "vc": {
                "vcId": VC_ID,
                "vcName": VC_NAME,
                "clusterId": CLUSTER_ID,
                "status": "ClusterCreationCompleted",
                "vcTier": "tier-1",
                "sparkVersion": "3.2.1",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_virtual_cluster(CLUSTER_ID, VC_ID)

        # Validate the response
        assert response is not None
        assert response["vcId"] == VC_ID
        assert response["vcName"] == VC_NAME
        assert response["clusterId"] == CLUSTER_ID
        assert response["sparkVersion"] == "3.2.1"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/describeVc",
            data={"clusterId": CLUSTER_ID, "vcId": VC_ID},
            squelch={404: None},
        )

    def test_describe_virtual_cluster_not_found(self, mocker):
        """Test describing a virtual cluster that doesn't exist (404 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = None

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_virtual_cluster(CLUSTER_ID, "nonexistent-vc")

        # Validate the response - should return None on 404
        assert response is None

    def test_get_virtual_cluster_by_name(self, mocker):
        """Test getting virtual cluster details by name."""

        # Mock list_virtual_clusters response
        list_mock = [
            {
                "vcId": VC_ID,
                "vcName": VC_NAME,
                "clusterId": CLUSTER_ID,
            },
            {
                "vcId": "vc-other",
                "vcName": "other-vc",
                "clusterId": CLUSTER_ID,
            },
        ]

        # Mock describe_virtual_cluster response
        describe_mock = {
            "vcId": VC_ID,
            "vcName": VC_NAME,
            "clusterId": CLUSTER_ID,
            "status": "ClusterCreationCompleted",
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_virtual_clusters", return_value=list_mock)
        mocker.patch.object(
            client,
            "describe_virtual_cluster",
            return_value=describe_mock,
        )

        # Test getting virtual cluster by name
        response = client.get_virtual_cluster_by_name(CLUSTER_ID, VC_NAME)

        # Validate the response
        assert response is not None
        assert response["vcName"] == VC_NAME
        assert response["vcId"] == VC_ID

        # Verify the methods were called
        client.list_virtual_clusters.assert_called_once_with(CLUSTER_ID)
        client.describe_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)

    def test_get_virtual_cluster_by_name_not_found(self, mocker):
        """Test getting virtual cluster by name when it doesn't exist."""

        # Mock list_virtual_clusters response
        list_mock = [
            {
                "vcId": "vc-other",
                "vcName": "other-vc",
                "clusterId": CLUSTER_ID,
            },
        ]

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_virtual_clusters", return_value=list_mock)

        # Test getting virtual cluster by name
        response = client.get_virtual_cluster_by_name(CLUSTER_ID, "nonexistent-vc")

        # Validate the response
        assert response is None

        # Verify the methods were called
        client.list_virtual_clusters.assert_called_once_with(CLUSTER_ID)
