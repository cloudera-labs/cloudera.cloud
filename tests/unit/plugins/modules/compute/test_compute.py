# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
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

from ansible_collections.cloudera.cloud.plugins.modules import compute
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    CdpComputeClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
CLUSTER_NAME = "my-compute-cluster"

SAMPLE_CLUSTER_RUNNING = {
    "clusterCrn": CLUSTER_CRN,
    "clusterId": "cluster-uuid",
    "clusterName": CLUSTER_NAME,
    "status": "Running",
    "envCrn": ENV_CRN,
    "envName": "test-env",
    "computePlatform": "EKS",
    "isDefault": False,
}

SAMPLE_CREATE_RESPONSE = {
    "clusterCrn": CLUSTER_CRN,
    "clusterId": "cluster-uuid",
    "clusterStatus": {"status": "Creating"},
}


def _patch_config(mocker):
    """Patch CDP config loading."""
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)
    return config


def _patch_client(mocker):
    """Patch CdpComputeClient and return the mock instance."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute.CdpComputeClient",
        autospec=True,
    ).return_value


# ============================================================================
# state=present — create
# ============================================================================


def test_compute_create(module_args, mocker):
    """state=present with no existing cluster creates the cluster."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "state": "present",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = None
    client.create_cluster.return_value = SAMPLE_CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = SAMPLE_CLUSTER_RUNNING

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.value.cluster["status"] == "Running"

    client.get_cluster_by_name_and_env.assert_called_once_with(CLUSTER_NAME, ENV_CRN)
    client.create_cluster.assert_called_once()
    client.wait_for_cluster_state.assert_called_once()


def test_compute_create_idempotent(module_args, mocker):
    """state=present with an existing cluster is idempotent (no create call)."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "state": "present",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = SAMPLE_CLUSTER_RUNNING

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is False
    assert result.value.cluster["cluster_crn"] == CLUSTER_CRN

    client.create_cluster.assert_not_called()
    client.wait_for_cluster_state.assert_not_called()


def test_compute_create_no_wait(module_args, mocker):
    """state=present with wait=false returns immediately after create."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "wait": False,
            "state": "present",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = None
    client.create_cluster.return_value = SAMPLE_CREATE_RESPONSE

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    client.create_cluster.assert_called_once()
    client.wait_for_cluster_state.assert_not_called()


# ============================================================================
# state=present — check mode
# ============================================================================


def test_compute_create_check_mode(module_args, mocker):
    """state=present in check mode does not call create_cluster."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "_ansible_check_mode": True,
            "state": "present",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    client.create_cluster.assert_not_called()


# ============================================================================
# state=absent — delete
# ============================================================================


def test_compute_absent(module_args, mocker):
    """state=absent with an existing cluster deletes it."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = SAMPLE_CLUSTER_RUNNING
    client.delete_cluster.return_value = {"clusterStatus": {"status": "Deleting"}}
    client.wait_for_cluster_state.return_value = None  # cluster gone

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    assert result.value.cluster == {}

    client.delete_cluster.assert_called_once_with(
        cluster_crn=CLUSTER_CRN,
        force=None,
        skip_validation=None,
        skip_workloads_validation=None,
    )
    client.wait_for_cluster_state.assert_called_once()


def test_compute_absent_idempotent(module_args, mocker):
    """state=absent when cluster does not exist is idempotent."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": CLUSTER_NAME,
            "environment": ENV_CRN,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_name_and_env.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is False
    assert result.value.cluster == {}

    client.delete_cluster.assert_not_called()


def test_compute_absent_with_crn(module_args, mocker):
    """state=absent using crn directly looks up via get_cluster_by_crn."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_RUNNING
    client.delete_cluster.return_value = {}
    client.wait_for_cluster_state.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    client.get_cluster_by_crn.assert_called_once_with(CLUSTER_CRN)
    client.get_cluster_by_name_and_env.assert_not_called()
    client.delete_cluster.assert_called_once()


def test_compute_absent_force(module_args, mocker):
    """state=absent with force=true passes force to delete_cluster."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
            "force": True,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_RUNNING
    client.delete_cluster.return_value = {}
    client.wait_for_cluster_state.return_value = None

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    call_kwargs = client.delete_cluster.call_args[1]
    assert call_kwargs["force"] is True


def test_compute_absent_no_wait(module_args, mocker):
    """state=absent with wait=false issues delete but does not poll."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
            "wait": False,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_RUNNING
    client.delete_cluster.return_value = {}

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    client.delete_cluster.assert_called_once()
    client.wait_for_cluster_state.assert_not_called()


# ============================================================================
# state=absent — check mode
# ============================================================================


def test_compute_absent_check_mode(module_args, mocker):
    """state=absent in check mode does not call delete_cluster."""
    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "crn": CLUSTER_CRN,
            "_ansible_check_mode": True,
            "state": "absent",
        },
    )

    _patch_config(mocker)
    client = _patch_client(mocker)
    client.get_cluster_by_crn.return_value = SAMPLE_CLUSTER_RUNNING

    with pytest.raises(AnsibleExitJson) as result:
        compute.main()

    assert result.value.changed is True
    client.delete_cluster.assert_not_called()
    client.wait_for_cluster_state.assert_not_called()
