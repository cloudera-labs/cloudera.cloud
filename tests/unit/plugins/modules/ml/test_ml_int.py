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

"""Integration tests for the ml module.

Read-only tests use the session-scoped ``existing_ml_workspace`` fixture.
Create/delete tests are slow (~20-40 min) and gated on ``CDP_ENVIRONMENT_NAME``.

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY, CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re

import pytest

from typing import Callable

from ansible.module_utils import basic

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import ml

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDP_ENVIRONMENT_NAME",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


_K8S_INSTANCE_GROUP = {
    "name": "cpu_settings",
    "instanceCount": 1,
    "instanceTier": "ON_DEMAND",
    "autoscaling": {
        "minInstances": 0,
        "maxInstances": 1,
        "enabled": True,
    },
    "rootVolume": {"size": 300},
}


def _k8s_request(env_name: str) -> dict:
    """Build a minimal provisioning request for module-level create tests."""
    return {
        "environmentName": env_name,
        "instanceGroups": [
            {
                **_K8S_INSTANCE_GROUP,
                "instanceType": os.getenv("CDP_ML_INSTANCE_TYPE", "m5.2xlarge"),
            },
        ],
    }


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


def test_present_idempotent(ml_module_args, existing_ml_workspace):
    """Re-run state=present on the shared workspace; verify changed=False."""
    workspace = existing_ml_workspace["workspace"]

    ml_module_args(
        {
            "state": "present",
            "name": workspace["instanceName"],
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is False
    assert exc.value.workspace.get("instanceName") == workspace["instanceName"]


def test_check_mode_present(ml_module_args, ml_client, env_context, request):
    """check_mode with state=present on a nonexistent name reports changed, makes no call."""
    env_name = env_context["CDP_ENVIRONMENT_NAME"]
    workspace_name = "ansible-" + re.sub(
        r"[^a-z0-9]",
        "-",
        request.node.name.lower(),
    )[
        :40
    ].strip("-")

    assert (
        ml_client.describe_workspace(name=workspace_name, env=env_name).get(
            "workspace",
        )
        is None
    )

    ml_module_args(
        {
            "state": "present",
            "name": workspace_name,
            "wait": False,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is True
    assert exc.value.workspace == {}

    # No API call was made: the workspace is still absent.
    assert (
        ml_client.describe_workspace(name=workspace_name, env=env_name).get(
            "workspace",
        )
        is None
    )


def test_check_mode_absent(ml_module_args, existing_ml_workspace):
    """check_mode with state=absent against the shared workspace reports changed=False.

    Per the module's absent-path semantics (ml.py), check_mode on an
    existing+removable workspace sets C(workspace) but does not flip
    C(changed) unless deletion would actually occur.
    """
    workspace = existing_ml_workspace["workspace"]

    ml_module_args(
        {
            "state": "absent",
            "name": workspace["instanceName"],
            "wait": False,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is False


def test_absent_idempotent(ml_module_args, request):
    """Re-run state=absent against a name that does not exist; verify changed=False."""
    workspace_name = "ansible-" + re.sub(
        r"[^a-z0-9]",
        "-",
        request.node.name.lower(),
    )[
        :40
    ].strip("-")

    ml_module_args(
        {
            "state": "absent",
            "name": workspace_name,
            "wait": False,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is False


@pytest.mark.slow
class TestMlWorkspaceLifecycle:
    """Full create -> present-idempotent -> absent -> absent-idempotent lifecycle.

    Tests within this class must run in definition order (pytest default).
    The class shares a single workspace created by the first test.
    """

    _workspace_name = None

    def test_present_creates(
        self,
        ml_module_args,
        cleanup_ml_workspace,
        env_context,
        request,
    ):
        """state=present creates a new workspace."""
        env_name = env_context["CDP_ENVIRONMENT_NAME"]
        workspace_name = request.node.name.replace("_", "-")

        ml_module_args(
            {
                "state": "present",
                "name": workspace_name,
                "wait": True,
                "timeout": 3600,
                "k8s_request": _k8s_request(env_name),
            },
        )

        cleanup_ml_workspace(workspace_name, env_name)

        with pytest.raises(AnsibleExitJson) as exc:
            ml.main()

        assert exc.value.changed is True
        assert exc.value.workspace.get("instanceName") == workspace_name

        TestMlWorkspaceLifecycle._workspace_name = workspace_name

    def test_present_idempotent(self, ml_module_args):
        """Re-running state=present on the just-created workspace -> changed=False."""
        workspace_name = TestMlWorkspaceLifecycle._workspace_name
        if workspace_name is None:
            pytest.skip("No workspace created by test_present_creates")

        ml_module_args(
            {
                "state": "present",
                "name": workspace_name,
                "wait": True,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            ml.main()

        assert exc.value.changed is False
        assert exc.value.workspace.get("instanceName") == workspace_name

    def test_absent_deletes(self, ml_module_args, ml_client, env_context):
        """state=absent deletes the workspace -> changed=True."""
        workspace_name = TestMlWorkspaceLifecycle._workspace_name
        if workspace_name is None:
            pytest.skip("No workspace created by test_present_creates")

        ml_module_args(
            {
                "state": "absent",
                "name": workspace_name,
                "wait": True,
                "timeout": 3600,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            ml.main()

        assert exc.value.changed is True
        assert (
            ml_client.describe_workspace(
                name=workspace_name,
                env=env_context["CDP_ENVIRONMENT_NAME"],
            ).get("workspace")
            is None
        )

    def test_absent_idempotent(self, ml_module_args):
        """Re-running state=absent on the deleted workspace -> changed=False."""
        workspace_name = TestMlWorkspaceLifecycle._workspace_name
        if workspace_name is None:
            pytest.skip("No workspace created by test_present_creates")

        ml_module_args(
            {
                "state": "absent",
                "name": workspace_name,
                "wait": False,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            ml.main()

        assert exc.value.changed is False


@pytest.mark.slow
def test_present_create_with_workspace_quota(
    ml_module_args,
    cleanup_ml_workspace,
    env_context,
    request,
):
    """resource_pool.parent_pool_name + workspace_quota creates successfully."""
    env_name = env_context["CDP_ENVIRONMENT_NAME"]
    workspace_name = request.node.name.replace("_", "-")
    parent_pool = os.getenv("CDP_ML_RESOURCE_POOL_PARENT", "root")

    ml_module_args(
        {
            "state": "present",
            "name": workspace_name,
            "wait": True,
            "timeout": 3600,
            "k8s_request": _k8s_request(env_name),
            "resource_pool": {
                "parent_pool_name": parent_pool,
                "workspace_quota": {
                    "cpu_quota": "4",
                    "memory_quota": "8Gi",
                },
            },
        },
    )

    cleanup_ml_workspace(workspace_name, env_name)

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is True
    assert exc.value.workspace.get("instanceName") == workspace_name


@pytest.mark.slow
def test_present_create_with_legacy_resource_pool(
    ml_module_args,
    cleanup_ml_workspace,
    env_context,
    request,
    mocker,
):
    """Deprecated resource_pool.{cpu,gpu,memory} form creates successfully and warns."""
    env_name = env_context["CDP_ENVIRONMENT_NAME"]
    workspace_name = request.node.name.replace("_", "-")

    deprecate_spy = mocker.spy(basic.AnsibleModule, "deprecate")

    ml_module_args(
        {
            "state": "present",
            "name": workspace_name,
            "wait": True,
            "timeout": 3600,
            "k8s_request": _k8s_request(env_name),
            "resource_pool": {
                "cpu": "4",
                "gpu": "1",
                "memory": "8Gi",
            },
        },
    )

    cleanup_ml_workspace(workspace_name, env_name)

    with pytest.raises(AnsibleExitJson) as exc:
        ml.main()

    assert exc.value.changed is True
    assert exc.value.workspace.get("instanceName") == workspace_name
    assert deprecate_spy.call_count >= 2
