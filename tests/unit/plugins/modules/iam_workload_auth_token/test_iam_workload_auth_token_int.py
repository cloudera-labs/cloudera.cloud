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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import CdpIamClient
from ansible_collections.cloudera.cloud.plugins.modules import iam_workload_auth_token


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "ENV_CRN",
]

BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def iam_client(test_cdp_client) -> CdpIamClient:
    """Fixture to provide an IAM client for tests."""
    return CdpIamClient(api_client=test_cdp_client)


def test_workload_auth_token_de(module_args):
    """Test generating workload auth token for DE workload with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DE",

        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] is not None
    assert isinstance(result.value.workload_auth_token["token"], str)
    assert len(result.value.workload_auth_token["token"]) > 0
    assert result.value.workload_auth_token["expire_at"] is not None
    assert "endpoint_url" not in result.value.workload_auth_token


def test_workload_auth_token_opdb(module_args):
    """Test generating workload auth token for OPDB workload with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "OPDB",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] is not None
    assert isinstance(result.value.workload_auth_token["token"], str)
    assert len(result.value.workload_auth_token["token"]) > 0
    assert "endpoint_url" not in result.value.workload_auth_token


def test_workload_auth_token_df_with_environment(module_args,env_context):
    """Test generating workload auth token for DF workload with environment."""


    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DF",
            "environment_crn": env_context["ENV_CRN"],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] is not None
    assert isinstance(result.value.workload_auth_token["token"], str)
    assert len(result.value.workload_auth_token["token"]) > 0
    
    # endpoint_url IS returned for DF workload
    assert "endpoint_url" in result.value.workload_auth_token
    assert result.value.workload_auth_token["endpoint_url"] is not None
    assert isinstance(result.value.workload_auth_token["endpoint_url"], str)
    assert result.value.workload_auth_token["endpoint_url"].startswith("http")


def test_workload_auth_token_df_missing_environment(module_args):
    """Test that DF workload fails without environment CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DF",
        },
    )

    with pytest.raises(AnsibleFailJson) as result:
        iam_workload_auth_token.main()

    # The error should be about missing required parameter when workload_name is DF
    assert "environment_crn" in result.value.msg or "required" in result.value.msg.lower()
