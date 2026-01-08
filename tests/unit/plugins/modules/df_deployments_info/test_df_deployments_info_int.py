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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_deployment_info


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


def test_df_deployment_info_list_all(module_args):
    """Test listing all DataFlow deployments with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    assert isinstance(result.value.deployments, list)


def test_df_deployment_info_by_name(module_args, df_client):
    """Test getting DataFlow deployment by name with real API calls."""

    response = df_client.list_deployments()

    if len(response.get("deployments", [])) == 0:
        pytest.skip("No DataFlow deployments available for testing")

    deployment_name = response["deployments"][0]["name"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": deployment_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    assert len(result.value.deployments) >= 1
    # Verify we got the right deployment
    assert result.value.deployments[0]["name"] == deployment_name


def test_df_deployment_info_by_crn(module_args, df_client):
    """Test getting DataFlow deployment by CRN with real API calls."""

    response = df_client.list_deployments()

    if len(response.get("deployments", [])) == 0:
        pytest.skip("No DataFlow deployments available for testing")

    deployment_crn = response["deployments"][0]["crn"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": deployment_crn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    assert len(result.value.deployments) >= 1
    # Verify we got the right deployment
    assert result.value.deployments[0]["crn"] == deployment_crn


def test_df_deployment_info_nonexistent_name(module_args):
    """Test querying for a non-existent deployment by name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-deployment-99999",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    assert len(result.value.deployments) == 0


def test_df_deployment_info_nonexistent_crn(module_args):
    """Test querying for a non-existent deployment by CRN."""

    # Use a properly formatted but non-existent CRN
    fake_crn = "crn:cdp:df:us-west-1:12345678-1234-1234-1234-123456789012:deployment:fake-deployment-id"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": fake_crn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    assert len(result.value.deployments) == 0


def test_df_deployment_info_deployment_structure(module_args, df_client):
    """Test that deployment structure contains expected fields."""

    response = df_client.list_deployments()

    if len(response.get("deployments", [])) == 0:
        pytest.skip("No DataFlow deployments available for testing")

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "deployments")
    
    if len(result.value.deployments) > 0:
        deployment = result.value.deployments[0]
        
        # Check for essential fields that should always be present
        assert "crn" in deployment
        assert "name" in deployment
        assert "status" in deployment
        
        # Check status structure
        if "status" in deployment:
            status = deployment["status"]
            assert isinstance(status, dict)
            # Status should have state at minimum
            assert "state" in status or "detailedState" in status
