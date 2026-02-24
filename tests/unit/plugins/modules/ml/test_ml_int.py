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

import os
import pytest

from typing import Callable, Generator, Optional

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_ml import CdpMlClient
from ansible_collections.cloudera.cloud.plugins.modules import ml

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    # "ENV_CRN",
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDP_ENVIRONMENT_NAME",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api

@pytest.fixture
def ml_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common ML module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
                "environment": env_context["CDP_ENVIRONMENT_NAME"],
            },
        )
        return module_args(args)

    return wrapped_args

@pytest.fixture
def ml_client(test_cdp_client) -> CdpMlClient:
    """Fixture to provide a Machine Learning client for tests."""
    return CdpMlClient(api_client=test_cdp_client)

@pytest.fixture
def ml_workspace_create(
    ml_client: CdpMlClient,
    ml_workspace_delete,
    env_context,
) -> Callable[[str, dict], dict]:
    """
    Fixture to create ML workspace for tests.

    Returns a function that creates the workspace and registers it for cleanup.
    """

    def _create_workspace(workspace_name: str, **kwargs) -> dict:
        """Create ML workspace and register for cleanup."""
        environment_name = env_context["CDP_ENVIRONMENT_NAME"]

        # Check if workspace already exists for this environment
        workspaces = ml_client.list_workspaces(env=environment_name)
        existing_workspace = None
        for ws in workspaces.get("workspaces", []):
            if ws.get("instanceName") == workspace_name:
                existing_workspace = ws
                break

        if existing_workspace:
            # Workspace already exists
            # Register for cleanup
            ml_workspace_delete(name=workspace_name, env=environment_name)

            # Wait for workspace to be in a healthy state if it's still creating
            current_state = existing_workspace.get("instanceStatus")
            if current_state not in ml_client.READY_STATES:
                # Workspace exists but is not yet in a stable state
                result = ml_client.wait_for_workspace_state(
                    environment=environment_name,
                    workspace_name=workspace_name,
                    target_states=ml_client.READY_STATES,
                    timeout=3600,  # 60 minutes
                    poll_interval=30,
                )
            else:
                # Already in ready state, just return workspace details
                result = {"workspace": existing_workspace}
        else:
            # Merge default kwargs with provided ones
            create_params = {
                "workspace_name": workspace_name,
                "environment_name": environment_name,
                "provision_k8s_request": {
                    "environmentName": environment_name,
                    "instanceGroups": [
                        {
                            "name": "cpu_settings",
                            "instanceCount": 1,
                            "instanceType": "m5.2xlarge",
                            "instanceTier": "ON_DEMAND",
                            "autoscaling": {
                                "minInstances": 0,
                                "maxInstances": 1,
                                "enabled": True,
                            },
                            "rootVolume": {"size": 300},
                        }
                    ],
                },
            }
            create_params.update(kwargs)

            ml_client.create_workspace(**create_params)
            
            # Register for cleanup
            ml_workspace_delete(name=workspace_name, env=environment_name)

            # Wait for workspace to be created
            result = ml_client.wait_for_workspace_state(
                environment=environment_name,
                workspace_name=workspace_name,
                target_states=ml_client.READY_STATES,
                timeout=3600,  # 60 minutes
                poll_interval=30,
            )

        return result

    return _create_workspace

@pytest.fixture
def ml_workspace_delete(ml_client: CdpMlClient, env_context) -> Generator[Optional[dict], None, None]:
    """
    Fixture to track and clean up ML workspace.

    Yields a setter function to register workspace details for cleanup.
    Ensures cleanup by deleting the workspace after test completion.
    """
    workspace_info = {"value": None}

    def _set_workspace(name: str = None, env: str = None):
        """Register workspace for cleanup by name+env."""
        # If all parameters are None, clear the registration
        if name is None and env is None:
            workspace_info["value"] = None
        else:
            workspace_info["value"] = {
                "name": name,
                "env": env or env_context["CDP_ENVIRONMENT_NAME"],
            }

    # Yield the setter function
    yield _set_workspace

    # Cleanup: delete workspace if it was registered
    if workspace_info["value"]:
        try:
            ws_info = workspace_info["value"]
            
            # Delete the workspace
            ml_client.delete_workspace(
                force=True,
                workspace_name=ws_info.get("name"),
                environment_name=ws_info.get("env"),
                remove_storage=True,
            )
            
            # Wait for workspace to be fully deleted
            if ws_info.get("name") and ws_info.get("env"):
                ml_client.wait_for_workspace_state(
                    environment=ws_info["env"],
                    workspace_name=ws_info["name"],
                    target_states=None,  # Wait for deletion
                    timeout=3600,  # 60 minutes
                    poll_interval=30,
                    ignore_failures=True,
                )
        except Exception as e:
            pytest.fail(
                f"Failed to clean up ML workspace: {workspace_info['value']}. {e}",
            )

def test_ml_create_workspace(ml_module_args, ml_workspace_delete, env_context, request):
    """Integration test for creating a Cloudera AI workspace."""

    # Generate a unique workspace name from the pytest node name
    workspace_name = request.node.name.replace("_", "-")

    ml_module_args(
        {
        "state": "present",
        "name": workspace_name,
        # "name": "se-sandbox-aws-ml",
        "wait": True,
        "k8s_request": {
            "environmentName": env_context["CDP_ENVIRONMENT_NAME"],
            "instanceGroups": [
                {
                    "name": "cpu_settings",
                    "instanceCount": 1,
                    "instanceType": "m5.2xlarge",
                    "instanceTier": "ON_DEMAND",
                    "autoscaling": {
                        "minInstances": 0,
                        "maxInstances": 1,
                        "enabled": True
                    },
                    "rootVolume": {
                        "size": 300
                    }
                }
            ]
        },
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    # Register the workspace for cleanup
    ml_workspace_delete(name=workspace_name, env=env_context["CDP_ENVIRONMENT_NAME"])

    # Verify the result
    assert hasattr(result.value, "workspace")
    assert isinstance(result.value.workspace, dict)
    assert result.value.changed is True

    # Idempotency check: run the same create again and expect no changes
    with pytest.raises(AnsibleExitJson) as idempotent_result:
        ml.main()

    assert hasattr(idempotent_result.value, "workspace")
    assert isinstance(idempotent_result.value.workspace, dict)
    assert idempotent_result.value.changed is False


def test_ml_delete_workspace(
    ml_module_args,
    ml_workspace_create,
    ml_workspace_delete,
    ml_client,
    request,
):
    """Integration test for deleting a Cloudera AI workspace."""

    # Generate a unique workspace name from the pytest node name
    workspace_name = request.node.name.replace("_", "-") + "v2"

    # Create the workspace first (or get existing one)
    ml_workspace_create(workspace_name)

    # Execute module to delete the workspace
    ml_module_args(
        {
            "state": "absent",
            "name": workspace_name,
            "wait": True,
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        ml.main()

    # Verify the result
    assert hasattr(result.value, "workspace")
    assert isinstance(result.value.workspace, dict)
    assert result.value.changed is True

    # Clear the registered workspace since we've already deleted it
    # This prevents the fixture cleanup from trying to delete again
    ml_workspace_delete()

    # Idempotency check: running again should not change anything
    with pytest.raises(AnsibleExitJson) as idempotent_result:
        ml.main()

    assert hasattr(idempotent_result.value, "workspace")
    assert isinstance(idempotent_result.value.workspace, dict)
    assert idempotent_result.value.changed is False