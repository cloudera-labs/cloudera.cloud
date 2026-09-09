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

from ansible_collections.cloudera.cloud.plugins.modules import de
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
    ServiceResources,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    required_or_skip,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

DEFAULT_INSTANCE_TYPE = "m5.2xlarge"


@pytest.fixture
def de_module_args(module_args, env_context):
    """Pre-populate common de module arguments from the env."""

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


def _service_name(request):
    return "ansible-" + re.sub(r"[^a-z0-9]", "", request.node.name.lower())[:20]


@pytest.mark.slow
def test_present_aws(request, de_module_args, cleanup_de_service):
    """Enable a service via the module, verify idempotency, then disable it."""
    # Skip the test if the required environment variables are not set
    env_name = required_or_skip("CDP_DE_ENVIRONMENT")
    subnets = required_or_skip("CDP_DE_SUBNETS").split(",")

    name = _service_name(request)

    create_args = {
        "name": name,
        "environment": env_name,
        "instance_type": DEFAULT_INSTANCE_TYPE,
        "minimum_instances": 1,
        "maximum_instances": 1,
        "minimum_spot_instances": 0,
        "maximum_spot_instances": 0,
        # "subnets": subnets,
        # "enable_public_endpoint": True,
        "state": "present",
        "wait": True,
        "timeout": 4500,
    }

    de_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()

    cleanup_de_service(exc.value.service["clusterId"])

    assert exc.value.changed is True
    assert exc.value.service["name"] == name
    assert exc.value.service["status"] in CdpDeClient.REMOVABLE_STATUSES

    # Idempotent re-run of present (no reconcilable drift)
    de_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is False


# @pytest.mark.slow
def test_present_update_aws(
    de_module_args,
    disposable_de_service,
):
    """Bump a service's maximum_instances, then re-check idempotency.

    Operates on C(disposable_de_service), a net-new service owned by this test,
    so the mutation has no side effects and the service is torn down at teardown.
    """
    service = disposable_de_service
    name = service.name
    env_name = service.environmentName
    timeout = 7200

    resources = service.resources
    if not isinstance(resources, ServiceResources):
        resources = ServiceResources()

    try:
        current_max = int(resources.max_instances)
    except (TypeError, ValueError):
        current_max = 1
    new_max = current_max + 1

    update_args = {
        "name": name,
        "environment": env_name,
        "maximum_instances": new_max,
        "state": "present",
        "wait": True,
        "timeout": timeout,
    }

    # Update maximum_instances
    de_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is True
    assert exc.value.service["resources"]["max_instances"] == new_max

    # Idempotent re-run after update
    de_module_args(update_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is False
    assert exc.value.service["resources"]["max_instances"] == new_max


@pytest.mark.slow
def test_absent_aws(de_module_args, de_client, disposable_de_service):
    """Disable an existing service via the module, then verify idempotency.

    Uses C(disposable_de_service) so the target service is owned by this test;
    the fixture disables it at teardown if the module did not.
    """
    service = disposable_de_service
    name = service.name
    env_name = service.environmentName
    timeout = 7200

    absent_args = {
        "name": name,
        "environment": env_name,
        "state": "absent",
        "wait": True,
        "timeout": timeout,
    }

    # Disable
    de_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is True

    assert de_client.get_service_by_name(name, env_name=env_name) is None

    # Idempotent re-run of absent (service already gone)
    de_module_args(absent_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is False


@pytest.mark.slow
def test_present_azure(
    request,
    de_module_args,
    env_context,
    de_client,
    cleanup_de_service,
):
    """Enable an Azure service with managed identities, verify idempotency, then disable it."""
    azure_service_identity = os.getenv("AZURE_MANAGED_IDENTITY_ID")
    azure_vc_identity = os.getenv("AZURE_VC_MANAGED_IDENTITIES")
    if not azure_service_identity or not azure_vc_identity:
        pytest.skip(
            "AZURE_MANAGED_IDENTITY_ID / AZURE_VC_MANAGED_IDENTITIES not set; "
            "skipping Azure DE service test",
        )

    name = _service_name(request)
    env_name = env_context["DE_ENV_NAME"]
    instance_type = "Standard_E16s_v4"
    timeout = 7200

    create_args = {
        "name": name,
        "environment": env_name,
        "instance_type": instance_type,
        "minimum_instances": 1,
        "maximum_instances": 1,
        "minimum_spot_instances": 0,
        "maximum_spot_instances": 0,
        "azure_service_managed_identity": azure_service_identity,
        "azure_virtual_cluster_managed_identities": azure_vc_identity,
        "state": "present",
        "wait": True,
        "timeout": timeout,
    }

    de_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()

    cleanup_de_service(exc.value.service["clusterId"])

    assert exc.value.changed is True
    assert exc.value.service["name"] == name
    assert exc.value.service["status"] in CdpDeClient.REMOVABLE_STATUSES

    # Idempotent re-run of present (service already exists)
    de_module_args(create_args)
    with pytest.raises(AnsibleExitJson) as exc:
        de.main()
    assert exc.value.changed is False
