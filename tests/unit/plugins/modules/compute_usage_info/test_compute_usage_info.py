# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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

from ansible_collections.cloudera.cloud.plugins.modules import compute_usage_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

SAMPLE_FROM_TIMESTAMP = "2024-01-01T00:00:00Z"
SAMPLE_TO_TIMESTAMP = "2024-01-31T23:59:59Z"


def test_compute_usage_info_default(module_args):
    """Test compute usage info module with missing parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Expect the module to fail due to missing required parameters
    with pytest.raises(AnsibleFailJson, match="from_timestamp, to_timestamp"):
        compute_usage_info.main()


def test_compute_usage_info_no_from_timestamp(module_args):
    """Test compute usage info module with missing from_timestamp parameter."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "to_timestamp": SAMPLE_TO_TIMESTAMP,
        },
    )

    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="from_timestamp"):
        compute_usage_info.main()


def test_compute_usage_info_no_to_timestamp(module_args):
    """Test compute usage info module with missing to_timestamp parameter."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "from_timestamp": SAMPLE_FROM_TIMESTAMP,
        },
    )

    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="to_timestamp"):
        compute_usage_info.main()


def test_compute_usage_info(module_args, mocker):
    """Test compute usage info module."""

    mock_return_value = {
        "records": [
            {
                "timestamp": "2024-01-31T12:00:00Z",
                "computeUnits": 42,
            },
            {
                "timestamp": "2024-01-31T13:00:00Z",
                "computeUnits": 58,
            },
        ],
    }

    expected_records = [
        {
            "timestamp": "2024-01-31T12:00:00Z",
            "compute_units": 42,  # Note the snake_case conversion
        },
        {
            "timestamp": "2024-01-31T13:00:00Z",
            "compute_units": 58,
        },
    ]

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "to_timestamp": SAMPLE_TO_TIMESTAMP,
            "from_timestamp": SAMPLE_FROM_TIMESTAMP,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_usage_info.CdpConsumptionClient",
        autospec=True,
    ).return_value
    client.list_compute_usage_records.return_value = mock_return_value

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        compute_usage_info.main()

    assert result.value.changed is False
    assert result.value.records == expected_records

    # Verify CdpConsumptionClient was called correctly
    client.list_compute_usage_records.assert_called_once_with(
        from_timestamp=SAMPLE_FROM_TIMESTAMP,
        to_timestamp=SAMPLE_TO_TIMESTAMP,
    )


@pytest.mark.integration_api
def test_compute_usage_info_integration(module_args):
    """Integration test for compute usage info module."""

    module_args(
        {
            "endpoint": os.getenv("CDP_API_ENDPOINT", BASE_URL),
            "access_key": os.getenv("CDP_ACCESS_KEY_ID", ACCESS_KEY),
            "private_key": os.getenv("CDP_PRIVATE_KEY", PRIVATE_KEY),
            "from_timestamp": "2024-01-31T00:00:00Z",
            "to_timestamp": "2024-01-31T23:59:59Z",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        compute_usage_info.main()

    assert hasattr(result.value, "records"), "'records' key not found in result"
    assert isinstance(result.value.records, list), "'records' is not a list"
