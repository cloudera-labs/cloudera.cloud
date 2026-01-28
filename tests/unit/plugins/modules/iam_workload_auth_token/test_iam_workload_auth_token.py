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

from ansible_collections.cloudera.cloud.plugins.modules import iam_workload_auth_token


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

SAMPLE_TOKEN = "eyJPbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.POstGetfAytaZS82wHcjoTyoqhMyxXiWdR7Nn7A29DNSl0EiXLdwJ6xC6AfgZWF1bOsS_TuYI3OG85AmiExREkrS6tDfTQ2B3WXlrr-wp5AokiRbz3_oB4OxG-W9KcEEbDRcZc0nH3L7LzYptiy1PtAylQGxHTWZXtGz4ht0bAecBgmpdgXMguEIcoqPJ1n3pIWk_dUZegpqx0Lka21H6XxUTxiy8OcaarA8zdnPUnV6AmNP3ecFawIFYdvJB_cm-GvpCSbr8G8y_Mllj8f4x9nBH8pQux89_6gUY618iYv7tuPWBFfEbLxtF2pZS6YC1aSfLQxeNe8djT9YjpvRZA"
SAMPLE_ENDPOINT = "https://sample.us-west-1.workload.cloudera.site/api"
SAMPLE_EXPIRE_AT = "2026-01-22T14:30:00.000Z"


def test_workload_auth_token_de(module_args, mocker):
    """Test generating workload auth token for DE workload."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DE",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_workload_auth_token.CdpIamClient",
        autospec=True,
    ).return_value
    # DE workload doesn't return endpointUrl
    client.generate_workload_auth_token.return_value = {
        "token": SAMPLE_TOKEN,
        "expireAt": SAMPLE_EXPIRE_AT,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] == SAMPLE_TOKEN
    assert result.value.workload_auth_token["expire_at"] == SAMPLE_EXPIRE_AT
    # endpoint_url should not be present for DE workload
    assert "endpoint_url" not in result.value.workload_auth_token

    # Verify CdpIamClient was called correctly
    client.generate_workload_auth_token.assert_called_once_with(
        workload_name="DE",
        environment_crn=None,
        exclude_groups=False,
    )


def test_workload_auth_token_df_with_environment(module_args, mocker):
    """Test generating workload auth token for DF workload with environment CRN."""

    environment_crn = "crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:environment:61eb5b97-226a-4be7-b56e-78d4e5d8c7e3"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DF",
            "environment_crn": environment_crn,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_workload_auth_token.CdpIamClient",
        autospec=True,
    ).return_value
    # DF workload returns endpointUrl
    client.generate_workload_auth_token.return_value = {
        "token": SAMPLE_TOKEN,
        "endpointUrl": SAMPLE_ENDPOINT,
        "expireAt": SAMPLE_EXPIRE_AT,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] == SAMPLE_TOKEN
    assert result.value.workload_auth_token["endpoint_url"] == SAMPLE_ENDPOINT
    assert result.value.workload_auth_token["expire_at"] == SAMPLE_EXPIRE_AT

    # Verify CdpIamClient was called correctly with environment CRN
    client.generate_workload_auth_token.assert_called_once_with(
        workload_name="DF",
        environment_crn=environment_crn,
        exclude_groups=False,
    )


def test_workload_auth_token_df_missing_environment(module_args, mocker):
    """Test that DF workload fails without environment CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "DF",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_workload_auth_token.CdpIamClient",
        autospec=True,
    )

    # Test module execution should fail due to required_if validation
    with pytest.raises(AnsibleFailJson) as result:
        iam_workload_auth_token.main()

    # The error should be about missing required parameter when workload_name is DF
    assert (
        "environment_crn" in result.value.msg or "required" in result.value.msg.lower()
    )


def test_workload_auth_token_opdb_exclude_groups(module_args, mocker):
    """Test generating workload auth token for OPDB with exclude_groups."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "OPDB",
            "exclude_groups": True,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_workload_auth_token.CdpIamClient",
        autospec=True,
    ).return_value
    # OPDB workload doesn't return endpointUrl
    client.generate_workload_auth_token.return_value = {
        "token": SAMPLE_TOKEN,
        "expireAt": SAMPLE_EXPIRE_AT,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] == SAMPLE_TOKEN
    assert result.value.workload_auth_token["expire_at"] == SAMPLE_EXPIRE_AT
    # endpoint_url should not be present for OPDB workload
    assert "endpoint_url" not in result.value.workload_auth_token

    # Verify CdpIamClient was called correctly with exclude_groups=True
    client.generate_workload_auth_token.assert_called_once_with(
        workload_name="OPDB",
        environment_crn=None,
        exclude_groups=True,
    )


def test_workload_auth_token_with_alias(module_args, mocker):
    """Test generating workload auth token using 'workload' alias."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload": "DE",  # Using alias instead of workload_name
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_workload_auth_token.CdpIamClient",
        autospec=True,
    ).return_value
    # DE workload doesn't return endpointUrl
    client.generate_workload_auth_token.return_value = {
        "token": SAMPLE_TOKEN,
        "expireAt": SAMPLE_EXPIRE_AT,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_workload_auth_token.main()

    assert result.value.changed is True
    assert result.value.workload_auth_token["token"] == SAMPLE_TOKEN
    # endpoint_url should not be present for DE workload
    assert "endpoint_url" not in result.value.workload_auth_token

    # Verify CdpIamClient was called correctly
    client.generate_workload_auth_token.assert_called_once_with(
        workload_name="DE",
        environment_crn=None,
        exclude_groups=False,
    )


def test_workload_auth_token_invalid_workload(module_args, mocker):
    """Test that an invalid workload name is rejected."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "workload_name": "INVALID",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Test module execution should fail during parameter validation
    with pytest.raises(AnsibleFailJson) as result:
        iam_workload_auth_token.main()

    # The error should be about invalid choice for workload_name
    assert "workload_name" in result.value.msg or "choices" in result.value.msg
