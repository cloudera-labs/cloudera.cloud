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

from ansible_collections.cloudera.cloud.plugins.modules import df_service_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import (
    CdpDfClient,
    DataFlowServiceDescription,
    DataFlowServiceSummary,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import from_dict


def _summary(data):
    return from_dict(DataFlowServiceSummary, data)


def _description(data):
    return from_dict(DataFlowServiceDescription, data)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_CRN = "crn:cdp:df:us-west-1:tenant:service:service-456"
SERVICE_CRN_2 = "crn:cdp:df:us-west-1:tenant:service:service-789"


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
    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    )
    mock_class.DISABLED_STATES = CdpDfClient.DISABLED_STATES
    client = mock_class.return_value

    # Mock list_services response
    client.list_services.return_value = [
        _summary(
            {
                "crn": SERVICE_CRN,
                "name": "env-1",
                "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-1",
                "status": {"state": "GOOD_HEALTH"},
            },
        ),
        _summary(
            {
                "crn": SERVICE_CRN_2,
                "name": "env-2",
                "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-2",
                "status": {"state": "GOOD_HEALTH"},
            },
        ),
    ]

    # Mock describe_service responses for each service
    def describe_service_side_effect(crn, squelch=None):
        if crn == SERVICE_CRN:
            return _description(
                {
                    "crn": SERVICE_CRN,
                    "name": "env-1",
                    "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-1",
                    "cloudPlatform": "AWS",
                    "status": {"state": "GOOD_HEALTH"},
                },
            )
        elif crn == SERVICE_CRN_2:
            return _description(
                {
                    "crn": SERVICE_CRN_2,
                    "name": "env-2",
                    "environmentCrn": "crn:cdp:environments:us-west-1:tenant:environment:env-2",
                    "cloudPlatform": "AWS",
                    "status": {"state": "GOOD_HEALTH"},
                },
            )

    client.describe_service.side_effect = describe_service_side_effect

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 2
    names = [svc["name"] for svc in result.value.services]
    assert "env-1" in names
    assert "env-2" in names

    # Verify CdpDfClient was called correctly
    client.list_services.assert_called_once()
    assert client.describe_service.call_count == 2


def test_df_service_info_list_all_skips_disabled(module_args, mocker):
    """Test df_service_info module skips disabled services when listing all."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    )
    mock_class.DISABLED_STATES = CdpDfClient.DISABLED_STATES
    client = mock_class.return_value

    client.list_services.return_value = [
        _summary(
            {
                "crn": SERVICE_CRN,
                "name": "env-1",
                "status": {"state": "NOT_ENABLED"},
            },
        ),
        _summary(
            {
                "crn": SERVICE_CRN_2,
                "name": "env-2",
                "status": {"state": "GOOD_HEALTH"},
            },
        ),
    ]
    client.describe_service.return_value = _description(
        {
            "crn": SERVICE_CRN_2,
            "name": "env-2",
            "status": {"state": "GOOD_HEALTH"},
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["crn"] == SERVICE_CRN_2

    # describe_service is only called for the non-disabled service
    client.describe_service.assert_called_once_with(SERVICE_CRN_2, squelch={500: {}})


def test_df_service_info_list_all_describe_failure_falls_back_to_summary(
    module_args,
    mocker,
):
    """A describeService failure for one service must not fail the whole listing."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    warn = mocker.patch("ansible.module_utils.basic.AnsibleModule.warn")

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    )
    mock_class.DISABLED_STATES = CdpDfClient.DISABLED_STATES
    client = mock_class.return_value

    client.list_services.return_value = [
        _summary(
            {
                "crn": SERVICE_CRN,
                "name": "env-1",
                "status": {"state": "CONCERNING_HEALTH"},
            },
        ),
        _summary(
            {
                "crn": SERVICE_CRN_2,
                "name": "env-2",
                "status": {"state": "GOOD_HEALTH"},
            },
        ),
    ]

    def describe_service_side_effect(crn, squelch=None):
        if crn == SERVICE_CRN:
            # The client returns None when the (squelched) describeService 500s
            assert squelch == {500: {}}
            return None
        return _description(
            {
                "crn": SERVICE_CRN_2,
                "name": "env-2",
                "cloudPlatform": "AWS",
                "status": {"state": "GOOD_HEALTH"},
            },
        )

    client.describe_service.side_effect = describe_service_side_effect

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 2
    by_crn = {svc["crn"]: svc for svc in result.value.services}
    assert by_crn[SERVICE_CRN]["name"] == "env-1"
    assert by_crn[SERVICE_CRN]["status"]["state"] == "CONCERNING_HEALTH"
    assert by_crn[SERVICE_CRN_2]["cloudPlatform"] == "AWS"

    warn.assert_called_once()
    assert SERVICE_CRN in warn.call_args.args[0]


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

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_name.return_value = _description(
        {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "GOOD_HEALTH", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
            "runningK8sNodeCount": 5,
            "instanceType": "m5.2xlarge",
            "dfLocalUrl": "https://df.test-environment.cloudera.site",
            "activeWarningAlertCount": 0,
            "activeErrorAlertCount": 0,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["name"] == ENV_NAME
    assert result.value.services[0]["crn"] == SERVICE_CRN

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

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_crn.return_value = _description(
        {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "GOOD_HEALTH"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["crn"] == SERVICE_CRN

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

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_env_crn.return_value = _description(
        {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "GOOD_HEALTH"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["environmentCrn"] == ENV_CRN

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

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_name.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    client.get_service_by_name.assert_called_once_with("nonexistent-environment")


def test_df_service_info_not_found_by_df_crn(module_args, mocker):
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

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_crn.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    client.get_service_by_crn.assert_called_once_with(nonexistent_crn)


def test_df_service_info_not_found_by_env_crn(module_args, mocker):
    """Test df_service_info module when service is not found by environment CRN."""

    nonexistent_env_crn = (
        "crn:cdp:environments:us-west-1:tenant:environment:nonexistent"
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_crn": nonexistent_env_crn,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_env_crn.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    client.get_service_by_env_crn.assert_called_once_with(nonexistent_env_crn)


def test_df_service_info_empty_list(module_args, mocker):
    """Test df_service_info module when no services exist."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    )
    mock_class.DISABLED_STATES = CdpDfClient.DISABLED_STATES
    client = mock_class.return_value

    client.list_services.return_value = []

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    client.list_services.assert_called_once()
    client.describe_service.assert_not_called()


def test_df_service_info_service_details(module_args, mocker):
    """Test that service details are properly returned."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "df_crn": SERVICE_CRN,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_service_info.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_service_by_crn.return_value = _description(
        {
            "crn": SERVICE_CRN,
            "name": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "region": "us-west-1",
            "status": {"state": "GOOD_HEALTH", "message": "Service is running"},
            "deploymentCount": 5,
            "minK8sNodeCount": 3,
            "maxK8sNodeCount": 10,
            "kubeApiAuthorizedIpRanges": ["10.0.0.0/16"],
            "loadBalancerAuthorizedIpRanges": ["192.168.1.0/24"],
            "tags": {"team": "df-team"},
            "encryptionParameters": {
                "encryptionKeyArn": "arn:aws:kms:us-west-1:tenant:key/abc123",
                "encryptionStrategy": "CUSTOM",
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        df_service_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    service = result.value.services[0]
    assert service["crn"] == SERVICE_CRN
    assert service["name"] == ENV_NAME
    assert service["cloudPlatform"] == "AWS"
    assert service["kubeApiAuthorizedIpRanges"] == ["10.0.0.0/16"]
    assert service["loadBalancerAuthorizedIpRanges"] == ["192.168.1.0/24"]
    assert service["tags"] == {"team": "df-team"}
    assert service["encryptionParameters"]["encryptionStrategy"] == "CUSTOM"

    client.get_service_by_crn.assert_called_once_with(SERVICE_CRN)
