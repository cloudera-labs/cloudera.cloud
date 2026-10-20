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

"""Integration tests for CdpMlClient.

Read-only tests use the session-scoped ``existing_ml_workspace`` fixture.
Create/delete tests are slow (~20-40 min) and gated on ``CDP_ENVIRONMENT_NAME``.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re

from urllib.error import HTTPError

import pytest

from ansible_collections.cloudera.cloud.tests.unit import required_or_skip


pytestmark = pytest.mark.integration_api


class TestWorkspaceIntegration:
    """Read-only tests against C(existing_ml_workspace)."""

    def test_list_workspaces(self, ml_client, existing_ml_workspace):
        """Listing workspaces returns at least the shared workspace."""
        response = ml_client.list_workspaces()

        assert "workspaces" in response
        assert len(response["workspaces"]) > 0
        assert isinstance(response["workspaces"][0], dict)

    def test_list_workspaces_by_environment(self, ml_client, existing_ml_workspace):
        """Listing workspaces filtered by environment returns the shared workspace."""
        workspace = existing_ml_workspace["workspace"]
        env_name = workspace["environmentName"]

        response = ml_client.list_workspaces(env=env_name)

        assert "workspaces" in response
        assert len(response["workspaces"]) > 0
        assert all(ws["environmentName"] == env_name for ws in response["workspaces"])

    def test_describe_workspace_by_name_and_env(
        self,
        ml_client,
        existing_ml_workspace,
    ):
        """Describing by name+environment returns the shared workspace."""
        workspace = existing_ml_workspace["workspace"]

        response = ml_client.describe_workspace(
            name=workspace["instanceName"],
            env=workspace["environmentName"],
        )

        assert response.get("workspace") is not None
        assert response["workspace"]["instanceName"] == workspace["instanceName"]

    def test_describe_workspace_by_crn(self, ml_client, existing_ml_workspace):
        """Describing by CRN returns the shared workspace, ignoring name/env."""
        workspace = existing_ml_workspace["workspace"]

        response = ml_client.describe_workspace(crn=workspace["crn"])

        assert response.get("workspace") is not None
        assert response["workspace"]["crn"] == workspace["crn"]

    def test_describe_workspace_not_found(self, ml_client):
        """Describing a non-existent workspace returns an empty response (squelched)."""
        response = ml_client.describe_workspace(
            env="non-existent-environment",
            name="non-existent-workspace",
        )

        assert response == {} or response is None or "workspace" not in response

    # @pytest.mark.slow
    def test_describe_all_workspaces(self, ml_client, existing_ml_workspace):
        """Describing all workspaces in the tenant returns at least the shared workspace."""
        response = ml_client.describe_all_workspaces()

        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)


# @pytest.mark.slow
class TestWorkspaceCreateDeleteIntegration:
    """Create/delete tests against C(disposable_ml_workspace). ~20-40 min each."""

    def test_create_and_delete_workspace(self, ml_client, disposable_ml_workspace):
        """A freshly created workspace is readable, then deletes to gone."""
        workspace = disposable_ml_workspace["workspace"]

        described = ml_client.describe_workspace(crn=workspace["crn"])
        assert described.get("workspace") is not None

        ml_client.delete_workspace(
            force=True,
            workspace_crn=workspace["crn"],
            remove_storage=True,
        )
        ml_client.wait_for_workspace_state(
            environment=workspace["environmentName"],
            workspace_name=workspace["instanceName"],
            target_states=None,
            delay=30,
            timeout=3600,
        )

        assert (
            ml_client.describe_workspace(crn=workspace["crn"]).get("workspace") is None
        )

    def test_delete_nonexistent_workspace_raises(self, ml_client):
        """delete_workspace on a nonexistent name/env raises."""
        env_name = required_or_skip("CDP_ENVIRONMENT_NAME")

        with pytest.raises(HTTPError):
            ml_client.delete_workspace(
                force=True,
                workspace_name="nonexistent-12345",
                environment_name=env_name,
            )

    def test_create_workspace_with_workspace_quota(
        self,
        ml_client,
        cleanup_ml_workspace,
        request,
    ):
        """create_workspace accepts resourcePoolConfig.workspaceQuota and the workspace is created."""
        env_name = required_or_skip("CDP_ENVIRONMENT_NAME")
        workspace_name = "ansible-" + re.sub(
            r"[^a-z0-9]",
            "-",
            request.node.name.lower(),
        )[:40].strip("-")
        parent_pool = os.getenv("CDP_ML_RESOURCE_POOL_PARENT", "root")

        cleanup_ml_workspace(workspace_name, env_name)

        ml_client.create_workspace(
            workspace_name=workspace_name,
            environment_name=env_name,
            provision_k8s_request={
                "environmentName": env_name,
                "instanceGroups": [
                    {
                        "name": "cpu_settings",
                        "instanceCount": 1,
                        "instanceType": os.getenv("CDP_ML_INSTANCE_TYPE", "m5.2xlarge"),
                        "instanceTier": "ON_DEMAND",
                        "autoscaling": {
                            "minInstances": 0,
                            "maxInstances": 1,
                            "enabled": True,
                        },
                        "rootVolume": {"size": 300},
                    },
                ],
            },
            resource_pool_config={
                "parentPoolName": parent_pool,
                "workspaceQuota": {
                    "cpuQuota": "4",
                    "memoryQuota": "8Gi",
                },
            },
        )

        result = ml_client.wait_for_workspace_state(
            environment=env_name,
            workspace_name=workspace_name,
            target_states=ml_client.READY_STATES,
            delay=30,
            timeout=3600,
        )

        workspace = result.get("workspace")
        assert workspace is not None
        assert workspace.get("instanceName") == workspace_name

        # NOTE: cdp_ml.py's RETURN doc does not document a resourcePoolConfig
        # key on describeWorkspace; only assert the quota round-trips if the
        # live API actually returns it
        if "resourcePoolConfig" in workspace:
            assert (
                workspace["resourcePoolConfig"]
                .get("workspaceQuota", {})
                .get("cpuQuota")
                == "4"
            )
