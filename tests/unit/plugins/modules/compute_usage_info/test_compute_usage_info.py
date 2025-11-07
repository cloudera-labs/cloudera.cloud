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


def test_compute_usage_info_no_from_timestamp(module_args, mocker):
    """Test compute usage info module with missing from_timestamp parameter."""
       
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "to_timestamp": "2024-01-31T23:59:59Z",
            # "from_timestamp" is intentionally omitted to test error handling
        }
    )
    
    # Patch AnsibleCdpClient to avoid real API calls
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.AnsibleCdpClient",
        autospec=True,
    )
    
    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="from_timestamp"):
        compute_usage_info.main()


@pytest.mark.integration_api
def test_compute_usage_info_integration(module_args):
    """Integration test for compute usage info module."""
    
    module_args(
        {
            "endpoint": os.getenv("CDP_API_ENDPOINT", BASE_URL),
            "access_key": os.getenv("CDP_ACCESS_KEY", ACCESS_KEY),
            "private_key": os.getenv("CDP_PRIVATE_KEY", PRIVATE_KEY),
            "from_timestamp": "2024-01-31T00:00:00Z",
            "to_timestamp": "2024-01-31T23:59:59Z",
        }
    )
    

    with pytest.raises(AnsibleExitJson) as result:
        compute_usage_info.main()
    
    assert hasattr(result.value, "records"), "'records' key not found in result"
    assert isinstance(result.value.records, list), "'records' is not a list"
