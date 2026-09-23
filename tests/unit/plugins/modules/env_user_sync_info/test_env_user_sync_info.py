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

from ansible_collections.cloudera.cloud.plugins.modules import env_user_sync_info
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

OPERATION_ID = "0e9bc67a-b308-4275-935c-b8c764dc13be"


@pytest.fixture
def env_user_sync_info_args(module_args):
    """Fixture to pre-populate common env_user_sync_info module arguments."""

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
def env_user_sync_info_client(mocker):
    """Patch load_cdp_config and CdpEnvClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_user_sync_info.CdpEnvClient",
        autospec=True,
    ).return_value


def test_get_sync_status(env_user_sync_info_args, env_user_sync_info_client):
    """Retrieves sync operation status by operation ID."""
    mock_sync = {
        "operationId": OPERATION_ID,
        "operationType": "USER_SYNC",
        "status": "COMPLETED",
        "success": [{"environmentCrn": "crn:cdp:env:1"}],
        "failure": [],
    }

    env_user_sync_info_args({"name": OPERATION_ID})
    env_user_sync_info_client.get_sync_status.return_value = mock_sync

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync_info.main()

    assert result.value.changed is False
    assert result.value.sync == mock_sync
    env_user_sync_info_client.get_sync_status.assert_called_once_with(OPERATION_ID)


def test_changed_is_always_false(env_user_sync_info_args, env_user_sync_info_client):
    """Info modules never report changed."""
    env_user_sync_info_args({"name": OPERATION_ID})
    env_user_sync_info_client.get_sync_status.return_value = {
        "operationId": OPERATION_ID,
        "status": "RUNNING",
    }

    with pytest.raises(AnsibleExitJson) as result:
        env_user_sync_info.main()

    assert result.value.changed is False


def test_name_required(module_args, env_user_sync_info_client):
    """Fails when required 'name' parameter is missing."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleFailJson):
        env_user_sync_info.main()
