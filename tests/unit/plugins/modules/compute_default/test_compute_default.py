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

from ansible_collections.cloudera.cloud.plugins.modules import compute_default
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    CdpError,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_compute import (
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_CREATING_STATUSES,
    COMPUTE_CLUSTER_FAILED_STATUSES,
    ComputeCluster,
    ComputeClusterSummary,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_env import (
    ComputeClusterConfig,
    InitializeComputeClusterResponse,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import NULLABLE

# ============================================================================
# Test constants
# ============================================================================

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

AUTH = {
    "endpoint": BASE_URL,
    "access_key": ACCESS_KEY,
    "private_key": PRIVATE_KEY,
}

ENV_NAME = "test-environment"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
OPERATION_ID = "op-uuid-1234"

ACTIVE = next(iter(COMPUTE_CLUSTER_ACTIVE_STATUSES))
CREATING = sorted(COMPUTE_CLUSTER_CREATING_STATUSES)[0]
FAILED = sorted(COMPUTE_CLUSTER_FAILED_STATUSES)[0]


def make_env(platform="AWS"):
    return {
        "environmentName": ENV_NAME,
        "crn": ENV_CRN,
        "cloudPlatform": platform,
        "status": "AVAILABLE",
    }


def make_summary(**overrides):
    values = dict(
        clusterCrn=CLUSTER_CRN,
        clusterName="default-cluster",
        status=ACTIVE,
        isDefault=True,
        envName=ENV_NAME,
    )
    values.update(overrides)
    return ComputeClusterSummary(**values)


def make_cluster(**overrides):
    values = dict(
        clusterCrn=CLUSTER_CRN,
        clusterId="cluster-uuid",
        clusterName="default-cluster",
        status=ACTIVE,
        isDefault=True,
        envName=ENV_NAME,
    )
    values.update(overrides)
    return ComputeCluster(**values)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client(mocker):
    """Patched CdpComputeClient instance; no default cluster by default."""
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
        return_value=(FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION),
    )
    mocked = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_default.CdpComputeClient",
        autospec=True,
    )
    instance = mocked.return_value
    instance.get_default_cluster.return_value = None
    instance.wait_for_default_cluster.return_value = make_cluster()
    instance.describe_cluster.return_value = make_cluster()
    return instance


@pytest.fixture
def env_client(mocker):
    """Patched CdpEnvClient instance; resolves any environment to an AWS environment."""
    mocked = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute_default.CdpEnvClient",
        autospec=True,
    )
    instance = mocked.return_value
    instance.describe_environment.return_value = make_env("AWS")
    instance.initialize_aws_compute_cluster.return_value = (
        InitializeComputeClusterResponse(operationId=OPERATION_ID)
    )
    instance.initialize_azure_compute_cluster.return_value = (
        InitializeComputeClusterResponse(operationId=OPERATION_ID)
    )
    return instance


def run(module_args, **params):
    module_args({**AUTH, "environment": ENV_NAME, **params})
    with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as result:
        compute_default.main()
    return result.value


# ============================================================================
# Initialize — AWS
# ============================================================================


def test_aws_initialize_minimal(module_args, client, env_client):
    result = run(module_args)

    assert result.changed is True
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.cluster["status"] == ACTIVE
    assert "operation_id" not in vars(result)  # not exposed when wait=True

    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(),
    )
    env_client.initialize_azure_compute_cluster.assert_not_called()
    client.wait_for_default_cluster.assert_called_once_with(ENV_NAME, 3600, 15)


def test_aws_initialize_with_options(module_args, client, env_client):
    result = run(
        module_args,
        worker_node_subnets=["subnet-abc", "subnet-def"],
        kube_api_authorized_ip_ranges=["10.0.0.0/8"],
    )

    assert result.changed is True
    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(
            workerNodeSubnets=["subnet-abc", "subnet-def"],
            kubeApiAuthorizedIpRanges=["10.0.0.0/8"],
        ),
    )


def test_aws_initialize_private_cluster(module_args, client, env_client):
    run(module_args, private_cluster=True)

    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(privateCluster=True),
    )


def test_private_cluster_false_is_sent(module_args, client, env_client):
    """An explicit false is a value, not 'unset'."""
    run(module_args, private_cluster=False)

    config = env_client.initialize_aws_compute_cluster.call_args.args[1]
    assert config.privateCluster is False


def test_unset_options_stay_nullable(module_args, client, env_client):
    run(module_args)

    config = env_client.initialize_aws_compute_cluster.call_args.args[1]
    assert config.privateCluster is NULLABLE
    assert config.kubeApiAuthorizedIpRanges is NULLABLE
    assert config.workerNodeSubnets is NULLABLE
    assert config.outboundType is NULLABLE


# ============================================================================
# Initialize — Azure
# ============================================================================


def test_azure_initialize_minimal(module_args, client, env_client):
    env_client.describe_environment.return_value = make_env("AZURE")

    result = run(module_args)

    assert result.changed is True
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    env_client.initialize_azure_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(),
    )
    env_client.initialize_aws_compute_cluster.assert_not_called()


def test_azure_initialize_with_options(module_args, client, env_client):
    env_client.describe_environment.return_value = make_env("AZURE")

    run(
        module_args,
        outbound_type="udr",
        worker_node_subnets=["subnet-abc"],
        private_cluster=True,
    )

    env_client.initialize_azure_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(
            privateCluster=True,
            workerNodeSubnets=["subnet-abc"],
            outboundType="udr",
        ),
    )


# ============================================================================
# Existing default cluster — F-D state table
# ============================================================================


@pytest.mark.parametrize("platform", ["AWS", "AZURE"])
def test_running_is_idempotent(module_args, client, env_client, platform):
    env_client.describe_environment.return_value = make_env(platform)
    client.get_default_cluster.return_value = make_summary(status=ACTIVE)

    result = run(module_args)

    assert result.changed is False
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.cluster["status"] == ACTIVE
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()
    client.wait_for_default_cluster.assert_not_called()


def test_running_returns_the_described_cluster(module_args, client, env_client):
    """RUNNING returns the describeCluster result, not the listClusters summary."""
    client.get_default_cluster.return_value = make_summary(status=ACTIVE)
    client.describe_cluster.return_value = make_cluster(
        status=ACTIVE,
        message="described",
    )

    result = run(module_args)

    client.describe_cluster.assert_called_once_with(CLUSTER_CRN)
    assert result.changed is False
    assert result.cluster["cluster_id"] == "cluster-uuid"  # only on ComputeCluster
    assert result.cluster["message"] == "described"


def test_running_falls_back_to_summary_if_describe_finds_nothing(
    module_args,
    client,
    env_client,
):
    """The cluster listed a moment ago is gone: still report what was listed."""
    client.get_default_cluster.return_value = make_summary(status=ACTIVE)
    client.describe_cluster.return_value = None

    result = run(module_args)

    assert result.changed is False
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert "cluster_id" not in result.cluster


@pytest.mark.parametrize("status", sorted(COMPUTE_CLUSTER_CREATING_STATUSES))
def test_in_progress_does_not_reinitialize(module_args, client, env_client, status):
    client.get_default_cluster.return_value = make_summary(status=status)

    result = run(module_args, wait=False)

    assert result.changed is False
    assert result.cluster["status"] == status
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()
    client.wait_for_default_cluster.assert_not_called()


def test_in_progress_waits_when_requested(module_args, client, env_client):
    client.get_default_cluster.return_value = make_summary(status=CREATING)

    result = run(module_args, wait=True)

    assert result.changed is False
    assert result.cluster["status"] == ACTIVE
    env_client.initialize_aws_compute_cluster.assert_not_called()
    client.wait_for_default_cluster.assert_called_once_with(ENV_NAME, 3600, 15)


def test_in_progress_does_not_wait_in_check_mode(module_args, client, env_client):
    client.get_default_cluster.return_value = make_summary(status=CREATING)

    result = run(module_args, _ansible_check_mode=True)

    assert result.changed is False
    assert result.cluster["status"] == CREATING
    client.wait_for_default_cluster.assert_not_called()


@pytest.mark.parametrize("status", sorted(COMPUTE_CLUSTER_FAILED_STATUSES))
def test_failed_default_cluster_fails(module_args, client, env_client, status):
    client.get_default_cluster.return_value = make_summary(
        status=status,
        message="quota exceeded",
    )

    result = run(module_args)

    assert status in result.msg
    assert "quota exceeded" in result.msg
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()


def test_failed_default_cluster_without_message(module_args, client, env_client):
    client.get_default_cluster.return_value = make_summary(status=FAILED)

    result = run(module_args)

    assert FAILED in result.msg
    assert "Unknown error" in result.msg


@pytest.mark.parametrize("status", [NULLABLE, None])
def test_null_status_is_in_progress(module_args, client, env_client, status):
    """A default cluster without a status is neither absent nor failed."""
    client.get_default_cluster.return_value = make_summary(status=status)

    result = run(module_args, wait=False)

    assert result.changed is False
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()


def test_null_status_waits_when_requested(module_args, client, env_client):
    client.get_default_cluster.return_value = make_summary(status=NULLABLE)

    result = run(module_args, wait=True)

    assert result.changed is False
    assert result.cluster["status"] == ACTIVE
    client.wait_for_default_cluster.assert_called_once_with(ENV_NAME, 3600, 15)


# ============================================================================
# Environment resolution — D8 / D9 / D10
# ============================================================================


def test_environment_crn_is_resolved_to_name(module_args, client, env_client):
    module_args({**AUTH, "environment": ENV_CRN})
    with pytest.raises(AnsibleExitJson) as result:
        compute_default.main()

    assert result.value.changed is True
    env_client.describe_environment.assert_called_once_with(ENV_CRN)
    env_client.initialize_aws_compute_cluster.assert_called_once_with(
        ENV_NAME,
        ComputeClusterConfig(),
    )
    client.get_default_cluster.assert_called_once_with(ENV_NAME)
    client.wait_for_default_cluster.assert_called_once_with(ENV_NAME, 3600, 15)


@pytest.mark.parametrize("check_mode", [False, True])
def test_unknown_environment_fails(module_args, client, env_client, check_mode):
    env_client.describe_environment.return_value = None

    result = run(module_args, _ansible_check_mode=check_mode)

    assert isinstance(result, AnsibleFailJson)
    assert ENV_NAME in result.msg
    client.get_default_cluster.assert_not_called()
    env_client.initialize_aws_compute_cluster.assert_not_called()


def test_unsupported_platform_fails(module_args, client, env_client):
    env_client.describe_environment.return_value = make_env("GCP")

    result = run(module_args)

    assert isinstance(result, AnsibleFailJson)
    assert "GCP" in result.msg
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()


def test_missing_platform_fails(module_args, client, env_client):
    env_client.describe_environment.return_value = {"environmentName": ENV_NAME}

    result = run(module_args)

    assert isinstance(result, AnsibleFailJson)
    env_client.initialize_aws_compute_cluster.assert_not_called()


@pytest.mark.parametrize("check_mode", [False, True])
def test_outbound_type_on_aws_fails(module_args, client, env_client, check_mode):
    result = run(module_args, outbound_type="udr", _ansible_check_mode=check_mode)

    assert isinstance(result, AnsibleFailJson)
    assert "outbound_type" in result.msg
    env_client.initialize_aws_compute_cluster.assert_not_called()
    client.get_default_cluster.assert_not_called()


def test_cloud_provider_is_not_a_parameter(module_args, client, env_client):
    result = run(module_args, cloud_provider="aws")

    assert isinstance(result, AnsibleFailJson)
    assert "cloud_provider" in result.msg


def test_private_cluster_and_ip_ranges_are_exclusive(module_args, client, env_client):
    result = run(
        module_args,
        private_cluster=True,
        kube_api_authorized_ip_ranges=["10.0.0.0/8"],
    )

    assert isinstance(result, AnsibleFailJson)


# ============================================================================
# check_mode / wait
# ============================================================================


@pytest.mark.parametrize("platform", ["AWS", "AZURE"])
def test_check_mode_makes_no_initialize_call(module_args, client, env_client, platform):
    env_client.describe_environment.return_value = make_env(platform)

    result = run(module_args, _ansible_check_mode=True)

    assert result.changed is True
    assert result.cluster == {}
    env_client.initialize_aws_compute_cluster.assert_not_called()
    env_client.initialize_azure_compute_cluster.assert_not_called()
    client.wait_for_default_cluster.assert_not_called()


def test_no_wait_returns_operation_id_and_empty_cluster(
    module_args,
    client,
    env_client,
):
    result = run(module_args, wait=False)

    assert result.changed is True
    assert result.operation_id == OPERATION_ID
    assert result.cluster == {}
    client.wait_for_default_cluster.assert_not_called()


def test_wait_passes_timeout_and_delay(module_args, client, env_client):
    run(module_args, timeout=120, delay=5)

    client.wait_for_default_cluster.assert_called_once_with(ENV_NAME, 120, 5)


def test_wait_result_is_rendered_with_cluster_to_result(
    module_args,
    client,
    env_client,
):
    client.wait_for_default_cluster.return_value = make_cluster(
        status=ACTIVE,
        message="all good",
    )

    result = run(module_args)

    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.cluster["message"] == "all good"
    assert "statusMessage" not in result.cluster


def test_wait_timeout_propagates_cdp_error(module_args, client, env_client):
    """CdpError is not caught by compute_default (same as compute); it propagates."""
    client.wait_for_default_cluster.side_effect = CdpError(
        "Timeout waiting for the default compute cluster",
    )
    module_args({**AUTH, "environment": ENV_NAME})

    with pytest.raises(CdpError, match="Timeout waiting for the default compute"):
        compute_default.main()


# ============================================================================
# diff
# ============================================================================


def test_initialize_reports_diff(module_args, client, env_client):
    result = run(
        module_args,
        worker_node_subnets=["subnet-abc"],
        private_cluster=True,
        _ansible_diff=True,
    )

    assert result.changed is True
    assert result.diff["before"] == {}
    assert result.diff["after"] == {
        "environmentName": ENV_NAME,
        "privateCluster": True,
        "workerNodeSubnets": ["subnet-abc"],
    }


def test_minimal_initialize_diff_shows_the_target(module_args, client, env_client):
    """No options set: the config is empty, so the diff shows only the target."""
    result = run(module_args, _ansible_diff=True)

    assert result.changed is True
    assert result.diff == {
        "before": {},
        "after": {"environmentName": ENV_NAME},
    }


def test_diff_uses_the_resolved_environment_name(module_args, client, env_client):
    """A CRN given as the option is reported as the name the API receives."""
    result = run(module_args, environment=ENV_CRN, _ansible_diff=True)

    assert result.diff["after"] == {"environmentName": ENV_NAME}


def test_azure_initialize_diff_includes_outbound_type(module_args, client, env_client):
    env_client.describe_environment.return_value = make_env("AZURE")

    result = run(module_args, outbound_type="udr", _ansible_diff=True)

    assert result.diff["before"] == {}
    assert result.diff["after"] == {
        "environmentName": ENV_NAME,
        "outboundType": "udr",
    }


def test_check_mode_diff_shows_the_plan(module_args, client, env_client):
    result = run(
        module_args,
        private_cluster=True,
        _ansible_check_mode=True,
        _ansible_diff=True,
    )

    assert result.changed is True
    assert result.diff["before"] == {}
    assert result.diff["after"] == {
        "environmentName": ENV_NAME,
        "privateCluster": True,
    }
    env_client.initialize_aws_compute_cluster.assert_not_called()


def test_no_diff_without_diff_mode(module_args, client, env_client):
    result = run(module_args, private_cluster=True)

    assert result.changed is True
    assert result.diff == {"before": {}, "after": {}}


@pytest.mark.parametrize(
    "status",
    [ACTIVE, CREATING, NULLABLE, None],
    ids=["running", "creating", "nullable", "none"],
)
def test_no_diff_when_nothing_changes(module_args, client, env_client, status):
    client.get_default_cluster.return_value = make_summary(status=status)

    result = run(module_args, private_cluster=True, _ansible_diff=True)

    assert result.changed is False
    assert result.diff == {"before": {}, "after": {}}


def test_failed_default_cluster_emits_no_diff(module_args, client, env_client):
    client.get_default_cluster.return_value = make_summary(status=FAILED)

    result = run(module_args, _ansible_diff=True)

    assert isinstance(result, AnsibleFailJson)
    assert "diff" not in vars(result)
