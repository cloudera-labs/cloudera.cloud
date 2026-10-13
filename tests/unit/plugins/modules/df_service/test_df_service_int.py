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

from typing import Callable, Generator, Optional

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
)
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


@pytest.mark.data_service
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


@pytest.mark.data_service
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


@pytest.mark.data_service
def test_df_service_update(df_module_args, df_service_disable):
    """Enable a service, bump its maximum node count, re-check idempotency, then disable it."""

    # Enable the service (same setup as test_df_service_enable)
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

    service_crn = result.value.service.get("crn")
    assert service_crn is not None
    df_service_disable(service_crn)
    assert result.value.changed is True

    new_max = TEST_MAX_NODES + 1
    update_args = {
        "nodes_min": TEST_MIN_NODES,
        "nodes_max": new_max,
        "wait": True,
    }

    # Update maximum node count
    df_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is True
    assert int(result.value.service["maxK8sNodeCount"]) == new_max

    # Idempotent re-run after update
    df_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is False
    assert int(result.value.service["maxK8sNodeCount"]) == new_max

    # Disable the service via the module; the fixture no longer needs to do it
    df_module_args(
        {"df_crn": service_crn, "state": "absent", "terminate": True, "wait": True},
    )
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is True
    df_service_disable(None)


@pytest.mark.data_service
def test_df_service_absent(df_module_args, df_service_disable, df_client):
    """Enable a service, then disable it via the module and verify idempotency."""

    # Enable the service (same setup as test_df_service_enable)
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

    service_crn = result.value.service.get("crn")
    assert service_crn is not None
    df_service_disable(service_crn)
    assert result.value.changed is True

    absent_args = {
        "df_crn": service_crn,
        "state": "absent",
        "terminate": True,
        "wait": True,
    }

    # Disable
    df_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is True

    assert df_client.get_service_by_crn(service_crn) is None
    df_service_disable(None)

    # Idempotent re-run of absent (service already gone)
    df_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is False
