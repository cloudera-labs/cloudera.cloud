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
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    format_tags_for_api,
)


FLOW_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123"
FLOW_NAME = "test-flow"
FLOW_VERSION_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123/v1"
COLLECTION_CRN = "crn:cdp:df:us-west-1:tenant:collection:col-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:svc-123"
SERVICE_NAME = "test-df-service"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"

FLOW_VERSION_SUMMARY = {
    "crn": FLOW_VERSION_CRN,
    "bucketIdentifier": "bucket-abc",
    "author": "test-user",
    "version": 1,
    "timestamp": 1640000000000,
    "deploymentCount": 0,
    "comments": "Initial version",
}

FLOW_DETAIL = {
    "crn": FLOW_CRN,
    "name": FLOW_NAME,
    "versionCount": 1,
    "createdTimestamp": 1640000000000,
    "modifiedTimestamp": 1640000000000,
    "description": "Test flow description",
    "versions": [FLOW_VERSION_SUMMARY],
}


class TestFormatTagsForApi:
    """Unit tests for the format_tags_for_api helper function."""

    def test_none_input(self):
        """Test that None input returns None."""
        assert format_tags_for_api(None) is None

    def test_empty_list(self):
        """Test that empty list returns empty list."""
        assert format_tags_for_api([]) == []

    def test_tags_with_color(self):
        """Test conversion of tags with both name and color."""
        tags = [
            {"tag_name": "production", "tag_color": "blue"},
            {"tag_name": "stable", "tag_color": "green"},
        ]
        result = format_tags_for_api(tags)
        assert result == [
            {"tagName": "production", "tagColor": "blue"},
            {"tagName": "stable", "tagColor": "green"},
        ]

    def test_tags_without_color(self):
        """Test that missing tag_color is omitted from the output."""
        tags = [{"tag_name": "production"}]
        result = format_tags_for_api(tags)
        assert result == [{"tagName": "production"}]
        assert "tagColor" not in result[0]

    def test_mixed_tags(self):
        """Test a mix of tags with and without color."""
        tags = [
            {"tag_name": "production", "tag_color": "blue"},
            {"tag_name": "stable"},
        ]
        result = format_tags_for_api(tags)
        assert result == [
            {"tagName": "production", "tagColor": "blue"},
            {"tagName": "stable"},
        ]


class TestCdpDfClientFlowDefinitions:
    """Unit tests for CdpDfClient flow definition methods."""

    def test_list_flow_definitions_default(self, mocker):
        """Test listing all flow definitions with no filters."""
        mock_response = {
            "flows": [
                {"crn": FLOW_CRN, "name": FLOW_NAME, "versionCount": 1},
                {"crn": "crn:other", "name": "other-flow", "versionCount": 2},
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.list_flow_definitions()

        assert "flows" in response
        assert len(response["flows"]) == 2
        assert response["flows"][0]["name"] == FLOW_NAME

        api_client.post.assert_called_once_with(
            "/api/v1/df/listFlowDefinitions",
            data={"pageSize": 100},
            squelch={404: {"flows": []}},
        )

    def test_list_flow_definitions_with_search(self, mocker):
        """Test listing flow definitions filtered by search term."""
        mock_response = {"flows": [{"crn": FLOW_CRN, "name": FLOW_NAME}]}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        client.list_flow_definitions(search_term=FLOW_NAME)

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["searchTerm"] == FLOW_NAME

    def test_list_flow_definitions_with_collection_crn(self, mocker):
        """Test listing flow definitions filtered by collection CRN."""
        mock_response = {"flows": [{"crn": FLOW_CRN, "name": FLOW_NAME}]}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        client.list_flow_definitions(collection_crn=COLLECTION_CRN)

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["collectionCrn"] == COLLECTION_CRN

    def test_list_flow_definitions_empty(self, mocker):
        """Test listing flow definitions when none exist."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"flows": []}

        client = CdpDfClient(api_client=api_client)
        response = client.list_flow_definitions()

        assert "flows" in response
        assert len(response["flows"]) == 0

    def test_describe_flow(self, mocker):
        """Test describing a flow definition by CRN."""
        mock_response = {"flow": {"flowDetail": FLOW_DETAIL}}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.describe_flow(FLOW_CRN)

        assert response == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/df/describeFlow",
            data={"flowCrn": FLOW_CRN},
            squelch={404: {}},
        )

    def test_describe_flow_not_found(self, mocker):
        """Test describing a flow that doesn't exist (404)."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.describe_flow("nonexistent-crn")

        assert response == {}

    def test_get_flow_by_name(self, mocker):
        """Test resolving a flow by name via list + describe."""
        list_mock = {
            "flows": [
                {"crn": FLOW_CRN, "name": FLOW_NAME},
                {"crn": "crn:other", "name": "other-flow"},
            ],
        }
        describe_mock = {"flow": {"flowDetail": FLOW_DETAIL}}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_flow_definitions", return_value=list_mock)
        mocker.patch.object(client, "describe_flow", return_value=describe_mock)

        result = client.get_flow_by_name(FLOW_NAME)

        assert result is not None
        assert result["crn"] == FLOW_CRN
        assert result["name"] == FLOW_NAME

        client.list_flow_definitions.assert_called_once_with(search_term=FLOW_NAME)
        client.describe_flow.assert_called_once_with(FLOW_CRN)

    def test_get_flow_by_name_not_found(self, mocker):
        """Test get_flow_by_name when no flow matches."""
        list_mock = {"flows": [{"crn": "crn:other", "name": "other-flow"}]}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "list_flow_definitions", return_value=list_mock)

        result = client.get_flow_by_name("nonexistent-flow")

        assert result is None
        client.list_flow_definitions.assert_called_once_with(search_term="nonexistent-flow")

    def test_get_flow_by_crn(self, mocker):
        """Test resolving a flow by CRN via describe."""
        describe_mock = {"flow": {"flowDetail": FLOW_DETAIL}}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "describe_flow", return_value=describe_mock)

        result = client.get_flow_by_crn(FLOW_CRN)

        assert result is not None
        assert result["crn"] == FLOW_CRN
        client.describe_flow.assert_called_once_with(FLOW_CRN)

    def test_get_flow_by_crn_not_found(self, mocker):
        """Test get_flow_by_crn when the CRN doesn't exist."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "describe_flow", return_value={})

        result = client.get_flow_by_crn("nonexistent-crn")

        assert result is None

    def test_import_flow_definition_minimal(self, mocker):
        """Test importing a flow definition with only required parameters."""
        mock_response = FLOW_DETAIL

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.import_flow_definition(
            name=FLOW_NAME,
            file_content='{"flow": "content"}',
        )

        assert response == mock_response

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["name"] == FLOW_NAME
        assert call_data["file"] == '{"flow": "content"}'
        assert "description" not in call_data
        assert "comments" not in call_data
        assert "collectionCrn" not in call_data
        assert "tags" not in call_data

    def test_import_flow_definition_all_params(self, mocker):
        """Test importing a flow definition with all optional parameters."""
        mock_response = {**FLOW_DETAIL, "collectionCrn": COLLECTION_CRN}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.import_flow_definition(
            name=FLOW_NAME,
            file_content='{"flow": "content"}',
            description="Test description",
            comments="Initial version",
            collection_crn=COLLECTION_CRN,
            tags=[{"tagName": "production", "tagColor": "blue"}],
        )

        assert response["collectionCrn"] == COLLECTION_CRN

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["description"] == "Test description"
        assert call_data["comments"] == "Initial version"
        assert call_data["collectionCrn"] == COLLECTION_CRN
        assert call_data["tags"] == [{"tagName": "production", "tagColor": "blue"}]

    def test_import_flow_definition_version_minimal(self, mocker):
        """Test importing a flow version with only required parameters."""
        mock_response = FLOW_VERSION_SUMMARY

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.import_flow_definition_version(
            flow_crn=FLOW_CRN,
            file_content='{"flow": "content"}',
        )

        assert response == mock_response

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["flowCrn"] == FLOW_CRN
        assert call_data["file"] == '{"flow": "content"}'
        assert "comments" not in call_data
        assert "tags" not in call_data

        api_client.post.assert_called_once_with(
            "/api/v1/df/importFlowDefinitionVersion",
            data=call_data,
        )

    def test_import_flow_definition_version_with_comments_and_tags(self, mocker):
        """Test importing a flow version with comments and tags."""
        mock_response = {**FLOW_VERSION_SUMMARY, "version": 2, "comments": "v2"}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.import_flow_definition_version(
            flow_crn=FLOW_CRN,
            file_content='{"flow": "content"}',
            comments="v2",
            tags=[{"tagName": "stable"}],
        )

        assert response["version"] == 2
        assert response["comments"] == "v2"

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["comments"] == "v2"
        assert call_data["tags"] == [{"tagName": "stable"}]

    def test_delete_flow(self, mocker):
        """Test deleting a flow definition."""
        mock_response = {"flow": {"crn": FLOW_CRN, "name": FLOW_NAME}}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.delete_flow(FLOW_CRN)

        assert response == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/df/deleteFlow",
            data={"flowCrn": FLOW_CRN},
        )


class TestCdpDfClientServices:
    """Unit tests for CdpDfClient DataFlow service management methods."""

    def test_list_services_default(self, mocker):
        """Test listing all DataFlow services with no filters."""
        mock_response = {
            "services": [
                {"crn": SERVICE_CRN, "name": SERVICE_NAME, "status": {"state": "GOOD_HEALTH"}},
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.list_services()

        assert "services" in response
        assert len(response["services"]) == 1
        assert response["services"][0]["crn"] == SERVICE_CRN

        api_client.post.assert_called_once_with(
            "/api/v1/df/listServices",
            data={"pageSize": 100},
            squelch={404: {"services": []}},
        )

    def test_list_services_with_search(self, mocker):
        """Test listing services filtered by search term."""
        mock_response = {"services": [{"crn": SERVICE_CRN, "name": SERVICE_NAME}]}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        client.list_services(search_term=SERVICE_NAME)

        call_data = api_client.post.call_args[1]["data"]
        assert call_data["searchTerm"] == SERVICE_NAME

    def test_list_services_empty(self, mocker):
        """Test listing services when none exist."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"services": []}

        client = CdpDfClient(api_client=api_client)
        response = client.list_services()

        assert "services" in response
        assert len(response["services"]) == 0

    def test_describe_service(self, mocker):
        """Test describing a DataFlow service by CRN."""
        mock_response = {
            "service": {
                "crn": SERVICE_CRN,
                "name": SERVICE_NAME,
                "environmentCrn": ENV_CRN,
                "status": {"state": "GOOD_HEALTH"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.describe_service(SERVICE_CRN)

        assert response == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/df/describeService",
            data={"serviceCrn": SERVICE_CRN},
            squelch={404: {}},
        )

    def test_describe_service_not_found(self, mocker):
        """Test describing a service that doesn't exist."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.describe_service("nonexistent-crn")

        assert response == {}

    def test_get_service_by_name(self, mocker):
        """Test resolving a service by name via list + describe."""
        list_mock = {
            "services": [
                {"crn": SERVICE_CRN, "name": SERVICE_NAME, "status": {"state": "GOOD_HEALTH"}},
                {"crn": "crn:other", "name": "other-service", "status": {"state": "GOOD_HEALTH"}},
            ],
        }
        describe_mock = {
            "service": {
                "crn": SERVICE_CRN,
                "name": SERVICE_NAME,
                "status": {"state": "GOOD_HEALTH"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        result = client.get_service_by_name(SERVICE_NAME)

        assert result is not None
        assert result["service"]["name"] == SERVICE_NAME
        client.describe_service.assert_called_once_with(SERVICE_CRN)

    def test_get_service_by_name_not_found(self, mocker):
        """Test get_service_by_name when no service matches."""
        list_mock = {"services": [{"crn": "crn:other", "name": "other-service", "status": {"state": "GOOD_HEALTH"}}]}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "list_services", return_value=list_mock)

        result = client.get_service_by_name("nonexistent-service")

        assert result is None

    def test_get_service_by_name_skips_disabled(self, mocker):
        """Test that get_service_by_name skips NOT_ENABLED services."""
        list_mock = {
            "services": [
                {"crn": SERVICE_CRN, "name": SERVICE_NAME, "status": {"state": "NOT_ENABLED"}},
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "list_services", return_value=list_mock)
        describe_spy = mocker.patch.object(client, "describe_service")

        result = client.get_service_by_name(SERVICE_NAME)

        assert result is None
        describe_spy.assert_not_called()
