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

import json
import pytest
import uuid
from typing import Generator

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


def _create_minimal_flow_definition(flow_name: str) -> str:
    """Return a minimal NiFi flow definition as a JSON string."""
    return json.dumps(
        {
            "snapshotMetadata": {
                "bucketIdentifier": None,
                "flowIdentifier": str(uuid.uuid4()),
                "version": 0,
                "timestamp": 1771317050573,
                "author": None,
                "comments": None,
                "link": None,
            },
            "flowContents": {
                "identifier": str(uuid.uuid4()),
                "instanceIdentifier": None,
                "name": flow_name,
                "comments": None,
                "position": None,
                "processGroups": [],
                "remoteProcessGroups": [],
                "processors": [],
                "inputPorts": [],
                "outputPorts": [],
                "connections": [],
                "labels": [],
                "funnels": [],
                "controllerServices": [],
                "versionedFlowCoordinates": None,
                "parameterContextName": flow_name,
                "defaultFlowFileExpiration": "0 sec",
                "defaultBackPressureObjectThreshold": 10000,
                "defaultBackPressureDataSizeThreshold": "1 GB",
                "scheduledState": None,
                "executionEngine": None,
                "maxConcurrentTasks": None,
                "statelessFlowTimeout": None,
                "logFileSuffix": None,
                "componentType": "PROCESS_GROUP",
                "flowFileConcurrency": "UNBOUNDED",
                "flowFileOutboundPolicy": "STREAM_WHEN_AVAILABLE",
                "groupIdentifier": None,
            },
            "externalControllerServices": None,
            "parameterProviders": None,
            "parameterContexts": {
                flow_name: {
                    "identifier": str(uuid.uuid4()),
                    "instanceIdentifier": None,
                    "name": flow_name,
                    "comments": None,
                    "position": None,
                    "parameters": [],
                    "inheritedParameterContexts": [],
                    "description": None,
                    "parameterProvider": None,
                    "parameterGroupName": None,
                    "synchronized": None,
                    "componentType": "PARAMETER_CONTEXT",
                    "groupIdentifier": None,
                },
            },
            "flowEncodingVersion": None,
            "flow": None,
            "bucket": None,
        },
    )


@pytest.fixture
def valid_df_flow(df_client) -> Generator[dict, None, None]:
    """
    Fixture to create a temporary flow for testing and clean it up afterwards.

    Yields the created flow dict. The flow is deleted after the test regardless
    of outcome.
    """
    flow_name = f"test-df-api-{uuid.uuid4().hex[:8]}"
    flow_content = _create_minimal_flow_definition(flow_name)

    flow = df_client.import_flow_definition(
        name=flow_name,
        file_content=flow_content,
        description=f"Integration test flow - {flow_name}",
        comments="Test version",
    )

    yield flow

    if flow and flow.get("crn"):
        try:
            df_client.delete_flow(flow_crn=flow["crn"])
        except Exception:
            pass


@pytest.fixture
def valid_df_service(df_client):
    """
    Fixture to find an active DataFlow service for testing.

    Returns a service summary dict. Skips the test if no active services exist.
    """
    services = df_client.list_services().get("services", [])

    for svc in services:
        state = svc.get("status", {}).get("state", "")
        if (
            state not in CdpDfClient.DISABLED_STATES
            and state not in CdpDfClient.FAILED_STATES
        ):
            details = df_client.describe_service(svc.get("crn"))
            if details:
                return svc

    pytest.skip("No active DataFlow services available for testing")


class TestCdpDfClientIntegration:
    """Integration tests for CdpDfClient using the real CDP API."""

    # -------------------------------------------------------------------------
    # Flow definition tests
    # -------------------------------------------------------------------------

    def test_list_flow_definitions_with_search(self, df_client, valid_df_flow):
        """Test that search_term filters results by name."""
        flow_name = valid_df_flow["name"]

        response = df_client.list_flow_definitions(search_term=flow_name)

        assert "flows" in response
        names = [f["name"] for f in response["flows"]]
        assert flow_name in names

    def test_describe_flow(self, df_client, valid_df_flow):
        """Test describing a flow definition by CRN returns expected fields."""
        flow_crn = valid_df_flow["crn"]

        response = df_client.describe_flow(flow_crn)

        assert response is not None
        assert response != {}

    def test_describe_flow_not_found(self, df_client):
        """Test that describing a nonexistent flow CRN returns an empty dict."""
        response = df_client.describe_flow(
            "crn:cdp:df:us-west-1:00000000-0000-0000-0000-000000000000:flow:nonexistent",
        )

        assert response == {}

    def test_get_flow_by_name(self, df_client, valid_df_flow):
        """Test resolving a flow by name."""
        flow_name = valid_df_flow["name"]

        result = df_client.get_flow_by_name(flow_name)

        assert result is not None
        assert result["name"] == flow_name
        assert "crn" in result
        assert "versionCount" in result

    def test_get_flow_by_crn(self, df_client, valid_df_flow):
        """Test resolving a flow by CRN."""
        flow_crn = valid_df_flow["crn"]

        result = df_client.get_flow_by_crn(flow_crn)

        assert result is not None
        assert result["crn"] == flow_crn
        assert "name" in result

    def test_get_flow_by_crn_not_found(self, df_client):
        """Test that get_flow_by_crn returns None for an unknown CRN."""
        result = df_client.get_flow_by_crn(
            "crn:cdp:df:us-west-1:00000000-0000-0000-0000-000000000000:flow:nonexistent",
        )

        assert result is None

    def test_import_flow_definition(self, df_client):
        """Test importing a new flow definition and then deleting it."""
        flow_name = f"test-import-{uuid.uuid4().hex[:8]}"
        flow_content = _create_minimal_flow_definition(flow_name)

        flow = None
        try:
            flow = df_client.import_flow_definition(
                name=flow_name,
                file_content=flow_content,
                description="Import test flow",
                comments="Initial version",
            )

            assert flow is not None
            assert "crn" in flow
            assert flow["name"] == flow_name
            assert flow["versionCount"] == 1
            assert len(flow["versions"]) == 1
            assert flow["versions"][0]["version"] == 1
            assert flow["versions"][0]["comments"] == "Initial version"
        finally:
            if flow and flow.get("crn"):
                df_client.delete_flow(flow_crn=flow["crn"])

    def test_import_flow_definition_version(self, df_client, valid_df_flow):
        """Test importing a new version into an existing flow."""
        flow_crn = valid_df_flow["crn"]
        flow_name = valid_df_flow["name"]
        flow_content = _create_minimal_flow_definition(flow_name)

        version = df_client.import_flow_definition_version(
            flow_crn=flow_crn,
            file_content=flow_content,
            comments="Second version",
        )

        assert version is not None
        assert "crn" in version
        assert version["version"] == 2
        assert version["comments"] == "Second version"

    def test_import_flow_definition_version_with_tags(self, df_client, valid_df_flow):
        """Test importing a flow version with tags."""
        flow_crn = valid_df_flow["crn"]
        flow_name = valid_df_flow["name"]
        flow_content = _create_minimal_flow_definition(flow_name)

        version = df_client.import_flow_definition_version(
            flow_crn=flow_crn,
            file_content=flow_content,
            comments="Tagged version",
            tags=[{"tagName": "production", "tagColor": "blue"}],
        )

        assert version is not None
        assert version["version"] == 2

    def test_delete_flow(self, df_client):
        """Test deleting a flow definition."""
        flow_name = f"test-delete-{uuid.uuid4().hex[:8]}"
        flow_content = _create_minimal_flow_definition(flow_name)

        flow = df_client.import_flow_definition(
            name=flow_name,
            file_content=flow_content,
            comments="To be deleted",
        )
        assert flow is not None
        flow_crn = flow["crn"]

        df_client.delete_flow(flow_crn=flow_crn)

        # Verify the flow is no longer retrievable
        result = df_client.get_flow_by_crn(flow_crn)
        assert result is None

    def test_flow_definition_completeness(self, df_client, valid_df_flow):
        """Test that a described flow contains all expected fields."""
        flow_crn = valid_df_flow["crn"]
        result = df_client.get_flow_by_crn(flow_crn)

        assert result is not None

        expected_fields = [
            "crn",
            "name",
            "versionCount",
            "createdTimestamp",
            "modifiedTimestamp",
        ]
        for field in expected_fields:
            assert field in result, f"Missing expected field: {field}"

        assert "versions" in result
        assert isinstance(result["versions"], list)

        if result["versions"]:
            version = result["versions"][0]
            version_fields = ["crn", "version", "timestamp", "deploymentCount"]
            for field in version_fields:
                assert field in version, f"Missing expected version field: {field}"

    # -------------------------------------------------------------------------
    # Service tests
    # -------------------------------------------------------------------------

    def test_list_services(self, df_client):
        """Test listing DataFlow services returns a valid structure."""
        response = df_client.list_services()

        assert "services" in response
        assert isinstance(response["services"], list)

        if response["services"]:
            service = response["services"][0]
            assert "crn" in service
            assert "name" in service
            assert "status" in service

    def test_describe_service(self, df_client, valid_df_service):
        """Test describing a DataFlow service returns expected fields."""
        service_crn = valid_df_service.get("crn")

        response = df_client.describe_service(service_crn)

        assert response is not None
        assert response != {}

    def test_describe_service_not_found(self, df_client):
        """Test that describing a nonexistent service CRN returns an empty dict."""
        response = df_client.describe_service(
            "crn:cdp:df:us-west-1:00000000-0000-0000-0000-000000000000:service:nonexistent",
        )

        assert response == {}

    def test_get_service_by_name(self, df_client, valid_df_service):
        """Test resolving a service by name."""
        service_name = valid_df_service.get("name")

        result = df_client.get_service_by_name(service_name)

        assert result is not None

    def test_get_service_by_name_not_found(self, df_client):
        """Test that get_service_by_name returns None for an unknown name."""
        result = df_client.get_service_by_name("nonexistent-service-name-zzz-12345")

        assert result is None
