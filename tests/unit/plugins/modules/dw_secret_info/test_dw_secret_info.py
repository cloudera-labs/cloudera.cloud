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
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cloudera.cloud.plugins.modules import dw_secret_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    DwSecret,
    DwSecretProperties,
)

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

MOCK_SECRETS = [
    DwSecret(
        secretName="secret-one",
        secretProviderKey="key-one",
        createdBy="crn:cdp:iam:us-west-1:account:user:user1",
        properties=DwSecretProperties(cloudProvider="AWS"),
    ),
    DwSecret(
        secretName="secret-two",
        secretProviderKey="key-two",
        createdBy="crn:cdp:iam:us-west-1:account:user:user2",
        properties=DwSecretProperties(azureVaultName="my-vault", cloudProvider="AZURE"),
    ),
]


@pytest.fixture
def mock_client(mocker):
    """Patch load_cdp_config and return the CdpDwClient mock."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.dw_secret_info.CdpDwClient",
        autospec=True,
    ).return_value
    return client


def test_cluster_id_required(module_args):
    """Module fails with AnsibleFailJson when cluster_id is not provided."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    with pytest.raises(AnsibleFailJson):
        dw_secret_info.main()


def test_list_all_secrets(module_args, mock_client):
    """Module returns all secrets when no name filter is provided."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": "env-abc123",
        },
    )

    client = mock_client
    client.list_secrets.return_value = MOCK_SECRETS

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret_info.main()

    assert result.value.changed is False
    assert len(result.value.secrets) == 2
    assert result.value.secrets[0]["secretName"] == "secret-one"
    assert result.value.secrets[1]["secretName"] == "secret-two"

    client.list_secrets.assert_called_once_with("env-abc123")


def test_name_filter_exact_match(module_args, mock_client):
    """Module returns only the secret whose secretName matches the name param."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": "env-abc123",
            "name": "secret-one",
        },
    )

    client = mock_client
    client.list_secrets.return_value = MOCK_SECRETS

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret_info.main()

    assert result.value.changed is False
    assert len(result.value.secrets) == 1
    assert result.value.secrets[0]["secretName"] == "secret-one"


def test_name_filter_no_match(module_args, mock_client):
    """Module returns empty list when name filter matches no secrets."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": "env-abc123",
            "name": "does-not-exist",
        },
    )

    client = mock_client
    client.list_secrets.return_value = MOCK_SECRETS

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret_info.main()

    assert result.value.changed is False
    assert result.value.secrets == []


def test_empty_api_result(module_args, mock_client):
    """Module returns empty list when the API returns no secrets."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": "env-abc123",
        },
    )

    client = mock_client
    client.list_secrets.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        dw_secret_info.main()

    assert result.value.changed is False
    assert result.value.secrets == []
