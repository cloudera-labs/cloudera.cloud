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

"""Integration tests for the compute_info module (read-only).

Tests share the session-scoped ``existing_compute_cluster`` fixture: a RUNNING,
externalized, non-default cluster named ``ansible-compute-inttest``. If it already
exists in the environment it is reused and left in place; otherwise the fixture
creates it (~35 min) and deletes it at the end of the session (~15 min). No extra
environment variables are needed.

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Callable

import pytest

from ansible_collections.cloudera.cloud.plugins.modules import compute_info
from ansible_collections.cloudera.cloud.tests.unit import AnsibleExitJson


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def compute_info_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Pre-populate common compute_info module arguments from the environment."""

    def wrapped_args(args=None):
        merged = {
            "endpoint": env_context["CDP_API_ENDPOINT"],
            "access_key": env_context["CDP_ACCESS_KEY_ID"],
            "private_key": env_context["CDP_PRIVATE_KEY"],
        }
        merged.update(args or {})
        return module_args(merged)

    return wrapped_args


def test_info_by_environment(compute_info_module_args, existing_compute_cluster):
    compute_info_module_args({"environment": existing_compute_cluster.envName})

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert exc.value.changed is False
    assert any(
        c["cluster_crn"] == existing_compute_cluster.clusterCrn
        for c in exc.value.clusters
    )


def test_info_by_crn(compute_info_module_args, existing_compute_cluster):
    compute_info_module_args({"crn": existing_compute_cluster.clusterCrn})

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert [c["cluster_name"] for c in exc.value.clusters] == [
        existing_compute_cluster.clusterName,
    ]


def test_info_default_true_excludes_shared_cluster(
    compute_info_module_args,
    existing_compute_cluster,
):
    """default=True returns only default clusters, never the shared externalized one."""
    compute_info_module_args(
        {"environment": existing_compute_cluster.envName, "default": True},
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert all(c["is_default"] is True for c in exc.value.clusters)
    assert existing_compute_cluster.clusterCrn not in [
        c["cluster_crn"] for c in exc.value.clusters
    ]


def test_info_default_false_includes_shared_cluster(
    compute_info_module_args,
    existing_compute_cluster,
):
    compute_info_module_args(
        {"environment": existing_compute_cluster.envName, "default": False},
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert existing_compute_cluster.clusterCrn in [
        c["cluster_crn"] for c in exc.value.clusters
    ]
    assert all(c["is_default"] is not True for c in exc.value.clusters)


def test_info_shape_externalized_includes_shared_cluster(
    compute_info_module_args,
    existing_compute_cluster,
):
    compute_info_module_args(
        {
            "environment": existing_compute_cluster.envName,
            "cluster_shape": "Externalized",
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert existing_compute_cluster.clusterCrn in [
        c["cluster_crn"] for c in exc.value.clusters
    ]


def test_info_unknown_crn_returns_empty(
    compute_info_module_args,
    existing_compute_cluster,
):
    prefix = existing_compute_cluster.clusterCrn.rsplit(":", 1)[0]
    compute_info_module_args({"crn": f"{prefix}:nonexistent-12345"})

    with pytest.raises(AnsibleExitJson) as exc:
        compute_info.main()

    assert exc.value.clusters == []
