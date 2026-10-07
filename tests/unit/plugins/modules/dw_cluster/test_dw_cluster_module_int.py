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

"""Integration tests for the dw_cluster module.

These tests hit the live CDP API. Read-only tests use the session-scoped
``existing_dw_cluster`` fixture. Create/delete tests are slow (~20-40 min)
and gated on ``CDP_ENVIRONMENT_NAME``.

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDW_CLUSTER_ID or CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os

import pytest

from typing import Callable

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import CdpEnvClient
from ansible_collections.cloudera.cloud.plugins.modules import dw_cluster
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    required_or_skip,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def dw_cluster_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Pre-populate common dw_cluster module arguments from the environment."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": env_context["CDP_API_ENDPOINT"],
            "access_key": env_context["CDP_ACCESS_KEY_ID"],
            "private_key": env_context["CDP_PRIVATE_KEY"],
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


def test_present_idempotent(dw_cluster_module_args, existing_dw_cluster):
    """Re-run state=present on an already-running cluster; verify changed=False."""
    dw_cluster_module_args(
        {
            "cluster_id": existing_dw_cluster.id,
            "env_crn": existing_dw_cluster.environmentCrn,
            "state": "present",
            "wait": False,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_cluster.main()

    assert exc.value.changed is False
    assert exc.value.cluster.get("id") == existing_dw_cluster.id


def test_present_with_cloud_platform_explicit(
    dw_cluster_module_args,
    existing_dw_cluster,
):
    """Explicit cloud_platform dispatches without env describe; idempotent on existing."""
    platform = existing_dw_cluster.cloudPlatform
    dw_cluster_module_args(
        {
            "cluster_id": existing_dw_cluster.id,
            "env_crn": existing_dw_cluster.environmentCrn,
            "cloud_platform": platform,
            "state": "present",
            "wait": False,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_cluster.main()

    assert exc.value.changed is False
    assert exc.value.cluster.get("cloudPlatform") == platform


def test_check_mode_present(dw_cluster_module_args, dw_client, env_context):
    """check_mode with state=present skips mutation.

    If the environment already has a cluster the module is idempotent
    (changed=False); otherwise it would create (changed=True).
    """
    env_name = required_or_skip("CDP_ENVIRONMENT_NAME")

    env_client = CdpEnvClient(api_client=dw_client.api_client)
    env_crn = env_client.get_environment_crn(env_name)
    clusters = dw_client.list_clusters(env_crn=env_crn) if env_crn else []

    dw_cluster_module_args(
        {
            "environment": env_name,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_cluster.main()

    if len(clusters) == 1:
        assert exc.value.changed is False
    else:
        assert exc.value.changed is True
        assert exc.value.cluster == {}


def test_check_mode_absent(dw_cluster_module_args, existing_dw_cluster):
    """check_mode with state=absent reports changed but does not delete."""
    dw_cluster_module_args(
        {
            "cluster_id": existing_dw_cluster.id,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_cluster.main()

    assert exc.value.changed is True


def test_absent_idempotent(dw_cluster_module_args):
    """Re-run state=absent on a cluster that does not exist; verify changed=False."""
    dw_cluster_module_args(
        {
            "cluster_id": "nonexistent-12345",
            "state": "absent",
            "wait": False,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        dw_cluster.main()

    assert exc.value.changed is False


@pytest.mark.slow
class TestDwClusterLifecycle:
    """Full create -> present-idempotent -> absent -> absent-idempotent lifecycle.

    Tests within this class must run in definition order (pytest default).
    The class shares a single cluster created by the first test.
    """

    _cluster_id = None
    _env_name = None

    def test_present_creates(self, dw_cluster_module_args, cleanup_dw_cluster):
        """state=present creates a new cluster."""
        env_name = required_or_skip("CDP_ENVIRONMENT_NAME")
        platform = os.getenv("CDW_CLUSTER_CLOUD_PLATFORM")

        create_args = {
            "environment": env_name,
            "state": "present",
            "wait": True,
            "timeout": 4500,
        }

        if platform:
            create_args["cloud_platform"] = platform

        if platform == "AZURE" or (not platform and os.getenv("CDW_AZURE_SUBNET_NAME")):
            create_args["azure"] = {
                "subnet": required_or_skip("CDW_AZURE_SUBNET_NAME"),
                "managed_identity": required_or_skip("CDW_AZURE_MANAGED_IDENTITY"),
            }

        if platform == "AWS" or (not platform and os.getenv("CDW_AWS_LB_SUBNETS")):
            aws_opts = {}
            lb = os.getenv("CDW_AWS_LB_SUBNETS")
            worker = os.getenv("CDW_AWS_WORKER_SUBNETS")
            if lb:
                aws_opts["lb_subnets"] = lb.split(",")
            if worker:
                aws_opts["worker_subnets"] = worker.split(",")
            if aws_opts:
                create_args["aws"] = aws_opts

        dw_cluster_module_args(create_args)
        with pytest.raises(AnsibleExitJson) as exc:
            dw_cluster.main()

        cluster_id = exc.value.cluster.get("id")
        if cluster_id:
            cleanup_dw_cluster(cluster_id)

        assert exc.value.changed is True
        assert exc.value.cluster.get("status") == "Running"

        TestDwClusterLifecycle._cluster_id = cluster_id
        TestDwClusterLifecycle._env_name = env_name

    def test_present_idempotent(self, dw_cluster_module_args):
        """Re-running state=present on the just-created cluster -> changed=False."""
        cluster_id = TestDwClusterLifecycle._cluster_id
        if cluster_id is None:
            pytest.skip("No cluster created by test_present_creates")

        dw_cluster_module_args(
            {
                "cluster_id": cluster_id,
                "environment": TestDwClusterLifecycle._env_name,
                "state": "present",
                "wait": False,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            dw_cluster.main()

        assert exc.value.changed is False
        assert exc.value.cluster.get("id") == cluster_id

    def test_absent_deletes(self, dw_cluster_module_args, dw_client):
        """state=absent deletes the cluster -> changed=True."""
        cluster_id = TestDwClusterLifecycle._cluster_id
        if cluster_id is None:
            pytest.skip("No cluster created by test_present_creates")

        dw_cluster_module_args(
            {
                "cluster_id": cluster_id,
                "state": "absent",
                "force": True,
                "wait": True,
                "timeout": 4500,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            dw_cluster.main()

        assert exc.value.changed is True
        assert dw_client.describe_cluster(cluster_id) is None

    def test_absent_idempotent(self, dw_cluster_module_args):
        """Re-running state=absent on the deleted cluster -> changed=False."""
        cluster_id = TestDwClusterLifecycle._cluster_id
        if cluster_id is None:
            pytest.skip("No cluster created by test_present_creates")

        dw_cluster_module_args(
            {
                "cluster_id": cluster_id,
                "state": "absent",
                "wait": False,
            },
        )

        with pytest.raises(AnsibleExitJson) as exc:
            dw_cluster.main()

        assert exc.value.changed is False
