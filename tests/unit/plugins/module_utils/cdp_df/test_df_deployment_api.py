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
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    check_deployment_updates,
)

SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-abc123"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-abc123"
FLOW_VERSION_CRN = "crn:cdp:df:us-west-1:tenant:flowVersion:flow-abc123/v1"
DEPLOYMENT_CRN = "crn:cdp:df:us-west-1:tenant:deployment:dep-abc123"
DEPLOYMENT_REQUEST_CRN = "crn:cdp:df:us-west-1:tenant:deploymentRequest:req-abc123"
DEPLOYMENT_NAME = "test-deployment"


class TestCdpDfClientDeploymentMethods:
    """Unit tests for CdpDfClient deployment management methods."""

    def test_list_deployments_default(self, mocker):
        """Test listing all deployments with no filters."""
        mock_response = {
            "deployments": [
                {
                    "crn": DEPLOYMENT_CRN,
                    "name": DEPLOYMENT_NAME,
                    "status": {"state": "GOOD_HEALTH"},
                },
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.list_deployments()

        assert "deployments" in response
        assert len(response["deployments"]) == 1
        assert response["deployments"][0]["crn"] == DEPLOYMENT_CRN

        api_client.post.assert_called_once_with(
            "/api/v1/df/listDeployments",
            data={"pageSize": 100},
            squelch={404: {"deployments": []}},
        )

    def test_list_deployments_with_filters(self, mocker):
        """Test listing deployments with filter criteria."""
        mock_response = {"deployments": []}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        client.list_deployments(filters=["name:test"])

        api_client.post.assert_called_once_with(
            "/api/v1/df/listDeployments",
            data={"filters": ["name:test"], "pageSize": 100},
            squelch={404: {"deployments": []}},
        )

    def test_list_deployments_not_found(self, mocker):
        """Test listing deployments when none exist (squelched 404)."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"deployments": []}

        client = CdpDfClient(api_client=api_client)
        response = client.list_deployments()

        assert "deployments" in response
        assert len(response["deployments"]) == 0

    def test_describe_deployment(self, mocker):
        """Test describing a deployment by CRN."""
        mock_response = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
                "status": {"state": "GOOD_HEALTH"},
                "staticNodeCount": 1,
                "clusterSize": {"name": "EXTRA_SMALL"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.describe_deployment(DEPLOYMENT_CRN)

        assert "deployment" in response
        assert response["deployment"]["crn"] == DEPLOYMENT_CRN
        assert response["deployment"]["name"] == DEPLOYMENT_NAME

        api_client.post.assert_called_once_with(
            "/api/v1/df/describeDeployment",
            data={"deploymentCrn": DEPLOYMENT_CRN},
            squelch={404: {}},
        )

    def test_describe_deployment_not_found(self, mocker):
        """Test describing a deployment that doesn't exist (squelched 404)."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.describe_deployment("nonexistent-crn")

        assert response == {}

    def test_get_deployment_by_name(self, mocker):
        """Test getting a deployment by name via list then describe."""
        list_mock = {
            "deployments": [
                {"crn": DEPLOYMENT_CRN, "name": DEPLOYMENT_NAME},
                {"crn": "crn:other", "name": "other-deployment"},
            ],
        }
        describe_mock = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
                "status": {"state": "GOOD_HEALTH"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_deployments", return_value=list_mock)
        mocker.patch.object(client, "describe_deployment", return_value=describe_mock)

        response = client.get_deployment_by_name(DEPLOYMENT_NAME)

        assert response is not None
        assert response["deployment"]["name"] == DEPLOYMENT_NAME
        client.list_deployments.assert_called_once()
        client.describe_deployment.assert_called_once_with(DEPLOYMENT_CRN)

    def test_get_deployment_by_name_not_found(self, mocker):
        """Test getting a deployment by name when it doesn't exist."""
        list_mock = {
            "deployments": [
                {"crn": "crn:other", "name": "other-deployment"},
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "list_deployments", return_value=list_mock)

        response = client.get_deployment_by_name("nonexistent")

        assert response is None
        client.list_deployments.assert_called_once()

    def test_get_deployment_by_crn(self, mocker):
        """Test getting a deployment by CRN wraps describe_deployment."""
        describe_mock = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "describe_deployment", return_value=describe_mock)

        response = client.get_deployment_by_crn(DEPLOYMENT_CRN)

        assert response is not None
        assert response["deployment"]["crn"] == DEPLOYMENT_CRN
        client.describe_deployment.assert_called_once_with(DEPLOYMENT_CRN)

    def test_get_deployment_by_crn_error_returns_none(self, mocker):
        """Test that a CdpError from describe_deployment returns None."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(
            client,
            "describe_deployment",
            side_effect=CdpError("not found"),
        )

        response = client.get_deployment_by_crn("nonexistent-crn")

        assert response is None

    def test_initiate_deployment(self, mocker):
        """Test initiating a deployment returns a deploymentRequestCrn."""
        mock_response = {
            "deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN,
            "dfxLocalUrl": "https://dfx.example.cloudera.site",
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.initiate_deployment(
            service_crn=SERVICE_CRN,
            flow_version_crn=FLOW_VERSION_CRN,
        )

        assert response["deploymentRequestCrn"] == DEPLOYMENT_REQUEST_CRN
        api_client.post.assert_called_once_with(
            "/api/v1/df/initiateDeployment",
            data={
                "serviceCrn": SERVICE_CRN,
                "flowVersionCrn": FLOW_VERSION_CRN,
            },
        )

    def test_initiate_deployment_with_existing_deployment_crn(self, mocker):
        """Test initiating a deployment for a flow version change includes deploymentCrn."""
        mock_response = {"deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        client.initiate_deployment(
            service_crn=SERVICE_CRN,
            flow_version_crn=FLOW_VERSION_CRN,
            deployment_crn=DEPLOYMENT_CRN,
        )

        api_client.post.assert_called_once_with(
            "/api/v1/df/initiateDeployment",
            data={
                "serviceCrn": SERVICE_CRN,
                "flowVersionCrn": FLOW_VERSION_CRN,
                "deploymentCrn": DEPLOYMENT_CRN,
            },
        )

    def test_create_deployment_calls_request_details_first(self, mocker):
        """Test that create_deployment primes the XSRF cookie before posting."""
        mock_response = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        workload_client = mocker.Mock()
        workload_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        get_details = mocker.patch.object(
            client,
            "get_deployment_request_details",
            return_value={},
        )

        response = client.create_deployment(
            workload_client=workload_client,
            environment_crn=ENV_CRN,
            deployment_request_crn=DEPLOYMENT_REQUEST_CRN,
            name=DEPLOYMENT_NAME,
            configuration_version=0,
            cluster_size="EXTRA_SMALL",
            static_node_count=1,
            parameter_groups=[],
        )

        get_details.assert_called_once_with(workload_client, DEPLOYMENT_REQUEST_CRN)
        workload_client.post.assert_called_once_with(
            "/dfx/api/rpc-v1/deployments/create-deployment",
            data={
                "environmentCrn": ENV_CRN,
                "deploymentRequestCrn": DEPLOYMENT_REQUEST_CRN,
                "name": DEPLOYMENT_NAME,
                "configurationVersion": 0,
                "clusterSize": {"name": "EXTRA_SMALL"},
                "staticNodeCount": 1,
                "parameterGroups": [],
            },
        )
        assert response["deployment"]["crn"] == DEPLOYMENT_CRN

    def test_create_deployment_sends_empty_parameter_groups_when_none(self, mocker):
        """Test that create_deployment sends empty parameterGroups when not provided."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        workload_client = mocker.Mock()
        workload_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "get_deployment_request_details", return_value={})

        client.create_deployment(
            workload_client=workload_client,
            environment_crn=ENV_CRN,
            deployment_request_crn=DEPLOYMENT_REQUEST_CRN,
            name=DEPLOYMENT_NAME,
            configuration_version=0,
        )

        call_data = workload_client.post.call_args[1]["data"]
        assert call_data["parameterGroups"] == []

    def test_terminate_deployment(self, mocker):
        """Test terminating a deployment calls the workload API."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        workload_client = mocker.Mock()
        workload_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        client.terminate_deployment(
            workload_client=workload_client,
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
        )

        workload_client.post.assert_called_once_with(
            "/dfx/api/rpc-v1/deployments/terminate-deployment",
            data={
                "deploymentCrn": DEPLOYMENT_CRN,
                "environmentCrn": ENV_CRN,
            },
        )

    def test_update_deployment_static_node_count(self, mocker):
        """Test updating a deployment's static node count."""
        mock_response = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "name": DEPLOYMENT_NAME,
                "staticNodeCount": 2,
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        workload_client = mocker.Mock()
        workload_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.update_deployment(
            workload_client=workload_client,
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            configuration_version=1,
            static_node_count=2,
        )

        workload_client.post.assert_called_once_with(
            "/dfx/api/rpc-v1/deployments/update-deployment",
            data={
                "deploymentCrn": DEPLOYMENT_CRN,
                "environmentCrn": ENV_CRN,
                "configurationVersion": 1,
                "staticNodeCount": 2,
            },
        )
        assert response["deployment"]["staticNodeCount"] == 2

    def test_update_deployment_cluster_size(self, mocker):
        """Test updating a deployment's cluster size wraps name in a dict."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        workload_client = mocker.Mock()
        workload_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        client.update_deployment(
            workload_client=workload_client,
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            configuration_version=1,
            cluster_size="SMALL",
        )

        call_data = workload_client.post.call_args[1]["data"]
        assert call_data["clusterSize"] == {"name": "SMALL"}

    def test_wait_for_deployment_state_raises_without_crn_or_name(self, mocker):
        """Test that wait_for_deployment_state raises if neither CRN nor name given."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        with pytest.raises(CdpError, match="Either deployment_crn or deployment_name"):
            client.wait_for_deployment_state(target_states=["GOOD_HEALTH"])

    def test_wait_for_deployment_state_immediate_success(self, mocker):
        """Test wait_for_deployment_state returns immediately when already in target state."""
        mock_deployment = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "status": {"state": "GOOD_HEALTH"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(
            client,
            "describe_deployment",
            return_value=mock_deployment,
        )
        mocker.patch("time.sleep")

        result = client.wait_for_deployment_state(
            target_states=["GOOD_HEALTH"],
            deployment_crn=DEPLOYMENT_CRN,
            timeout=60,
            delay=5,
        )

        assert result == mock_deployment

    def test_wait_for_deployment_state_timeout(self, mocker):
        """Test that wait_for_deployment_state raises CdpError on timeout."""
        mock_deployment = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "status": {"state": "DEPLOYING"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(
            client,
            "describe_deployment",
            return_value=mock_deployment,
        )
        mocker.patch("time.sleep")

        # Mock time to force immediate timeout
        mock_time = mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df.time",
        )
        mock_time.time.side_effect = [0, 999]
        mock_time.sleep = mocker.Mock()

        with pytest.raises(CdpError, match="Timeout"):
            client.wait_for_deployment_state(
                target_states=["GOOD_HEALTH"],
                deployment_crn=DEPLOYMENT_CRN,
                timeout=10,
                delay=5,
            )

    def test_wait_for_deployment_state_failed_state_raises(self, mocker):
        """Test that wait_for_deployment_state raises CdpError when deployment fails."""
        mock_deployment = {
            "deployment": {
                "crn": DEPLOYMENT_CRN,
                "status": {"state": "FAILED", "message": "Out of resources"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(
            client,
            "describe_deployment",
            return_value=mock_deployment,
        )

        mock_time = mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df.time",
        )
        mock_time.time.side_effect = [0, 5]
        mock_time.sleep = mocker.Mock()

        with pytest.raises(CdpError, match="FAILED"):
            client.wait_for_deployment_state(
                target_states=["GOOD_HEALTH"],
                deployment_crn=DEPLOYMENT_CRN,
                timeout=60,
                delay=5,
            )

    def test_wait_for_deployment_deleted_state_returns_none(self, mocker):
        """Test that deleted deployment returns None when DELETED is a target state."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)
        mocker.patch.object(client, "describe_deployment", return_value={})

        mock_time = mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df.time",
        )
        mock_time.time.side_effect = [0, 5]
        mock_time.sleep = mocker.Mock()

        result = client.wait_for_deployment_state(
            target_states=["DELETED", "NOT_FOUND"],
            deployment_crn=DEPLOYMENT_CRN,
            timeout=60,
            delay=5,
        )

        assert result is None


class TestCheckDeploymentUpdates:
    """Unit tests for the check_deployment_updates helper function."""

    def _base_deployment(self):
        return {
            "clusterSize": {"name": "EXTRA_SMALL"},
            "staticNodeCount": 1,
            "autoScalingEnabled": False,
            "autoScaleMinNodes": None,
            "autoScaleMaxNodes": None,
            "flowMetricsScalingEnabled": False,
        }

    def test_no_changes_returns_empty(self):
        """Test that identical values produce no update params."""
        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=self._base_deployment(),
            configuration_version=1,
            cluster_size="EXTRA_SMALL",
            static_node_count=1,
        )
        assert result == {}

    def test_static_node_count_change(self):
        """Test that a changed static_node_count is included in update params."""
        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=self._base_deployment(),
            configuration_version=1,
            static_node_count=3,
        )
        assert result["static_node_count"] == 3
        assert result["deployment_crn"] == DEPLOYMENT_CRN
        assert result["environment_crn"] == ENV_CRN
        assert result["configuration_version"] == 1

    def test_cluster_size_change(self):
        """Test that a changed cluster_size is included in update params."""
        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=self._base_deployment(),
            configuration_version=1,
            cluster_size="SMALL",
        )
        assert result["cluster_size"] == "SMALL"

    def test_autoscaling_enabled_change(self):
        """Test enabling autoscaling is detected as a change."""
        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=self._base_deployment(),
            configuration_version=1,
            autoscaling_enabled=True,
            autoscale_min_nodes=1,
            autoscale_max_nodes=5,
        )
        assert result["auto_scaling_enabled"] is True
        assert result["auto_scale_min_nodes"] == 1
        assert result["auto_scale_max_nodes"] == 5

    def test_parameter_groups_always_included_when_provided(self):
        """Test that parameter_groups is always included when provided (API cannot compare)."""
        groups = [{"name": "pg1", "parameters": []}]
        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=self._base_deployment(),
            configuration_version=1,
            parameter_groups=groups,
        )
        assert result["parameter_groups"] == groups

    def test_cluster_size_as_string_in_deployment_details(self):
        """Test cluster_size comparison when API returns it as a plain string."""
        deployment = dict(self._base_deployment())
        deployment["clusterSize"] = "EXTRA_SMALL"

        result = check_deployment_updates(
            deployment_crn=DEPLOYMENT_CRN,
            environment_crn=ENV_CRN,
            deployment_details=deployment,
            configuration_version=1,
            cluster_size="EXTRA_SMALL",
        )
        assert result == {}
