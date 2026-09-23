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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    CdpEnvClient,
    SYNC_COMPLETED_STATUSES,
    SYNC_FAILED_STATUSES,
)


OPERATION_ID = "0e9bc67a-b308-4275-935c-b8c764dc13be"
ENV_NAME = "test-environment"


class TestCdpEnvClientSync:
    """Unit tests for CdpEnvClient user sync methods."""

    def test_sync_all_users_with_environments(self, mocker):
        """sync_all_users passes environmentNames when given."""
        mock_response = {
            "operationId": OPERATION_ID,
            "operationType": "USER_SYNC",
            "status": "RUNNING",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpEnvClient(api_client=api_client)
        result = client.sync_all_users(["env-1", "env-2"])

        assert result == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/environments2/syncAllUsers",
            json_data={"environmentNames": ["env-1", "env-2"]},
        )

    def test_sync_all_users_without_environments(self, mocker):
        """sync_all_users sends empty body when no environments specified."""
        mock_response = {
            "operationId": OPERATION_ID,
            "status": "RUNNING",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpEnvClient(api_client=api_client)
        result = client.sync_all_users()

        assert result == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/environments2/syncAllUsers",
            json_data={},
        )

    def test_sync_user(self, mocker):
        """sync_user sends empty body to syncUser endpoint."""
        mock_response = {
            "operationId": OPERATION_ID,
            "status": "RUNNING",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpEnvClient(api_client=api_client)
        result = client.sync_user()

        assert result == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/environments2/syncUser",
            json_data={},
        )

    def test_get_sync_status(self, mocker):
        """get_sync_status passes operationId in request body."""
        mock_response = {
            "operationId": OPERATION_ID,
            "operationType": "USER_SYNC",
            "status": "COMPLETED",
            "success": [{"environmentCrn": "crn:env:1"}],
            "failure": [],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpEnvClient(api_client=api_client)
        result = client.get_sync_status(OPERATION_ID)

        assert result == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/environments2/syncStatus",
            json_data={"operationId": OPERATION_ID},
        )

    def test_get_environment_user_sync_state(self, mocker):
        """get_environment_user_sync_state passes environmentName."""
        mock_response = {
            "state": "SYNC_COMPLETED",
            "userSyncOperationId": OPERATION_ID,
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpEnvClient(api_client=api_client)
        result = client.get_environment_user_sync_state(ENV_NAME)

        assert result == mock_response
        api_client.post.assert_called_once_with(
            "/api/v1/environments2/getEnvironmentUserSyncState",
            json_data={"environmentName": ENV_NAME},
        )


class TestCdpEnvClientWaitForSync:
    """Unit tests for CdpEnvClient.wait_for_sync polling method."""

    def test_wait_for_sync_already_completed(self, mocker):
        """Returns immediately when status is already in target_statuses."""
        completed_response = {
            "operationId": OPERATION_ID,
            "status": "COMPLETED",
            "success": [{"environmentCrn": "crn:env:1"}],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            return_value=completed_response,
        )

        result = client.wait_for_sync(OPERATION_ID)

        assert result == completed_response
        assert result["status"] == "COMPLETED"

    def test_wait_for_sync_polls_until_completed(self, mocker):
        """Polls multiple times until target status is reached."""
        running_response = {"operationId": OPERATION_ID, "status": "RUNNING"}
        completed_response = {
            "operationId": OPERATION_ID,
            "status": "COMPLETED",
            "endTime": "1602080301000",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            side_effect=[running_response, running_response, completed_response],
        )
        mock_sleep = mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env.time.sleep",
        )

        result = client.wait_for_sync(OPERATION_ID, delay=10, timeout=3600)

        assert result == completed_response
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(10)

    def test_wait_for_sync_raises_on_error_status(self, mocker):
        """Raises CdpError when sync enters an error status."""
        failed_response = {
            "operationId": OPERATION_ID,
            "status": "FAILED",
            "error": "Sync failed due to network error",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            return_value=failed_response,
        )

        with pytest.raises(CdpError, match="FAILED"):
            client.wait_for_sync(OPERATION_ID)

    def test_wait_for_sync_raises_on_timedout_status(self, mocker):
        """Raises CdpError when sync status is TIMEDOUT."""
        timedout_response = {
            "operationId": OPERATION_ID,
            "status": "TIMEDOUT",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            return_value=timedout_response,
        )

        with pytest.raises(CdpError, match="TIMEDOUT"):
            client.wait_for_sync(OPERATION_ID)

    def test_wait_for_sync_raises_on_rejected_status(self, mocker):
        """Raises CdpError when sync status is REJECTED."""
        rejected_response = {
            "operationId": OPERATION_ID,
            "status": "REJECTED",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            return_value=rejected_response,
        )

        with pytest.raises(CdpError, match="REJECTED"):
            client.wait_for_sync(OPERATION_ID)

    def test_wait_for_sync_raises_on_timeout(self, mocker):
        """Raises CdpError when polling exceeds timeout."""
        running_response = {"operationId": OPERATION_ID, "status": "RUNNING"}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(
            client,
            "get_sync_status",
            return_value=running_response,
        )
        mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env.time.sleep",
        )
        mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env.time.time",
            side_effect=[0, 0, 3700],
        )

        with pytest.raises(CdpError, match="Timeout"):
            client.wait_for_sync(OPERATION_ID, timeout=3600)

    def test_wait_for_sync_custom_target_statuses(self, mocker):
        """Accepts custom target_statuses."""
        response = {"operationId": OPERATION_ID, "status": "CUSTOM_DONE"}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpEnvClient(api_client=api_client)

        mocker.patch.object(client, "get_sync_status", return_value=response)

        result = client.wait_for_sync(
            OPERATION_ID,
            target_statuses={"CUSTOM_DONE"},
        )

        assert result == response
