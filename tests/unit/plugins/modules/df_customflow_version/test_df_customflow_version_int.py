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
    AnsibleFailJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_customflow_version

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

        flow_definition = create_minimal_flow_definition(flow_name)
        flow_content = json.dumps(flow_definition)

        if description is None:
            description = f"Test flow - {flow_name}"

        result = df_client.import_flow_definition(
            name=flow_name,
            file_content=flow_content,
            description=description,
            comments=comments,
        )

        if result and "crn" in result:
            df_flow_delete(result["crn"])

        return result

    return _df_flow_create


def test_df_flow_version_create_and_verify(df_flow_create, df_client):
    """Test creating a flow version directly via the client."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-version-{random_suffix}"

    # Create the parent flow
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow for versioning - {flow_name}",
        comments="Version 1",
    )

    assert flow is not None
    assert "crn" in flow
    assert flow["versionCount"] == 1

    # Import a new version
    flow_definition = create_minimal_flow_definition(flow_name)
    flow_content = json.dumps(flow_definition)

    version = df_client.import_flow_definition_version(
        flow_crn=flow["crn"],
        file_content=flow_content,
        comments="Version 2",
    )

    assert version is not None
    assert "crn" in version
    assert version["version"] == 2
    assert version["comments"] == "Version 2"

    # Verify the flow now has 2 versions
    updated_flow = df_client.get_flow_by_crn(flow["crn"])
    assert updated_flow is not None
    assert updated_flow["versionCount"] == 2


def test_df_customflow_version_import_via_module(
    df_module_args,
    env_context,
    df_flow_create,
):
    """Test importing a CustomFlow version via the Ansible module using a file."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-version-{random_suffix}"

    # Create the parent flow first
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow for versioning - {flow_name}",
        comments="Initial version",
    )

    assert flow is not None
    assert "crn" in flow

    with temporary_flow_file(flow_name) as flow_file:
        df_module_args(
            {
                "flow_crn": flow["crn"],
                "file": flow_file,
                "comments": "Second version",
                "state": "present",
            },
        )

        with pytest.raises(AnsibleExitJson) as result:
            df_customflow_version.main()

        assert result.value.changed is True
        assert result.value.customflow_version is not None
        assert result.value.customflow_version["version"] == 2
        assert result.value.customflow_version["comments"] == "Second version"


def test_df_customflow_version_import_with_content_via_module(
    df_module_args,
    env_context,
    df_flow_create,
):
    """Test importing a CustomFlow version using the content parameter."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-version-content-{random_suffix}"

    # Create the parent flow first
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow for versioning - {flow_name}",
        comments="Initial version",
    )

    assert flow is not None
    assert "crn" in flow

    # Create flow definition and convert to JSON string
    flow_definition = create_minimal_flow_definition(flow_name)
    flow_content = json.dumps(flow_definition)

    df_module_args(
        {
            "flow_crn": flow["crn"],
            "content": flow_content,
            "comments": "Second version from content",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version is not None
    assert result.value.customflow_version["version"] == 2
    assert result.value.customflow_version["comments"] == "Second version from content"


def test_df_customflow_version_import_with_tags_via_module(
    df_module_args,
    env_context,
    df_flow_create,
):
    """Test importing a CustomFlow version with tags via the Ansible module."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-version-tags-{random_suffix}"

    # Create the parent flow first
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow for versioning with tags - {flow_name}",
        comments="Initial version",
    )

    assert flow is not None
    assert "crn" in flow

    with temporary_flow_file(flow_name) as flow_file:
        df_module_args(
            {
                "flow_crn": flow["crn"],
                "file": flow_file,
                "comments": "Second version with tags",
                "tags": [
                    {"tag_name": "production", "tag_color": "blue"},
                    {"tag_name": "stable", "tag_color": "green"},
                    {"tag_name": "tested"},
                ],
                "state": "present",
            },
        )

        with pytest.raises(AnsibleExitJson) as result:
            df_customflow_version.main()

        assert result.value.changed is True
        assert result.value.customflow_version is not None
        assert result.value.customflow_version["version"] == 2


def test_df_customflow_version_multiple_versions_via_module(
    df_module_args,
    env_context,
    df_flow_create,
):
    """Test that each module invocation always creates a new version (non-idempotent by design)."""

    random_suffix = random.randint(100000, 999999)
    flow_name = f"test-customflow-version-multi-{random_suffix}"

    # Create the parent flow first
    flow = df_flow_create(
        flow_name=flow_name,
        description=f"Integration test flow for multiple versions - {flow_name}",
        comments="Version 1",
    )

    assert flow is not None
    assert "crn" in flow

    flow_definition = create_minimal_flow_definition(flow_name)
    flow_content = json.dumps(flow_definition)

    # Import version 2
    df_module_args(
        {
            "flow_crn": flow["crn"],
            "content": flow_content,
            "comments": "Version 2",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["version"] == 2

    # Import version 3 - same args, always changed
    df_module_args(
        {
            "flow_crn": flow["crn"],
            "content": flow_content,
            "comments": "Version 3",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["version"] == 3


def test_df_customflow_version_nonexistent_flow_via_module(
    df_module_args,
    env_context,
):
    """Test that the module fails when the referenced flow CRN does not exist."""

    flow_definition = create_minimal_flow_definition("nonexistent-flow")
    flow_content = json.dumps(flow_definition)

    df_module_args(
        {
            "flow_crn": "crn:cdp:df:us-west-1:00000000-0000-0000-0000-000000000000:flow:nonexistent-flow-crn",
            "content": flow_content,
            "comments": "Should fail",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert result.value.failed is True
    assert "does not exist" in result.value.msg
