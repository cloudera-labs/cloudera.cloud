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
)

from ansible_collections.cloudera.cloud.plugins.modules import env_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"

SAMPLE_ENV = {
    "environmentName": ENV_NAME,
    "crn": ENV_CRN,
    "status": "AVAILABLE",
    "cloudPlatform": "AWS",
    "credentialName": "test-credential",
}


def _patch_config(mocker):
    """Patch load_cdp_config to avoid reading real credential files."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    return config


def test_env_info_list_all(module_args, mocker):
    """Test env_info with no name returns all environments from list_environments."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    _patch_config(mocker)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value

    client.list_environments.return_value = [
        {
            "environmentName": "env-1",
            "crn": "crn:cdp:environments:us-west-1:tenant:environment:env-1",
            "status": "AVAILABLE",
        },
        {
            "environmentName": "env-2",
            "crn": "crn:cdp:environments:us-west-1:tenant:environment:env-2",
            "status": "AVAILABLE",
        },
    ]

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert len(result.value.environments) == 2
    assert result.value.environments[0]["environmentName"] == "env-1"
    assert result.value.environments[1]["environmentName"] == "env-2"

    client.list_environments.assert_called_once()
    client.describe_environment.assert_not_called()


def test_env_info_by_name(module_args, mocker):
    """Test env_info with a name calls describe_environment and returns a single result."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ENV_NAME,
        },
    )

    _patch_config(mocker)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value

    client.describe_environment.return_value = SAMPLE_ENV

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert len(result.value.environments) == 1
    assert result.value.environments[0]["environmentName"] == ENV_NAME
    assert result.value.environments[0]["crn"] == ENV_CRN

    client.describe_environment.assert_called_once_with(ENV_NAME)
    client.list_environments.assert_not_called()


def test_env_info_by_name_not_found(module_args, mocker):
    """Test env_info returns an empty list when the named environment is not found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-env",
        },
    )

    _patch_config(mocker)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value

    client.describe_environment.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert result.value.environments == []

    client.describe_environment.assert_called_once_with("nonexistent-env")


def test_env_info_list_empty(module_args, mocker):
    """Test env_info returns an empty list when no environments exist."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    _patch_config(mocker)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value

    client.list_environments.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert result.value.environments == []


def test_env_info_with_descendants(module_args, mocker):
    """Test env_info with descendants=True calls ML, DE, and DF clients.
    datahub, dw, and opdb are expected to return empty lists (pending migration).
    """

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "descendants": True,
        },
    )

    _patch_config(mocker)

    env_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value
    env_client.list_environments.return_value = [SAMPLE_ENV]

    ml_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpMlClient",
        autospec=True,
    ).return_value
    ml_client.describe_all_workspaces.return_value = [
        {"workspaceName": "ml-ws-1", "environmentName": ENV_NAME},
    ]

    de_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpDeClient",
        autospec=True,
    ).return_value
    de_client.list_services.return_value = {
        "services": [
            {"clusterId": "de-123", "name": "de-svc-1", "environmentName": ENV_NAME},
        ],
    }

    df_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpDfClient",
        autospec=True,
    ).return_value
    df_client.list_services.return_value = {
        "services": [
            {"crn": "crn:df:svc:1", "name": "df-svc-1", "environmentCrn": ENV_CRN},
            # This service belongs to a different environment and should be filtered out
            {"crn": "crn:df:svc:2", "name": "df-svc-2", "environmentCrn": "crn:other"},
        ],
    }

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert len(result.value.environments) == 1

    desc = result.value.environments[0]["descendants"]

    # ML and DE and DF should be populated from their respective clients
    assert len(desc["ml"]) == 1
    assert desc["ml"][0]["workspaceName"] == "ml-ws-1"

    assert len(desc["de"]) == 1
    assert desc["de"][0]["clusterId"] == "de-123"

    assert len(desc["df"]) == 1
    assert desc["df"][0]["name"] == "df-svc-1"

    # datahub, dw, opdb are pending migration — must be empty lists
    assert desc["datahub"] == []
    assert desc["dw"] == []
    assert desc["opdb"] == []

    # Verify correct client calls
    ml_client.describe_all_workspaces.assert_called_once_with(env=ENV_NAME)
    de_client.list_services.assert_called_once_with(
        remove_deleted=True, env_name=ENV_NAME
    )
    df_client.list_services.assert_called_once()


def test_env_info_descendants_skipped_when_no_envs(module_args, mocker):
    """Test that descendant lookups are skipped entirely when no environments are found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "descendants": True,
        },
    )

    _patch_config(mocker)

    env_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpEnvClient",
        autospec=True,
    ).return_value
    env_client.list_environments.return_value = []

    ml_client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.env_info.CdpMlClient",
        autospec=True,
    ).return_value

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert result.value.environments == []

    # Descendant clients must not be called when there are no environments
    ml_client.describe_all_workspaces.assert_not_called()
