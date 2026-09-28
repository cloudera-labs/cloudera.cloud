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

from ansible_collections.cloudera.cloud.plugins.modules import de_virtual_cluster_info
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    ServiceDescription,
    VcDescription,
    VcSummary,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    from_dict,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

ENV_NAME = "test-environment"
SERVICE_NAME = "test-de-service"
CLUSTER_ID = "cluster-abc-123"
VC_NAME = "test-virtual-cluster"
VC_ID = "vc-abc-123"


@pytest.fixture
def vc_info_module_args(module_args):
    """Pre-populate common de_virtual_cluster_info module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "environment": ENV_NAME,
            "service_name": SERVICE_NAME,
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


@pytest.fixture
def de_client(mocker):
    """Patch load_cdp_config and CdpDeClient, returning the mocked client."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (ACCESS_KEY, PRIVATE_KEY, "us-west-1")

    mock_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.de_virtual_cluster_info.CdpDeClient",
        autospec=True,
    )
    return mock_class.return_value


def _existing_service():
    return from_dict(
        ServiceDescription,
        {
            "clusterId": CLUSTER_ID,
            "name": SERVICE_NAME,
            "status": "ClusterCreationCompleted",
            "environmentName": ENV_NAME,
        },
    )


def _vc_summary(vc_id, status="AppInstalled"):
    return from_dict(
        VcSummary,
        {"vcId": vc_id, "clusterId": CLUSTER_ID, "status": status},
    )


def _existing_vc(vc_id=VC_ID, vc_name=VC_NAME, status="AppInstalled"):
    return from_dict(
        VcDescription,
        {
            "vcId": vc_id,
            "vcName": vc_name,
            "clusterId": CLUSTER_ID,
            "status": status,
            "vcTier": "ALLP",
            "sparkVersion": "SPARK3_5_4",
        },
    )


def test_list_all(vc_info_module_args, de_client):
    """No name filter returns every Virtual Cluster in the CDE service."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.list_virtual_clusters.return_value = [
        _vc_summary("vc-1"),
        _vc_summary("vc-2"),
    ]
    de_client.describe_virtual_cluster.side_effect = [
        _existing_vc(vc_id="vc-1", vc_name="vc-one"),
        _existing_vc(vc_id="vc-2", vc_name="vc-two"),
    ]

    vc_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert len(result.value.virtual_clusters) == 2
    names = [vc["vcName"] for vc in result.value.virtual_clusters]
    assert "vc-one" in names
    assert "vc-two" in names

    de_client.get_service_by_name.assert_called_once_with(
        SERVICE_NAME,
        env_name=ENV_NAME,
    )
    de_client.list_virtual_clusters.assert_called_once_with(CLUSTER_ID)
    assert de_client.describe_virtual_cluster.call_count == 2


def test_list_by_name(vc_info_module_args, de_client):
    """A name filter returns just that one Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_info_module_args({"name": VC_NAME})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert len(result.value.virtual_clusters) == 1
    assert result.value.virtual_clusters[0]["vcName"] == VC_NAME
    assert result.value.virtual_clusters[0]["vcId"] == VC_ID

    de_client.get_virtual_cluster_by_name.assert_called_once_with(CLUSTER_ID, VC_NAME)
    de_client.list_virtual_clusters.assert_not_called()


def test_list_by_name_not_found(vc_info_module_args, de_client):
    """A name filter that matches nothing returns an empty list."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None

    vc_info_module_args({"name": "nonexistent-vc"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters == []


def test_service_not_found(vc_info_module_args, de_client):
    """When the CDE service cannot be resolved, the result is an empty list, not a failure."""
    de_client.get_service_by_name.return_value = None

    vc_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters == []

    de_client.list_virtual_clusters.assert_not_called()
    de_client.get_virtual_cluster_by_name.assert_not_called()


def test_list_empty(vc_info_module_args, de_client):
    """A CDE service with no Virtual Clusters returns an empty list."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.list_virtual_clusters.return_value = []

    vc_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert result.value.virtual_clusters == []

    de_client.describe_virtual_cluster.assert_not_called()


def test_list_all_skips_deleted(vc_info_module_args, de_client):
    """A summary whose full description is gone (deleted) is skipped, not included."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.list_virtual_clusters.return_value = [
        _vc_summary("vc-1"),
        _vc_summary("vc-2"),
    ]
    de_client.describe_virtual_cluster.side_effect = [
        _existing_vc(vc_id="vc-1"),
        None,
    ]

    vc_info_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    assert result.value.changed is False
    assert len(result.value.virtual_clusters) == 1
    assert result.value.virtual_clusters[0]["vcId"] == "vc-1"


def test_vc_details(vc_info_module_args, de_client):
    """Full Virtual Cluster details, including nested dict fields, are returned."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = from_dict(
        VcDescription,
        {
            "vcId": VC_ID,
            "vcName": VC_NAME,
            "clusterId": CLUSTER_ID,
            "status": "AppInstalled",
            "vcTier": "ALLP",
            "sparkVersion": "SPARK3_5_4",
            "creatorEmail": "user@example.com",
            "vcApiUrl": "https://vc.example.com/api",
            "accessControl": {"fullAccessUsers": ["alice"]},
            "resources": {"instance_type": "m5.2xlarge"},
        },
    )

    vc_info_module_args({"name": VC_NAME})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster_info.main()

    vc = result.value.virtual_clusters[0]
    assert vc["vcId"] == VC_ID
    assert vc["creatorEmail"] == "user@example.com"
    assert vc["vcApiUrl"] == "https://vc.example.com/api"
    assert vc["accessControl"]["fullAccessUsers"] == ["alice"]
    assert vc["resources"]["instance_type"] == "m5.2xlarge"
