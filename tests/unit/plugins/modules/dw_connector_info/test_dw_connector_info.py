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

from ansible_collections.cloudera.cloud.plugins.modules import (
    dw_connector_info,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import Connector
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "example-cluster-id"

CONNECTOR_1 = Connector(
    id="connector-1",
    name="connector-1",
    template="hive",
    crn="crn:cdp:dw:us-west-1:tenant:connector:connector-1",
    description="Test connector 1",
    config={"key": "value"},
    createdAt=1234567890,
    createdBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
    updatedAt=1234567890,
    updatedBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
)

CONNECTOR_2 = Connector(
    id="connector-2",
    name="connector-2",
    template="iceberg",
    crn="crn:cdp:dw:us-west-1:tenant:connector:connector-2",
    description="Test connector 2",
    config={"key2": "value2"},
    createdAt=1234567890,
    createdBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
    updatedAt=1234567890,
    updatedBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
)


def test_list_all_connectors(module_args, mocker):
    """Test listing all connectors in a cluster."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.list_connectors.return_value = [CONNECTOR_1, CONNECTOR_2]

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 2
    assert result.value.connectors[0]["id"] == "connector-1"
    assert result.value.connectors[1]["id"] == "connector-2"
    client.list_connectors.assert_called_once_with(CLUSTER_ID)


def test_list_connectors_empty(module_args, mocker):
    """Test listing connectors when none exist."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.list_connectors.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 0


def test_get_connector_by_id(module_args, mocker):
    """Test getting connector by ID."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "connector_id": "connector-1",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.get_connector_by_id.return_value = CONNECTOR_1

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 1
    assert result.value.connectors[0]["id"] == "connector-1"


def test_get_connector_by_id_not_found(module_args, mocker):
    """Test getting connector by ID when it doesn't exist."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "connector_id": "nonexistent-id",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.get_connector_by_id.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 0


def test_get_connector_by_name(module_args, mocker):
    """Test getting connector by name."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "name": "connector-2",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.get_connector_by_name.return_value = CONNECTOR_2

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 1
    assert result.value.connectors[0]["name"] == "connector-2"


def test_get_connector_by_name_not_found(module_args, mocker):
    """Test getting connector by name when it doesn't exist."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "name": "nonexistent-name",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    # Patch CdpDwClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector_info.CdpDwClient",
        autospec=True,
    ).return_value

    client.get_connector_by_name.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector_info.main()

    assert result.value.changed is False
    assert len(result.value.connectors) == 0


def test_mutually_exclusive_connector_id_and_name(module_args, mocker):
    """Test that connector_id and name are mutually exclusive."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": CLUSTER_ID,
            "connector_id": "connector-1",
            "name": "connector-1",
        },
    )

    # Patch load_cdp_config
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    ).return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    with pytest.raises(AnsibleFailJson):
        dw_connector_info.main()
