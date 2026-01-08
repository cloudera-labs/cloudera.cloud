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

from ansible_collections.cloudera.cloud.plugins.modules import df_deployment_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import CdpClient
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

DEPLOYMENT_NAME = "test-deployment"
DEPLOYMENT_CRN = "crn:cdp:df:us-west-1:tenant:deployment:dep-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-456"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-789"


def test_df_deployment_info_list_all(module_args, mocker):
    """Test df_deployment_info module with no parameters returns all deployments."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_deployments response
    client.list_deployments.return_value = {
        "deployments": [
            {
                "name": "deployment-1",
                "crn": "crn:cdp:df:us-west-1:tenant:deployment:dep-1",
                "status": {"state": "RUNNING", "detailedState": "RUNNING"},
                "service": {
                    "crn": SERVICE_CRN,
                    "environmentCrn": ENV_CRN,
                },
            },
            {
                "name": "deployment-2",
                "crn": "crn:cdp:df:us-west-1:tenant:deployment:dep-2",
                "status": {"state": "RUNNING", "detailedState": "RUNNING"},
                "service": {
                    "crn": SERVICE_CRN,
                    "environmentCrn": ENV_CRN,
                },
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 2
    assert result.value.deployments[0]["name"] == "deployment-1"
    assert result.value.deployments[1]["name"] == "deployment-2"

    # Verify CdpDfClient was called correctly
    client.list_deployments.assert_called_once()


def test_df_deployment_info_by_name(module_args, mocker):
    """Test df_deployment_info module filtering by deployment name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": DEPLOYMENT_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_deployment_by_name response
    client.get_deployment_by_name.return_value = {
        "deployment": {
            "crn": DEPLOYMENT_CRN,
            "name": DEPLOYMENT_NAME,
            "status": {
                "state": "RUNNING",
                "detailedState": "RUNNING",
                "message": "Deployment is running",
            },
            "service": {
                "crn": SERVICE_CRN,
                "name": "test-service",
                "cloudProvider": "AWS",
                "region": "us-west-1",
                "environmentCrn": ENV_CRN,
            },
            "updated": 1609459200000,
            "clusterSize": "SMALL",
            "flowVersionCrn": "crn:cdp:df:us-west-1:tenant:flow-version:fv-123",
            "flowCrn": "crn:cdp:df:us-west-1:tenant:flow:flow-123",
            "nifiUrl": "https://nifi.test-deployment.cloudera.site",
            "flowName": "Test Flow",
            "flowVersion": 1,
            "currentNodeCount": 3,
            "autoscalingEnabled": False,
            "staticNodeCount": 3,
            "activeWarningAlertCount": 0,
            "activeErrorAlertCount": 0,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 1
    assert result.value.deployments[0]["name"] == DEPLOYMENT_NAME
    assert result.value.deployments[0]["crn"] == DEPLOYMENT_CRN

    # Verify CdpDfClient was called correctly
    client.get_deployment_by_name.assert_called_once_with(DEPLOYMENT_NAME)


def test_df_deployment_info_by_crn(module_args, mocker):
    """Test df_deployment_info module filtering by deployment CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": DEPLOYMENT_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_deployment_by_crn response
    client.get_deployment_by_crn.return_value = {
        "deployment": {
            "crn": DEPLOYMENT_CRN,
            "name": DEPLOYMENT_NAME,
            "status": {
                "state": "RUNNING",
                "detailedState": "RUNNING",
                "message": "Deployment is running",
            },
            "service": {
                "crn": SERVICE_CRN,
                "name": "test-service",
                "cloudProvider": "AWS",
                "region": "us-west-1",
                "environmentCrn": ENV_CRN,
            },
            "updated": 1609459200000,
            "clusterSize": "MEDIUM",
            "flowVersionCrn": "crn:cdp:df:us-west-1:tenant:flow-version:fv-123",
            "flowCrn": "crn:cdp:df:us-west-1:tenant:flow:flow-123",
            "nifiUrl": "https://nifi.test-deployment.cloudera.site",
            "flowName": "Test Flow",
            "flowVersion": 1,
            "currentNodeCount": 5,
            "autoscalingEnabled": True,
            "autoscaleMinNodes": 3,
            "autoscaleMaxNodes": 10,
            "activeWarningAlertCount": 1,
            "activeErrorAlertCount": 0,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 1
    assert result.value.deployments[0]["crn"] == DEPLOYMENT_CRN

    # Verify CdpDfClient was called correctly
    client.get_deployment_by_crn.assert_called_once_with(DEPLOYMENT_CRN)


def test_df_deployment_info_by_crn_alias(module_args, mocker):
    """Test df_deployment_info module using dep_crn alias."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "dep_crn": DEPLOYMENT_CRN,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_deployment_by_crn response
    client.get_deployment_by_crn.return_value = {
        "deployment": {
            "crn": DEPLOYMENT_CRN,
            "name": DEPLOYMENT_NAME,
            "status": {"state": "RUNNING", "detailedState": "RUNNING"},
            "service": {
                "crn": SERVICE_CRN,
                "environmentCrn": ENV_CRN,
            },
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 1
    assert result.value.deployments[0]["crn"] == DEPLOYMENT_CRN

    # Verify CdpDfClient was called correctly
    client.get_deployment_by_crn.assert_called_once_with(DEPLOYMENT_CRN)


def test_df_deployment_info_not_found_by_name(module_args, mocker):
    """Test df_deployment_info module when deployment is not found by name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-deployment",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_deployment_by_name returning None
    client.get_deployment_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 0

    # Verify CdpDfClient was called correctly
    client.get_deployment_by_name.assert_called_once_with("nonexistent-deployment")


def test_df_deployment_info_not_found_by_crn(module_args, mocker):
    """Test df_deployment_info module when deployment is not found by CRN."""

    nonexistent_crn = "crn:cdp:df:us-west-1:tenant:deployment:nonexistent"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": nonexistent_crn,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock get_deployment_by_crn returning None
    client.get_deployment_by_crn.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 0

    # Verify CdpDfClient was called correctly
    client.get_deployment_by_crn.assert_called_once_with(nonexistent_crn)


def test_df_deployment_info_empty_list(module_args, mocker):
    """Test df_deployment_info module when no deployments exist."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.df_deployment_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_deployments returning empty list
    client.list_deployments.return_value = {"deployments": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_deployment_info.main()

    assert result.value.changed is False
    assert len(result.value.deployments) == 0

    # Verify CdpDfClient was called correctly
    client.list_deployments.assert_called_once()
