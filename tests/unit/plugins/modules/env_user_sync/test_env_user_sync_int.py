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
from ansible_collections.cloudera.cloud.plugins.modules import env_user_sync
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
    required_or_skip,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

pytestmark = pytest.mark.integration_api


@pytest.fixture
def _wait_for_idle_sync(test_cdp_client):
    """Block until the target environment has no sync in flight.

    Polls ``get_environment_user_sync_state`` for the environment named
    by ``CDP_ENVIRONMENT_NAME``.  When a sync is still running it waits
    for the operation to finish via ``get_sync_status`` so the next test
    won't hit a 409.
    """
    env_name = required_or_skip("CDP_ENVIRONMENT_NAME")
    client = CdpEnvClient(api_client=test_cdp_client)

    state = client.get_environment_user_sync_state(env_name)
    if state.userSyncOperationId:
        status = client.get_sync_status(state.userSyncOperationId)
        if status.status not in ("COMPLETED", "FAILED", "TIMEDOUT", "REJECTED"):
            client.wait_for_sync(
                state.userSyncOperationId,
                delay=5,
                timeout=600,
            )


@pytest.fixture
def env_user_sync_module_args(module_args, env_context):
    """Fixture to pre-populate common env_user_sync module arguments."""

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


def test_sync_all_environments_no_wait(env_user_sync_module_args):
    """Sync all environments without waiting for completion."""
    env_user_sync_module_args({"wait": False})

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert isinstance(result.value.sync, dict)
    assert result.value.sync["operationId"] is not None
    assert result.value.sync["status"] is not None


def test_sync_named_environment_no_wait(env_user_sync_module_args, _wait_for_idle_sync):
    """Sync a specific named environment without waiting for completion."""
    env_name = required_or_skip("CDP_ENVIRONMENT_NAME")

    env_user_sync_module_args({"name": [env_name], "wait": False})

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert isinstance(result.value.sync, dict)
    assert result.value.sync["operationId"] is not None
    assert result.value.sync["status"] is not None


def test_sync_named_environment_wait(env_user_sync_module_args, _wait_for_idle_sync):
    """Sync a specific named environment and wait for completion."""
    env_name = required_or_skip("CDP_ENVIRONMENT_NAME")

    env_user_sync_module_args(
        {"name": [env_name], "wait": True, "delay": 5, "timeout": 600},
    )

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert isinstance(result.value.sync, dict)
    assert result.value.sync["operationId"] is not None
    assert result.value.sync["status"] == "COMPLETED"


def test_check_mode_no_api_call(env_user_sync_module_args):
    """Check mode reports changed=False and makes no API call."""
    env_user_sync_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is False
    assert result.value.sync == {}
