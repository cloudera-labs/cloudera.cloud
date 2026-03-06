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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import CdpDeClient
from ansible_collections.cloudera.cloud.plugins.modules import de_info

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


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


@pytest.fixture
def de_client(test_cdp_client) -> CdpDeClient:
    """Fixture to provide a Data Engineering client for tests."""
    return CdpDeClient(api_client=test_cdp_client)


@pytest.fixture
def valid_de_service(de_client):
    """Fixture to find a valid, describable Data Engineering service for testing."""
    services = de_client.list_services().get("services", [])

    if not services:
        pytest.skip("No Data Engineering services available for testing")

    # Find a service that can be described successfully
    for svc in services:
        cluster_id = svc.get("clusterId")
        if cluster_id:
            details = de_client.describe_service(cluster_id)
            if details and details.get("service"):
                return svc

    pytest.skip("No describable Data Engineering services available for testing")


def test_de_service_info_list_all(de_info_module_args):
    """Test listing all Data Engineering services."""

    de_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert isinstance(result.value.services, list)


def test_de_service_info_by_name(de_info_module_args, valid_de_service):
    """Test getting Data Engineering service by name."""

    service_name = valid_de_service.get("name")

    de_info_module_args({"name": service_name})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) == 1
    assert result.value.services[0]["name"] == service_name
    assert "clusterId" in result.value.services[0]


def test_de_service_info_by_cluster_id(de_info_module_args, valid_de_service):
    """Test getting Data Engineering service by cluster ID."""

    cluster_id = valid_de_service.get("clusterId")

    de_info_module_args({"cluster_id": cluster_id})

    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    # Verify the result
    assert result.value.changed is False
    assert result.value.services is not None
    assert len(result.value.services) == 1
    assert result.value.services[0]["clusterId"] == cluster_id
    assert "name" in result.value.services[0]


def test_de_service_info_by_env_name(de_info_module_args, valid_de_service):
    """Test getting Data Engineering service by environment name."""

    env_name = valid_de_service.get("environmentName")

    if not env_name:
        pytest.skip("Service does not have environmentName")

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
