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

# pylint: disable=redefined-outer-name,unused-argument

from ansible_collections.cloudera.cloud.plugins.modules import env_user_sync
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

OPERATION_ID = "0e9bc67a-b308-4275-935c-b8c764dc13be"


@pytest.fixture
def env_user_sync_args(module_args):
    """Fixture to pre-populate common env_user_sync module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def env_user_sync_client(mocker):
    """Patch load_cdp_config and CdpEnvClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_user_sync.CdpEnvClient",
        autospec=True,
    ).return_value


def test_sync_all_environments(env_user_sync_args, env_user_sync_client):
    """Syncs all environments when no name is specified."""
    sync_response = {"operationId": OPERATION_ID, "status": "RUNNING"}
    completed_response = {
        "operationId": OPERATION_ID,
        "status": "COMPLETED",
        "success": [{"environmentCrn": "crn:cdp:env:1"}],
    }

    env_user_sync_args({})
    env_user_sync_client.sync_all_users.return_value = sync_response
    env_user_sync_client.wait_for_sync.return_value = completed_response

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert result.value.sync == completed_response
    env_user_sync_client.sync_all_users.assert_called_once_with(None)
    env_user_sync_client.wait_for_sync.assert_called_once()


def test_sync_named_environments(env_user_sync_args, env_user_sync_client):
    """Syncs specific environments by name."""
    env_names = ["env-1", "env-2"]
    sync_response = {"operationId": OPERATION_ID, "status": "RUNNING"}
    completed_response = {
        "operationId": OPERATION_ID,
        "status": "COMPLETED",
    }

    env_user_sync_args({"name": env_names})
    env_user_sync_client.sync_all_users.return_value = sync_response
    env_user_sync_client.wait_for_sync.return_value = completed_response

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert result.value.sync == completed_response
    env_user_sync_client.sync_all_users.assert_called_once_with(env_names)


def test_sync_current_user(env_user_sync_args, env_user_sync_client):
    """Syncs only the current user when current_user=True."""
    sync_response = {"operationId": OPERATION_ID, "status": "RUNNING"}
    completed_response = {
        "operationId": OPERATION_ID,
        "status": "COMPLETED",
    }

    env_user_sync_args({"current_user": True})
    env_user_sync_client.sync_user.return_value = sync_response
    env_user_sync_client.wait_for_sync.return_value = completed_response

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    env_user_sync_client.sync_user.assert_called_once()
    env_user_sync_client.sync_all_users.assert_not_called()


def test_sync_with_wait(env_user_sync_args, env_user_sync_client):
    """Wait=True (default) calls wait_for_sync with correct parameters."""
    sync_response = {"operationId": OPERATION_ID, "status": "RUNNING"}
    completed_response = {
        "operationId": OPERATION_ID,
        "status": "COMPLETED",
    }

    env_user_sync_args({"delay": 30, "timeout": 600})
    env_user_sync_client.sync_all_users.return_value = sync_response
    env_user_sync_client.wait_for_sync.return_value = completed_response

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.sync == completed_response
    env_user_sync_client.wait_for_sync.assert_called_once_with(
        operation_id=OPERATION_ID,
        timeout=600,
        delay=30,
    )


def test_sync_without_wait(env_user_sync_args, env_user_sync_client):
    """Wait=False returns the initial sync response without polling."""
    sync_response = {"operationId": OPERATION_ID, "status": "RUNNING"}

    env_user_sync_args({"wait": False})
    env_user_sync_client.sync_all_users.return_value = sync_response

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is True
    assert result.value.sync == sync_response
    env_user_sync_client.wait_for_sync.assert_not_called()


def test_check_mode(env_user_sync_args, env_user_sync_client):
    """Check mode reports changed=False and makes no API calls."""
    env_user_sync_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync.main()

    assert result.value.changed is False
    assert result.value.sync == {}
    env_user_sync_client.sync_all_users.assert_not_called()
    env_user_sync_client.sync_user.assert_not_called()
    env_user_sync_client.wait_for_sync.assert_not_called()


def test_mutually_exclusive_name_and_current_user(
    env_user_sync_args,
    env_user_sync_client,
):
    """Fails when both name and current_user are specified."""
    env_user_sync_args({"name": ["env-1"], "current_user": True})

    with pytest.raises(AnsibleFailJson):
        env_user_sync.main()
