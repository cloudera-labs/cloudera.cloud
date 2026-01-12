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

from ansible_collections.cloudera.cloud.plugins.modules import df_service_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import CdpClient
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-456"


def test_df_service_info_list_all(module_args, mocker):
    """Test df_service_info module with no parameters returns all services."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_services response
    client.list_services.return_value = {
        "services": [
            {
                "name": "env-1",
                "crn": "crn:cdp:df:us-west-1:tenant:service:service-1",
                "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-1",
            },
            {
                "name": "env-2",
                "crn": "crn:cdp:df:us-west-1:tenant:service:service-2",
                "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-2",
            },
        ],
    }

    # Mock describe_service response - returns generic service details
    client.describe_service.return_value = {
        "service": {
            "crn": "crn:cdp:df:us-west-1:tenant:service:service-1",
            "name": "env-1",
            "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-1",
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "ENABLED", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 2
    assert result.value.services[0]["name"] == "env-1"

    # Verify CdpDfClient was called correctly
    client.list_services.assert_called_once()
    assert client.describe_service.call_count == 2


def test_df_service_info_by_name(module_args, mocker):
    """Test df_service_info module filtering by environment name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": ENV_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_name response
    client.get_service_by_name.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "ENABLED", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
            "k8sNodeCount": 5,
            "instanceType": "m5.2xlarge",
            "dfLocalUrl": "https://df.test-environment.cloudera.site",
            "activeWarningAlertCount": 0,
            "activeErrorAlertCount": 0,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["name"] == ENV_NAME
    assert result.value.services[0]["crn"] == SERVICE_CRN

    # Verify CdpDfClient was called correctly
    client.get_service_by_name.assert_called_once_with(ENV_NAME)


def test_df_service_info_by_df_crn(module_args, mocker):
    """Test df_service_info module filtering by DataFlow service CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_crn response
    client.get_service_by_crn.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "ENABLED", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["crn"] == SERVICE_CRN

    # Verify CdpDfClient was called correctly
    client.get_service_by_crn.assert_called_once_with(SERVICE_CRN)


def test_df_service_info_by_env_crn(module_args, mocker):
    """Test df_service_info module filtering by environment CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": ENV_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_env_crn response
    client.get_service_by_env_crn.return_value = {
        "service": {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "ENABLED", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["environmentCrn"] == ENV_CRN

    # Verify CdpDfClient was called correctly
    client.get_service_by_env_crn.assert_called_once_with(ENV_CRN)


def test_df_service_info_not_found_by_name(module_args, mocker):
    """Test df_service_info module when service is not found by name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-environment",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_name returning None
    client.get_service_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDfClient was called correctly
    client.get_service_by_name.assert_called_once_with("nonexistent-environment")


def test_df_service_info_not_found_by_crn(module_args, mocker):
    """Test df_service_info module when service is not found by CRN."""

    nonexistent_crn = "crn:cdp:df:us-west-1:tenant:service:nonexistent"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": nonexistent_crn,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_crn returning None
    client.get_service_by_crn.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDfClient was called correctly
    client.get_service_by_crn.assert_called_once_with(nonexistent_crn)


def test_df_service_info_empty_list(module_args, mocker):
    """Test df_service_info module when no services exist."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_services returning empty list
    client.list_services.return_value = {"services": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDfClient was called correctly
    client.list_services.assert_called_once()
    client.describe_service.assert_not_called()
