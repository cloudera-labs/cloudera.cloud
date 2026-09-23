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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

pytestmark = pytest.mark.integration_api


@pytest.fixture(scope="module")
def sync_result(test_cdp_client):
    """Fire a single sync_all_users call shared across all tests in this module."""
    client = CdpEnvClient(api_client=test_cdp_client)
    return client.sync_all_users()


def test_sync_all_users(sync_result):
    """sync_all_users() returns a dict with operationId and status."""
    assert isinstance(sync_result, dict)
    assert "operationId" in sync_result
    assert "status" in sync_result


def test_sync_all_users_named_environment(test_cdp_client, sync_result):
    """sync_all_users() with a specific environment name."""
    env_name = os.getenv("CDP_ENVIRONMENT_NAME")
    if not env_name:
        pytest.skip("CDP_ENVIRONMENT_NAME not set; skipping named-environment sync test")

    client = CdpEnvClient(api_client=test_cdp_client)
    client.wait_for_sync(sync_result["operationId"], delay=5)

    result = client.sync_all_users(environment_names=[env_name])

    assert isinstance(result, dict)
    assert "operationId" in result
    assert "status" in result


def test_get_sync_status(test_cdp_client, sync_result):
    """get_sync_status() returns matching operationId after a sync."""
    client = CdpEnvClient(api_client=test_cdp_client)
    operation_id = sync_result["operationId"]

    status_result = client.get_sync_status(operation_id)

    assert isinstance(status_result, dict)
    assert status_result["operationId"] == operation_id
    assert "status" in status_result
