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
    DataFlowEncryptionParameters,
    DataFlowServiceDescription,
    DataFlowServiceStatus,
    DataFlowServiceSummary,
    check_service_updates,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
)


SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-abc123"
SERVICE_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"


class TestCdpDfClient:
    """Unit tests for CdpDfClient service management methods."""

    def test_list_services_default(self, mocker):
        """Test listing all DataFlow services (default behavior)."""

        mock_response = {
            "services": [
                {
                    "crn": SERVICE_CRN,
                    "name": SERVICE_NAME,
                    "environmentCrn": ENV_CRN,
                    "status": {"state": "GOOD_HEALTH"},
                },
                {
                    "crn": "crn:cdp:df:us-west-1:tenant:service:service-456",
                    "name": "other-service",
                    "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-456",
                    "status": {"state": "GOOD_HEALTH"},
                },
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.list_services()

        assert isinstance(response, list)
        assert len(response) == 2
        assert all(isinstance(s, DataFlowServiceSummary) for s in response)
        assert response[0].crn == SERVICE_CRN
        assert response[1].name == "other-service"

        api_client.post.assert_called_once_with(
            "/api/v1/df/listServices",
            data={},
            squelch={404: {"services": []}},
        )

    def test_list_services_search_term(self, mocker):
        """Test listing services filtered by a search term."""

        mock_response = {
            "services": [
                {"crn": SERVICE_CRN, "name": SERVICE_NAME},
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.list_services(search_term=SERVICE_NAME)

        assert len(response) == 1
        assert response[0].name == SERVICE_NAME

        api_client.post.assert_called_once_with(
            "/api/v1/df/listServices",
            data={"searchTerm": SERVICE_NAME},
            squelch={404: {"services": []}},
        )

    def test_list_services_not_found(self, mocker):
        """Test listing services when none exist (404 error)."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"services": []}

        client = CdpDfClient(api_client=api_client)
        response = client.list_services()

        assert isinstance(response, list)
        assert len(response) == 0

    def test_describe_service(self, mocker):
        """Test describing a DataFlow service."""

        mock_response = {
            "service": {
                "crn": SERVICE_CRN,
                "name": SERVICE_NAME,
                "environmentCrn": ENV_CRN,
                "status": {"state": "GOOD_HEALTH"},
                "minK8sNodeCount": 3,
                "maxK8sNodeCount": 10,
                "encryptionParameters": {"encryptionStrategy": "DEFAULT"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.describe_service(SERVICE_CRN)

        assert isinstance(response, DataFlowServiceDescription)
        assert response.crn == SERVICE_CRN
        assert response.name == SERVICE_NAME
        assert isinstance(response.status, DataFlowServiceStatus)
        assert response.status.state == "GOOD_HEALTH"
        assert isinstance(response.encryptionParameters, DataFlowEncryptionParameters)
        assert response.encryptionParameters.encryptionStrategy == "DEFAULT"

        api_client.post.assert_called_once_with(
            "/api/v1/df/describeService",
            data={"serviceCrn": SERVICE_CRN},
            squelch={404: {}},
        )

    def test_describe_service_not_found(self, mocker):
        """Test describing a service that doesn't exist (404 error)."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.describe_service(SERVICE_CRN)

        assert response is None

    def test_get_service_by_name(self, mocker):
        """Test getting service details by environment name."""

        list_mock = [
            DataFlowServiceSummary(
                crn=SERVICE_CRN,
                name=SERVICE_NAME,
                status=DataFlowServiceStatus(state="GOOD_HEALTH"),
            ),
            DataFlowServiceSummary(
                crn="crn:cdp:df:us-west-1:tenant:service:other",
                name="other-env",
                status=DataFlowServiceStatus(state="GOOD_HEALTH"),
            ),
        ]

        describe_mock = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            name=SERVICE_NAME,
            status=DataFlowServiceStatus(state="GOOD_HEALTH"),
        )

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        response = client.get_service_by_name(SERVICE_NAME)

        assert isinstance(response, DataFlowServiceDescription)
        assert response.name == SERVICE_NAME
        assert response.crn == SERVICE_CRN

        client.list_services.assert_called_once_with(search_term=SERVICE_NAME)
        client.describe_service.assert_called_once_with(
            SERVICE_CRN,
            squelch={500: {}},
        )

    def test_get_service_by_name_not_found(self, mocker):
        """Test getting service by name when it doesn't exist."""

        list_mock = [
            DataFlowServiceSummary(crn="crn:other", name="other-env"),
        ]

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)

        response = client.get_service_by_name("nonexistent-env")

        assert response is None

    def test_get_service_by_name_disabled_skips_describe(self, mocker):
        """A NOT_ENABLED match is treated as absent without calling describe_service."""

        list_mock = [
            DataFlowServiceSummary(
                crn=SERVICE_CRN,
                name=SERVICE_NAME,
                status=DataFlowServiceStatus(state="NOT_ENABLED"),
            ),
        ]

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)
        describe = mocker.patch.object(client, "describe_service")

        response = client.get_service_by_name(SERVICE_NAME)

        assert response is None
        describe.assert_not_called()

    def test_get_service_by_crn(self, mocker):
        """Test getting service details by service CRN."""

        list_mock = [
            DataFlowServiceSummary(
                crn=SERVICE_CRN,
                status=DataFlowServiceStatus(state="GOOD_HEALTH"),
            ),
        ]
        describe_mock = DataFlowServiceDescription(crn=SERVICE_CRN)

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        response = client.get_service_by_crn(SERVICE_CRN)

        assert isinstance(response, DataFlowServiceDescription)
        assert response.crn == SERVICE_CRN
        client.describe_service.assert_called_once_with(
            SERVICE_CRN,
            squelch={500: {}},
        )

    def test_get_service_by_env_crn(self, mocker):
        """Test getting service details by environment CRN."""

        list_mock = [
            DataFlowServiceSummary(
                crn=SERVICE_CRN,
                environmentCrn=ENV_CRN,
                status=DataFlowServiceStatus(state="GOOD_HEALTH"),
            ),
        ]
        describe_mock = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            environmentCrn=ENV_CRN,
        )

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)
        mocker.patch.object(client, "describe_service", return_value=describe_mock)

        response = client.get_service_by_env_crn(ENV_CRN)

        assert isinstance(response, DataFlowServiceDescription)
        assert response.environmentCrn == ENV_CRN
        client.describe_service.assert_called_once_with(
            SERVICE_CRN,
            squelch={500: {}},
        )

    @pytest.mark.parametrize(
        "lookup, arg",
        [
            ("get_service_by_name", SERVICE_NAME),
            ("get_service_by_crn", SERVICE_CRN),
            ("get_service_by_env_crn", ENV_CRN),
        ],
    )
    def test_get_service_falls_back_to_summary_when_describe_fails(
        self,
        mocker,
        lookup,
        arg,
    ):
        """An orphaned service (describeService 500) is returned from its list summary."""

        list_mock = [
            DataFlowServiceSummary(
                crn=SERVICE_CRN,
                name=SERVICE_NAME,
                environmentCrn=ENV_CRN,
                status=DataFlowServiceStatus(
                    state="CONCERNING_HEALTH",
                    detailedState="ORPHANED_NOT_ENABLED",
                ),
            ),
        ]

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "list_services", return_value=list_mock)
        # The squelched 500 makes describe_service return None
        mocker.patch.object(client, "describe_service", return_value=None)

        response = getattr(client, lookup)(arg)

        assert isinstance(response, DataFlowServiceDescription)
        assert response.crn == SERVICE_CRN
        assert response.name == SERVICE_NAME
        assert response.environmentCrn == ENV_CRN
        assert isinstance(response.status, DataFlowServiceStatus)
        assert response.status.detailedState == "ORPHANED_NOT_ENABLED"
        # Detail-only fields stay unset
        assert response.privateCluster is NULLABLE
        client.describe_service.assert_called_once_with(
            SERVICE_CRN,
            squelch={500: {}},
        )

    def test_enable_service(self, mocker):
        """Test enabling a service returns an unwrapped DataFlowServiceDescription."""

        mock_response = {
            "service": {
                "crn": SERVICE_CRN,
                "name": SERVICE_NAME,
                "environmentCrn": ENV_CRN,
                "status": {"state": "ENABLING"},
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.enable_service(
            environment_crn=ENV_CRN,
            min_k8s_node_count=3,
            max_k8s_node_count=10,
            tags={"team": "platform"},
        )

        assert isinstance(response, DataFlowServiceDescription)
        assert response.crn == SERVICE_CRN

        api_client.post.assert_called_once_with(
            "/api/v1/df/enableService",
            data={
                "environmentCrn": ENV_CRN,
                "minK8sNodeCount": 3,
                "maxK8sNodeCount": 10,
                "tags": {"team": "platform"},
            },
        )

    def test_enable_service_no_service_in_response(self, mocker):
        """Test enabling a service returns None when response lacks a service."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.enable_service(environment_crn=ENV_CRN)

        assert response is None

    def test_update_service(self, mocker):
        """Test updating a service returns an unwrapped DataFlowServiceDescription."""

        mock_response = {
            "service": {
                "crn": SERVICE_CRN,
                "minK8sNodeCount": 5,
                "maxK8sNodeCount": 15,
            },
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.update_service(
            service_crn=SERVICE_CRN,
            min_k8s_node_count=5,
            max_k8s_node_count=15,
        )

        assert isinstance(response, DataFlowServiceDescription)
        assert response.minK8sNodeCount == 5

        api_client.post.assert_called_once_with(
            "/api/v1/df/updateService",
            data={
                "serviceCrn": SERVICE_CRN,
                "minK8sNodeCount": 5,
                "maxK8sNodeCount": 15,
            },
        )

    def test_update_service_no_service_in_response(self, mocker):
        """Test updating a service returns None when response lacks a service."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.update_service(service_crn=SERVICE_CRN)

        assert response is None

    def test_disable_service(self, mocker):
        """Test disabling a service returns an unwrapped DataFlowServiceStatus."""

        mock_response = {"status": {"state": "DISABLING"}}

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDfClient(api_client=api_client)
        response = client.disable_service(crn=SERVICE_CRN, terminate_deployments=True)

        assert isinstance(response, DataFlowServiceStatus)
        assert response.state == "DISABLING"

        api_client.post.assert_called_once_with(
            "/api/v1/df/disableService",
            data={
                "serviceCrn": SERVICE_CRN,
                "terminateDeployments": True,
                "persist": False,
            },
        )

    def test_disable_service_no_status_in_response(self, mocker):
        """Test disabling a service returns None when response lacks a status."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.disable_service(crn=SERVICE_CRN)

        assert response is None

    def test_reset_service(self, mocker):
        """reset_service stays a raw passthrough (not dataclass-modeled)."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDfClient(api_client=api_client)
        response = client.reset_service(SERVICE_CRN)

        assert response == {}
        api_client.post.assert_called_once_with(
            "/api/v1/df/resetService",
            data={"serviceCrn": SERVICE_CRN},
        )

    def test_wait_for_service_state_already_target(self, mocker):
        """wait_for_service_state returns the DataFlowServiceDescription when already at target."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        described = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="GOOD_HEALTH"),
        )
        mocker.patch.object(client, "get_service_by_crn", return_value=described)

        result = client.wait_for_service_state(
            service_crn=SERVICE_CRN,
            target_states=["GOOD_HEALTH"],
        )

        assert isinstance(result, DataFlowServiceDescription)
        assert result.crn == SERVICE_CRN

    def test_wait_for_service_state_gone_returns_none(self, mocker):
        """wait_for_service_state returns None once the service is fully gone."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        mocker.patch.object(client, "get_service_by_crn", return_value=None)

        result = client.wait_for_service_state(
            service_crn=SERVICE_CRN,
            target_states=["NOT_ENABLED"],
        )

        assert result is None

    def test_wait_for_service_state_raises_on_failed_state(self, mocker):
        """wait_for_service_state raises when the service enters a failed state."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        described = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="BAD_HEALTH", message="boom"),
        )
        mocker.patch.object(client, "get_service_by_crn", return_value=described)

        with pytest.raises(CdpError, match="boom"):
            client.wait_for_service_state(
                service_crn=SERVICE_CRN,
                target_states=["GOOD_HEALTH"],
            )

    def test_wait_for_service_state_initiates_disable(self, mocker):
        """When targeting NOT_ENABLED from a removable state, disable_service is called."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        running = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="GOOD_HEALTH"),
        )
        disabled = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="NOT_ENABLED"),
        )
        mocker.patch.object(
            client,
            "get_service_by_crn",
            side_effect=[running, disabled],
        )
        disable = mocker.patch.object(client, "disable_service")

        result = client.wait_for_service_state(
            service_crn=SERVICE_CRN,
            target_states=["NOT_ENABLED"],
            delay=0,
        )

        disable.assert_called_once_with(
            crn=SERVICE_CRN,
            terminate_deployments=False,
            persist=False,
        )
        assert result.status.state == "NOT_ENABLED"

    def test_wait_for_service_state_cannot_disable_raises(self, mocker):
        """Targeting NOT_ENABLED from an unrecognized state raises CdpError."""

        api_client = mocker.create_autospec(CdpClient, instance=True)
        client = CdpDfClient(api_client=api_client)

        described = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="ENABLING"),
        )
        mocker.patch.object(client, "get_service_by_crn", return_value=described)

        with pytest.raises(CdpError, match="Cannot disable service"):
            client.wait_for_service_state(
                service_crn=SERVICE_CRN,
                target_states=["NOT_ENABLED"],
            )


class TestCheckServiceUpdates:
    """Unit tests for check_service_updates reading a DataFlowServiceDescription."""

    def test_no_changes_returns_empty(self):
        details = DataFlowServiceDescription(minK8sNodeCount=3, maxK8sNodeCount=10)
        assert (
            check_service_updates(
                service_crn=SERVICE_CRN,
                service_details=details,
                min_k8s_node_count=3,
                max_k8s_node_count=10,
            )
            == {}
        )

    def test_detects_node_count_change(self):
        details = DataFlowServiceDescription(minK8sNodeCount=3, maxK8sNodeCount=10)
        result = check_service_updates(
            service_crn=SERVICE_CRN,
            service_details=details,
            min_k8s_node_count=5,
        )
        assert result == {
            "service_crn": SERVICE_CRN,
            "min_k8s_node_count": 5,
            "max_k8s_node_count": 10,
        }

    def test_ip_ranges_compared_as_set(self):
        details = DataFlowServiceDescription(
            kubeApiAuthorizedIpRanges=["10.0.0.0/8", "192.168.0.0/16"],
        )
        assert (
            check_service_updates(
                service_crn=SERVICE_CRN,
                service_details=details,
                kubernetes_ip_cidr_blocks=["192.168.0.0/16", "10.0.0.0/8"],
            )
            == {}
        )
        result = check_service_updates(
            service_crn=SERVICE_CRN,
            service_details=details,
            kubernetes_ip_cidr_blocks=["10.0.0.0/8"],
        )
        assert result == {
            "service_crn": SERVICE_CRN,
            "kubernetes_ip_cidr_blocks": ["10.0.0.0/8"],
        }

    def test_nullable_ip_ranges_treated_as_empty(self):
        details = DataFlowServiceDescription()
        result = check_service_updates(
            service_crn=SERVICE_CRN,
            service_details=details,
            load_balancer_ip_cidr_blocks=["10.0.0.0/8"],
        )
        assert result == {
            "service_crn": SERVICE_CRN,
            "load_balancer_ip_cidr_blocks": ["10.0.0.0/8"],
        }

    def test_skip_preflight_checks_passthrough(self):
        details = DataFlowServiceDescription(minK8sNodeCount=3, maxK8sNodeCount=10)
        result = check_service_updates(
            service_crn=SERVICE_CRN,
            service_details=details,
            min_k8s_node_count=5,
            skip_preflight_checks=True,
        )
        assert result == {
            "service_crn": SERVICE_CRN,
            "min_k8s_node_count": 5,
            "max_k8s_node_count": 10,
            "skip_preflight_checks": True,
        }


class TestDataFlowDataclasses:
    """Unit tests for DataFlow dataclass construction and serialization."""

    def test_defaults_are_nullable(self):
        desc = DataFlowServiceDescription()
        assert desc.crn is NULLABLE
        assert desc.status is NULLABLE
        assert desc.encryptionParameters is NULLABLE
        assert desc.tags is NULLABLE

    def test_from_dict_populates_flat_fields(self):
        desc = from_dict(
            DataFlowServiceDescription,
            {"crn": SERVICE_CRN, "name": SERVICE_NAME},
        )
        assert desc.crn == SERVICE_CRN
        assert desc.name == SERVICE_NAME
        assert desc.environmentCrn is NULLABLE

    def test_from_dict_nested_status(self):
        desc = from_dict(
            DataFlowServiceDescription,
            {"crn": SERVICE_CRN, "status": {"state": "GOOD_HEALTH"}},
        )
        assert isinstance(desc.status, DataFlowServiceStatus)
        assert desc.status.state == "GOOD_HEALTH"

    def test_from_dict_nested_encryption_parameters(self):
        desc = from_dict(
            DataFlowServiceDescription,
            {
                "crn": SERVICE_CRN,
                "encryptionParameters": {"encryptionStrategy": "DEFAULT"},
            },
        )
        assert isinstance(desc.encryptionParameters, DataFlowEncryptionParameters)
        assert desc.encryptionParameters.encryptionStrategy == "DEFAULT"

    def test_from_dict_tags_is_plain_map(self):
        desc = from_dict(
            DataFlowServiceDescription,
            {"crn": SERVICE_CRN, "tags": {"team": "platform"}},
        )
        assert desc.tags == {"team": "platform"}

    def test_to_dict_excludes_nullable(self):
        desc = DataFlowServiceDescription(crn=SERVICE_CRN)
        result = to_dict(desc)
        assert result == {"crn": SERVICE_CRN}
        assert "status" not in result

    def test_to_dict_round_trip_nested(self):
        desc = DataFlowServiceDescription(
            crn=SERVICE_CRN,
            status=DataFlowServiceStatus(state="GOOD_HEALTH"),
        )
        result = to_dict(desc)
        assert result["crn"] == SERVICE_CRN
        assert result["status"] == {"state": "GOOD_HEALTH"}

    def test_summary_from_dict_and_to_dict(self):
        summary = from_dict(
            DataFlowServiceSummary,
            {"crn": SERVICE_CRN, "name": SERVICE_NAME},
        )
        assert summary.crn == SERVICE_CRN
        assert to_dict(summary) == {"crn": SERVICE_CRN, "name": SERVICE_NAME}
