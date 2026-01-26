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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_service

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "ENV_CRN",
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Test configuration constants
TEST_MIN_NODES = 3
TEST_MAX_NODES = 10
TEST_USE_PUBLIC_LB = True
TEST_PRIVATE_CLUSTER = False
TEST_CLUSTER_SUBNET_FILTER = "pub"
TEST_LB_SUBNET_FILTER = "pub"
TEST_TAGS = {
    "test1": "test1value",
    "test2": "test2_value",
}

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
                "env_crn": env_context["ENV_CRN"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


@pytest.fixture
def df_service_disable(df_client) -> Generator[Optional[str], None, None]:
    """
    Fixture to track and clean up DataFlow service.

    Yields the service CRN if service is enabled during test.
    Ensures cleanup by disabling the service after test completion.
    """
    service_crn = {"value": None}

    def _set_crn(crn: str):
        service_crn["value"] = crn

    # Yield the setter function
    yield _set_crn

    # Cleanup: disable service if it was created
    if service_crn["value"]:
        try:
            df_client.disable_service(
                crn=service_crn["value"],
                terminate_deployments=True,
            )
            # Wait for service to be fully disabled
            df_client.wait_for_service_state(
                service_crn=service_crn["value"],
                target_states=["NOT_ENABLED"],
                timeout=1800,  # 30 minutes
                delay=30,
            )
        except Exception as e:
            pytest.fail(
                f"Failed to clean up DataFlow service: {service_crn['value']}. {e}",
            )


@pytest.fixture
def df_service_enable(
    df_client,
    df_service_disable,
    env_context,
) -> Callable[[str, dict], dict]:
    """
    Fixture to enable DataFlow service for tests.

    Returns a function that enables the service and registers it for cleanup.
    """

    def _enable_service(env_crn: str = None, **kwargs) -> dict:
        """Enable DataFlow service and register for cleanup."""
        if env_crn is None:
            env_crn = env_context["ENV_CRN"]

        # Check if service is already enabled for this environment
        services = df_client.list_services().get("services", [])
        existing_service = None
        for service in services:
            if service.get("environmentCrn") == env_crn:
                existing_service = service
                break

        if existing_service:
            # Service already exists, get full details
            service_crn = existing_service.get("crn")
            result = {"service": df_client.describe_service(service_crn)}

            # Register for cleanup
            df_service_disable(service_crn)

            # Wait for service to be in a healthy state if it's still enabling
            current_state = existing_service.get("status", {}).get("state")
            if current_state not in df_client.REMOVABLE_STATES:
                # Service exists but is not yet in a stable state (e.g., still ENABLING)
                df_client.wait_for_service_state(
                    service_crn=service_crn,
                    target_states=df_client.REMOVABLE_STATES,
                    timeout=1800,  # 30 minutes
                    delay=30,
                )
        else:
            # Merge default kwargs with provided ones
            enable_params = {
                "environment_crn": env_crn,
                "min_k8s_node_count": TEST_MIN_NODES,
                "max_k8s_node_count": TEST_MAX_NODES,
                "use_public_load_balancer": TEST_USE_PUBLIC_LB,
                "private_cluster": TEST_PRIVATE_CLUSTER,
                "skip_preflight_checks": False,
                "user_defined_routing": False,
                "tags": TEST_TAGS,
            }
            enable_params.update(kwargs)

            result = df_client.enable_service(**enable_params)

            # Wait for service to be enabled
            service_crn = result.get("service", {}).get("crn")
            if service_crn:
                df_service_disable(service_crn)
                df_client.wait_for_service_state(
                    service_crn=service_crn,
                    target_states=["ENABLED"],
                    timeout=1800,  # 30 minutes
                    delay=30,
                )

        return result

    return _enable_service


def test_df_service_enable(df_module_args, df_service_disable):
    """Test enabling DataFlow service with subnet filters."""

    df_module_args(
        {
            "state": "present",
            "nodes_min": TEST_MIN_NODES,
            "nodes_max": TEST_MAX_NODES,
            "cluster_subnets_filter": TEST_CLUSTER_SUBNET_FILTER,
            "loadbalancer_subnets_filter": TEST_LB_SUBNET_FILTER,
            "public_loadbalancer": TEST_USE_PUBLIC_LB,
            "private_cluster": TEST_PRIVATE_CLUSTER,
            "tags": TEST_TAGS,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # Register the service CRN for cleanup
    service_crn = result.value.service.get("crn")
    assert service_crn is not None
    df_service_disable(service_crn)

    # Verify the result
    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
    assert "environmentCrn" in result.value.service

    # Idempotency check - running again should not change anything
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn


def test_df_service_enable_with_jmespath_filters(
    df_module_args,
    df_service_disable,
):
    """Test enabling DataFlow service using JMESPath subnet filters."""

    # Execute module with JMESPath filters
    df_module_args(
        {
            "state": "present",
            "nodes_min": TEST_MIN_NODES,
            "nodes_max": TEST_MAX_NODES,
            "cluster_subnets_filter": "[?contains(subnetName, 'pub')]",  # JMESPath query
            "loadbalancer_subnets_filter": "[?contains(subnetName, 'pub')]",  # JMESPath query
            "public_loadbalancer": TEST_USE_PUBLIC_LB,
            "private_cluster": TEST_PRIVATE_CLUSTER,
            "tags": TEST_TAGS,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # Register the service CRN for cleanup
    service_crn = result.value.service.get("crn")
    assert service_crn is not None
    df_service_disable(service_crn)

    # Verify the result
    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
    assert "environmentCrn" in result.value.service

    # Verify that subnets were selected (should have cluster and load balancer subnets)
    assert "clusterSubnets" in result.value.service
    assert "loadBalancerSubnets" in result.value.service
    assert len(result.value.service.get("clusterSubnets", [])) > 0
    assert len(result.value.service.get("loadBalancerSubnets", [])) > 0


def test_df_service_disable(
    df_module_args,
    df_service_enable,
    df_service_disable,
    df_client,
):
    """
    Test disabling DataFlow service with real API calls.

    NOTE: This test will disable the DataFlow service if one exists on the environment.
    If you don't want to disable an existing service, skip this test.
    """

    # Enable the service first (or get existing one)
    enable_result = df_service_enable()
    service_crn = enable_result["service"].get("service", {}).get("crn")

    # Execute module to disable the service
    df_module_args(
        {
            "df_crn": service_crn,
            "state": "absent",
            "terminate": True,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # Verify the result
    assert result.value.changed is True

    # Clear the registered CRN since we've already disabled the service
    # This prevents the fixture cleanup from trying to disable again
    df_service_disable(None)

    # Idempotency check - running again should not change anything
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False
