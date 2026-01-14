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
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_service


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")
TEST_ENV_CRN = "crn:cdp:environments:us-west-1:5125151-8867-4357-8524-31231:environment:138fb0e4-5407-4538-b995-90e977b23ca3"
TEST_SERVICE_CRN = "crn:cdp:df:us-west-1:142141-8867-4357-8524-41241:service:16f9c856-543c-4c68-81ec-8cd6624e7117"
TEST_CLUSTER_SUBNETS = [
    "subnet-058206f46dba69f9a",
    "subnet-0f998049366aaebe0",
    "subnet-06f423bb2ca14a4f9",
]
TEST_LOADBALANCER_SUBNETS = [
    "subnet-058206f46dba69f9a",
    "subnet-0f998049366aaebe0",
    "subnet-06f423bb2ca14a4f9",
]
TEST_MIN_NODES = 3
TEST_MAX_NODES = 10
TEST_USE_PUBLIC_LB = True
TEST_PRIVATE_CLUSTER = False
TEST_TAGS = {
    "test1": "test1value",
    "test2": "test2_value",
}

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


@pytest.fixture
def df_service_crn(df_client) -> Generator[Optional[str], None, None]:
    """
    Fixture to track and clean up DataFlow service.
    
    Yields the service CRN if service is enabled during test.
    Ensures cleanup by disabling the service after test completion.
    """
    service_crn = None

    def _set_crn(crn: str):
        nonlocal service_crn
        service_crn = crn

    # Yield the setter function
    yield _set_crn

    # Cleanup: disable service if it was created
    if service_crn:
        try:
            df_client.disable_service(crn=service_crn, terminate_deployments=True)
            # Wait for service to be fully disabled
            df_client.wait_for_service_state(
                service_crn=service_crn,
                target_states=["DISABLED"],
                timeout=1800,  # 30 minutes
                delay=30,
            )
        except Exception as e:
            pytest.fail(f"Failed to clean up DataFlow service: {service_crn}. {e}")


@pytest.fixture
def df_service_enable(df_client, df_service_crn) -> Callable[[str], dict]:
    """
    Fixture to enable DataFlow service for tests.
    
    Returns a function that enables the service and registers it for cleanup.
    """

    def _enable_service(env_crn: str) -> dict:
        """Enable DataFlow service and register for cleanup."""
        result = df_client.enable_service(
            environment_crn=env_crn,
            min_k8s_node_count=TEST_MIN_NODES,
            max_k8s_node_count=TEST_MAX_NODES,
            cluster_subnet_ids=TEST_CLUSTER_SUBNETS,
            load_balancer_subnet_ids=TEST_LOADBALANCER_SUBNETS,
            use_public_load_balancer=TEST_USE_PUBLIC_LB,
            private_cluster=TEST_PRIVATE_CLUSTER,
            skip_preflight_checks=False,
            user_defined_routing=False,
            tags=TEST_TAGS,
        )
        
        # Wait for service to be enabled
        service_crn = result.get("service", {}).get("crn")
        if service_crn:
            df_service_crn(service_crn)
            df_client.wait_for_service_state(
                service_crn=service_crn,
                target_states=["ENABLED"],
                timeout=1800,  # 30 minutes
                delay=30,
            )
        
        return result

    return _enable_service



def test_df_service_enable(module_args, df_service_crn):
    """Test enabling DataFlow service with real API calls."""

    # Ensure cleanup after the test
    # The df_service_crn fixture will track the CRN for cleanup

    # Execute module
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": TEST_ENV_CRN,
            "state": "present",
            "nodes_min": TEST_MIN_NODES,
            "nodes_max": TEST_MAX_NODES,
            "cluster_subnets": TEST_CLUSTER_SUBNETS,
            "loadbalancer_subnets": TEST_LOADBALANCER_SUBNETS,
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
    # assert service_crn is not None
    # df_service_crn(service_crn)

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


def test_df_service_disable(module_args, df_service_enable):
    """Test disabling DataFlow service with real API calls."""

    # Enable the service first
    # enable_result = df_service_enable(TEST_ENV_CRN)
    # service_crn = enable_result.get("service", {}).get("crn")
    # assert service_crn is not None

    # Execute module to disable the service
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": TEST_SERVICE_CRN,
            "state": "absent",
            "wait" : True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    # Verify the result
    assert result.value.changed is True


    # Idempotency check - running again should not change anything
    # with pytest.raises(AnsibleExitJson) as result:
    #     df_service.main()

    # assert result.value.changed is False
