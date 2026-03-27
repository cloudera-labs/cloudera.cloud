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

from ansible_collections.cloudera.cloud.plugins.modules import de_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import CdpClient
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import CdpDeClient


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant:environment:env-123"
SERVICE_NAME = "test-service"
CLUSTER_ID = "cluster-abc123"


def test_de_info_list_all(module_args, mocker):
    """Test de_info module with no parameters returns all services."""

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

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock list_services response
    client.list_services.return_value = {
        "services": [
            {
                "clusterId": "cluster-123",
                "name": "service-1",
                "status": "ClusterCreationCompleted",
            },
            {
                "clusterId": "cluster-456",
                "name": "service-2",
                "status": "ClusterCreationCompleted",
            },
        ],
    }

    # Mock describe_service response - returns generic service details
    client.describe_service.return_value = {
        "service": {
            "clusterId": "cluster-123",
            "name": "service-1",
            "status": "ClusterCreationCompleted",
            "environmentName": "env-1",
            "cloudPlatform": "AWS",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 2
    assert result.value.services[0]["name"] == "service-1"

    # Verify CdpDeClient was called correctly
    client.list_services.assert_called_once()
    assert client.describe_service.call_count == 2


def test_de_info_by_name(module_args, mocker):
    """Test de_info module filtering by service name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": SERVICE_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_name response
    client.get_service_by_name.return_value = {
        "service": {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "status": "ClusterCreationCompleted",
            "environmentName": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
            "clusterFqdn": "test.cloudera.com",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["name"] == SERVICE_NAME
    assert result.value.services[0]["clusterId"] == CLUSTER_ID

    # Verify CdpDeClient was called correctly
    client.get_service_by_name.assert_called_once_with(SERVICE_NAME)


def test_de_info_by_cluster_id(module_args, mocker):
    """Test de_info module filtering by cluster ID."""

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
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_cluster_id response (direct lookup by cluster_id)
    client.get_service_by_cluster_id.return_value = {
        "service": {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "status": "ClusterCreationCompleted",
            "environmentName": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "cloudPlatform": "AWS",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["clusterId"] == CLUSTER_ID

    # Verify CdpDeClient was called correctly
    client.get_service_by_cluster_id.assert_called_once_with(CLUSTER_ID)


def test_de_info_by_env_name(module_args, mocker):
    """Test de_info module filtering by environment name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_name": ENV_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_env_name response
    client.get_service_by_env_name.return_value = [
        {
            "service": {
                "clusterId": CLUSTER_ID,
                "name": SERVICE_NAME,
                "environmentName": ENV_NAME,
                "environmentCrn": ENV_CRN,
                "status": "ClusterCreationCompleted",
                "cloudPlatform": "AWS",
            },
        },
    ]

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["environmentName"] == ENV_NAME

    # Verify CdpDeClient was called correctly
    client.get_service_by_env_name.assert_called_once_with(ENV_NAME)


def test_de_info_multiple_services_same_env(module_args, mocker):
    """Test de_info module with multiple services in same environment (DE supports 1-to-many)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "env_name": ENV_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_env_name response with multiple services
    client.get_service_by_env_name.return_value = [
        {
            "service": {
                "clusterId": "cluster-123",
                "name": "service-1",
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        },
        {
            "service": {
                "clusterId": "cluster-456",
                "name": "service-2",
                "environmentName": ENV_NAME,
                "status": "ClusterCreationCompleted",
            },
        },
    ]

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 2
    assert all(svc["environmentName"] == ENV_NAME for svc in result.value.services)
    cluster_ids = [svc["clusterId"] for svc in result.value.services]
    assert "cluster-123" in cluster_ids
    assert "cluster-456" in cluster_ids

    # Verify CdpDeClient was called correctly
    client.get_service_by_env_name.assert_called_once_with(ENV_NAME)


def test_de_info_not_found_by_name(module_args, mocker):
    """Test de_info module when service is not found by name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "nonexistent-service",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_name returning None
    client.get_service_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDeClient was called correctly
    client.get_service_by_name.assert_called_once_with("nonexistent-service")


def test_de_info_not_found_by_cluster_id(module_args, mocker):
    """Test de_info module when service is not found by cluster ID."""

    nonexistent_cluster_id = "cluster-nonexistent"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "cluster_id": nonexistent_cluster_id,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_cluster_id returning None
    client.get_service_by_cluster_id.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDeClient was called correctly
    client.get_service_by_cluster_id.assert_called_once_with(nonexistent_cluster_id)


def test_de_info_empty_list(module_args, mocker):
    """Test de_info module when no services exist."""

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

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock list_services returning empty list
    client.list_services.return_value = {"services": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 0

    # Verify CdpDeClient was called correctly
    client.list_services.assert_called_once()
    client.describe_service.assert_not_called()


def test_de_info_deleted_service_via_cluster_id(module_args, mocker):
    """Test de_info module returns deleted service when queried by cluster_id."""

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
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_cluster_id returning deleted service
    client.get_service_by_cluster_id.return_value = {
        "service": {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "status": "ClusterDeletionCompleted",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    assert result.value.services[0]["status"] == "ClusterDeletionCompleted"

    # Verify CdpDeClient was called correctly
    client.get_service_by_cluster_id.assert_called_once_with(CLUSTER_ID)


def test_de_info_service_details(module_args, mocker):
    """Test that service details are properly returned."""

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
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDeClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_info.CdpDeClient",
        autospec=True,
    ).return_value

    # Mock get_service_by_cluster_id with full details
    client.get_service_by_cluster_id.return_value = {
        "service": {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "environmentName": ENV_NAME,
            "environmentCrn": ENV_CRN,
            "status": "ClusterCreationCompleted",
            "cloudPlatform": "AWS",
            "clusterFqdn": "test.cloudera.com",
            "resources": {
                "instance_type": "m5.2xlarge",
                "min_instances": "1",
                "max_instances": "10",
            },
            "creatorEmail": "user@example.com",
            "whitelistIps": "10.0.0.0/16",
            "loadbalancerAllowlist": "10.1.0.0/16",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        de_info.main()

    assert result.value.changed is False
    assert len(result.value.services) == 1
    service = result.value.services[0]
    assert service["clusterId"] == CLUSTER_ID
    assert service["name"] == SERVICE_NAME
    assert service["environmentName"] == ENV_NAME
    assert service["cloudPlatform"] == "AWS"
    assert service["resources"]["instance_type"] == "m5.2xlarge"
    assert service["creatorEmail"] == "user@example.com"

    # Verify CdpDeClient was called correctly
    client.get_service_by_cluster_id.assert_called_once_with(CLUSTER_ID)
