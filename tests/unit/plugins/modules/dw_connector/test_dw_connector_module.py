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

from ansible_collections.cloudera.cloud.plugins.modules import dw_connector
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import Connector
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "example-cluster-id"
CONNECTOR_ID = "connectorabc123"
CONNECTOR_NAME = "mytestconnector"

CONNECTOR_1 = Connector(
    id=CONNECTOR_ID,
    name=CONNECTOR_NAME,
    template="hive",
    crn=f"crn:cdp:dw:us-west-1:tenant:connector:{CONNECTOR_ID}",
    description="My test connector",
    config={"key": "value"},
    createdAt=1234567890,
    createdBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
    updatedAt=1234567890,
    updatedBy="crn:cdp:iam:us-west-1:tenant:user:test-user",
)


@pytest.fixture
def dw_connector_module_args(module_args):
    """Fixture to pre-populate common dw_connector module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
                "cluster_id": CLUSTER_ID,
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def dw_connector_client(mocker):
    """Fixture that patches load_cdp_config and CdpDwClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_connector.CdpDwClient",
        autospec=True,
    ).return_value


class TestDwConnectorModule:
    """Unit tests for the dw_connector module."""

    def test_missing_cluster_id(self, module_args):
        """Test that omitting cluster_id raises AnsibleFailJson."""
        module_args(
            {
                "endpoint": BASE_URL,
                "access_key": ACCESS_KEY,
                "private_key": PRIVATE_KEY,
                "name": CONNECTOR_NAME,
                "template": "hive",
            },
        )

        with pytest.raises(AnsibleFailJson, match="cluster_id"):
            dw_connector.main()

    @pytest.mark.parametrize(
        "invalid_name",
        ["my-connector", "my_connector", "my connector", "connector!"],
    )
    def test_invalid_connector_name(
        self,
        dw_connector_module_args,
        dw_connector_client,
        invalid_name,
    ):
        """Test that a name containing non-alphanumeric characters raises AnsibleFailJson."""
        dw_connector_module_args(
            {
                "name": invalid_name,
                "template": "hive",
                "state": "present",
            },
        )

        with pytest.raises(AnsibleFailJson, match="alphanumeric"):
            dw_connector.main()

    def test_absent_not_found(self, dw_connector_module_args, dw_connector_client):
        """Test state=absent when connector does not exist is a no-op."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "state": "absent",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = None

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is False
        assert result.value.connector == {}
        dw_connector_client.delete_connector.assert_not_called()

    def test_absent_found(self, dw_connector_module_args, dw_connector_client):
        """Test state=absent when connector exists deletes it."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "state": "absent",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        assert result.value.connector == {}
        dw_connector_client.delete_connector.assert_called_once_with(
            CLUSTER_ID,
            CONNECTOR_ID,
        )

    def test_present_creates(self, dw_connector_module_args, dw_connector_client):
        """Test state=present creates a new connector when none exists."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "description": "My test connector",
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = None
        dw_connector_client.create_connector.return_value = CONNECTOR_1

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        assert result.value.connector["id"] == CONNECTOR_ID
        assert result.value.connector["name"] == CONNECTOR_NAME
        dw_connector_client.create_connector.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            name=CONNECTOR_NAME,
            template="hive",
            description="My test connector",
            config=None,
        )

    def test_present_idempotent(self, dw_connector_module_args, dw_connector_client):
        """Test state=present is idempotent when connector matches desired state."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "description": "My test connector",
                "config": {"key": "value"},
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is False
        assert result.value.connector["id"] == CONNECTOR_ID
        dw_connector_client.update_connector.assert_not_called()
        dw_connector_client.create_connector.assert_not_called()

    def test_present_updates(self, dw_connector_module_args, dw_connector_client):
        """Test state=present updates the connector when a mutable field differs."""
        updated_connector = Connector(
            id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            template="hive",
            crn=CONNECTOR_1.crn,
            description="Updated description",
            config={"key": "value"},
        )

        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "description": "Updated description",
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1
        dw_connector_client.update_connector.return_value = updated_connector

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        assert result.value.connector["description"] == "Updated description"
        dw_connector_client.update_connector.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            connector_id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            description="Updated description",
            template="hive",
            config={"key": "value"},
        )
        dw_connector_client.get_connector_by_id.assert_not_called()

    def test_present_update_reports_diff(
        self,
        dw_connector_module_args,
        dw_connector_client,
    ):
        """Test state=present populates diff before/after for changed fields under --diff."""
        updated_connector = Connector(
            id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            template="hive",
            crn=CONNECTOR_1.crn,
            description="Updated description",
            config={"key": "value"},
        )

        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "description": "Updated description",
                "state": "present",
                "_ansible_diff": True,
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1
        dw_connector_client.update_connector.return_value = updated_connector

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        assert result.value.diff == {
            "before": {"description": "My test connector"},
            "after": {"description": "Updated description"},
        }

    def test_present_update_unset_config_defaults_to_empty(
        self,
        dw_connector_module_args,
        dw_connector_client,
    ):
        """A connector with no config sends config={} on update, never the NULLABLE sentinel."""
        existing = Connector(
            id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            template="hive",
            crn=CONNECTOR_1.crn,
            description="My test connector",
            # config intentionally left unset -> NULLABLE
        )

        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "description": "Updated description",
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = existing
        dw_connector_client.update_connector.return_value = existing

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        dw_connector_client.update_connector.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            connector_id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            description="Updated description",
            template="hive",
            config={},
        )

    def test_present_template_change_fails(
        self,
        dw_connector_module_args,
        dw_connector_client,
    ):
        """Test state=present fails when template differs (immutable field)."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "iceberg",  # CONNECTOR_1 has "hive"
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1

        with pytest.raises(AnsibleFailJson, match="immutable"):
            dw_connector.main()

    def test_present_create_requires_template(
        self,
        dw_connector_module_args,
        dw_connector_client,
    ):
        """Creating a new connector without template fails."""
        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = None

        with pytest.raises(AnsibleFailJson, match="template"):
            dw_connector.main()

        dw_connector_client.create_connector.assert_not_called()

    def test_present_update_without_template(
        self,
        dw_connector_module_args,
        dw_connector_client,
    ):
        """Updating an existing connector needs no template; the existing one is reused."""
        updated_connector = Connector(
            id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            template="hive",
            crn=CONNECTOR_1.crn,
            description="Updated description",
            config={"key": "value"},
        )

        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "description": "Updated description",
                "state": "present",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1
        dw_connector_client.update_connector.return_value = updated_connector

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        dw_connector_client.update_connector.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            connector_id=CONNECTOR_ID,
            name=CONNECTOR_NAME,
            description="Updated description",
            template="hive",
            config={"key": "value"},
        )

    def test_tested_state(self, dw_connector_module_args, dw_connector_client):
        """Test state=tested always runs a test job and returns test_job output."""
        job_id = "test-job-xyz789"

        dw_connector_module_args(
            {
                "name": CONNECTOR_NAME,
                "template": "hive",
                "state": "tested",
            },
        )

        dw_connector_client.get_connector_by_name.return_value = CONNECTOR_1
        dw_connector_client.create_connector_test_job.return_value = job_id

        with pytest.raises(AnsibleExitJson) as result:
            dw_connector.main()

        assert result.value.changed is True
        assert result.value.connector["id"] == CONNECTOR_ID
        assert result.value.test_job == {"jobId": job_id}
        dw_connector_client.create_connector_test_job.assert_called_once_with(
            cluster_id=CLUSTER_ID,
            connector_id=CONNECTOR_ID,
        )
