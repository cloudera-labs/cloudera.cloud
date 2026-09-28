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

from ansible_collections.cloudera.cloud.plugins.modules import de_virtual_cluster
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CDE_VC_REMOVABLE_STATUSES,
    CDE_VC_STOPPED_STATUSES,
    CDE_VC_SUSPENDED_STATUSES,
    ServiceDescription,
    VcDescription,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    from_dict,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"

VC_NAME = "test-virtual-cluster"
ENV_NAME = "test-environment"
SERVICE_NAME = "test-de-service"
CLUSTER_ID = "cluster-abc-123"
VC_ID = "vc-abc-123"
CPU_REQUESTS = "2"
MEMORY_REQUESTS = "4Gi"


@pytest.fixture
def vc_module_args(module_args):
    """Pre-populate common Virtual Cluster module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": VC_NAME,
            "environment": ENV_NAME,
            "service_name": SERVICE_NAME,
            "cpu_requests": CPU_REQUESTS,
            "memory_requests": MEMORY_REQUESTS,
            "wait": False,
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
        "ansible_collections.cloudera.cloud.plugins.modules.de_virtual_cluster.CdpDeClient",
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


def _existing_vc(status="AppInstalled", **overrides):
    data = {
        "vcId": VC_ID,
        "vcName": VC_NAME,
        "clusterId": CLUSTER_ID,
        "status": status,
        "vcTier": "ALLP",
        "sparkVersion": "SPARK3_5_4",
    }
    data.update(overrides)
    return from_dict(VcDescription, data)


def test_present_create(vc_module_args, de_client):
    """A new Virtual Cluster is created and its parameters are passed through."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None
    de_client.create_virtual_cluster.return_value = _existing_vc()

    vc_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["vcName"] == VC_NAME
    assert result.value.virtual_cluster["clusterId"] == CLUSTER_ID

    de_client.get_service_by_name.assert_called_once_with(
        SERVICE_NAME,
        env_name=ENV_NAME,
    )
    de_client.get_virtual_cluster_by_name.assert_called_once_with(CLUSTER_ID, VC_NAME)

    de_client.create_virtual_cluster.assert_called_once()
    call_args = de_client.create_virtual_cluster.call_args.kwargs
    assert call_args["name"] == VC_NAME
    assert call_args["cluster_id"] == CLUSTER_ID
    assert call_args["cpu_requests"] == CPU_REQUESTS
    assert call_args["memory_requests"] == MEMORY_REQUESTS

    de_client.wait_for_vc_state.assert_not_called()


def test_present_create_with_wait(vc_module_args, de_client):
    """Creating with wait polls to REMOVABLE_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None
    de_client.create_virtual_cluster.return_value = _existing_vc(
        status="AppInstallationInProgress",
    )
    de_client.wait_for_vc_state.return_value = _existing_vc()

    vc_module_args({"wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["status"] == "AppInstalled"

    de_client.create_virtual_cluster.assert_called_once()
    de_client.wait_for_vc_state.assert_called_once()
    wait_args = de_client.wait_for_vc_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["vc_id"] == VC_ID
    assert wait_args["target_statuses"] == CDE_VC_REMOVABLE_STATUSES


def test_present_create_optional_params(vc_module_args, de_client):
    """Optional create parameters are passed through to the client."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None
    de_client.create_virtual_cluster.return_value = _existing_vc()

    vc_module_args(
        {
            "chart_value_overrides": [
                {"chart_name": "my-chart", "overrides": "airflow.enabled:true"},
            ],
            "runtime_spot_component": "ALL",
            "spark_version": "SPARK3_5_4",
            "acl_users": "user1,user2",
            "tier": "ALLP",
            "spark_os_name": "REDHAT",
            "session_timeout": "3600",
            "spark_configs": {"spark.executor.memory": "4g"},
            "full_access_users": ["alice"],
            "full_access_groups": ["admins"],
            "view_only_users": ["bob"],
            "view_only_groups": ["viewers"],
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.create_virtual_cluster.assert_called_once()
    call_args = de_client.create_virtual_cluster.call_args.kwargs
    assert call_args["chart_value_overrides"] == [
        {"chart_name": "my-chart", "overrides": "airflow.enabled:true"},
    ]
    assert call_args["runtime_spot_component"] == "ALL"
    assert call_args["spark_version"] == "SPARK3_5_4"
    assert call_args["acl_users"] == "user1,user2"
    assert call_args["vc_tier"] == "ALLP"
    assert call_args["spark_os_name"] == "REDHAT"
    assert call_args["session_timeout"] == "3600"
    assert call_args["spark_configs"] == {"spark.executor.memory": "4g"}
    assert call_args["full_access_users"] == ["alice"]
    assert call_args["full_access_groups"] == ["admins"]
    assert call_args["view_only_users"] == ["bob"]
    assert call_args["view_only_groups"] == ["viewers"]


def test_present_create_check_mode(vc_module_args, de_client):
    """check_mode reports changed without creating the Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None

    vc_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster == {}
    de_client.create_virtual_cluster.assert_not_called()
    de_client.wait_for_vc_state.assert_not_called()


def test_present_service_not_found_fails(vc_module_args, de_client):
    """state=present fails when the CDE service cannot be resolved."""
    de_client.get_service_by_name.return_value = None

    vc_module_args({})

    with pytest.raises(AnsibleFailJson) as result:
        de_virtual_cluster.main()

    assert SERVICE_NAME in result.value.msg
    assert ENV_NAME in result.value.msg
    de_client.get_virtual_cluster_by_name.assert_not_called()


def test_present_idempotent(vc_module_args, de_client):
    """A Virtual Cluster that already exists reports no change."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False
    assert result.value.virtual_cluster["vcId"] == VC_ID

    de_client.create_virtual_cluster.assert_not_called()


def test_present_recreates_over_stopped_status(vc_module_args, de_client):
    """A same-named Virtual Cluster left in a stopped status is treated as gone.

    CDE retains a record for a deleted Virtual Cluster (e.g. status
    AppDeleted) instead of removing it from listVcs, so state=present must
    still create a new one rather than treating the stale record as existing.
    """
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppDeleted",
    )
    de_client.create_virtual_cluster.return_value = _existing_vc()

    vc_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    de_client.create_virtual_cluster.assert_called_once()


# ============================================================================
# Delete / absent tests
# ============================================================================


def test_absent_delete(vc_module_args, de_client):
    """state=absent without wait deletes the Virtual Cluster directly."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.delete_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_not_called()


def test_absent_delete_with_wait(vc_module_args, de_client):
    """state=absent with wait polls to STOPPED_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()
    de_client.wait_for_vc_state.return_value = _existing_vc(status="AppDeleted")

    vc_module_args({"state": "absent", "wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["status"] == "AppDeleted"

    de_client.delete_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_called_once()
    wait_args = de_client.wait_for_vc_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["vc_id"] == VC_ID
    assert wait_args["target_statuses"] == CDE_VC_STOPPED_STATUSES


def test_absent_delete_wait_returns_none(vc_module_args, de_client):
    """virtual_cluster is {} when the wait reports the Virtual Cluster fully gone."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()
    de_client.wait_for_vc_state.return_value = None

    vc_module_args({"state": "absent", "wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster == {}


def test_absent_check_mode(vc_module_args, de_client):
    """check_mode reports changed without deleting the Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "absent", "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["vcId"] == VC_ID

    de_client.delete_virtual_cluster.assert_not_called()
    de_client.wait_for_vc_state.assert_not_called()


def test_absent_noop_no_service(vc_module_args, de_client):
    """state=absent is a no-op when the CDE service does not exist."""
    de_client.get_service_by_name.return_value = None

    vc_module_args({"state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False
    assert result.value.virtual_cluster == {}

    de_client.get_virtual_cluster_by_name.assert_not_called()
    de_client.delete_virtual_cluster.assert_not_called()


def test_absent_noop_no_vc(vc_module_args, de_client):
    """state=absent is a no-op when the Virtual Cluster does not exist."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None

    vc_module_args({"state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False
    assert result.value.virtual_cluster == {}

    de_client.delete_virtual_cluster.assert_not_called()


def test_absent_noop_vc_already_stopped(vc_module_args, de_client):
    """state=absent is a no-op when the only record is already in a stopped status.

    CDE retains a record for a deleted Virtual Cluster (e.g. status
    AppDeleted) instead of removing it from listVcs, so it must not be
    re-deleted.
    """
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppDeleted",
    )

    vc_module_args({"state": "absent"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False
    assert result.value.virtual_cluster == {}

    de_client.delete_virtual_cluster.assert_not_called()


def test_suspended_suspend(vc_module_args, de_client):
    """state=suspended without wait suspends the Virtual Cluster directly."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "suspended"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.suspend_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_not_called()


def test_suspended_with_wait(vc_module_args, de_client):
    """state=suspended with wait polls to SUSPENDED_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()
    de_client.wait_for_vc_state.return_value = _existing_vc(status="AppSuspended")

    vc_module_args({"state": "suspended", "wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["status"] == "AppSuspended"

    de_client.suspend_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_called_once()
    wait_args = de_client.wait_for_vc_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["vc_id"] == VC_ID
    assert wait_args["target_statuses"] == CDE_VC_SUSPENDED_STATUSES


def test_suspended_idempotent(vc_module_args, de_client):
    """A Virtual Cluster already suspended reports no change."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppSuspended",
    )

    vc_module_args({"state": "suspended"})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False

    de_client.suspend_virtual_cluster.assert_not_called()


def test_suspended_check_mode(vc_module_args, de_client):
    """check_mode reports changed without suspending the Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "suspended", "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.suspend_virtual_cluster.assert_not_called()
    de_client.wait_for_vc_state.assert_not_called()


def test_suspended_service_not_found_fails(vc_module_args, de_client):
    """state=suspended fails when the CDE service cannot be resolved."""
    de_client.get_service_by_name.return_value = None

    vc_module_args({"state": "suspended"})

    with pytest.raises(AnsibleFailJson) as result:
        de_virtual_cluster.main()

    assert SERVICE_NAME in result.value.msg
    de_client.get_virtual_cluster_by_name.assert_not_called()


def test_suspended_vc_not_found_fails(vc_module_args, de_client):
    """state=suspended fails when the Virtual Cluster does not exist."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None

    vc_module_args({"state": "suspended"})

    with pytest.raises(AnsibleFailJson) as result:
        de_virtual_cluster.main()

    assert VC_NAME in result.value.msg
    assert SERVICE_NAME in result.value.msg

    de_client.suspend_virtual_cluster.assert_not_called()


def test_present_resumes_suspended_vc(vc_module_args, de_client):
    """state=present without wait resumes a suspended Virtual Cluster directly."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppSuspended",
    )

    vc_module_args({})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.resume_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_not_called()
    de_client.update_virtual_cluster.assert_not_called()


def test_present_resume_with_wait(vc_module_args, de_client):
    """Resuming with wait polls to REMOVABLE_STATUSES."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppSuspended",
    )
    de_client.wait_for_vc_state.return_value = _existing_vc()

    vc_module_args({"wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["status"] == "AppInstalled"

    de_client.resume_virtual_cluster.assert_called_once_with(CLUSTER_ID, VC_ID)
    de_client.wait_for_vc_state.assert_called_once()
    wait_args = de_client.wait_for_vc_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["vc_id"] == VC_ID
    assert wait_args["target_statuses"] == CDE_VC_REMOVABLE_STATUSES


def test_present_resume_check_mode(vc_module_args, de_client):
    """check_mode reports changed without resuming the Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        status="AppSuspended",
    )

    vc_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.resume_virtual_cluster.assert_not_called()
    de_client.wait_for_vc_state.assert_not_called()


def test_present_update_full_access_users(vc_module_args, de_client):
    """A changed full_access_users triggers an in-place update."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["bob"]},
    )

    vc_module_args({"full_access_users": ["alice"]})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.update_virtual_cluster.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vc_id=VC_ID,
        full_access_users=["alice"],
    )


def test_present_update_spark_configs(vc_module_args, de_client):
    """A changed spark_configs triggers an in-place update."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        sparkConfigs={"spark.executor.memory": "2g"},
    )

    vc_module_args({"spark_configs": {"spark.executor.memory": "4g"}})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.update_virtual_cluster.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vc_id=VC_ID,
        spark_configs={"spark.executor.memory": "4g"},
    )


def test_present_update_no_changes_idempotent(vc_module_args, de_client):
    """Matching desired and existing configuration reports no change."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["alice"]},
        sparkConfigs={"spark.executor.memory": "4g"},
    )

    vc_module_args(
        {
            "full_access_users": ["alice"],
            "spark_configs": {"spark.executor.memory": "4g"},
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False

    de_client.update_virtual_cluster.assert_not_called()


def test_present_update_with_wait(vc_module_args, de_client):
    """An update with wait polls to REMOVABLE_STATUSES and refreshes the result."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["bob"]},
    )
    de_client.wait_for_vc_state.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["alice"]},
    )

    vc_module_args({"full_access_users": ["alice"], "wait": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True
    assert result.value.virtual_cluster["accessControl"]["fullAccessUsers"] == [
        "alice",
    ]

    de_client.update_virtual_cluster.assert_called_once()
    de_client.wait_for_vc_state.assert_called_once()
    wait_args = de_client.wait_for_vc_state.call_args.kwargs
    assert wait_args["cluster_id"] == CLUSTER_ID
    assert wait_args["vc_id"] == VC_ID
    assert wait_args["target_statuses"] == CDE_VC_REMOVABLE_STATUSES


def test_present_update_check_mode(vc_module_args, de_client):
    """check_mode reports changed without updating the Virtual Cluster."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["bob"]},
    )

    vc_module_args({"full_access_users": ["alice"], "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.update_virtual_cluster.assert_not_called()
    de_client.wait_for_vc_state.assert_not_called()


def test_present_update_passthrough_flags_no_change(vc_module_args, de_client):
    """acl_users/discard_spark_configs/enable_compute_override alone cannot
    trigger an update, since CDE reports no current state for them to diff
    against."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["alice"]},
    )

    vc_module_args(
        {
            "full_access_users": ["alice"],
            "discard_spark_configs": True,
            "enable_compute_override": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False

    de_client.update_virtual_cluster.assert_not_called()


def test_present_update_passthrough_flags_ride_along(vc_module_args, de_client):
    """acl_users/discard_spark_configs/enable_compute_override ride along on
    an update already triggered by a comparable field."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        sparkConfigs={"spark.executor.memory": "2g"},
    )

    vc_module_args(
        {
            "spark_configs": {"spark.executor.memory": "4g"},
            "acl_users": "user1,user2",
            "discard_spark_configs": True,
            "enable_compute_override": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is True

    de_client.update_virtual_cluster.assert_called_once_with(
        cluster_id=CLUSTER_ID,
        vc_id=VC_ID,
        spark_configs={"spark.executor.memory": "4g"},
        acl_users="user1,user2",
        discard_spark_configs=True,
        enable_compute_override=True,
    )


def test_create_reports_diff(vc_module_args, de_client):
    """Creating a Virtual Cluster populates diff.after under --diff (check_mode)."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = None

    vc_module_args({"_ansible_check_mode": True, "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.diff["before"] == {}
    assert result.value.diff["after"] == {
        "vcName": VC_NAME,
        "clusterId": CLUSTER_ID,
        "status": "AppInstallationInProgress",
    }


def test_absent_reports_diff(vc_module_args, de_client):
    """Deleting reports the Virtual Cluster representation in diff.before."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "absent", "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.diff["before"]["vcId"] == VC_ID
    assert result.value.diff["after"] == {}


def test_suspend_reports_diff(vc_module_args, de_client):
    """Suspending reports the Virtual Cluster representation in diff.before."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"state": "suspended", "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.diff["before"]["vcId"] == VC_ID
    assert result.value.diff["after"] == {}


def test_update_reports_diff(vc_module_args, de_client):
    """Updating reports before/after representations under --diff."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc(
        accessControl={"fullAccessUsers": ["bob"]},
    )

    vc_module_args({"full_access_users": ["alice"], "_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.diff["before"]["vcId"] == VC_ID
    assert result.value.diff["after"]["full_access_users"] == ["alice"]


def test_present_idempotent_reports_no_diff(vc_module_args, de_client):
    """An idempotent present run leaves diff empty, so the diff key is omitted."""
    de_client.get_service_by_name.return_value = _existing_service()
    de_client.get_virtual_cluster_by_name.return_value = _existing_vc()

    vc_module_args({"_ansible_diff": True})

    with pytest.raises(AnsibleExitJson) as result:
        de_virtual_cluster.main()

    assert result.value.changed is False
    assert "diff" not in result.value
