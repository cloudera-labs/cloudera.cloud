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

"""Integration tests for the dw_cluster_info module.

These tests hit the live CDP API. They use the session-scoped
``existing_dw_cluster`` fixture (never torn down).

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDW_CLUSTER_ID or CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os

import pytest

from typing import Callable

from ansible_collections.cloudera.cloud.plugins.modules import dw_cluster_info
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def dw_info_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Pre-populate common dw_cluster_info module arguments from the environment."""

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


def test_list_all_clusters(dw_info_module_args, existing_dw_cluster):
    """No filters: verify changed=False, returns a non-empty list, existing cluster present."""
    dw_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        dw_cluster_info.main()

    assert result.value.changed is False
    assert isinstance(result.value.clusters, list)
    assert len(result.value.clusters) >= 1
    assert any(
        c.get("id") == existing_dw_cluster.id for c in result.value.clusters
    )


def test_describe_by_cluster_id(dw_info_module_args, existing_dw_cluster):
    """cluster_id set: verify single-element list with matching id."""
    dw_info_module_args({"cluster_id": existing_dw_cluster.id})

    with pytest.raises(AnsibleExitJson) as result:
        dw_cluster_info.main()

    assert result.value.changed is False
    assert len(result.value.clusters) == 1
    assert result.value.clusters[0]["id"] == existing_dw_cluster.id


def test_list_by_environment(dw_info_module_args, existing_dw_cluster):
    """environment set to the env name: verify results are in that environment."""
    env_name = os.getenv("CDP_ENVIRONMENT_NAME")
    if not env_name:
        pytest.skip("CDP_ENVIRONMENT_NAME required for env-based listing test")

    dw_info_module_args({"environment": env_name})

    with pytest.raises(AnsibleExitJson) as result:
        dw_cluster_info.main()

    assert result.value.changed is False
    assert isinstance(result.value.clusters, list)
    assert len(result.value.clusters) >= 1
    assert any(
        c.get("id") == existing_dw_cluster.id for c in result.value.clusters
    )


def test_nonexistent_cluster_id(dw_info_module_args):
    """cluster_id set to bogus value: verify empty list (not fail_json)."""
    dw_info_module_args({"cluster_id": "nonexistent-12345"})

    with pytest.raises(AnsibleExitJson) as result:
        dw_cluster_info.main()

    assert result.value.changed is False
    assert result.value.clusters == []


def test_nonexistent_environment(dw_info_module_args):
    """environment set to bogus name: verify empty list."""
    dw_info_module_args({"environment": "nonexistent-env-99999"})

    with pytest.raises(AnsibleExitJson) as result:
        dw_cluster_info.main()

    assert result.value.changed is False
    assert result.value.clusters == []
