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
import warnings
from typing import Callable, Generator

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient

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
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for workload token generation."""
    return CdpIamClient(api_client=test_cdp_client)


@pytest.fixture
def valid_df_deployment(df_client):
    """
    Fixture to find an existing healthy deployment for read-only tests.

    Skips the test if no deployments in a healthy state are available.
    """
    response = df_client.list_deployments()
    for dep in response.get("deployments", []):
        state = dep.get("status", {}).get("state")
        if state in CdpDfClient.DEPLOYMENT_HEALTHY_STATES:
            crn = dep.get("crn")
            if crn:
                details = df_client.describe_deployment(crn)
                if details and details.get("deployment"):
                    return dep

    pytest.skip("No healthy DataFlow deployments available for testing")


@pytest.fixture
def df_deployment_delete(
    df_client,
    iam_client,
) -> Generator[Callable[[str, str], None], None, None]:
    """Fixture to track and clean up deployments created during tests."""
    deployments_to_delete = []

    def _track(deployment_crn: str, env_crn: str):
        deployments_to_delete.append((deployment_crn, env_crn))

    yield _track

    for deployment_crn, env_crn in deployments_to_delete:
        try:
            workload_client = df_client.create_workload_client(
                iam_client=iam_client,
                environment_crn=env_crn,
            )
            df_client.terminate_deployment(
                workload_client=workload_client,
                deployment_crn=deployment_crn,
                environment_crn=env_crn,
            )
            df_client.wait_for_deployment_state(
                target_states=CdpDfClient.DEPLOYMENT_DELETED_STATES,
                deployment_crn=deployment_crn,
                timeout=600,
                delay=15,
            )
        except Exception as e:
            warnings.warn(f"Failed to clean up deployment {deployment_crn}: {e}")


@pytest.fixture
def df_deployment_create(
    df_client,
    iam_client,
    df_deployment_delete,
    env_context,
) -> Callable[..., dict]:
    """Fixture to create deployments directly via the API and register for cleanup."""

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

        workload_client = df_client.create_workload_client(
            iam_client=iam_client,
            environment_crn=resolved_env_crn,
        )

        if parameter_groups is None:
            parameter_groups = [{"name": "test-customflow-141072", "parameters": []}]

        result = df_client.create_deployment(
            workload_client=workload_client,
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
            df_deployment_delete(deployment_crn, resolved_env_crn)

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


class TestCdpDfClientDeploymentIntegration:
    """Integration tests for CdpDfClient deployment management methods."""

    def test_list_deployments(self, df_client):
        """Test listing DataFlow deployments returns a valid response structure."""
        response = df_client.list_deployments()

        assert "deployments" in response
        assert isinstance(response["deployments"], list)

        if response["deployments"]:
            dep = response["deployments"][0]
            assert "crn" in dep
            assert "name" in dep

    def test_describe_deployment(self, df_client, valid_df_deployment):
        """Test describing a known healthy deployment returns full details."""
        crn = valid_df_deployment.get("crn")

        response = df_client.describe_deployment(crn)

        assert response is not None
        assert "deployment" in response
        dep = response["deployment"]
        assert dep["crn"] == crn
        assert "name" in dep
        assert "status" in dep

    def test_describe_deployment_not_found(self, df_client):
        """Test that describing a nonexistent deployment returns empty dict."""
        response = df_client.describe_deployment(
            "crn:cdp:df:us-west-1:fake:deployment:nonexistent-12345",
        )

        assert response == {}

    def test_get_deployment_by_name(self, df_client, valid_df_deployment):
        """Test retrieving a deployment by name returns matching details."""
        name = valid_df_deployment.get("name")

        response = df_client.get_deployment_by_name(name)

        assert response is not None
        assert "deployment" in response
        assert response["deployment"]["name"] == name

    def test_get_deployment_by_name_not_found(self, df_client):
        """Test get_deployment_by_name returns None when name does not exist."""
        response = df_client.get_deployment_by_name("nonexistent-deployment-xyz-12345")

        assert response is None

    def test_get_deployment_by_crn(self, df_client, valid_df_deployment):
        """Test retrieving a deployment by CRN returns matching details."""
        crn = valid_df_deployment.get("crn")

        response = df_client.get_deployment_by_crn(crn)

        assert response is not None
        assert "deployment" in response
        assert response["deployment"]["crn"] == crn

    def test_get_deployment_by_crn_not_found(self, df_client):
        """Test get_deployment_by_crn returns empty dict for an unknown CRN (squelched 404)."""
        response = df_client.get_deployment_by_crn(
            "crn:cdp:df:us-west-1:fake:deployment:nonexistent-12345",
        )

        assert response == {}

    def test_describe_deployment_expected_fields(self, df_client, valid_df_deployment):
        """Test that describe_deployment returns all expected core fields."""
        crn = valid_df_deployment.get("crn")

        response = df_client.describe_deployment(crn)
        dep = response["deployment"]

        expected_fields = ["crn", "name", "status"]
        for field in expected_fields:
            assert field in dep, f"Missing expected field: {field}"

        assert "state" in dep["status"], "Missing state in deployment status"

    def test_create_deployment_via_client(
        self,
        df_client,
        iam_client,
        df_deployment_delete,
        env_context,
    ):
        """Test creating a deployment directly via CdpDfClient."""
        random_suffix = random.randint(100000, 999999)
        deployment_name = f"test-api-dep-{random_suffix}"

        service = df_client.get_service_by_env_crn(env_context["DF_TEST_ENV_CRN"])
        service_crn = service.get("service", {}).get("crn")
        assert service_crn is not None, "No DataFlow service found for test environment"

        initiate_result = df_client.initiate_deployment(
            service_crn=service_crn,
            flow_version_crn=env_context["DF_TEST_FLOW_VERSION_CRN"],
        )
        deployment_request_crn = initiate_result.get("deploymentRequestCrn")
        assert deployment_request_crn is not None

        workload_client = df_client.create_workload_client(
            iam_client=iam_client,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
        )

        result = df_client.create_deployment(
            workload_client=workload_client,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
            deployment_request_crn=deployment_request_crn,
            name=deployment_name,
            configuration_version=0,
            cluster_size="EXTRA_SMALL",
            static_node_count=1,
            parameter_groups=[{"name": "test-customflow-141072", "parameters": []}],
        )

        deployment = result.get("deployment", result)
        deployment_crn = deployment.get("crn")
        assert deployment_crn is not None

        df_deployment_delete(deployment_crn, env_context["DF_TEST_ENV_CRN"])

        assert deployment.get("name") == deployment_name

    def test_wait_for_deployment_state_already_healthy(
        self,
        df_client,
        valid_df_deployment,
    ):
        """Test wait_for_deployment_state returns immediately for a healthy deployment."""
        crn = valid_df_deployment.get("crn")

        result = df_client.wait_for_deployment_state(
            target_states=CdpDfClient.DEPLOYMENT_HEALTHY_STATES,
            deployment_crn=crn,
            timeout=30,
            delay=5,
        )

        assert result is not None
        dep = result.get("deployment", {})
        assert (
            dep.get("status", {}).get("state") in CdpDfClient.DEPLOYMENT_HEALTHY_STATES
        )

    def test_terminate_and_wait(
        self,
        df_client,
        iam_client,
        df_deployment_create,
        env_context,
    ):
        """Test terminating a deployment and waiting for it to be deleted."""
        random_suffix = random.randint(100000, 999999)
        deployment_name = f"test-api-term-{random_suffix}"

        deployment = df_deployment_create(name=deployment_name)
        assert deployment is not None
        deployment_crn = deployment.get("crn")
        assert deployment_crn is not None

        workload_client = df_client.create_workload_client(
            iam_client=iam_client,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
        )

        df_client.terminate_deployment(
            workload_client=workload_client,
            deployment_crn=deployment_crn,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
        )

        result = df_client.wait_for_deployment_state(
            target_states=CdpDfClient.DEPLOYMENT_DELETED_STATES,
            deployment_crn=deployment_crn,
            timeout=600,
            delay=15,
        )

        assert result is None or result == {}

    def test_update_deployment_static_node_count(
        self,
        df_client,
        iam_client,
        df_deployment_create,
        env_context,
    ):
        """Test updating a deployment's static node count via CdpDfClient."""
        random_suffix = random.randint(100000, 999999)
        deployment_name = f"test-api-upd-{random_suffix}"

        deployment = df_deployment_create(name=deployment_name, static_node_count=1)
        assert deployment is not None
        deployment_crn = deployment.get("crn")
        assert deployment_crn is not None

        describe = df_client.describe_deployment(deployment_crn)
        configuration_version = describe.get("deployment", {}).get(
            "configurationVersion",
            0,
        )

        workload_client = df_client.create_workload_client(
            iam_client=iam_client,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
        )

        df_client.update_deployment(
            workload_client=workload_client,
            deployment_crn=deployment_crn,
            environment_crn=env_context["DF_TEST_ENV_CRN"],
            configuration_version=configuration_version,
            static_node_count=2,
        )

        df_client.wait_for_deployment_state(
            target_states=CdpDfClient.DEPLOYMENT_HEALTHY_STATES,
            deployment_crn=deployment_crn,
            timeout=600,
            delay=15,
        )

        updated = df_client.describe_deployment(deployment_crn)
        assert updated.get("deployment", {}).get("staticNodeCount") == 2
