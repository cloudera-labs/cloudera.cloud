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

from ansible_collections.cloudera.cloud.plugins.modules import de_info

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def de_info_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common Data Engineering info module arguments."""

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


def test_de_service_info_list_all(de_info_module_args, existing_de_service):
    """Test listing all Data Engineering services."""

    de_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert isinstance(result.value.services, list)
    assert any(
        svc.get("name") == existing_de_service.name for svc in result.value.services
    )


def test_de_service_info_by_name(de_info_module_args, existing_de_service):
    """Test getting Data Engineering service by name."""

    service_name = existing_de_service.name

    de_info_module_args({"name": service_name})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) == 1
    assert result.value.services[0]["name"] == service_name
    assert "clusterId" in result.value.services[0]


def test_de_service_info_by_cluster_id(de_info_module_args, existing_de_service):
    """Test getting Data Engineering service by cluster ID."""

    cluster_id = existing_de_service.clusterId

    de_info_module_args({"cluster_id": cluster_id})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) == 1
    assert result.value.services[0]["clusterId"] == cluster_id
    assert "name" in result.value.services[0]


def test_de_service_info_by_env_name(de_info_module_args, existing_de_service):
    """Test getting Data Engineering service by environment name."""

    env_name = existing_de_service.environmentName

    de_info_module_args({"env_name": env_name})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) >= 1
    # Verify at least one service has the expected environment name
    assert any(svc.get("environmentName") == env_name for svc in result.value.services)


def test_de_service_info_nonexistent_name(de_info_module_args):
    """Test getting Data Engineering service with non-existent name."""

    de_info_module_args({"name": "non-existent-service-12345"})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) == 0
