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

"""Shared fixtures for Cloudera Data Warehouse (CDW) integration tests.

These are used by both the module_utils client tests (cdp_dw) and the module
tests (dw_secret_info, dw_connector) and therefore live in the common ancestor
conftest so they need not be duplicated per test file.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re
import warnings

from typing import Callable, Generator

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    DwSecret,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    CdpTestClient,
)


@pytest.fixture
def dw_client(env_context) -> CdpDwClient:
    """Provide a live Data Warehouse client, skipping when credentials are absent."""
    api_client = CdpTestClient(
        endpoint=env_context["CDP_API_ENDPOINT"],
        access_key=env_context["CDP_ACCESS_KEY_ID"],
        private_key=env_context["CDP_PRIVATE_KEY"],
    )
    return CdpDwClient(api_client=api_client)


@pytest.fixture
def existing_dw_cluster_id(env_context) -> str:
    """Provide a valid DW cluster id from the environment."""
    return env_context["CDW_CLUSTER_ID"]


@pytest.fixture
def delete_dw_secret(
    dw_client,
    existing_dw_cluster_id,
) -> Generator[Callable[[str], None], None, None]:
    """Return a callable that registers secret names for deletion at teardown."""
    secret_names = []

    def _register(secret_name) -> None:
        secret_names.append(secret_name)

    yield _register

    for secret_name in secret_names:
        try:
            dw_client.delete_secret(existing_dw_cluster_id, secret_name)
        except Exception as e:
            warnings.warn(
                f"Failed to delete test secret {secret_name} during cleanup: {e}",
            )


@pytest.fixture
def created_dw_secret(
    request,
    dw_client,
    existing_dw_cluster_id,
    delete_dw_secret,
) -> Generator[DwSecret, None, None]:
    """Create a Kubernetes secret (gated by CDW_SECRET_VALUE) and clean it up after."""
    secret_value = os.getenv("CDW_SECRET_VALUE")
    if not secret_value:
        pytest.skip(
            "CDW_SECRET_VALUE not set; skipping Kubernetes secret creation test"
        )

    secret_name = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    secret = dw_client.create_secret(
        cluster_id=existing_dw_cluster_id,
        secret_name=secret_name,
        secret_value=secret_value,
    )

    assert isinstance(secret, DwSecret)
    delete_dw_secret(secret_name)

    yield secret


@pytest.fixture
def registered_dw_secret(
    request,
    dw_client,
    existing_dw_cluster_id,
    delete_dw_secret,
) -> Generator[DwSecret, None, None]:
    """Register a cloud-provider vault secret (gated by CDW_SECRET_PROVIDER_KEY)."""
    provider_key = os.getenv("CDW_SECRET_PROVIDER_KEY")
    if not provider_key:
        pytest.skip(
            "CDW_SECRET_PROVIDER_KEY not set; skipping cloud provider registration test",
        )

    secret_name = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    secret = dw_client.register_secret(
        cluster_id=existing_dw_cluster_id,
        secret_name=secret_name,
        secret_provider_key=provider_key,
        azure_vault_name=os.getenv("CDW_SECRET_AZURE_VAULT_NAME"),
    )

    assert isinstance(secret, DwSecret)
    delete_dw_secret(secret_name)

    yield secret
