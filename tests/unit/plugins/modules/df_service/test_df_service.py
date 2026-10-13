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


from ansible_collections.cloudera.cloud.plugins.modules import df_service
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    DataFlowServiceDescription,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    from_dict,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-456"


@pytest.fixture
def df_module_args(module_args):
    """Pre-populate common DF module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "wait": False,
        }
        if "df_crn" not in args:
            merged["env_crn"] = ENV_CRN
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def df_client(mocker):
    """Patch load_cdp_config and CdpDfClient, returning the mocked client.

    autospec replaces the class constants with mocks, so restore the real
    state lists the module reads (C(DISABLED_STATES)).
    """
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.CdpDfClient",
        autospec=True,
    )
    mock_class.DISABLED_STATES = CdpDfClient.DISABLED_STATES
    mock_class.REMOVABLE_STATES = CdpDfClient.REMOVABLE_STATES
    mock_class.TERMINATION_STATES = CdpDfClient.TERMINATION_STATES
    mock_class.FAILED_STATES = CdpDfClient.FAILED_STATES
    return mock_class.return_value


def _existing_service(
    state="GOOD_HEALTH",
    min_k8s_node_count=3,
    max_k8s_node_count=3,
    **overrides,
):
    data = {
        "crn": SERVICE_CRN,
        "name": ENV_NAME,
        "environmentCrn": ENV_CRN,
        "cloudPlatform": "AWS",
        "region": "us-west-1",
        "status": {"state": state},
        "deploymentCount": 0,
        "minK8sNodeCount": min_k8s_node_count,
        "maxK8sNodeCount": max_k8s_node_count,
        "kubeApiAuthorizedIpRanges": [],
        "loadBalancerAuthorizedIpRanges": [],
    }
    data.update(overrides)
    return from_dict(DataFlowServiceDescription, data)


# ============================================================================
# Enable tests
# ============================================================================


def test_present_enable(df_module_args, df_client):
    """A new service is enabled and its parameters are passed through."""
    df_client.get_service_by_env_crn.return_value = None
    df_client.enable_service.return_value = _existing_service(state="ENABLING")

    df_module_args(
        {
            "nodes_min": 3,
            "nodes_max": 3,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN
    assert result.value.service["status"]["state"] == "ENABLING"

    df_client.enable_service.assert_called_once()
    call_args = df_client.enable_service.call_args.kwargs
    assert call_args["environment_crn"] == ENV_CRN
    assert call_args["min_k8s_node_count"] == 3
    assert call_args["max_k8s_node_count"] == 3

    df_client.wait_for_service_state.assert_not_called()


def test_present_enable_with_wait(df_module_args, df_client):
    """Enabling with wait polls to GOOD_HEALTH."""
    df_client.get_service_by_env_crn.return_value = None
    df_client.enable_service.return_value = _existing_service(state="ENABLING")
    df_client.wait_for_service_state.return_value = _existing_service(
        state="GOOD_HEALTH",
    )

    df_module_args({"wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["status"]["state"] == "GOOD_HEALTH"

    df_client.enable_service.assert_called_once()
    df_client.wait_for_service_state.assert_called_once()
    wait_args = df_client.wait_for_service_state.call_args.kwargs
    assert wait_args["service_crn"] == SERVICE_CRN
    assert wait_args["target_states"] == ["GOOD_HEALTH"]


def test_present_enable_custom_params(df_module_args, df_client):
    """Optional enable parameters are passed through to the client."""
    df_client.get_service_by_env_crn.return_value = None
    df_client.enable_service.return_value = _existing_service()

    df_module_args(
        {
            "nodes_min": 5,
            "nodes_max": 20,
            "public_loadbalancer": True,
            "private_cluster": True,
            "k8s_ip_ranges": ["10.0.0.0/16"],
            "loadbalancer_ip_ranges": ["192.168.1.0/24"],
            "cluster_subnets": ["subnet-abc123"],
            "loadbalancer_subnets": ["subnet-def456"],
            "tags": {"team": "df-team"},
            "skip_preflight_checks": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    df_client.enable_service.assert_called_once()
    call_args = df_client.enable_service.call_args.kwargs
    assert call_args["min_k8s_node_count"] == 5
    assert call_args["max_k8s_node_count"] == 20
    assert call_args["use_public_load_balancer"] is True
    assert call_args["private_cluster"] is True
    assert call_args["kubernetes_ip_cidr_blocks"] == ["10.0.0.0/16"]
    assert call_args["load_balancer_ip_cidr_blocks"] == ["192.168.1.0/24"]
    assert call_args["cluster_subnet_ids"] == ["subnet-abc123"]
    assert call_args["load_balancer_subnet_ids"] == ["subnet-def456"]
    assert call_args["tags"] == {"team": "df-team"}
    assert call_args["skip_preflight_checks"] is True


def test_present_enable_check_mode(df_module_args, df_client):
    """check_mode reports changed without enabling the service."""
    df_client.get_service_by_env_crn.return_value = None

    df_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service == {}
    df_client.enable_service.assert_not_called()
    df_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Update tests
# ============================================================================


def test_present_idempotent(df_module_args, df_client, mocker):
    """A service already matching the desired state reports no change."""
    df_client.get_service_by_env_crn.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {}

    df_module_args({"nodes_min": 3, "nodes_max": 3})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False
    assert result.value.service["crn"] == SERVICE_CRN

    check_updates.assert_called_once()
    df_client.enable_service.assert_not_called()
    df_client.update_service.assert_not_called()


def test_reconcile_update(df_module_args, df_client, mocker):
    """A reconcilable difference triggers update_service with those params."""
    existing = _existing_service()
    df_client.get_service_by_env_crn.return_value = existing

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "min_k8s_node_count": 5,
        "max_k8s_node_count": 15,
    }
    df_client.update_service.return_value = _existing_service(
        min_k8s_node_count=5,
        max_k8s_node_count=15,
    )

    df_module_args({"nodes_min": 5, "nodes_max": 15})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    check_updates.assert_called_once()
    check_args = check_updates.call_args.kwargs
    assert check_args["service_crn"] == SERVICE_CRN
    assert check_args["service_details"] == existing
    assert check_args["min_k8s_node_count"] == 5
    assert check_args["max_k8s_node_count"] == 15

    df_client.update_service.assert_called_once_with(
        service_crn=SERVICE_CRN,
        min_k8s_node_count=5,
        max_k8s_node_count=15,
    )
    df_client.wait_for_service_state.assert_not_called()
    assert result.value.service["minK8sNodeCount"] == 5
    assert result.value.service["maxK8sNodeCount"] == 15


def test_reconcile_update_with_wait(df_module_args, df_client, mocker):
    """Updating with wait polls to GOOD_HEALTH."""
    df_client.get_service_by_env_crn.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "max_k8s_node_count": 15,
    }
    df_client.update_service.return_value = _existing_service(
        state="UPDATING",
        max_k8s_node_count=15,
    )
    df_client.wait_for_service_state.return_value = _existing_service(
        state="GOOD_HEALTH",
        max_k8s_node_count=15,
    )

    df_module_args({"nodes_max": 15, "wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["status"]["state"] == "GOOD_HEALTH"
    assert result.value.service["maxK8sNodeCount"] == 15

    df_client.update_service.assert_called_once()
    df_client.wait_for_service_state.assert_called_once()
    wait_args = df_client.wait_for_service_state.call_args.kwargs
    assert wait_args["service_crn"] == SERVICE_CRN
    assert wait_args["target_states"] == ["GOOD_HEALTH"]


def test_reconcile_update_check_mode(df_module_args, df_client, mocker):
    """check_mode reports changed without calling update_service."""
    df_client.get_service_by_env_crn.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "max_k8s_node_count": 15,
    }

    df_module_args({"nodes_max": 15, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN

    check_updates.assert_called_once()
    df_client.update_service.assert_not_called()
    df_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Disable tests
# ============================================================================


def test_absent_disable(df_module_args, df_client):
    """state=absent without wait disables the service directly."""
    df_client.get_service_by_crn.return_value = _existing_service()

    df_module_args({"df_crn": SERVICE_CRN, "state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    df_client.disable_service.assert_called_once()
    call_args = df_client.disable_service.call_args.kwargs
    assert call_args["crn"] == SERVICE_CRN
    assert call_args["terminate_deployments"] is False

    df_client.wait_for_service_state.assert_not_called()


def test_absent_disable_with_terminate(df_module_args, df_client):
    """state=absent with terminate=True passes terminate_deployments through."""
    df_client.get_service_by_crn.return_value = _existing_service()

    df_module_args(
        {
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "terminate": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    df_client.disable_service.assert_called_once()
    call_args = df_client.disable_service.call_args.kwargs
    assert call_args["terminate_deployments"] is True


def test_absent_disable_with_wait(df_module_args, df_client):
    """state=absent with wait polls to DISABLED_STATES."""
    df_client.get_service_by_crn.return_value = _existing_service()
    df_client.wait_for_service_state.return_value = _existing_service(
        state="NOT_ENABLED",
    )

    df_module_args(
        {
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "wait": True,
            "terminate": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["status"]["state"] == "NOT_ENABLED"

    df_client.disable_service.assert_not_called()
    df_client.wait_for_service_state.assert_called_once()
    wait_args = df_client.wait_for_service_state.call_args.kwargs
    assert wait_args["service_crn"] == SERVICE_CRN
    assert wait_args["target_states"] == CdpDfClient.DISABLED_STATES
    assert wait_args["terminate_deployments"] is True


def test_absent_force_reset(df_module_args, df_client):
    """state=absent with force=True on an already-disabled service calls reset_service."""
    df_client.get_service_by_crn.return_value = _existing_service(state="NOT_ENABLED")

    df_module_args(
        {
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "force": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True

    df_client.reset_service.assert_called_once_with(crn=SERVICE_CRN)
    df_client.disable_service.assert_not_called()


def test_absent_check_mode(df_module_args, df_client):
    """check_mode reports changed without disabling the service."""
    df_client.get_service_by_crn.return_value = _existing_service()

    df_module_args(
        {
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is True
    assert result.value.service["crn"] == SERVICE_CRN

    df_client.disable_service.assert_not_called()
    df_client.wait_for_service_state.assert_not_called()


def test_absent_noop(df_module_args, df_client):
    """state=absent is a no-op when the service does not exist."""
    df_client.get_service_by_crn.return_value = None

    df_module_args({"df_crn": SERVICE_CRN, "state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.changed is False
    assert result.value.service == {}

    df_client.disable_service.assert_not_called()
    df_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Diff tests
# ============================================================================


def test_create_reports_diff(df_module_args, df_client):
    """Creating a service populates diff.after under --diff (check_mode)."""
    df_client.get_service_by_env_crn.return_value = None

    df_module_args({"_ansible_check_mode": True, "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "environmentCrn": ENV_CRN,
        "status": {"state": "ENABLING"},
    }


def test_reconcile_reports_diff(df_module_args, df_client, mocker):
    """Reconciling reports before/after under --diff."""
    df_client.get_service_by_env_crn.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service.check_service_updates",
    )
    check_updates.return_value = {
        "service_crn": SERVICE_CRN,
        "max_k8s_node_count": 15,
    }

    df_module_args(
        {
            "nodes_max": 15,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.diff["before"]["crn"] == SERVICE_CRN
    assert result.value.diff["after"]["max_k8s_node_count"] == 15


def test_absent_reports_diff(df_module_args, df_client):
    """Disabling reports the service representation in diff.before."""
    df_client.get_service_by_crn.return_value = _existing_service()

    df_module_args(
        {
            "df_crn": SERVICE_CRN,
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service.main()

    assert result.value.diff["before"]["crn"] == SERVICE_CRN
