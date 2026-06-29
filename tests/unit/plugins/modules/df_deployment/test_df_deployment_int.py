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
import random
import time
from typing import Callable, Generator

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import df_deployment

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "DF_TEST_ENV_CRN",
    "DF_TEST_FLOW_VERSION_CRN",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common DataFlow deployment module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
            }
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for direct API calls."""
    return CdpDfClient(api_client=test_cdp_client)


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for workload token generation."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def df_deployment_delete(
    df_client,
) -> Generator[Callable[[str], None], None, None]:
    """Fixture to track and clean up deployments created during tests."""
    deployment_crns = []

    def _track(deployment_crn: str):
        deployment_crns.append(deployment_crn)

    yield _track

    for deployment_crn in deployment_crns:
        try:
            deployment = df_client.get_deployment_by_crn(deployment_crn)
            if deployment:
                deployment_data = deployment.get("deployment", deployment)
                env_crn = (
                    deployment_data.get("service", {}).get("environmentCrn")
                    or deployment_data.get("environmentCrn")
                )
                if env_crn:
                    dataservice_client = df_client.create_workload_client(
                        iam_client=iam_client,
                        module=df_client.api_client.module,
                        environment_crn=env_crn,
                    )
                    df_client.terminate_deployment(
                        dataservice_client=dataservice_client,
                        deployment_crn=deployment_crn,
                        environment_crn=env_crn,
                    )
        except Exception:
            pass


@pytest.fixture
def df_deployment_create(
    df_client,
    iam_client,
    df_deployment_delete,
    env_context,
) -> Callable[..., dict]:
    """
    Fixture to create deployments directly via the API and register for cleanup.

    Returns a function that creates a deployment and registers its CRN for teardown.
    """

    def _create(
        name: str,
        flow_version_crn: str = None,
        env_crn: str = None,
        cluster_size: str = "EXTRA_SMALL",
        static_node_count: int = 1,
        parameter_groups: list = None,
        wait: bool = True,
        timeout: int = 600,
    ) -> dict:
        resolved_env_crn = env_crn or env_context["DF_TEST_ENV_CRN"]
        resolved_flow_version_crn = (
            flow_version_crn or env_context["DF_TEST_FLOW_VERSION_CRN"]
        )

        service = df_client.get_service_by_env_crn(resolved_env_crn)
        service_crn = service.get("service", {}).get("crn")

        initiate_result = df_client.initiate_deployment(
            service_crn=service_crn,
            flow_version_crn=resolved_flow_version_crn,
        )
        deployment_request_crn = initiate_result.get("deploymentRequestCrn")

        dataservice_client = df_client.create_workload_client(
            iam_client=iam_client,
            module=df_client.api_client.module,
            environment_crn=resolved_env_crn,
        )

        # Default parameter groups to avoid missing parameter group errors
        if parameter_groups is None:
            parameter_groups = [
                {
                    "name": "test-customflow-141072",
                    "parameters": []
                }
            ]

        result = df_client.create_deployment(
            dataservice_client=dataservice_client,
            environment_crn=resolved_env_crn,
            deployment_request_crn=deployment_request_crn,
            name=name,
            configuration_version=0,
            cluster_size=cluster_size,
            static_node_count=static_node_count,
            parameter_groups=parameter_groups,
        )

        deployment = result.get("deployment", result)
        deployment_crn = deployment.get("crn")

        if deployment_crn:
            df_deployment_delete(deployment_crn)

        if wait and deployment_crn:
            result = df_client.wait_for_deployment_state(
                target_states=["GOOD_HEALTH"],
                deployment_crn=deployment_crn,
                timeout=timeout,
                delay=15,
            )
            deployment = result.get("deployment", deployment)

        return deployment

    return _create


def test_df_deployment_create_via_module(
    df_module_args,
    env_context,
    df_deployment_delete,
):
    """Test creating a deployment via the Ansible module with real API calls."""
    random_suffix = random.randint(100000, 999999)
    deployment_name = f"test-deployment-{random_suffix}"

    df_module_args(
        {
            "name": deployment_name,
            "env_crn": env_context["DF_TEST_ENV_CRN"],
            "flow_version_crn": env_context["DF_TEST_FLOW_VERSION_CRN"],
            "cluster_size": "EXTRA_SMALL",
            "static_node_count": 1,
            "parameter_groups": [
                {
                    "name": "test-customflow-141072",
                    "parameters": []
                }
            ],
            "state": "present",
            "wait": True,
            "timeout": 600,
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    deployment_crn = result.value.deployment.get("crn")
    if deployment_crn:
        df_deployment_delete(deployment_crn)

    assert result.value.changed is True
    assert result.value.deployment is not None
    assert result.value.deployment["name"] == deployment_name


def test_df_deployment_create_idempotent(
    df_module_args,
    env_context,
    df_deployment_create,
):
    """Test that re-running present on an existing deployment is idempotent."""
    random_suffix = random.randint(100000, 999999)
    deployment_name = f"test-deployment-idem-{random_suffix}"

    # Create the deployment directly
    deployment = df_deployment_create(name=deployment_name)
    assert deployment is not None
    assert deployment.get("crn") is not None

    # Re-run module - should be idempotent (no update params provided)
    df_module_args(
        {
            "name": deployment_name,
            "env_crn": env_context["DF_TEST_ENV_CRN"],
            "flow_version_crn": env_context["DF_TEST_FLOW_VERSION_CRN"],
            "parameter_groups": [
                {
                    "name": "test-customflow-141072",
                    "parameters": []
                }
            ],
            "state": "present",
            "wait": False,
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is False
    assert result.value.deployment["name"] == deployment_name


def test_df_deployment_delete_via_module(
    df_module_args,
    env_context,
    df_deployment_create,
):
    """Test terminating a deployment via the Ansible module with real API calls."""
    random_suffix = random.randint(100000, 999999)
    deployment_name = f"test-deployment-del-{random_suffix}"

    deployment = df_deployment_create(name=deployment_name)
    assert deployment is not None
    deployment_crn = deployment.get("crn")
    assert deployment_crn is not None

    df_module_args(
        {
            "deployment_crn": deployment_crn,
            "env_crn": env_context["DF_TEST_ENV_CRN"],
            "state": "absent",
            "wait": True,
            "timeout": 600,
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    assert result.value.deployment == {}

    # Verify idempotent delete
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is False


def test_df_deployment_delete_by_name_via_module(
    df_module_args,
    env_context,
    df_deployment_create,
):
    """Test terminating a deployment by name via the Ansible module."""
    random_suffix = random.randint(100000, 999999)
    deployment_name = f"test-deployment-delname-{random_suffix}"

    deployment = df_deployment_create(name=deployment_name)
    assert deployment is not None

    df_module_args(
        {
            "name": deployment_name,
            "env_crn": env_context["DF_TEST_ENV_CRN"],
            "state": "absent",
            "wait": True,
            "timeout": 600,
        }
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment.main()

    assert result.value.changed is True
    assert result.value.deployment == {}