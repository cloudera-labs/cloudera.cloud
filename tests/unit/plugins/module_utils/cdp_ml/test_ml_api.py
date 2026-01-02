# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_ml import (
    CdpMlClient,
)


class TestCdpMlClient:
    """Unit tests for CdpMlClient."""

    def test_list_workspaces_no_filter(self, mocker):
        """Test listing all ML workspaces."""

        # Mock response data
        mock_response = {
            "workspaces": [
                {
                    "name": "workspace1",
                    "environment": "env1",
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:workspace1",
                    "creationDate": "2025-01-01T00:00:00Z",
                },
                {
                    "name": "workspace2",
                    "environment": "env2",
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:workspace2",
                    "creationDate": "2025-01-02T00:00:00Z",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.list_workspaces()

        # Validate the response
        assert "workspaces" in response
        assert len(response["workspaces"]) == 2
        assert response["workspaces"][0]["name"] == "workspace1"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )

    def test_list_workspaces_with_env_filter(self, mocker):
        """Test listing ML workspaces with environment filter."""

        # Mock response data
        mock_response = {
            "workspaces": [
                {
                    "name": "workspace1",
                    "environmentName": "env1",
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:workspace1",
                    "creationDate": "2025-01-01T00:00:00Z",
                },
                {
                    "name": "workspace2",
                    "environmentName": "env2",
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:workspace2",
                    "creationDate": "2025-01-02T00:00:00Z",
                },
            ],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.list_workspaces(env="env1")

        # Validate the response
        assert "workspaces" in response
        assert len(response["workspaces"]) == 1
        assert response["workspaces"][0]["name"] == "workspace1"

        # Verify that the post method was called with correct parameters
        api_client.post.assert_called_once_with(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )

    def test_list_workspaces_empty_response(self, mocker):
        """Test listing workspaces with empty response."""

        # Mock empty response data
        mock_response = {
            "workspaces": [],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.list_workspaces()

        # Validate the response
        assert "workspaces" in response
        assert len(response["workspaces"]) == 0
        assert response["workspaces"] == []

        # Verify that the post method was called with correct parameters including squelch for 404
        api_client.post.assert_called_once_with(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )

    def test_describe_workspace_by_crn(self, mocker):
        """Test describing a workspace by CRN only."""

        # Mock response data
        mock_response = {
            "workspace": {
                "instanceName": "test-workspace",
                "environmentName": "test-env",
                "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123",
                "instanceStatus": "installation:finished",
                "instanceUrl": "https://test.cloudera.site",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.describe_workspace(
            crn="crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123"
        )

        # Validate the response
        assert "workspace" in response
        assert response["workspace"]["instanceName"] == "test-workspace"
        assert (
            response["workspace"]["crn"]
            == "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123"
        )

        # Verify that the post method was called with ONLY workspaceCrn
        api_client.post.assert_called_once_with(
            "/api/v1/ml/describeWorkspace",
            json_data={
                "workspaceCrn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:abc123"
            },
            squelch={404: {}, 500: {}},
        )

        # Verify env and name are NOT included
        call_args = api_client.post.call_args
        assert "environmentName" not in call_args[1]["json_data"]
        assert "workspaceName" not in call_args[1]["json_data"]

    def test_describe_workspace_by_name_and_env(self, mocker):
        """Test describing a workspace by name and environment."""

        # Mock response data
        mock_response = {
            "workspace": {
                "instanceName": "my-workspace",
                "environmentName": "my-env",
                "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:xyz789",
                "instanceStatus": "installation:finished",
                "instanceUrl": "https://my-workspace.cloudera.site",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.describe_workspace(name="my-workspace", env="my-env")

        # Validate the response
        assert "workspace" in response
        assert response["workspace"]["instanceName"] == "my-workspace"
        assert response["workspace"]["environmentName"] == "my-env"

        # Verify that the post method was called with workspaceName and environmentName
        api_client.post.assert_called_once_with(
            "/api/v1/ml/describeWorkspace",
            json_data={
                "environmentName": "my-env",
                "workspaceName": "my-workspace",
            },
            squelch={404: {}, 500: {}},
        )

        # Verify crn is NOT included
        call_args = api_client.post.call_args
        assert "workspaceCrn" not in call_args[1]["json_data"]

    def test_describe_workspace_by_name_only(self, mocker):
        """Test describing a workspace by name only."""

        # Mock response data
        mock_response = {
            "workspace": {
                "instanceName": "name-only-workspace",
                "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:name123",
                "instanceStatus": "installation:finished",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.describe_workspace(name="name-only-workspace")

        # Validate the response
        assert "workspace" in response
        assert response["workspace"]["instanceName"] == "name-only-workspace"

        # Verify that the post method was called with only workspaceName
        api_client.post.assert_called_once_with(
            "/api/v1/ml/describeWorkspace",
            json_data={"workspaceName": "name-only-workspace"},
            squelch={404: {}, 500: {}},
        )

        # Verify environmentName and workspaceCrn are NOT included
        call_args = api_client.post.call_args
        assert "environmentName" not in call_args[1]["json_data"]
        assert "workspaceCrn" not in call_args[1]["json_data"]

    def test_describe_workspace_by_env_only(self, mocker):
        """Test describing a workspace by environment only."""

        # Mock response data
        mock_response = {
            "workspace": {
                "environmentName": "env-only-test",
                "crn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:env456",
                "instanceStatus": "installation:finished",
            },
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.describe_workspace(env="env-only-test")

        # Validate the response
        assert "workspace" in response
        assert response["workspace"]["environmentName"] == "env-only-test"

        # Verify that the post method was called with only environmentName
        api_client.post.assert_called_once_with(
            "/api/v1/ml/describeWorkspace",
            json_data={"environmentName": "env-only-test"},
            squelch={404: {}, 500: {}},
        )

        # Verify workspaceName and workspaceCrn are NOT included
        call_args = api_client.post.call_args
        assert "workspaceName" not in call_args[1]["json_data"]
        assert "workspaceCrn" not in call_args[1]["json_data"]

    def test_describe_workspace_not_found(self, mocker):
        """Test describing a non-existent workspace."""

        # Mock response returning empty dict (simulating 404/500 being squelched)
        mock_response = {}

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        response = client.describe_workspace(
            crn="crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:nonexistent"
        )

        # Validate the response is empty
        assert response == {}
        assert "workspace" not in response

        # Verify that the post method was called with squelch parameters for 404 and 500
        api_client.post.assert_called_once_with(
            "/api/v1/ml/describeWorkspace",
            json_data={
                "workspaceCrn": "crn:cdp:ml:us-west-1:558bc1d2-8867-4357-8524-311d51259233:workspace:nonexistent"
            },
            squelch={404: {}, 500: {}},
        )

    def test_describe_all_workspaces_no_filter(self, mocker):
        """Test describing all workspaces without filter."""

        # Mock list_workspaces response
        mock_list_response = {
            "workspaces": [
                {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws1",
                    "instanceName": "workspace1",
                },
                {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws2",
                    "instanceName": "workspace2",
                },
                {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws3",
                    "instanceName": "workspace3",
                },
            ],
        }

        # Mock describe_workspace responses
        mock_describe_responses = [
            {
                "workspace": {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws1",
                    "instanceName": "workspace1",
                    "instanceStatus": "installation:finished",
                }
            },
            {
                "workspace": {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws2",
                    "instanceName": "workspace2",
                    "instanceStatus": "installation:finished",
                }
            },
            {
                "workspace": {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws3",
                    "instanceName": "workspace3",
                    "instanceStatus": "installation:finished",
                }
            },
        ]

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        # Set up post method to return different responses based on endpoint
        def post_side_effect(endpoint, json_data, squelch=None):
            if endpoint == "/api/v1/ml/listWorkspaces":
                return mock_list_response
            elif endpoint == "/api/v1/ml/describeWorkspace":
                # Return appropriate response based on CRN
                for response in mock_describe_responses:
                    if response["workspace"]["crn"] == json_data.get("workspaceCrn"):
                        return response
            return {}

        api_client.post.side_effect = post_side_effect

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        result = client.describe_all_workspaces()

        # Validate the result
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["instanceName"] == "workspace1"
        assert result[1]["instanceName"] == "workspace2"
        assert result[2]["instanceName"] == "workspace3"

        # Verify each workspace detail is extracted from "workspace" key
        for workspace in result:
            assert "crn" in workspace
            assert "instanceName" in workspace
            assert "instanceStatus" in workspace

        # Verify describe_workspace was called 3 times with correct CRNs
        assert api_client.post.call_count == 4  # 1 list + 3 describe calls
        describe_calls = [
            call
            for call in api_client.post.call_args_list
            if "/api/v1/ml/describeWorkspace" in str(call)
        ]
        assert len(describe_calls) == 3

    def test_describe_all_workspaces_with_env_filter(self, mocker):
        """Test describing all workspaces with environment filter."""

        # Mock list_workspaces response (already filtered by env)
        mock_list_response = {
            "workspaces": [
                {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws1",
                    "instanceName": "workspace1",
                    "environmentName": "test-env",
                },
                {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws2",
                    "instanceName": "workspace2",
                    "environmentName": "test-env",
                },
            ],
        }

        # Mock describe_workspace responses
        mock_describe_responses = [
            {
                "workspace": {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws1",
                    "instanceName": "workspace1",
                    "environmentName": "test-env",
                }
            },
            {
                "workspace": {
                    "crn": "crn:cdp:ml:us-west-1:account:workspace:ws2",
                    "instanceName": "workspace2",
                    "environmentName": "test-env",
                }
            },
        ]

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)

        def post_side_effect(endpoint, json_data, squelch=None):
            if endpoint == "/api/v1/ml/listWorkspaces":
                return mock_list_response
            elif endpoint == "/api/v1/ml/describeWorkspace":
                for response in mock_describe_responses:
                    if response["workspace"]["crn"] == json_data.get("workspaceCrn"):
                        return response
            return {}

        api_client.post.side_effect = post_side_effect

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        result = client.describe_all_workspaces(env="test-env")

        # Validate the result
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify all workspaces are from test-env
        for workspace in result:
            assert workspace["environmentName"] == "test-env"

        # Verify list_workspaces was called with env filter
        list_call = api_client.post.call_args_list[0]
        assert list_call[0][0] == "/api/v1/ml/listWorkspaces"

    def test_describe_all_workspaces_empty_list(self, mocker):
        """Test describing all workspaces with empty list."""

        # Mock list_workspaces response with empty list
        mock_list_response = {
            "workspaces": [],
        }

        # Mock the CdpClient instance
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_list_response

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=api_client)
        result = client.describe_all_workspaces()

        # Validate the result
        assert isinstance(result, list)
        assert len(result) == 0
        assert result == []

        # Verify describe_workspace was never called (only list_workspaces)
        assert api_client.post.call_count == 1
        api_client.post.assert_called_once_with(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )
