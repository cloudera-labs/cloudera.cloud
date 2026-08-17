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

from ansible_collections.cloudera.cloud.plugins.modules import (
    dw_secret_info,
)
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
def dw_secret_info_module_args(module_args, env_context):
    """Fixture to pre-populate common dw_secret_info module arguments."""

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


# Integration tests for the dw_secret_info module.
#
# The created_secret (Kubernetes) and registered_secret (cloud provider vault)
# fixtures are shared via tests/unit/plugins/conftest.py; each self-skips unless
# its gating environment variable (CDW_SECRET_VALUE / CDW_SECRET_PROVIDER_KEY) is set.


def test_list_all_secrets_k8s(dw_secret_info_module_args, existing_dw_secret_k8s):
    """Listing all secrets includes the created (Kubernetes) secret."""
    dw_secret_info_module_args({})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret_info.main()

    result = exc.value
    assert result.changed is False
    assert isinstance(result.secrets, list)

    names = [s["secretName"] for s in result.secrets]
    assert existing_dw_secret_k8s.secretName in names


def test_list_all_secrets_provider(
    dw_secret_info_module_args,
    existing_dw_secret_provider,
):
    """Listing all secrets includes the registered (cloud provider) secret."""
    dw_secret_info_module_args({})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret_info.main()

    result = exc.value
    assert result.changed is False
    assert isinstance(result.secrets, list)

    names = [s["secretName"] for s in result.secrets]
    assert existing_dw_secret_provider.secretName in names


def test_name_filter_exact_match_k8s(
    dw_secret_info_module_args,
    existing_dw_secret_k8s,
):
    """Filtering by the created secret's name returns only that secret."""
    dw_secret_info_module_args({"name": existing_dw_secret_k8s.secretName})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret_info.main()

    result = exc.value
    assert result.changed is False
    assert len(result.secrets) == 1
    assert result.secrets[0]["secretName"] == existing_dw_secret_k8s.secretName


def test_name_filter_exact_match_provider(
    dw_secret_info_module_args,
    existing_dw_secret_provider,
):
    """Filtering by the registered secret's name returns only that secret."""
    dw_secret_info_module_args({"name": existing_dw_secret_provider.secretName})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret_info.main()

    result = exc.value
    assert result.changed is False
    assert len(result.secrets) == 1
    assert result.secrets[0]["secretName"] == existing_dw_secret_provider.secretName


def test_name_filter_no_match(dw_secret_info_module_args):
    """Filtering by a nonexistent name returns an empty list."""
    dw_secret_info_module_args({"name": "nonexistent-secret-99999"})

    with pytest.raises(AnsibleExitJson) as exc:
        dw_secret_info.main()

    result = exc.value
    assert result.changed is False
    assert result.secrets == []
