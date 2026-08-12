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

from ansible_collections.cloudera.cloud.plugins.modules import dw_secret
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]


@pytest.fixture
def dw_secret_module_args(module_args, env_context):
    """Fixture to pre-populate common dw_secret module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
                "cluster_id": env_context["CDW_CLUSTER_ID"],
            },
        )
        return module_args(args)

    return wrapped_args


def _secret_name(request):
    return re.sub(r"[^A-Za-z0-9]", "", request.node.name)


def test_present_create_idempotent(
    request,
    dw_secret_module_args,
    delete_dw_secret,
):
    """state=present creates a Kubernetes secret, then is idempotent (gated by CDW_SECRET_VALUE)."""
    secret_value = os.getenv("CDW_SECRET_VALUE")
    if not secret_value:
        pytest.skip(
            "CDW_SECRET_VALUE not set; skipping Kubernetes secret creation test",
        )

    name = _secret_name(request)
    delete_dw_secret(name)

    # First run: creates the secret
    dw_secret_module_args(
        {"name": name, "secret_value": secret_value, "state": "present"},
    )
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is True
    assert exc.value.secret["secretName"] == name

    # Second run: idempotent (secrets are immutable)
    dw_secret_module_args(
        {"name": name, "secret_value": secret_value, "state": "present"},
    )
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is False


def test_present_register_idempotent(
    request,
    dw_secret_module_args,
    delete_dw_secret,
):
    """state=present registers a provider secret, then is idempotent (gated by CDW_SECRET_PROVIDER_KEY)."""
    provider_key = os.getenv("CDW_SECRET_PROVIDER_KEY")
    if not provider_key:
        pytest.skip(
            "CDW_SECRET_PROVIDER_KEY not set; skipping cloud provider registration test",
        )

    name = _secret_name(request)
    delete_dw_secret(name)

    args = {
        "name": name,
        "secret_provider_key": provider_key,
        "state": "present",
    }
    azure_vault_name = os.getenv("CDW_SECRET_AZURE_VAULT_NAME")
    if azure_vault_name:
        args["azure_vault_name"] = azure_vault_name

    # First run: registers the secret
    dw_secret_module_args(dict(args))
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is True
    assert exc.value.secret["secretName"] == name

    # Second run: idempotent
    dw_secret_module_args(dict(args))
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is False


def test_absent_k8s(
    request,
    dw_secret_module_args,
    dw_client,
    existing_dw_cluster_id,
    created_dw_secret,
):
    """state=absent deletes a created secret (gated by CDW_SECRET_VALUE)."""

    dw_secret_module_args(
        {
            "name": created_dw_secret.secretName,
            "state": "absent",
        },
    )
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is True
    assert (
        dw_client.get_secret(existing_dw_cluster_id, created_dw_secret.secretName)
        is None
    )


def test_absent_provider(
    request,
    dw_secret_module_args,
    dw_client,
    existing_dw_cluster_id,
    registered_dw_secret,
):
    """state=absent deletes a registered secret (gated by CDW_SECRET_PROVIDER_KEY)."""

    dw_secret_module_args(
        {
            "name": registered_dw_secret.secretName,
            "state": "absent",
        },
    )
    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret.main()

    assert exc.value.changed is True
    assert (
        dw_client.get_secret(existing_dw_cluster_id, registered_dw_secret.secretName)
        is None
    )
