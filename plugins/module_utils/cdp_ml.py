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

"""
A REST client for the Cloudera on Cloud Platform (CDP) AI API
"""

from typing import Any, Dict, List, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpClient,
)


class CdpMlClient:
    """CDP AI API client."""

    def __init__(self, api_client: CdpClient):
        """
        Initialize CDP AI client.

        Args:
            api_client: RestClient instance for managing HTTP method calls
        """
        self.api_client = api_client

    def list_workspaces(
        self,
        env: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List ML Workspaces in the Tenant.

        Args:
            env: Optional environment name to filter workspaces by.

        Returns:
            List of workspaces in the tenant, optionally filtered by environment.
        """

        resp = self.api_client.post(
            "/api/v1/ml/listWorkspaces",
            json_data={},
            squelch={404: []},
        )

        if env:
            workspaces = resp.get("workspaces", [])
            resp["workspaces"] = [x for x in workspaces if env == x["environmentName"]]

        return resp

    def describe_workspace(
        self,
        env: Optional[str] = None,
        name: Optional[str] = None,
        crn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Describe a single ML Workspace.

        Args:
            env: Optional environment name.
            name: Optional workspace name.
            crn: Optional workspace CRN. If provided, env and name are ignored.

        Returns:
            Workspace details dictionary.
        """

        json_data: Dict[str, Any] = {}

        if crn is not None:
            json_data["workspaceCrn"] = crn
        else:
            if env is not None:
                json_data["environmentName"] = env
            if name is not None:
                json_data["workspaceName"] = name

        return self.api_client.post(
            "/api/v1/ml/describeWorkspace",
            json_data=json_data,
            squelch={
                404: {},
                500: {},
            },
        )

    def describe_all_workspaces(
        self,
        env: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Describe all ML Workspaces in the Tenant, optionally filtered by environment.

        Args:
            env: Optional environment name to filter workspaces by.

        Returns:
            List of workspace details for all workspaces in the tenant.
        """
        ws_list = self.list_workspaces(env)
        resp = []

        for ws in ws_list.get("workspaces", []):
            ws_desc = self.describe_workspace(crn=ws["crn"])
            if ws_desc is not None:
                resp.append(ws_desc.get("workspace", {}))
        return resp
