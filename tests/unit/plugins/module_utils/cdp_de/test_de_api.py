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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    AllPurposeInstanceGroupDetails,
    CdpDeClient,
    ServiceDescription,
    ServiceResources,
    ServiceSummary,
    VcDescription,
    VcSummary,
    check_service_updates,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
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

        # Validate the response is a list of ServiceSummary dataclasses
        assert isinstance(response, list)
        assert len(response) == 2
        assert all(isinstance(s, ServiceSummary) for s in response)
        assert response[0].clusterId == "cluster-123"
        assert response[1].name == "service-2"

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

        # Validate the response is a list of ServiceSummary dataclasses
        assert isinstance(response, list)
        assert len(response) == 2
        assert response[1].status == "ClusterDeletionCompleted"

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
        assert isinstance(response, list)
        assert len(response) == 0

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

        # Validate the response is an unwrapped ServiceDescription dataclass
        assert isinstance(response, ServiceDescription)
        assert response.clusterId == CLUSTER_ID
        assert response.name == SERVICE_NAME
        assert response.environmentName == ENV_NAME
        assert isinstance(response.resources, ServiceResources)
        assert response.resources.instance_type == "m5.2xlarge"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/de/describeService",
            data={"clusterId": CLUSTER_ID},
            squelch={404: {}},
        )

    def test_describe_service_not_found(self, mocker):
        """Test describing a service that doesn't exist (404 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_service("nonexistent-cluster")

        # Validate the response - should return None on 404
        assert response is None

    def test_describe_service_invalid_state(self, mocker):
        """Test describing a service in invalid state (500 error)."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)
        response = client.describe_service(CLUSTER_ID)

        # Validate the response - should return None on 500
        assert response is None

    def test_get_service_by_name(self, mocker):
        """Test getting service details by name."""

        # Mock list_services response (list of ServiceSummary dataclasses)
        list_mock = [
            ServiceSummary(
                clusterId=CLUSTER_ID,
                name=SERVICE_NAME,
                environmentName=ENV_NAME,
            ),
            ServiceSummary(
                clusterId="cluster-other",
                name="other-service",
                environmentName="other-env",
            ),
        ]

        # Mock describe_service response (unwrapped ServiceDescription)
        describe_mock = ServiceDescription(
            clusterId=CLUSTER_ID,
            name=SERVICE_NAME,
            environmentName=ENV_NAME,
            status="ClusterCreationCompleted",
        )

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the methods
        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        # Test getting service by name
        response = client.get_service_by_name(SERVICE_NAME)

        # Validate the response is an unwrapped ServiceDescription
        assert isinstance(response, ServiceDescription)
        assert response.name == SERVICE_NAME
        assert response.clusterId == CLUSTER_ID

        # Verify the methods were called
        client.list_services.assert_called_once()
        client.describe_service.assert_called_once_with(CLUSTER_ID)

    def test_get_service_by_name_not_found(self, mocker):
        """Test getting service by name when it doesn't exist."""

        # Mock list_services response (list of ServiceSummary dataclasses)
        list_mock = [
            ServiceSummary(
                clusterId="cluster-other",
                name="other-service",
                environmentName="other-env",
            ),
        ]

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

    def test_enable_service(self, mocker):
        """Test enabling a service returns an unwrapped ServiceDescription."""

        mock_response = {
            "service": {
                "clusterId": CLUSTER_ID,
                "name": SERVICE_NAME,
                "environmentName": ENV_NAME,
                "status": "ClusterCreationInProgress",
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDeClient(api_client=api_client)
        response = client.enable_service(
            name=SERVICE_NAME,
            env=ENV_NAME,
            instance_type="m5.2xlarge",
            minimum_instances=1,
            maximum_instances=4,
        )

        assert isinstance(response, ServiceDescription)
        assert response.clusterId == CLUSTER_ID
        assert response.name == SERVICE_NAME

        api_client.post.assert_called_once_with(
            "/api/v1/de/enableService",
            data={
                "name": SERVICE_NAME,
                "env": ENV_NAME,
                "instanceType": "m5.2xlarge",
                "minimumInstances": 1,
                "maximumInstances": 4,
            },
        )

    def test_enable_service_no_service_in_response(self, mocker):
        """Test enabling a service returns None when response lacks a service."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDeClient(api_client=api_client)
        response = client.enable_service(
            name=SERVICE_NAME,
            env=ENV_NAME,
            instance_type="m5.2xlarge",
            minimum_instances=1,
            maximum_instances=4,
        )

        assert response is None

    def test_update_service(self, mocker):
        """update_service posts camelCase params and returns the raw status dict."""

        mock_response = {"status": "ClusterCreationInProgress"}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDeClient(api_client=api_client)
        response = client.update_service(
            cluster_id=CLUSTER_ID,
            minimum_instances=1,
            maximum_instances=5,
            minimum_spot_instances=0,
            maximum_spot_instances=2,
            whitelist_ips=["10.0.0.0/8"],
            loadbalancer_allowlist=["192.168.0.0/16"],
        )

        assert response == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/de/updateService",
            data={
                "clusterId": CLUSTER_ID,
                "minimumInstances": 1,
                "maximumInstances": 5,
                "minimumSpotInstances": 0,
                "maximumSpotInstances": 2,
                "whitelistIps": ["10.0.0.0/8"],
                "loadbalancerAllowlist": ["192.168.0.0/16"],
            },
        )

    def test_update_service_no_changes(self, mocker):
        """update_service with only a cluster id posts just the clusterId."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDeClient(api_client=api_client)
        response = client.update_service(cluster_id=CLUSTER_ID)

        assert response == {}
        api_client.post.assert_called_once_with(
            "/api/v1/de/updateService",
            data={"clusterId": CLUSTER_ID},
        )

    def test_update_service_all_purpose_instances(self, mocker):
        """update_service maps All Purpose Instance Group params to camelCase."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDeClient(api_client=api_client)
        client.update_service(
            cluster_id=CLUSTER_ID,
            all_purpose_minimum_instances=1,
            all_purpose_maximum_instances=3,
            all_purpose_minimum_spot_instances=0,
            all_purpose_maximum_spot_instances=2,
        )

        api_client.post.assert_called_once_with(
            "/api/v1/de/updateService",
            data={
                "clusterId": CLUSTER_ID,
                "allPurposeMinimumInstances": 1,
                "allPurposeMaximumInstances": 3,
                "allPurposeMinimumSpotInstances": 0,
                "allPurposeMaximumSpotInstances": 2,
            },
        )

    def test_get_service_by_cluster_id(self, mocker):
        """Test getting service details by cluster ID."""

        # Mock describe_service response (unwrapped ServiceDescription)
        describe_mock = ServiceDescription(
            clusterId=CLUSTER_ID,
            name=SERVICE_NAME,
            environmentName=ENV_NAME,
            status="ClusterCreationCompleted",
        )

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the describe_service method
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        # Test getting service by cluster ID
        response = client.get_service_by_cluster_id(CLUSTER_ID)

        # Validate the response is an unwrapped ServiceDescription
        assert isinstance(response, ServiceDescription)
        assert response.clusterId == CLUSTER_ID
        assert response.name == SERVICE_NAME

        # Verify the method was called
        client.describe_service.assert_called_once_with(CLUSTER_ID)

    def test_get_service_by_cluster_id_not_found(self, mocker):
        """Test getting service by cluster ID when it doesn't exist."""

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Create the CdpDeClient instance
        client = CdpDeClient(api_client=api_client)

        # Mock the describe_service method to return None (not found)
        mocker.patch.object(client, "describe_service", return_value=None)

        # Test getting service by cluster ID
        response = client.get_service_by_cluster_id("nonexistent-cluster")

        # Validate the response
        assert response is None

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

        # Validate the response is a list of VcSummary dataclasses
        assert isinstance(response, list)
        assert len(response) == 2
        assert all(isinstance(vc, VcSummary) for vc in response)
        assert response[0].vcId == "vc-123"
        assert response[1].vcName == "vc-2"

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

        # Validate the response is a VcDescription dataclass
        assert isinstance(response, VcDescription)
        assert response.vcId == VC_ID
        assert response.vcName == VC_NAME
        assert response.clusterId == CLUSTER_ID
        assert response.sparkVersion == "3.2.1"

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

        # Mock list_virtual_clusters response (list of VcSummary dataclasses)
        list_mock = [
            VcSummary(vcId=VC_ID, vcName=VC_NAME, clusterId=CLUSTER_ID),
            VcSummary(vcId="vc-other", vcName="other-vc", clusterId=CLUSTER_ID),
        ]

        # Mock describe_virtual_cluster response (VcDescription)
        describe_mock = VcDescription(
            vcId=VC_ID,
            vcName=VC_NAME,
            clusterId=CLUSTER_ID,
            status="ClusterCreationCompleted",
        )

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

        # Validate the response is a VcDescription dataclass
        assert isinstance(response, VcDescription)
        assert response.vcName == VC_NAME
        assert response.vcId == VC_ID

        # Verify the methods were called
        client.list_virtual_clusters.assert_called_once_with(CLUSTER_ID)
        client.describe_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)

    def test_get_virtual_cluster_by_name_not_found(self, mocker):
        """Test getting virtual cluster by name when it doesn't exist."""

        # Mock list_virtual_clusters response (list of VcSummary dataclasses)
        list_mock = [
            VcSummary(vcId="vc-other", vcName="other-vc", clusterId=CLUSTER_ID),
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

    def test_create_virtual_cluster(self, mocker):
        """Test creating a virtual cluster returns an unwrapped VcDescription."""

        mock_response = {
            "Vc": {
                "vcId": VC_ID,
                "vcName": VC_NAME,
                "clusterId": CLUSTER_ID,
                "status": "AppInstalling",
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDeClient(api_client=api_client)
        response = client.create_virtual_cluster(
            name=VC_NAME,
            cluster_id=CLUSTER_ID,
            cpu_requests="10",
            memory_requests="30Gi",
        )

        assert isinstance(response, VcDescription)
        assert response.vcId == VC_ID
        assert response.vcName == VC_NAME

        api_client.post.assert_called_once_with(
            "/api/v1/de/createVc",
            data={
                "name": VC_NAME,
                "clusterId": CLUSTER_ID,
                "cpuRequests": "10",
                "memoryRequests": "30Gi",
            },
        )

    def test_create_virtual_cluster_no_vc_in_response(self, mocker):
        """Test creating a virtual cluster returns None when response lacks a Vc."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDeClient(api_client=api_client)
        response = client.create_virtual_cluster(
            name=VC_NAME,
            cluster_id=CLUSTER_ID,
            cpu_requests="10",
            memory_requests="30Gi",
        )

        assert response is None

    def test_wait_for_service_state_already_target(self, mocker):
        """Test wait returns the ServiceDescription when already at target status."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDeClient(api_client=api_client)

        described = ServiceDescription(
            clusterId=CLUSTER_ID,
            name=SERVICE_NAME,
            status="ClusterCreationCompleted",
        )
        mocker.patch.object(client, "describe_service", return_value=described)

        result = client.wait_for_service_state(
            cluster_id=CLUSTER_ID,
            target_statuses={"ClusterCreationCompleted"},
        )

        assert isinstance(result, ServiceDescription)
        assert result.clusterId == CLUSTER_ID

    def test_get_service_state_falls_back_to_list(self, mocker):
        """Test _get_service_state falls back to list_services on a 404 describe."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDeClient(api_client=api_client)

        mocker.patch.object(client, "describe_service", return_value=None)
        mocker.patch.object(
            client,
            "list_services",
            return_value=[
                ServiceSummary(
                    clusterId=CLUSTER_ID,
                    name=SERVICE_NAME,
                    status="ClusterDeletionInProgress",
                ),
            ],
        )

        status, service = client._get_service_state(CLUSTER_ID)

        assert status == "ClusterDeletionInProgress"
        assert isinstance(service, ServiceSummary)
        assert service.clusterId == CLUSTER_ID

    def test_wait_for_vc_state_already_target(self, mocker):
        """Test VC wait returns the VcDescription when already at target status."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDeClient(api_client=api_client)

        described = VcDescription(
            vcId=VC_ID,
            vcName=VC_NAME,
            clusterId=CLUSTER_ID,
            status="AppInstalled",
        )
        mocker.patch.object(
            client,
            "describe_virtual_cluster",
            return_value=described,
        )

        result = client.wait_for_vc_state(
            cluster_id=CLUSTER_ID,
            vc_id=VC_ID,
            target_statuses={"AppInstalled"},
        )

        assert isinstance(result, VcDescription)
        assert result.vcId == VC_ID


class TestCheckServiceUpdates:
    """Unit tests for check_service_updates reading a ServiceDescription."""

    def test_no_changes_returns_empty(self):
        details = ServiceDescription(
            clusterId=CLUSTER_ID,
            resources=ServiceResources(min_instances=1, max_instances=5),
        )
        assert (
            check_service_updates(
                cluster_id=CLUSTER_ID,
                service_details=details,
                minimum_instances=1,
                maximum_instances=5,
            )
            == {}
        )

    def test_detects_instance_change(self):
        details = ServiceDescription(
            clusterId=CLUSTER_ID,
            resources=ServiceResources(min_instances=1, max_instances=5),
        )
        result = check_service_updates(
            cluster_id=CLUSTER_ID,
            service_details=details,
            minimum_instances=2,
        )
        assert result == {"minimum_instances": 2, "cluster_id": CLUSTER_ID}

    def test_nullable_resources_treated_as_zero(self):
        details = ServiceDescription(clusterId=CLUSTER_ID)
        result = check_service_updates(
            cluster_id=CLUSTER_ID,
            service_details=details,
            minimum_instances=3,
        )
        assert result == {"minimum_instances": 3, "cluster_id": CLUSTER_ID}

    def test_whitelist_ips_compared_as_set(self):
        details = ServiceDescription(
            clusterId=CLUSTER_ID,
            whitelistIps="10.0.0.0/8,192.168.0.0/16",
        )
        assert (
            check_service_updates(
                cluster_id=CLUSTER_ID,
                service_details=details,
                whitelist_ips=["192.168.0.0/16", "10.0.0.0/8"],
            )
            == {}
        )
        assert check_service_updates(
            cluster_id=CLUSTER_ID,
            service_details=details,
            whitelist_ips=["10.0.0.0/8"],
        ) == {"whitelist_ips": ["10.0.0.0/8"], "cluster_id": CLUSTER_ID}

    def test_all_purpose_instance_group_change(self):
        details = ServiceDescription(
            clusterId=CLUSTER_ID,
            resources=ServiceResources(
                allPurposeInstanceGroupDetails=AllPurposeInstanceGroupDetails(
                    min_instances=1,
                ),
            ),
        )
        result = check_service_updates(
            cluster_id=CLUSTER_ID,
            service_details=details,
            all_purpose_minimum_instances=4,
        )
        assert result == {
            "all_purpose_minimum_instances": 4,
            "cluster_id": CLUSTER_ID,
        }


class TestDeDataclasses:
    """Unit tests for DE dataclass construction and serialization."""

    def test_defaults_are_nullable(self):
        desc = ServiceDescription()
        assert desc.clusterId is NULLABLE
        assert desc.resources is NULLABLE
        assert desc.whitelistIps is NULLABLE

    def test_from_dict_populates_flat_fields(self):
        desc = from_dict(
            ServiceDescription,
            {"clusterId": CLUSTER_ID, "name": SERVICE_NAME, "status": "OK"},
        )
        assert desc.clusterId == CLUSTER_ID
        assert desc.name == SERVICE_NAME
        assert desc.status == "OK"
        assert desc.environmentName is NULLABLE

    def test_from_dict_nested_resources(self):
        desc = from_dict(
            ServiceDescription,
            {
                "clusterId": CLUSTER_ID,
                "resources": {
                    "min_instances": "1",
                    "allPurposeInstanceGroupDetails": {"min_instances": "2"},
                },
            },
        )
        assert isinstance(desc.resources, ServiceResources)
        assert desc.resources.min_instances == "1"
        assert isinstance(
            desc.resources.allPurposeInstanceGroupDetails,
            AllPurposeInstanceGroupDetails,
        )
        assert desc.resources.allPurposeInstanceGroupDetails.min_instances == "2"

    def test_to_dict_excludes_nullable(self):
        desc = ServiceDescription(clusterId=CLUSTER_ID)
        result = to_dict(desc)
        assert result == {"clusterId": CLUSTER_ID}
        assert "resources" not in result

    def test_to_dict_round_trip_nested(self):
        desc = ServiceDescription(
            clusterId=CLUSTER_ID,
            resources=ServiceResources(min_instances="1", max_instances="5"),
        )
        result = to_dict(desc)
        assert result["clusterId"] == CLUSTER_ID
        assert result["resources"] == {"min_instances": "1", "max_instances": "5"}

    def test_vc_from_dict_and_to_dict(self):
        vc = from_dict(
            VcDescription,
            {"vcId": VC_ID, "vcName": VC_NAME, "clusterId": CLUSTER_ID},
        )
        assert vc.vcId == VC_ID
        assert to_dict(vc) == {
            "vcId": VC_ID,
            "vcName": VC_NAME,
            "clusterId": CLUSTER_ID,
        }
