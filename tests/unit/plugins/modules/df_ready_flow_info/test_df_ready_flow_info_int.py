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
from ansible_collections.cloudera.cloud.plugins.modules import df_readyflow_info


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
def existing_readyflow_name(df_client) -> str:
    """Fixture to provide an existing ReadyFlow name for tests."""
    response = df_client.list_readyflows()

    if len(response.get("readyflows", [])) == 0:
        pytest.skip("No ReadyFlows available for testing")

    return response["readyflows"][0]["name"]

@pytest.mark.slow
def test_df_readyflow_info_list_all(module_args):
    """Test listing all ReadyFlows with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "readyflows")
    assert isinstance(result.value.readyflows, list)



def test_df_readyflow_info_by_name(module_args, existing_readyflow_name):
    """Test getting information about a specific ReadyFlow by name with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": existing_readyflow_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "readyflows")
    assert isinstance(result.value.readyflows, list)
    assert len(result.value.readyflows) >= 1

    # Verify all returned ReadyFlows contain the search term in their name
    for readyflow in result.value.readyflows:
        assert "readyflowCrn" in readyflow
        assert "name" in readyflow
        assert existing_readyflow_name.lower() in readyflow["name"].lower()


def test_df_readyflow_info_search_term(module_args):
    """Test searching ReadyFlows with a search term with real API calls."""

    search_term = "Kafka"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": search_term,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "readyflows")
    assert isinstance(result.value.readyflows, list)

    # If ReadyFlows are returned, verify they match the search term
    if len(result.value.readyflows) > 0:
        for readyflow in result.value.readyflows:
            assert "name" in readyflow
            # Search term could match name, summary, or other fields
            readyflow_str = str(readyflow).lower()
            assert search_term.lower() in readyflow_str


def test_df_readyflow_info_nonexistent(module_args):
    """Test querying for a non-existent ReadyFlow."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": "NonexistentReadyFlow112233XYZ",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "readyflows")
    assert len(result.value.readyflows) == 0



