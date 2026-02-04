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
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient
from ansible_collections.cloudera.cloud.plugins.modules import df_customflow_info


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)



@pytest.fixture
def existing_flow_name(df_client) -> str:
    """Fixture to provide an existing custom flow name for tests."""
    # response = df_client.list_flow_definitions()  # This times out due to pagination decorator
    # Using direct API call to avoid pagination overhead in test fixture
    response = df_client.api_client.post(
        "/api/v1/df/listFlowDefinitions",
        data={"pageSize": 1},
        squelch={404: {"flows": []}},
    )
    if len(response.get("flows", [])) == 0:
        pytest.skip("No custom flows available for testing")

    return response["flows"][0]["name"]



@pytest.mark.slow
def test_df_customflow_info_list_all(module_args):
    """Test listing all custom flows with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "flows")
    assert isinstance(result.value.flows, list)


def test_df_customflow_info_by_name_with_details(module_args, existing_flow_name):
    """Test getting information about a specific custom flow by search_term with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": existing_flow_name,
            "include_details": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "flows")
    assert isinstance(result.value.flows, list)

def test_df_customflow_info_by_name(module_args, existing_flow_name):
    """Test getting information about a specific custom flow by search_term with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": existing_flow_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "flows")
    assert isinstance(result.value.flows, list)


def test_df_customflow_info_nonexistent_name(module_args):
    """Test querying for a non-existent custom flow by search_term."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": "NonexistentCustomFlow112233XYZ",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "flows")
    assert len(result.value.flows) == 0


def test_df_customflow_info_name_alias(module_args, existing_flow_name):
    """Test that the 'name' alias works for backward compatibility."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": existing_flow_name,  # Using the alias
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "flows")
    assert isinstance(result.value.flows, list)
