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
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
    ConnectorTestJob,
    DwSecret,
    DwSecretProperties,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    NULLABLE,
    from_dict,
    to_dict,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

CLUSTER_ID = "cluster-abc123"
CONNECTOR_ID = "connector-xyz789"
CONNECTOR_NAME = "test-connector"


def test_list_connectors_success(mocker):
    """Test listing all connectors in a cluster returns Connector dataclass instances."""

    mock_response = {
        "connectors": [
            {
                "id": "connector-1",
                "name": "connector-1",
                "template": "hive",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-1",
            },
            {
                "id": "connector-2",
                "name": "connector-2",
                "template": "iceberg",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-2",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.list_connectors(CLUSTER_ID)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(c, Connector) for c in result)
    assert result[0].id == "connector-1"
    assert result[1].name == "connector-2"

    api_client.post.assert_called_once_with(
        "/api/v1/dw/listConnectors",
        data={"clusterId": CLUSTER_ID},
        squelch={404: {"connectors": []}},
    )


def test_list_connectors_empty(mocker):
    """Test listing connectors when none exist returns an empty list."""

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = {"connectors": []}

    client = CdpDwClient(api_client=api_client)
    result = client.list_connectors(CLUSTER_ID)

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_connector_by_id_found(mocker):
    """Test getting connector details by ID returns a Connector dataclass."""

    mock_response = {
        "connectors": [
            {
                "id": CONNECTOR_ID,
                "name": CONNECTOR_NAME,
                "template": "hive",
                "crn": f"crn:cdp:dw:us-west-1:tenant:connector:{CONNECTOR_ID}",
            },
            {
                "id": "connector-other",
                "name": "other-connector",
                "template": "iceberg",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-other",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.get_connector_by_id(CLUSTER_ID, CONNECTOR_ID)

    assert result is not None
    assert isinstance(result, Connector)
    assert result.id == CONNECTOR_ID
    assert result.name == CONNECTOR_NAME


def test_get_connector_by_id_not_found(mocker):
    """Test getting connector by ID when it doesn't exist returns None."""

    mock_response = {
        "connectors": [
            {
                "id": "connector-1",
                "name": "connector-1",
                "template": "hive",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-1",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.get_connector_by_id(CLUSTER_ID, "nonexistent-id")

    assert result is None


def test_get_connector_by_name_found(mocker):
    """Test getting connector details by name returns a Connector dataclass."""

    mock_response = {
        "connectors": [
            {
                "id": CONNECTOR_ID,
                "name": CONNECTOR_NAME,
                "template": "hive",
                "crn": f"crn:cdp:dw:us-west-1:tenant:connector:{CONNECTOR_ID}",
            },
            {
                "id": "connector-other",
                "name": "other-connector",
                "template": "iceberg",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-other",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.get_connector_by_name(CLUSTER_ID, CONNECTOR_NAME)

    assert result is not None
    assert isinstance(result, Connector)
    assert result.name == CONNECTOR_NAME
    assert result.id == CONNECTOR_ID


def test_get_connector_by_name_not_found(mocker):
    """Test getting connector by name when it doesn't exist returns None."""

    mock_response = {
        "connectors": [
            {
                "id": "connector-1",
                "name": "connector-1",
                "template": "hive",
                "crn": "crn:cdp:dw:us-west-1:tenant:connector:connector-1",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.get_connector_by_name(CLUSTER_ID, "nonexistent-name")

    assert result is None


def test_create_connector(mocker):
    """Test creating a connector returns a Connector dataclass instance."""

    mock_response = {
        "result": {
            "id": CONNECTOR_ID,
            "name": CONNECTOR_NAME,
            "template": "hive",
            "crn": f"crn:cdp:dw:us-west-1:tenant:connector:{CONNECTOR_ID}",
            "description": "My connector",
        },
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.create_connector(
        cluster_id=CLUSTER_ID,
        name=CONNECTOR_NAME,
        template="hive",
        description="My connector",
    )

    assert isinstance(result, Connector)
    assert result.id == CONNECTOR_ID
    assert result.name == CONNECTOR_NAME
    assert result.template == "hive"
    assert result.description == "My connector"

    api_client.post.assert_called_once_with(
        "/api/v1/dw/createConnector",
        data={
            "clusterId": CLUSTER_ID,
            "name": CONNECTOR_NAME,
            "template": "hive",
            "description": "My connector",
        },
    )


def test_update_connector(mocker):
    """Test updating a connector posts the correct payload and returns the updated Connector."""

    updated_connector = {
        "id": CONNECTOR_ID,
        "name": CONNECTOR_NAME,
        "template": "hive",
        "crn": f"crn:cdp:dw:us-west-1:tenant:connector:{CONNECTOR_ID}",
        "description": "Updated description",
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    # First call: updateConnector (empty response), second call: listConnectors (re-fetch)
    api_client.post.side_effect = [
        {},
        {"connectors": [updated_connector]},
    ]

    client = CdpDwClient(api_client=api_client)
    result = client.update_connector(
        cluster_id=CLUSTER_ID,
        connector_id=CONNECTOR_ID,
        name=CONNECTOR_NAME,
        description="Updated description",
        template="hive",
        config={"key": "value"},
    )

    assert isinstance(result, Connector)
    assert result.id == CONNECTOR_ID
    assert result.description == "Updated description"

    update_call, fetch_call = api_client.post.call_args_list
    assert update_call == mocker.call(
        "/api/v1/dw/updateConnector",
        data={
            "clusterId": CLUSTER_ID,
            "connectorId": CONNECTOR_ID,
            "name": CONNECTOR_NAME,
            "description": "Updated description",
            "template": "hive",
            "config": {"key": "value"},
        },
    )
    assert fetch_call == mocker.call(
        "/api/v1/dw/listConnectors",
        data={"clusterId": CLUSTER_ID},
        squelch={404: {"connectors": []}},
    )


def test_delete_connector(mocker):
    """Test deleting a connector posts the correct payload and returns None."""

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = {}

    client = CdpDwClient(api_client=api_client)
    result = client.delete_connector(
        cluster_id=CLUSTER_ID,
        connector_id=CONNECTOR_ID,
    )

    assert result is None

    api_client.post.assert_called_once_with(
        "/api/v1/dw/deleteConnector",
        data={
            "clusterId": CLUSTER_ID,
            "connectorId": CONNECTOR_ID,
        },
        squelch={404: {}},
    )


def test_create_connector_test_job(mocker):
    """Test creating a connector test job returns a job ID string."""

    job_id = "test-job-abc123"

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = {"jobId": job_id}

    client = CdpDwClient(api_client=api_client)
    result = client.create_connector_test_job(
        cluster_id=CLUSTER_ID,
        connector_id=CONNECTOR_ID,
    )

    assert isinstance(result, str)
    assert result == job_id

    api_client.post.assert_called_once_with(
        "/api/v1/dw/createConnectorTestJob",
        data={
            "clusterId": CLUSTER_ID,
            "connectorId": CONNECTOR_ID,
        },
    )


def test_list_connector_test_jobs(mocker):
    """Test listing connector test jobs returns ConnectorTestJob instances."""

    job_id = "test-job-abc123"

    mock_response = {
        "results": [
            {
                "jobId": job_id,
                "status": "Succeeded",
                "jobStartTime": "2026-01-01T00:00:00Z",
                "jobFinishTime": "2026-01-01T00:01:00Z",
                "outputLog": "Connection successful",
            },
        ],
    }

    api_client = mocker.create_autospec(CdpClient, instance=True)
    api_client.post.return_value = mock_response

    client = CdpDwClient(api_client=api_client)
    result = client.list_connector_test_jobs(
        cluster_id=CLUSTER_ID,
        job_id=job_id,
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], ConnectorTestJob)
    assert result[0].jobId == job_id
    assert result[0].status == "Succeeded"

    api_client.post.assert_called_once_with(
        "/api/v1/dw/listConnectorTestJobs",
        data={
            "clusterId": CLUSTER_ID,
            "jobId": job_id,
        },
        squelch={404: {"results": []}},
    )


class TestDwSecretProperties:
    """Unit tests for DwSecretProperties dataclass."""

    def test_defaults_are_nullable(self):
        """All optional fields default to NULLABLE sentinel."""
        props = DwSecretProperties()
        assert props.azureVaultName is NULLABLE
        assert props.cloudProvider is NULLABLE
        assert props.version is NULLABLE

    def test_from_dict_populates_fields(self):
        """from_dict correctly populates DwSecretProperties fields."""
        data = {
            "azureVaultName": "my-vault",
            "cloudProvider": "AZURE",
            "version": "1",
        }
        props = from_dict(DwSecretProperties, data)
        assert props.azureVaultName == "my-vault"
        assert props.cloudProvider == "AZURE"
        assert props.version == "1"

    def test_from_dict_partial_fields(self):
        """from_dict handles partial data, leaving unset fields as NULLABLE."""
        data = {"cloudProvider": "AWS"}
        props = from_dict(DwSecretProperties, data)
        assert props.cloudProvider == "AWS"
        assert props.azureVaultName is NULLABLE
        assert props.version is NULLABLE

    def test_to_dict_excludes_nullable(self):
        """to_dict omits NULLABLE fields from output."""
        props = DwSecretProperties(cloudProvider="AWS")
        result = to_dict(props)
        assert result == {"cloudProvider": "AWS"}
        assert "azureVaultName" not in result
        assert "version" not in result


class TestDwSecret:
    """Unit tests for DwSecret dataclass."""

    def test_defaults_are_nullable(self):
        """All optional fields default to NULLABLE sentinel."""
        secret = DwSecret()
        assert secret.secretName is NULLABLE
        assert secret.secretProviderKey is NULLABLE
        assert secret.createdBy is NULLABLE
        assert secret.properties is NULLABLE

    def test_from_dict_flat_fields(self):
        """from_dict correctly populates flat DwSecret fields."""
        data = {
            "secretName": "db-password",
            "secretProviderKey": "db-password-key",
            "createdBy": "crn:cdp:iam:us-west-1:account:user:user1",
        }
        secret = from_dict(DwSecret, data)
        assert secret.secretName == "db-password"
        assert secret.secretProviderKey == "db-password-key"
        assert secret.createdBy == "crn:cdp:iam:us-west-1:account:user:user1"

    def test_from_dict_with_nested_properties(self):
        """from_dict correctly populates nested DwSecretProperties."""
        data = {
            "secretName": "azure-secret",
            "properties": {
                "azureVaultName": "my-vault",
                "cloudProvider": "AZURE",
                "version": "2",
            },
        }
        secret = from_dict(DwSecret, data)
        assert secret.secretName == "azure-secret"
        assert isinstance(secret.properties, DwSecretProperties)
        assert secret.properties.azureVaultName == "my-vault"
        assert secret.properties.cloudProvider == "AZURE"
        assert secret.properties.version == "2"

    def test_to_dict_round_trip(self):
        """to_dict produces clean dict with no NULLABLE values."""
        secret = DwSecret(
            secretName="my-secret",
            secretProviderKey="my-key",
            properties=DwSecretProperties(cloudProvider="AWS"),
        )
        result = to_dict(secret)
        assert result["secretName"] == "my-secret"
        assert result["secretProviderKey"] == "my-key"
        assert result["properties"] == {"cloudProvider": "AWS"}
        assert "createdBy" not in result


class TestCdpDwClientListSecrets:
    """Unit tests for CdpDwClient.list_secrets."""

    def test_list_secrets_returns_dw_secret_list(self, mocker):
        """list_secrets returns a List[DwSecret] from API result."""
        mock_response = {
            "result": [
                {
                    "secretName": "secret-one",
                    "secretProviderKey": "key-one",
                    "createdBy": "crn:cdp:iam:us-west-1:account:user:user1",
                    "properties": {"cloudProvider": "AWS"},
                },
                {
                    "secretName": "secret-two",
                    "secretProviderKey": "key-two",
                    "createdBy": "crn:cdp:iam:us-west-1:account:user:user2",
                    "properties": {"azureVaultName": "vault", "cloudProvider": "AZURE"},
                },
            ],
        }

        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = mock_response

        client = CdpDwClient(api_client=api_client)
        result = client.list_secrets("env-abc123")

        assert len(result) == 2
        assert isinstance(result[0], DwSecret)
        assert result[0].secretName == "secret-one"
        assert result[1].secretName == "secret-two"

        api_client.post.assert_called_once_with(
            "/api/v1/dw/listSecrets",
            json_data={"clusterId": "env-abc123"},
        )

    def test_list_secrets_empty_result_key(self, mocker):
        """list_secrets returns [] when result key is an empty list."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {"result": []}

        client = CdpDwClient(api_client=api_client)
        result = client.list_secrets("env-abc123")

        assert result == []

    def test_list_secrets_missing_result_key(self, mocker):
        """list_secrets returns [] when result key is absent from response."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.return_value = {}

        client = CdpDwClient(api_client=api_client)
        result = client.list_secrets("env-abc123")

        assert result == []

    def test_list_secrets_api_error_propagates(self, mocker):
        """list_secrets propagates exceptions raised by the API client."""
        api_client = mocker.create_autospec(CdpClient, instance=True)
        api_client.post.side_effect = Exception("API error")

        client = CdpDwClient(api_client=api_client)

        with pytest.raises(Exception, match="API error"):
            client.list_secrets("env-abc123")
