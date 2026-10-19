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
def test_df_service_update(df_module_args, deletable_df_service):
    """Bump the maximum node count of an existing service and verify idempotency."""

    new_max = int(deletable_df_service.maxK8sNodeCount) + 1
    update_args = {
        "nodes_min": int(deletable_df_service.minK8sNodeCount),
        "nodes_max": new_max,
        "wait": True,
    }

    # Update maximum node count
    df_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is True
    assert result.value.service.get("crn") == deletable_df_service.crn
    assert int(result.value.service["maxK8sNodeCount"]) == new_max

    # Idempotent re-run after update
    df_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is False
    assert int(result.value.service["maxK8sNodeCount"]) == new_max


@pytest.mark.data_service
def test_df_service_absent(df_module_args, deletable_df_service, df_client):
    """Disable an existing service via the module and verify idempotency."""

    absent_args = {
        "df_crn": deletable_df_service.crn,
        "state": "absent",
        "terminate": True,
        "wait": True,
    }

    # Disable
    df_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is True

    assert df_client.get_service_by_crn(deletable_df_service.crn) is None

    # Idempotent re-run of absent (service already gone)
    df_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()
    assert result.value.changed is False
