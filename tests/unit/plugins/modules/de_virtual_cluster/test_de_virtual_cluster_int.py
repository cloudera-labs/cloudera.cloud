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

import os
import re

import pytest

from ansible_collections.cloudera.cloud.plugins.modules import de_virtual_cluster
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CDE_VC_REMOVABLE_STATUSES,
    CDE_VC_STOPPED_STATUSES,
    CDE_VC_SUSPENDED_STATUSES,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


@pytest.fixture
def vc_module_args(module_args, env_context):
    """Pre-populate common de_virtual_cluster module arguments from the env."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        merged = {
            "endpoint": env_context["CDP_API_ENDPOINT"],
            "access_key": env_context["CDP_ACCESS_KEY_ID"],
            "private_key": env_context["CDP_PRIVATE_KEY"],
        }
        merged.update(args)
        return module_args(merged)

    return wrapped_args


def test_present_aws(
    request,
    vc_module_args,
    existing_de_service,
    cleanup_de_virtual_cluster,
):
    """Create a Virtual Cluster via the module, verify idempotency, then tear it down.

    Created inside C(existing_de_service), the shared DE service for the suite,
    so only the Virtual Cluster itself is scoped to this test.
    """
    service = existing_de_service
    name = "ansible-" + re.sub(r"[^a-z0-9]", "-", request.node.name.lower())[:20]

    create_args = {
        "name": name,
        "environment": service.environmentName,
        "service_name": service.name,
        "cpu_requests": os.getenv("CDP_DE_VC_CPU_REQUESTS", "8"),
        "memory_requests": os.getenv("CDP_DE_VC_MEMORY_REQUESTS", "16Gi"),
        "tier": "ALLP",
        "spark_version": os.getenv("CDP_DE_VC_SPARK_VERSION", "SPARK3_5_4"),
        "state": "present",
        "wait": True,
        "timeout": 1800,
    }

    vc_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()

    cleanup_de_virtual_cluster(
        exc.value.virtual_cluster["clusterId"],
        exc.value.virtual_cluster["vcId"],
    )

    assert exc.value.changed is True
    assert exc.value.virtual_cluster["vcName"] == name
    assert exc.value.virtual_cluster["status"] in CDE_VC_REMOVABLE_STATUSES

    # Idempotent re-run of present (no configuration changes)
    vc_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is False
    assert exc.value.virtual_cluster["vcName"] == name
    assert exc.value.virtual_cluster["status"] in CDE_VC_REMOVABLE_STATUSES


def test_absent_aws(vc_module_args, de_client, disposable_de_virtual_cluster):
    """Delete an existing Virtual Cluster via the module, then verify idempotency.

    Uses C(disposable_de_virtual_cluster) so the target Virtual Cluster is owned
    by this test; the fixture deletes it at teardown if the module did not.
    """
    vc = disposable_de_virtual_cluster
    cluster_id = vc.clusterId
    name = vc.vcName
    service = de_client.describe_service(cluster_id)

    absent_args = {
        "name": name,
        "environment": service.environmentName,
        "service_name": service.name,
        "state": "absent",
        "wait": True,
        "timeout": 1800,
    }

    # Delete
    vc_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is True

    # CDE retains a record for a deleted Virtual Cluster rather than removing
    # it from listVcs, so "gone" means a stopped status, not a None result.
    deleted = de_client.get_virtual_cluster_by_name(cluster_id, name)
    assert deleted is None or deleted.status in CDE_VC_STOPPED_STATUSES

    # Idempotent re-run of absent (Virtual Cluster already gone)
    vc_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is False


def test_suspend_resume_aws(vc_module_args, de_client, disposable_de_virtual_cluster):
    """Suspend then resume a Virtual Cluster via the module, verifying idempotency.

    Uses C(disposable_de_virtual_cluster) so the target Virtual Cluster is owned
    by this test; the fixture deletes it at teardown regardless of the state
    this test leaves it in.
    """
    vc = disposable_de_virtual_cluster
    cluster_id = vc.clusterId
    name = vc.vcName
    service = de_client.describe_service(cluster_id)

    base_args = {
        "name": name,
        "environment": service.environmentName,
        "service_name": service.name,
        "wait": True,
        "timeout": 1800,
    }

    # Suspend
    vc_module_args({**base_args, "state": "suspended"})
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is True
    # The exact suspended status string is unverified against a live sandbox
    # (see CDE_VC_SUSPENDED_STATUSES); this assertion is what confirms or
    # corrects that guess.
    assert exc.value.virtual_cluster["status"] not in CDE_VC_REMOVABLE_STATUSES
    assert exc.value.virtual_cluster["status"] in CDE_VC_SUSPENDED_STATUSES

    # Idempotent re-run of suspended
    vc_module_args({**base_args, "state": "suspended"})
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is False

    # Resume
    vc_module_args({**base_args, "state": "present"})
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is True
    assert exc.value.virtual_cluster["status"] in CDE_VC_REMOVABLE_STATUSES

    # Idempotent re-run of present
    vc_module_args({**base_args, "state": "present"})
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is False


def test_update_vc_aws(vc_module_args, de_client, disposable_de_virtual_cluster):
    """Update a Virtual Cluster's access control via the module, verifying idempotency.

    Uses C(disposable_de_virtual_cluster) so the target Virtual Cluster is owned
    by this test; the fixture deletes it at teardown regardless of the state
    this test leaves it in.
    """
    vc = disposable_de_virtual_cluster
    cluster_id = vc.clusterId
    name = vc.vcName
    service = de_client.describe_service(cluster_id)

    update_args = {
        "name": name,
        "environment": service.environmentName,
        "service_name": service.name,
        "full_access_users": ["ansible-integration-test"],
        "state": "present",
        "wait": True,
        "timeout": 1800,
    }

    # Update
    vc_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is True

    # Idempotent re-run of the same update
    vc_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de_virtual_cluster.main()
    assert exc.value.changed is False
