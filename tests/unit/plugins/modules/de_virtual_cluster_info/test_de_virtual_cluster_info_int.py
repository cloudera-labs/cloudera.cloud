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

from typing import Callable

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import de_virtual_cluster_info

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def vc_info_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common Virtual Cluster info module arguments."""

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


def test_vc_info_list_all(
    vc_info_module_args,
    existing_de_service,
    disposable_de_virtual_cluster,
):
    """Test listing all Virtual Clusters within a CDE service."""

    vc_info_module_args(
        {
            "environment": existing_de_service.environmentName,
            "service_name": existing_de_service.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters is not None
    assert isinstance(result.value.virtual_clusters, list)
    assert any(
        vc.get("vcName") == disposable_de_virtual_cluster.vcName
        for vc in result.value.virtual_clusters
    )


def test_vc_info_by_name(
    vc_info_module_args,
    existing_de_service,
    disposable_de_virtual_cluster,
):
    """Test getting a single Virtual Cluster by name."""

    vc_name = disposable_de_virtual_cluster.vcName

    vc_info_module_args(
        {
            "environment": existing_de_service.environmentName,
            "service_name": existing_de_service.name,
            "name": vc_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert len(result.value.virtual_clusters) == 1
    assert result.value.virtual_clusters[0]["vcName"] == vc_name
    assert result.value.virtual_clusters[0]["vcId"] == disposable_de_virtual_cluster.vcId


def test_vc_info_nonexistent_name(vc_info_module_args, existing_de_service):
    """Test getting a Virtual Cluster with a non-existent name."""

    vc_info_module_args(
        {
            "environment": existing_de_service.environmentName,
            "service_name": existing_de_service.name,
            "name": "non-existent-vc-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters is not None
    assert len(result.value.virtual_clusters) == 0


def test_vc_info_nonexistent_service(vc_info_module_args, existing_de_service):
    """Test that a non-existent CDE service yields an empty list, not a failure."""

    vc_info_module_args(
        {
            "environment": existing_de_service.environmentName,
            "service_name": "non-existent-service-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters == []
