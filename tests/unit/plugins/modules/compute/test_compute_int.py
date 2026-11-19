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

"""Integration tests for the compute module.

These tests hit the live CDP API. Read-only and check-mode tests use the
session-scoped ``existing_compute_cluster`` fixture and never change anything.
The lifecycle class is slow (~50 min) and bills real cloud resources.

Required environment variables:
    CDP_API_ENDPOINT, CDP_ACCESS_KEY_ID, CDP_PRIVATE_KEY
    CDP_ENVIRONMENT_NAME
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time

from typing import Callable

import pytest

from ansible_collections.cloudera.cloud.plugins.modules import compute
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
    required_or_skip,
)


REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def compute_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Pre-populate common compute module arguments from the environment."""

    def wrapped_args(args=None):
        merged = {
            "endpoint": env_context["CDP_API_ENDPOINT"],
            "access_key": env_context["CDP_ACCESS_KEY_ID"],
            "private_key": env_context["CDP_PRIVATE_KEY"],
        }
        merged.update(args or {})
        return module_args(merged)

    return wrapped_args


def test_absent_idempotent_name_not_found(
    compute_module_args,
    existing_compute_cluster,
):
    """state=absent for a name that does not exist -> changed=False."""
    compute_module_args(
        {
            "name": "nonexistent-12345",
            "environment": existing_compute_cluster.envName,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute.main()

    assert exc.value.changed is False


def test_absent_unknown_environment_is_noop(compute_module_args):
    compute_module_args(
        {
            "name": "nonexistent-12345",
            "environment": "nonexistent-env-12345",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute.main()

    assert exc.value.changed is False


def test_present_unknown_environment_fails(compute_module_args):
    compute_module_args(
        {
            "name": "ansible-inttest-never-created",
            "environment": "nonexistent-env-12345",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleFailJson):
        compute.main()


def test_check_mode_present_new_cluster(compute_module_args, existing_compute_cluster):
    """check_mode create reports changed with a planned cluster and creates nothing."""
    compute_module_args(
        {
            "name": "ansible-inttest-check-mode",
            "environment": existing_compute_cluster.envName,
            "description": "never created",
            "state": "present",
            "_ansible_check_mode": True,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as exc:
        compute.main()

    assert exc.value.changed is True
    assert exc.value.cluster["cluster_name"] == "ansible-inttest-check-mode"
    assert exc.value.diff["before"] == {}
    assert exc.value.diff["after"]["name"] == "ansible-inttest-check-mode"


def test_crn_of_default_or_embedded_cluster_is_refused(
    compute_module_args,
    existing_compute_cluster,
):
    """Safety: the module never acts on default or embedded clusters (check mode only)."""
    if not existing_compute_cluster.isDefault and (
        existing_compute_cluster.clusterShape == "Externalized"
    ):
        pytest.skip("existing cluster is a user-managed externalized cluster")

    compute_module_args(
        {
            "crn": existing_compute_cluster.clusterCrn,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleFailJson):
        compute.main()


@pytest.mark.slow
class TestComputeLifecycle:
    """Full create -> present-idempotent -> absent -> absent-idempotent lifecycle.

    Tests within this class must run in definition order (pytest default). The
    class shares the single cluster created by the first test.
    """

    _name = f"ansible-inttest-{time.strftime('%m%d%H%M')}"
    _env_name = None
    _crn = None
    _tags = {"purpose": "ansible-inttest", "Mixed_Case": "Value"}

    def test_present_creates(self, compute_module_args, cleanup_compute_cluster):
        env_name = required_or_skip("CDP_ENVIRONMENT_NAME")

        compute_module_args(
            {
                "name": self._name,
                "environment": env_name,
                "description": "ansible integration test",
                "tags": self._tags,
                "state": "present",
                "wait": True,
                "timeout": 3600,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        crn = exc.value.cluster.get("cluster_crn")
        if crn:
            cleanup_compute_cluster(crn)

        assert exc.value.changed is True
        assert exc.value.cluster["status"] == "RUNNING"
        assert exc.value.cluster["labels"] == self._tags

        TestComputeLifecycle._env_name = env_name
        TestComputeLifecycle._crn = crn

    def test_present_idempotent(self, compute_module_args, mocker):
        """Same arguments again -> changed=False and no warning (tags/description match)."""
        if self._crn is None:
            pytest.skip("No cluster created by test_present_creates")
        warn = mocker.patch("ansible.module_utils.basic.AnsibleModule.warn")

        compute_module_args(
            {
                "name": self._name,
                "environment": self._env_name,
                "description": "ansible integration test",
                "tags": self._tags,
                "state": "present",
                "wait": False,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        assert exc.value.changed is False
        assert exc.value.cluster["cluster_crn"] == self._crn
        warn.assert_not_called()

    def test_present_with_different_tags_warns_and_is_unchanged(
        self,
        compute_module_args,
        mocker,
    ):
        if self._crn is None:
            pytest.skip("No cluster created by test_present_creates")
        warn = mocker.patch("ansible.module_utils.basic.AnsibleModule.warn")

        compute_module_args(
            {
                "name": self._name,
                "environment": self._env_name,
                "tags": {"purpose": "something-else"},
                "state": "present",
                "wait": False,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        assert exc.value.changed is False
        warn.assert_called_once()
        assert "tags" in warn.call_args[0][0]

    def test_absent_deletes(self, compute_module_args, compute_client):
        if self._crn is None:
            pytest.skip("No cluster created by test_present_creates")

        compute_module_args(
            {
                "name": self._name,
                "environment": self._env_name,
                "state": "absent",
                "wait": True,
                "timeout": 3600,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        assert exc.value.changed is True
        # Verified live: the final DELETED record is returned (no 404)
        assert exc.value.cluster["status"] == "DELETED"
        assert compute_client.describe_cluster(self._crn).status == "DELETED"

    def test_absent_idempotent(self, compute_module_args):
        """DELETED records are ignored by name lookup -> changed=False."""
        if self._crn is None:
            pytest.skip("No cluster created by test_present_creates")

        compute_module_args(
            {
                "name": self._name,
                "environment": self._env_name,
                "state": "absent",
                "wait": False,
            },
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        assert exc.value.changed is False

    def test_absent_idempotent_by_crn(self, compute_module_args):
        if self._crn is None:
            pytest.skip("No cluster created by test_present_creates")

        compute_module_args(
            {"crn": self._crn, "state": "absent", "wait": False},
        )
        with pytest.raises(AnsibleExitJson) as exc:
            compute.main()

        assert exc.value.changed is False
