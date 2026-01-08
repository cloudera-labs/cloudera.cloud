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
from ansible_collections.cloudera.cloud.plugins.modules import df_service_info


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def df_client(test_cdp_client) -> CdpDfClient:
    """Fixture to provide a DataFlow client for tests."""
    return CdpDfClient(api_client=test_cdp_client)


def test_df_service_info_list_all(module_args):
    """Test listing all DataFlow services with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "services")
    assert isinstance(result.value.services, list)



def test_df_service_info_list_by_name(module_args, df_client):
    """Test listing DataFlow services by environment name with real API calls."""

    response = df_client.list_services()
    
    if len(response.get("services", [])) == 0:
        pytest.skip("No DataFlow services available for testing")
    
    service_name = response["services"][0]["name"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": service_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "services")
    assert len(result.value.services) >= 1



def test_df_service_info_by_crn(module_args, df_client):
    """Test getting DataFlow service by CRN with real API calls."""

    response = df_client.list_services()
    
    if len(response.get("services", [])) == 0:
        pytest.skip("No DataFlow services available for testing")
    

    service_crn = response["services"][0]["crn"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": service_crn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "services")
    assert len(result.value.services) >= 1


def test_df_service_info_by_env_crn(module_args, df_client):
    """Test getting DataFlow service by environment CRN with real API calls."""

    response = df_client.list_services()
    
    if len(response.get("services", [])) == 0:
        pytest.skip("No DataFlow services available for testing")
    
    env_crn = response["services"][0]["environmentCrn"]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": env_crn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "services")
    assert len(result.value.services) >= 1



def test_df_service_info_nonexistent(module_args):
    """Test querying for a non-existent service."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-dataflow-service-99999",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert hasattr(result.value, "services")
    assert len(result.value.services) == 0
