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
import os
import pytest
import random
import tempfile
import uuid
from contextlib import contextmanager
from typing import Callable, Generator

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_customflow

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common DataFlow module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


def create_minimal_flow_definition(flow_name: str) -> dict:
    """
    Factory function to create a minimal NiFi flow definition.

    Args:
        flow_name: The name of the flow

    Returns:
        A minimal flow definition dictionary with random identifiers
    """

    return {
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
    }


@contextmanager
def temporary_flow_file(flow_name: str):
    """
    Context manager to create a temporary flow definition file.

    Args:
        flow_name: The name of the flow

    Yields:
        The path to the temporary flow file

    Example:
        with temporary_flow_file("my-flow") as flow_file:
            # Use flow_file path
            pass
    """
    flow_definition = create_minimal_flow_definition(flow_name)
    flow_content = json.dumps(flow_definition)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file_path = os.path.join(tmpdir, "flow.json")
        with open(temp_file_path, "w") as f:
            f.write(flow_content)
        yield temp_file_path


@pytest.fixture
def df_flow_delete(df_client) -> Generator[Callable[[str], None], None, None]:
    """Fixture to clean up DataFlow flows created during tests."""
    flow_crns = []

    def _df_flow_delete(flow_crn: str):
        flow_crns.append(flow_crn)
        return

    yield _df_flow_delete

    # Cleanup: delete all tracked flows
    for flow_crn in flow_crns:
        try:
            df_client.delete_flow(flow_crn=flow_crn)
        except Exception:
            pass


@pytest.fixture
def df_flow_create(df_client, df_flow_delete) -> Callable[[str, str, str], dict]:
    """
    Fixture to create DataFlow flows and ensure cleanup.

    Returns a function that creates a flow and registers it for cleanup.
    """

    def _df_flow_create(
        flow_name: str,
        description: str = None,
        comments: str = "Test Flow",
    ) -> dict:
        """
        Create a minimal DataFlow flow.

        Args:
            flow_name: Name of the flow to create
            description: Optional description for the flow
            comments: Version comments (default: "Test Flow")

        Returns:
            The created flow object from the API
        """

        # Create flow definition using factory function
        flow_definition = create_minimal_flow_definition(flow_name)
        flow_content = json.dumps(flow_definition)

        # Set default description if not provided
        if description is None:
            description = f"Test flow - {flow_name}"

        # Import the flow
        result = df_client.import_flow_definition(
            name=flow_name,
            file_content=flow_content,
            description=description,
            comments=comments,
        )

        # Register for cleanup
        if result and "crn" in result:
            df_flow_delete(result["crn"])

        return result

    return _df_flow_create


def test_df_flow_create_and_delete(df_flow_create):
    """Test creating and deleting a flow using fixtures."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-{random_suffix}"

    # Create flow using fixture
    result = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test custom flow - {flow_name}",
        comments="Initial Version",
    )

    # Verify the result
    assert result is not None
    assert "crn" in result
    assert result["name"] == flow_name
    assert result["versionCount"] == 1
    assert len(result["versions"]) == 1

    # Verify the version details
    version = result["versions"][0]
    assert version["version"] == 1
    assert version["comments"] == "Initial Version"
    assert "crn" in version


def test_df_customflow_import_via_module(df_module_args, env_context, df_flow_delete):
    """Test importing a CustomFlow via the Ansible module with real API calls."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-{random_suffix}"

    with temporary_flow_file(flow_name) as flow_file:
        # Execute module
        df_module_args(
            {
                "name": flow_name,
                "file": flow_file,
                "description": "Integration test flow",
                "comments": "Initial version",
                "state": "present",
            },
        )

        with pytest.raises(AnsibleExitJson) as result:
            df_customflow.main()

        assert result.value.changed is True
        assert result.value.customflow is not None
        assert result.value.customflow["name"] == flow_name

        # Register flow for cleanup using fixture
        flow_crn = result.value.customflow.get("crn")
        if flow_crn:
            df_flow_delete(flow_crn)

        # Test idempotency
        with pytest.raises(AnsibleExitJson) as result:
            df_customflow.main()

        assert result.value.changed is False
        assert result.value.customflow is not None
        assert result.value.customflow["name"] == flow_name


def test_df_customflow_delete_via_module(df_module_args, env_context, df_flow_create):
    """Test deleting a CustomFlow via the Ansible module with real API calls."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-{random_suffix}"

    # First, create a flow using the fixture
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow - {flow_name}",
        comments="Initial version",
    )

    assert flow is not None
    assert "crn" in flow

    df_module_args(
        {
            "name": flow_name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is False


def test_df_customflow_import_with_tags_via_module(
    df_module_args,
    env_context,
    df_flow_delete,
):
    """Test importing a CustomFlow with tags via the Ansible module with real API calls."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-tags-{random_suffix}"

    with temporary_flow_file(flow_name) as flow_file:
        # Execute module with tags
        df_module_args(
            {
                "name": flow_name,
                "file": flow_file,
                "description": "Integration test flow with tags",
                "comments": "Initial version with tags",
                "tags": [
                    {"tag_name": "production", "tag_color": "blue"},
                    {"tag_name": "stable", "tag_color": "green"},
                    {"tag_name": "tested"},
                ],
                "state": "present",
            },
        )

        with pytest.raises(AnsibleExitJson) as result:
            df_customflow.main()

        assert result.value.changed is True
        assert result.value.customflow is not None
        assert result.value.customflow["name"] == flow_name

        # Register flow for cleanup using fixture
        flow_crn = result.value.customflow.get("crn")
        if flow_crn:
            df_flow_delete(flow_crn)
