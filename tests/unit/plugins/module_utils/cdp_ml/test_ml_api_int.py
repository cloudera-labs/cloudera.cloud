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

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_ml import (
    CdpMlClient,
)


@pytest.mark.integration_api
class TestCdpMlClientIntegration:
    """Integration tests for CdpMlClient."""

    def test_list_workspaces(self, ansible_cdp_client):
        """Test listing Cloudera AI workspaces."""

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=ansible_cdp_client)

        response = client.list_workspaces()

        assert "workspaces" in response
        assert len(response["workspaces"]) > 0
        assert isinstance(response["workspaces"][0], dict)

    @pytest.mark.slow
    def test_describe_all_workspaces(self, ansible_cdp_client):
        """Test describing all Cloudera AI workspaces."""

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=ansible_cdp_client)

        response = client.describe_all_workspaces()

        assert isinstance(response, list)
        assert len(response) > 0
        assert isinstance(response[0], dict)

    def test_describe_workspace_not_found(self, ansible_cdp_client):
        """Test describing a non-existent Cloudera AI workspace."""

        # Create the CdpMlClient instance
        client = CdpMlClient(api_client=ansible_cdp_client)

        # Use non-existent workspace name and environment for testing
        test_workspace_name = "non-existent-workspace"
        env_name = "non-existent-environment"

        response = client.describe_workspace(env=env_name, name=test_workspace_name)

        # Assert that response is empty dict due to squelch handling 404/500
        assert response == {} or response is None or "workspace" not in response
