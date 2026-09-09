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

from ansible_collections.cloudera.cloud.plugins.modules import de
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
    ServiceDescription,
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

SERVICE_NAME = "test-de-service"
ENV_NAME = "test-environment"
CLUSTER_ID = "cluster-abc-123"
INSTANCE_TYPE = "r5.2xlarge"


@pytest.fixture
def de_module_args(module_args):
    """Pre-populate common DE module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "wait": False,
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def de_client(mocker):
    """Patch load_cdp_config and CdpDeClient, returning the mocked client.

    autospec replaces the class constants with mocks, so restore the real
    status lists the module reads (C(REMOVABLE_STATUSES), C(STOPPED_STATUSES)).
    """
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.CdpDeClient",
        autospec=True,
    )
    mock_class.REMOVABLE_STATUSES = CdpDeClient.REMOVABLE_STATUSES
    mock_class.STOPPED_STATUSES = CdpDeClient.STOPPED_STATUSES
    return mock_class.return_value


def _existing_service(
    status="ClusterCreationCompleted",
    min_instances="1",
    max_instances="2",
    min_spot_instances="0",
    max_spot_instances="0",
):
    return from_dict(
        ServiceDescription,
        {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "status": status,
            "environmentName": ENV_NAME,
            "resources": {
                "instance_type": INSTANCE_TYPE,
                "min_instances": min_instances,
                "max_instances": max_instances,
                "min_spot_instances": min_spot_instances,
                "max_spot_instances": max_spot_instances,
            },
        },
    )


# ============================================================================
# Enable tests
# ============================================================================


def test_present_enable(de_module_args, de_client):
    """A new service is enabled and its parameters are passed through."""
    de_client.get_service_by_name.return_value = None
    de_client.enable_service.return_value = _existing_service()

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["name"] == SERVICE_NAME
    assert result.value.service["clusterId"] == CLUSTER_ID

    de_client.enable_service.assert_called_once()
    call_args = de_client.enable_service.call_args.kwargs
    assert call_args["name"] == SERVICE_NAME
    assert call_args["env"] == ENV_NAME
    assert call_args["instance_type"] == INSTANCE_TYPE
    assert call_args["minimum_instances"] == 1
    assert call_args["maximum_instances"] == 2
    assert call_args["minimum_spot_instances"] == 0
    assert call_args["maximum_spot_instances"] == 0

    de_client.wait_for_service_state.assert_not_called()


def test_present_enable_with_wait(de_module_args, de_client):
    """Enabling with wait polls to REMOVABLE_STATUSES."""
    de_client.get_service_by_name.return_value = None
    de_client.enable_service.return_value = _existing_service(
        status="ClusterCreationInProgress",
    )
    de_client.wait_for_service_state.return_value = _existing_service()

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["status"] == "ClusterCreationCompleted"

    de_client.enable_service.assert_called_once()
    de_client.wait_for_service_state.assert_called_once()
    wait_args = de_client.wait_for_service_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == CdpDeClient.REMOVABLE_STATUSES


def test_present_enable_custom_params(de_module_args, de_client):
    """Optional enable parameters are passed through to the client."""
    de_client.get_service_by_name.return_value = None
    de_client.enable_service.return_value = _existing_service()

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "enable_public_endpoint": False,
            "enable_workload_analytics": False,
            "whitelist_ips": ["10.0.0.0/8"],
            "loadbalancer_ips": ["192.168.0.0/16"],
            "tags": {"team": "de-team"},
            "skip_validation": True,
            "root_volume_size": 200,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    de_client.enable_service.assert_called_once()
    call_args = de_client.enable_service.call_args.kwargs
    assert call_args["enable_public_endpoint"] is False
    assert call_args["enable_workload_analytics"] is False
    assert call_args["whitelist_ips"] == ["10.0.0.0/8"]
    assert call_args["loadbalancer_allowlist"] == ["192.168.0.0/16"]
    assert call_args["tags"] == {"team": "de-team"}
    assert call_args["skip_validation"] is True
    assert call_args["root_volume_size"] == 200


def test_present_enable_check_mode(de_module_args, de_client):
    """check_mode reports changed without enabling the service."""
    de_client.get_service_by_name.return_value = None

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service == {}
    de_client.enable_service.assert_not_called()
    de_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Update tests
# ============================================================================


def test_present_idempotent(de_module_args, de_client, mocker):
    """A service already matching the desired state reports no change."""
    de_client.get_service_by_name.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {}

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service["clusterId"] == CLUSTER_ID

    check_updates.assert_called_once()
    de_client.enable_service.assert_not_called()
    de_client.update_service.assert_not_called()


def test_reconcile_update(de_module_args, de_client, mocker):
    """A reconcilable difference triggers update_service with those params."""
    existing = _existing_service()
    de_client.get_service_by_name.return_value = existing

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }
    de_client.update_service.return_value = _existing_service(max_instances="3")

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 3,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    check_updates.assert_called_once()
    check_args = check_updates.call_args.kwargs
    assert check_args["cluster_id"] == CLUSTER_ID
    assert check_args["service_details"] == existing
    assert check_args["minimum_instances"] == 1
    assert check_args["maximum_instances"] == 3

    de_client.update_service.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        maximum_instances=3,
    )
    de_client.wait_for_service_state.assert_not_called()


def test_reconcile_update_with_wait(de_module_args, de_client, mocker):
    """Updating with wait polls to REMOVABLE_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }
    de_client.update_service.return_value = _existing_service(
        status="ClusterCreationInProgress",
        max_instances="3",
    )
    de_client.wait_for_service_state.return_value = _existing_service(max_instances="3")

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "maximum_instances": 3,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["resources"]["max_instances"] == "3"

    de_client.update_service.assert_called_once()
    de_client.wait_for_service_state.assert_called_once()
    wait_args = de_client.wait_for_service_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == CdpDeClient.REMOVABLE_STATUSES


def test_reconcile_update_check_mode(de_module_args, de_client, mocker):
    """check_mode reports changed without calling update_service."""
    de_client.get_service_by_name.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "maximum_instances": 3,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["clusterId"] == CLUSTER_ID

    check_updates.assert_called_once()
    de_client.update_service.assert_not_called()
    de_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Disable tests
# ============================================================================


def test_absent_disable(de_module_args, de_client):
    """state=absent without wait disables the service directly."""
    de_client.get_service_by_name.return_value = _existing_service()

    de_module_args({"state": "absent", "force": False})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    de_client.disable_service.assert_called_once()
    call_args = de_client.disable_service.call_args
    assert call_args[0][0] == CLUSTER_ID
    assert call_args.kwargs["force"] is False

    de_client.wait_for_service_state.assert_not_called()


def test_absent_disable_with_wait(de_module_args, de_client):
    """state=absent with wait polls to STOPPED_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.wait_for_service_state.return_value = _existing_service(
        status="ClusterDeletionCompleted",
    )

    de_module_args({"state": "absent", "wait": True, "force": False})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["status"] == "ClusterDeletionCompleted"

    de_client.disable_service.assert_called_once()
    disable_args = de_client.disable_service.call_args
    assert disable_args[0][0] == CLUSTER_ID
    assert disable_args.kwargs["force"] is False

    de_client.wait_for_service_state.assert_called_once()
    wait_args = de_client.wait_for_service_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == CdpDeClient.STOPPED_STATUSES


def test_absent_disable_wait_returns_none(de_module_args, de_client):
    """service is {} when the wait reports the service fully gone."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.wait_for_service_state.return_value = None

    de_module_args({"state": "absent", "wait": True, "force": False})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service == {}


def test_absent_check_mode(de_module_args, de_client):
    """check_mode reports changed without disabling the service."""
    de_client.get_service_by_name.return_value = _existing_service()

    de_module_args({"state": "absent", "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["clusterId"] == CLUSTER_ID

    de_client.disable_service.assert_not_called()
    de_client.wait_for_service_state.assert_not_called()


def test_absent_noop(de_module_args, de_client):
    """state=absent is a no-op when the service does not exist."""
    de_client.get_service_by_name.return_value = None

    de_module_args({"state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service == {}

    de_client.disable_service.assert_not_called()
    de_client.wait_for_service_state.assert_not_called()


# ============================================================================
# Diff tests
# ============================================================================


def test_create_reports_diff(de_module_args, de_client):
    """Creating a service populates diff.after under --diff (check_mode)."""
    de_client.get_service_by_name.return_value = None

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "name": SERVICE_NAME,
        "status": "ClusterCreationInProgress",
    }


def test_reconcile_reports_diff(de_module_args, de_client, mocker):
    """Reconciling reports before/after under --diff."""
    de_client.get_service_by_name.return_value = _existing_service()

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }

    de_module_args(
        {
            "instance_type": INSTANCE_TYPE,
            "maximum_instances": 3,
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.diff["before"]["clusterId"] == CLUSTER_ID
    assert result.value.diff["after"]["maximum_instances"] == 3


def test_absent_reports_diff(de_module_args, de_client):
    """Disabling reports the service representation in diff.before."""
    de_client.get_service_by_name.return_value = _existing_service()

    de_module_args({"state": "absent", "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.diff["before"]["clusterId"] == CLUSTER_ID
    assert result.value.diff["after"] == {}
