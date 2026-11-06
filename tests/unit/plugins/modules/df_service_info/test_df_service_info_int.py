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

from ansible_collections.cloudera.cloud.plugins.modules import df_service_info


BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


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


def test_df_service_info_list_by_name(module_args, existing_df_service):
    """Test getting a DataFlow service by name with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": existing_df_service.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert [s["crn"] for s in result.value.services] == [existing_df_service.crn]


def test_df_service_info_by_crn(module_args, existing_df_service):
    """Test getting DataFlow service by CRN with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": existing_df_service.crn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert [s["crn"] for s in result.value.services] == [existing_df_service.crn]


def test_df_service_info_by_env_crn(module_args, existing_df_service):
    """Test getting DataFlow service by environment CRN with real API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": existing_df_service.environmentCrn,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert [s["crn"] for s in result.value.services] == [existing_df_service.crn]


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
