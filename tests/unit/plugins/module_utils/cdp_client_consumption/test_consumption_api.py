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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


@pytest.mark.integration_api
def test_list_compute_usage_records_integration(mock_ansible_module):
    """Test listing compute usage records."""

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url="https://api.us-west-1.cdp.cloudera.com",
        access_key=os.getenv("CDP_ACCESS_KEY", "unknown"),
        private_key=os.getenv("CDP_PRIVATE_KEY", "unknown"),
    )

    response = client.list_compute_usage_records(
        from_timestamp="2024-01-01T00:00:00Z",
        to_timestamp="2024-01-31T23:59:59Z",
    )

    assert "records" in response
    assert len(response["records"]) > 0
    assert isinstance(response["records"][0], dict)
