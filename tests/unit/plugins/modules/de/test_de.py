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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import de


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

SERVICE_NAME = "test-de-service"
ENV_NAME = "test-environment"
CLUSTER_ID = "cluster-abc-123"
INSTANCE_TYPE = "r5.2xlarge"


def _patch_common(mocker):
    """Patch load_cdp_config and return the mocked CdpDeClient instance."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.CdpDeClient",
        autospec=True,
    ).return_value

    return client


def _patch_common_with_class(mocker):
    """Patch load_cdp_config and return both the CdpDeClient class mock and its instance."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    mock_client_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.CdpDeClient",
        autospec=True,
    )
    return mock_client_class, mock_client_class.return_value


def _existing_service(
    status="ClusterCreationCompleted",
    min_instances="1",
    max_instances="2",
    min_spot_instances="0",
    max_spot_instances="0",
):
    return {
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
    }


# ============================================================================
# Enable tests
# ============================================================================


def test_de_service_enable_success(module_args, mocker):
    """Test enabling a CDE service successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": False,
        },
    )

    client = _patch_common(mocker)
    client.get_service_by_name.return_value = None
    client.enable_service.return_value = {
        "service": _existing_service(),
    }

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["name"] == SERVICE_NAME
    assert result.value.service["clusterId"] == CLUSTER_ID

    client.enable_service.assert_called_once()
    call_args = client.enable_service.call_args[1]
    assert call_args["name"] == SERVICE_NAME
    assert call_args["env"] == ENV_NAME
    assert call_args["instance_type"] == INSTANCE_TYPE
    assert call_args["minimum_instances"] == 1
    assert call_args["maximum_instances"] == 2
    assert call_args["minimum_spot_instances"] == 0
    assert call_args["maximum_spot_instances"] == 0

    client.wait_for_service_state.assert_not_called()


def test_de_service_enable_with_wait(module_args, mocker):
    """Test enabling a CDE service with wait enabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    mock_client_class, client = _patch_common_with_class(mocker)
    mock_client_class.REMOVABLE_STATUSES = ["ClusterCreationCompleted"]

    client.get_service_by_name.return_value = None
    client.enable_service.return_value = {
        "service": _existing_service(status="ClusterCreationInProgress"),
    }
    client.wait_for_service_state.return_value = _existing_service()

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["status"] == "ClusterCreationCompleted"

    client.enable_service.assert_called_once()
    client.wait_for_service_state.assert_called_once()
    wait_args = client.wait_for_service_state.call_args[1]
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == ["ClusterCreationCompleted"]


def test_de_service_enable_check_mode(module_args, mocker):
    """Test enabling a CDE service in check mode — changed=True but no API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    client = _patch_common(mocker)
    client.get_service_by_name.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service == {}
    client.enable_service.assert_not_called()
    client.wait_for_service_state.assert_not_called()


def test_de_service_enable_with_custom_params(module_args, mocker):
    """Test enabling a CDE service with optional parameters passed through correctly."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "enable_public_endpoint": False,
            "enable_workload_analytics": False,
            "whitelist_ips": ["10.0.0.0/8"],
            "loadbalancer_ips": ["192.168.0.0/16"],
            "tags": {"team": "de-team"},
            "skip_validation": True,
            "root_volume_size": 200,
            "state": "present",
            "wait": False,
        },
    )

    client = _patch_common(mocker)
    client.get_service_by_name.return_value = None
    client.enable_service.return_value = {
        "service": _existing_service(),
    }

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    client.enable_service.assert_called_once()
    call_args = client.enable_service.call_args[1]
    assert call_args["enable_public_endpoint"] is False
    assert call_args["enable_workload_analytics"] is False
    assert call_args["whitelist_ips"] == ["10.0.0.0/8"]
    assert call_args["loadbalancer_allowlist"] == ["192.168.0.0/16"]
    assert call_args["tags"] == {"team": "de-team"}
    assert call_args["skip_validation"] is True
    assert call_args["root_volume_size"] == 200


# ============================================================================
# Update tests
# ============================================================================


def test_de_service_already_enabled(module_args, mocker):
    """Test that no changes are made when service config already matches."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": False,
        },
    )

    client = _patch_common(mocker)
    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service["clusterId"] == CLUSTER_ID

    check_updates.assert_called_once()
    client.enable_service.assert_not_called()
    client.update_service.assert_not_called()


def test_de_service_update_success(module_args, mocker):
    """Test updating an existing CDE service's instance counts."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 3,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": False,
        },
    )

    client = _patch_common(mocker)
    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }

    client.update_service.return_value = _existing_service(max_instances="3")

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    check_updates.assert_called_once()
    check_args = check_updates.call_args[1]
    assert check_args["cluster_id"] == CLUSTER_ID
    assert check_args["service_details"] == existing
    assert check_args["minimum_instances"] == 1
    assert check_args["maximum_instances"] == 3
    assert check_args["minimum_spot_instances"] == 0
    assert check_args["maximum_spot_instances"] == 0

    client.update_service.assert_called_once()
    client.wait_for_service_state.assert_not_called()


def test_de_service_update_with_wait(module_args, mocker):
    """Test updating a CDE service with wait enabled."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 3,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    mock_client_class, client = _patch_common_with_class(mocker)
    mock_client_class.REMOVABLE_STATUSES = ["ClusterCreationCompleted"]

    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }

    client.update_service.return_value = _existing_service(
        status="ClusterCreationInProgress",
        max_instances="3",
    )
    client.wait_for_service_state.return_value = _existing_service(max_instances="3")

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["resources"]["max_instances"] == "3"

    client.update_service.assert_called_once()
    client.wait_for_service_state.assert_called_once()
    wait_args = client.wait_for_service_state.call_args[1]
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == ["ClusterCreationCompleted"]


def test_de_service_update_check_mode(module_args, mocker):
    """Test updating a CDE service in check mode — changed=True but update_service not called."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 3,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    client = _patch_common(mocker)
    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {
        "cluster_id": CLUSTER_ID,
        "maximum_instances": 3,
    }

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["clusterId"] == CLUSTER_ID

    check_updates.assert_called_once()
    client.update_service.assert_not_called()
    client.wait_for_service_state.assert_not_called()


def test_de_service_update_no_changes(module_args, mocker):
    """Test that update_service is not called when check_service_updates returns no changes."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "instance_type": INSTANCE_TYPE,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    client = _patch_common(mocker)
    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    check_updates = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de.check_service_updates",
    )
    check_updates.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service["clusterId"] == CLUSTER_ID

    check_updates.assert_called_once()
    client.update_service.assert_not_called()
    client.wait_for_service_state.assert_not_called()


# ============================================================================
# Disable tests
# ============================================================================


def test_de_service_disable_success(module_args, mocker):
    """Test disabling a CDE service without wait."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": False,
            "force": False,
        },
    )

    client = _patch_common(mocker)
    client.get_service_by_name.return_value = {"service": _existing_service()}
    client.disable_service.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    client.disable_service.assert_called_once()
    call_args = client.disable_service.call_args
    assert call_args[0][0] == CLUSTER_ID
    assert call_args[1]["force"] is False

    client.wait_for_service_state.assert_not_called()


def test_de_service_disable_with_wait(module_args, mocker):
    """Test disabling a CDE service with wait — uses wait_for_service_state with STOPPED_STATUSES."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": True,
            "force": False,
        },
    )

    mock_client_class, client = _patch_common_with_class(mocker)
    mock_client_class.STOPPED_STATUSES = ["ClusterDeletionCompleted"]

    client.get_service_by_name.return_value = {"service": _existing_service()}
    client.wait_for_service_state.return_value = _existing_service(
        status="ClusterDeletionCompleted",
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["status"] == "ClusterDeletionCompleted"

    client.wait_for_service_state.assert_called_once()
    wait_args = client.wait_for_service_state.call_args[1]
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["target_statuses"] == ["ClusterDeletionCompleted"]
    assert wait_args["force"] is False

    client.disable_service.assert_not_called()


def test_de_service_disable_with_wait_returns_none(module_args, mocker):
    """Test that service={} when wait_for_service_state returns None (service fully gone)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": True,
            "force": False,
        },
    )

    mock_client_class, client = _patch_common_with_class(mocker)
    mock_client_class.STOPPED_STATUSES = ["ClusterDeletionCompleted"]

    client.get_service_by_name.return_value = {"service": _existing_service()}
    client.wait_for_service_state.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service == {}


def test_de_service_disable_check_mode(module_args, mocker):
    """Test disabling a CDE service in check mode — changed=True but no API calls."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    client = _patch_common(mocker)
    existing = _existing_service()
    client.get_service_by_name.return_value = {"service": existing}

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service["clusterId"] == CLUSTER_ID

    client.disable_service.assert_not_called()
    client.wait_for_service_state.assert_not_called()


def test_de_service_disable_already_disabled(module_args, mocker):
    """Test that no changes are made when service does not exist and state=absent."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
            "environment": ENV_NAME,
            "state": "absent",
            "wait": False,
        },
    )

    client = _patch_common(mocker)
    client.get_service_by_name.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service == {}

    client.disable_service.assert_not_called()
    client.wait_for_service_state.assert_not_called()
