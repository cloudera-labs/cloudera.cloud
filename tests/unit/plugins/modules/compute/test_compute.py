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
    COMPUTE_CLUSTER_ACTIVE_STATUSES,
    COMPUTE_CLUSTER_DELETED_STATUSES,
    CommonNetwork,
    CommonStatusMessage,
    ComputeCluster,
    ComputeClusterSummary,
    CreateClusterResponse,
    DeleteClusterResponse,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

CLUSTER_CRN = "crn:cdp:compute:us-west-1:tenant-uuid:cluster:cluster-uuid"
ENV_CRN = "crn:cdp:environments:us-west-1:tenant-uuid:environment:env-uuid"
ENV_NAME = "test-env"
CLUSTER_NAME = "my-compute-cluster"

AUTH = {
    "endpoint": BASE_URL,
    "access_key": ACCESS_KEY,
    "private_key": PRIVATE_KEY,
}


def make_cluster(**overrides):
    values = dict(
        clusterCrn=CLUSTER_CRN,
        clusterId="cluster-uuid",
        clusterName=CLUSTER_NAME,
        status="RUNNING",
        clusterShape="Externalized",
        isDefault=False,
        envCrn=ENV_CRN,
        envName=ENV_NAME,
    )
    values.update(overrides)
    return ComputeCluster(**values)


def make_summary(**overrides):
    values = dict(
        clusterCrn=CLUSTER_CRN,
        clusterName=CLUSTER_NAME,
        status="RUNNING",
        clusterShape="Externalized",
        isDefault=False,
    )
    values.update(overrides)
    return ComputeClusterSummary(**values)


CREATE_RESPONSE = CreateClusterResponse(
    clusterCrn=CLUSTER_CRN,
    clusterId="cluster-uuid",
    clusterStatus=CommonStatusMessage(status="CREATING"),
)


@pytest.fixture
def client(mocker):
    """Patched CdpComputeClient instance."""
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
        return_value=(FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION),
    )
    mocked = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute.CdpComputeClient",
        autospec=True,
    )
    instance = mocked.return_value
    instance.get_cluster_by_name_and_env.return_value = None
    instance.get_cluster_by_crn.return_value = None
    return instance


@pytest.fixture
def env_client(mocker):
    """Patched CdpEnvClient instance; resolves any name to ENV_CRN."""
    mocked = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.compute.CdpEnvClient",
        autospec=True,
    )
    instance = mocked.return_value
    instance.describe_environment.return_value = {
        "environmentName": ENV_NAME,
        "crn": ENV_CRN,
        "status": "AVAILABLE",
    }
    return instance


@pytest.fixture
def warn(mocker):
    return mocker.patch("ansible.module_utils.basic.AnsibleModule.warn")


def run(module_args, **params):
    module_args({**AUTH, **params})
    with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as result:
        compute.main()
    return result.value


# ============================================================================
# state=present — create
# ============================================================================


def test_create(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = make_cluster()

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN)

    assert isinstance(result, AnsibleExitJson)
    assert result.changed is True
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.cluster["status"] == "RUNNING"
    client.get_cluster_by_name_and_env.assert_called_once_with(CLUSTER_NAME, ENV_CRN)
    client.create_cluster.assert_called_once_with(
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description=None,
        network=None,
        tags=None,
        skip_validation=None,
    )
    client.wait_for_cluster_state.assert_called_once()
    assert (
        client.wait_for_cluster_state.call_args[1]["target_states"]
        == COMPUTE_CLUSTER_ACTIVE_STATUSES
    )


def test_create_with_options_builds_common_network(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = make_cluster()

    run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description="desc",
        network={
            "subnets": ["subnet-1"],
            "pod_cidr": "10.0.0.0/16",
            "service_cidr": "10.1.0.0/16",
            "outbound_type": "loadBalancer",
        },
        tags={"team": "platform"},
        skip_validation=True,
    )

    kwargs = client.create_cluster.call_args[1]
    assert kwargs["description"] == "desc"
    assert kwargs["network"] == CommonNetwork(
        subnets=["subnet-1"],
        podCidr="10.0.0.0/16",
        serviceCidr="10.1.0.0/16",
        outboundType="loadBalancer",
    )
    assert kwargs["tags"] == {"team": "platform"}
    assert kwargs["skip_validation"] is True


def test_create_empty_network_is_omitted(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = make_cluster()

    run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, network={})

    assert client.create_cluster.call_args[1]["network"] is None


def test_create_environment_crn_skips_lookup(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = make_cluster()

    run(module_args, name=CLUSTER_NAME, environment=ENV_CRN)

    env_client.describe_environment.assert_not_called()


def test_create_environment_name_is_resolved_to_crn(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.wait_for_cluster_state.return_value = make_cluster()

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_NAME)

    assert result.changed is True
    env_client.describe_environment.assert_called_once_with(ENV_NAME)
    client.get_cluster_by_name_and_env.assert_called_once_with(CLUSTER_NAME, ENV_CRN)
    assert client.create_cluster.call_args[1]["environment"] == ENV_CRN


def test_create_environment_not_found_fails(module_args, client, env_client):
    env_client.describe_environment.return_value = None

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_NAME)

    assert isinstance(result, AnsibleFailJson)
    assert ENV_NAME in result.msg
    client.create_cluster.assert_not_called()


def test_create_environment_not_found_fails_in_check_mode(
    module_args,
    client,
    env_client,
):
    env_client.describe_environment.return_value = None

    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_NAME,
        _ansible_check_mode=True,
    )

    assert isinstance(result, AnsibleFailJson)


def test_create_no_wait_describes_created_cluster(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.get_cluster_by_crn.return_value = make_cluster(status="CREATING")

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, wait=False)

    assert result.changed is True
    assert result.cluster["status"] == "CREATING"
    client.wait_for_cluster_state.assert_not_called()


def test_create_no_wait_falls_back_to_create_response(module_args, client, env_client):
    client.create_cluster.return_value = CREATE_RESPONSE
    client.get_cluster_by_crn.return_value = None  # not yet describable

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, wait=False)

    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    assert result.cluster["status"] == "CREATING"


def test_create_check_mode_returns_planned_cluster(module_args, client, env_client):
    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description="desc",
        _ansible_check_mode=True,
    )

    assert result.changed is True
    assert result.cluster["cluster_name"] == CLUSTER_NAME
    assert result.cluster["env_crn"] == ENV_CRN
    client.create_cluster.assert_not_called()
    client.wait_for_cluster_state.assert_not_called()


def test_create_reports_diff(module_args, client, env_client):
    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_NAME,
        description="desc",
        tags={"team": "platform"},
        _ansible_check_mode=True,
        _ansible_diff=True,
    )

    assert result.diff["before"] == {}
    assert result.diff["after"] == {
        "name": CLUSTER_NAME,
        "environment": ENV_CRN,
        "description": "desc",
        "tags": {"team": "platform"},
    }


def test_no_diff_without_diff_mode(module_args, client, env_client):
    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        _ansible_check_mode=True,
    )

    assert result.diff == {"before": {}, "after": {}}


# ============================================================================
# state=present — existing cluster (idempotent, warn and skip)
# ============================================================================


def existing(client, **overrides):
    client.get_cluster_by_name_and_env.return_value = make_summary()
    client.get_cluster_by_crn.return_value = make_cluster(**overrides)


def test_present_existing_is_idempotent(module_args, client, env_client, warn):
    existing(client)

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN)

    assert result.changed is False
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    client.get_cluster_by_crn.assert_called_once_with(CLUSTER_CRN)
    client.create_cluster.assert_not_called()
    client.wait_for_cluster_state.assert_not_called()
    warn.assert_not_called()


def test_present_existing_with_different_description_warns(
    module_args,
    client,
    env_client,
    warn,
):
    existing(client, description="old")

    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description="new",
    )

    assert result.changed is False
    client.create_cluster.assert_not_called()
    warn.assert_called_once()
    assert "description" in warn.call_args[0][0]


def test_present_existing_with_same_description_does_not_warn(
    module_args,
    client,
    env_client,
    warn,
):
    existing(client, description="same")

    run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description="same",
    )

    warn.assert_not_called()


SUBNETS = ["subnet-a", "subnet-b", "subnet-c"]
EKS = {
    "subnets": SUBNETS,
    "workerSubnets": SUBNETS,
    "serviceCidr": "10.100.0.0/16",
    "tags": {"team": "platform"},
}


def test_present_existing_with_matching_tags_and_network_does_not_warn(
    module_args,
    client,
    env_client,
    warn,
):
    """Live API: tags come back as ``labels``; network comes back as ``eks.subnets``."""
    existing(client, labels={"team": "platform", "extra": "x"}, eks=EKS)

    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        tags={"team": "platform"},
        network={"subnets": list(reversed(SUBNETS)), "service_cidr": "10.100.0.0/16"},
    )

    assert result.changed is False
    warn.assert_not_called()


def test_present_existing_with_different_tags_warns(
    module_args,
    client,
    env_client,
    warn,
):
    existing(client, labels={"team": "other"}, eks=EKS)

    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        tags={"team": "platform"},
    )

    assert result.changed is False
    client.create_cluster.assert_not_called()
    warn.assert_called_once()
    assert "tags" in warn.call_args[0][0]


def test_present_existing_with_missing_labels_warns(
    module_args,
    client,
    env_client,
    warn,
):
    existing(client)

    run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        tags={"team": "platform"},
    )

    warn.assert_called_once()
    assert "tags" in warn.call_args[0][0]


def test_present_existing_with_different_subnets_warns(
    module_args,
    client,
    env_client,
    warn,
):
    existing(client, eks=EKS)

    result = run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        network={"subnets": ["subnet-a", "subnet-z"]},
    )

    assert result.changed is False
    warn.assert_called_once()
    assert "network" in warn.call_args[0][0]


def test_present_existing_network_unverifiable_warns(
    module_args,
    client,
    env_client,
    warn,
):
    """No ``eks`` block (non-EKS platform) or CIDR/outbound options: cannot be verified."""
    existing(client)

    run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        network={"subnets": SUBNETS, "pod_cidr": "10.0.0.0/16"},
    )

    warn.assert_called_once()
    message = warn.call_args[0][0]
    assert "network" in message and "verified" in message


def test_present_existing_without_description_warns_when_one_supplied(
    module_args,
    client,
    env_client,
    warn,
):
    """describeCluster returns ``description`` when set, so a missing one is a difference."""
    existing(client)

    run(
        module_args,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
        description="new",
    )

    warn.assert_called_once()
    assert "description" in warn.call_args[0][0]


@pytest.mark.parametrize(
    "overrides",
    [{"isDefault": True}, {"clusterShape": "Embedded"}],
)
def test_present_crn_of_default_or_embedded_cluster_fails(
    module_args,
    client,
    env_client,
    overrides,
):
    client.get_cluster_by_crn.return_value = make_cluster(**overrides)

    result = run(
        module_args,
        crn=CLUSTER_CRN,
        name=CLUSTER_NAME,
        environment=ENV_CRN,
    )

    assert isinstance(result, AnsibleFailJson)
    client.create_cluster.assert_not_called()


# ============================================================================
# state=absent
# ============================================================================


def test_absent_deletes_and_returns_deleted_record(module_args, client, env_client):
    existing(client)
    client.delete_cluster.return_value = DeleteClusterResponse(
        clusterStatus=CommonStatusMessage(status="DELETING"),
    )
    client.wait_for_cluster_state.return_value = make_cluster(status="DELETED")

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, state="absent")

    assert result.changed is True
    assert result.cluster["status"] == "DELETED"
    client.delete_cluster.assert_called_once_with(
        cluster_crn=CLUSTER_CRN,
        force=None,
        skip_validation=None,
        skip_workloads_validation=None,
    )
    assert (
        client.wait_for_cluster_state.call_args[1]["target_states"]
        == COMPUTE_CLUSTER_DELETED_STATUSES
    )


def test_absent_cluster_gone_returns_empty_cluster(module_args, client, env_client):
    existing(client)
    client.delete_cluster.return_value = DeleteClusterResponse()
    client.wait_for_cluster_state.return_value = None

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, state="absent")

    assert result.changed is True
    assert result.cluster == {}


def test_absent_idempotent(module_args, client, env_client):
    result = run(module_args, name=CLUSTER_NAME, environment=ENV_CRN, state="absent")

    assert result.changed is False
    assert result.cluster == {}
    client.delete_cluster.assert_not_called()


def test_absent_environment_name_not_found_is_noop(module_args, client, env_client):
    env_client.describe_environment.return_value = None

    result = run(module_args, name=CLUSTER_NAME, environment=ENV_NAME, state="absent")

    assert result.changed is False
    client.get_cluster_by_name_and_env.assert_not_called()
    client.delete_cluster.assert_not_called()


def test_absent_by_crn_skips_environment_lookup(module_args, client, env_client):
    client.get_cluster_by_crn.return_value = make_cluster()
    client.delete_cluster.return_value = DeleteClusterResponse()
    client.wait_for_cluster_state.return_value = None

    result = run(module_args, crn=CLUSTER_CRN, state="absent")

    assert result.changed is True
    client.get_cluster_by_crn.assert_called_once_with(CLUSTER_CRN)
    client.get_cluster_by_name_and_env.assert_not_called()
    env_client.describe_environment.assert_not_called()


def test_absent_by_crn_of_deleted_cluster_is_idempotent(
    module_args,
    client,
    env_client,
):
    client.get_cluster_by_crn.return_value = make_cluster(status="DELETED")

    result = run(module_args, crn=CLUSTER_CRN, state="absent")

    assert result.changed is False
    client.delete_cluster.assert_not_called()


def test_absent_force_and_skip_flags(module_args, client, env_client):
    client.get_cluster_by_crn.return_value = make_cluster()
    client.delete_cluster.return_value = DeleteClusterResponse()
    client.wait_for_cluster_state.return_value = None

    run(
        module_args,
        crn=CLUSTER_CRN,
        force=True,
        skip_validation=True,
        skip_workloads_validation=True,
        state="absent",
    )

    kwargs = client.delete_cluster.call_args[1]
    assert kwargs["force"] is True
    assert kwargs["skip_validation"] is True
    assert kwargs["skip_workloads_validation"] is True


def test_absent_no_wait_returns_cluster_as_found(module_args, client, env_client):
    client.get_cluster_by_crn.return_value = make_cluster()
    client.delete_cluster.return_value = DeleteClusterResponse()

    result = run(module_args, crn=CLUSTER_CRN, wait=False, state="absent")

    assert result.changed is True
    assert result.cluster["cluster_crn"] == CLUSTER_CRN
    client.wait_for_cluster_state.assert_not_called()


def test_absent_check_mode(module_args, client, env_client):
    client.get_cluster_by_crn.return_value = make_cluster()

    result = run(
        module_args,
        crn=CLUSTER_CRN,
        state="absent",
        _ansible_check_mode=True,
    )

    assert result.changed is True
    client.delete_cluster.assert_not_called()
    client.wait_for_cluster_state.assert_not_called()


def test_absent_reports_diff(module_args, client, env_client):
    client.get_cluster_by_crn.return_value = make_cluster()

    result = run(
        module_args,
        crn=CLUSTER_CRN,
        state="absent",
        _ansible_check_mode=True,
        _ansible_diff=True,
    )

    assert result.diff["before"]["clusterCrn"] == CLUSTER_CRN
    assert result.diff["after"] == {}


@pytest.mark.parametrize(
    "overrides",
    [{"isDefault": True}, {"clusterShape": "Embedded"}],
)
def test_absent_crn_of_default_or_embedded_cluster_fails(
    module_args,
    client,
    env_client,
    overrides,
):
    client.get_cluster_by_crn.return_value = make_cluster(**overrides)

    result = run(module_args, crn=CLUSTER_CRN, state="absent")

    assert isinstance(result, AnsibleFailJson)
    client.delete_cluster.assert_not_called()


# ============================================================================
# argument validation
# ============================================================================


def test_absent_name_without_environment_fails(module_args, client, env_client):
    result = run(module_args, name=CLUSTER_NAME, state="absent")

    assert isinstance(result, AnsibleFailJson)
    assert "environment" in result.msg
    client.delete_cluster.assert_not_called()


def test_absent_requires_crn_or_name(module_args, client, env_client):
    result = run(module_args, state="absent")

    assert isinstance(result, AnsibleFailJson)


def test_present_requires_name_and_environment(module_args, client, env_client):
    result = run(module_args, name=CLUSTER_NAME)

    assert isinstance(result, AnsibleFailJson)
