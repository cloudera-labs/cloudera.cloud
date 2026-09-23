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

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
)
from ansible_collections.cloudera.cloud.plugins.modules import env_user_sync_info
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

pytestmark = pytest.mark.integration_api


@pytest.fixture
def env_user_sync_info_module_args(module_args, env_context):
    """Fixture to pre-populate common env_user_sync_info module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def sync_operation_id(test_cdp_client):
    """Fire a quick sync and return the operationId for the info module to query."""
    client = CdpEnvClient(api_client=test_cdp_client)
    result = client.sync_all_users()
    return result["operationId"]


def test_get_sync_status(env_user_sync_info_module_args, sync_operation_id):
    """Info module retrieves status for a known sync operation."""
    env_user_sync_info_module_args({"name": sync_operation_id})

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync_info.main()

    assert result.value.changed is False
    assert isinstance(result.value.sync, dict)
    assert result.value.sync["operationId"] == sync_operation_id
    assert "status" in result.value.sync
