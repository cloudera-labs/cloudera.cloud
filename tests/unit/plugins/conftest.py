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
import time
import warnings

from typing import Callable, Generator

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import (
    CdpDwClient,
    Connector,
    DwSecret,
    VirtualWarehouse,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    required_or_skip,
    CdpTestClient,
    HIVE_CONNECTOR_CONFIG,
    ICEBERG_CONNECTOR_CONFIG,
)


# Virtual Warehouse lifecycle helpers for integration tests
_VW_STABLE_STATES = frozenset({"Running", "Created", "Stopped"})
_VW_FAILED_STATES = frozenset({"Failed", "Error"})


# Session-scoped and self-contained (reads os.environ directly rather than via
# the function-scoped env_context) so the class-scoped existing_vw_* fixtures can
# depend on it. These do no network I/O; the value is the single shared client.
@pytest.fixture(scope="session")
def dw_client() -> CdpDwClient:
    """Provide a live Data Warehouse client, skipping when credentials are absent."""
    api_client = CdpTestClient(
        endpoint=required_or_skip("CDP_API_ENDPOINT"),
        access_key=required_or_skip("CDP_ACCESS_KEY_ID"),
        private_key=required_or_skip("CDP_PRIVATE_KEY"),
    )
    return CdpDwClient(api_client=api_client)


@pytest.fixture(scope="session")
def existing_dw_cluster_id() -> str:
    """Provide a valid DW cluster id from the environment."""
    return required_or_skip("CDW_CLUSTER_ID")


# TODO Refactor fixture to use future CDW Data Catalog API to discover a valid catalog ID from an existing DW cluster
@pytest.fixture(scope="session")
def existing_dw_dbc_id() -> str:
    """Provide a Database Catalog id for Virtual Warehouse tests.

    Virtual Warehouse creation is slow and costly, so these tests are gated on
    C(CDW_DBC_ID) being present in the environment.
    """
    return required_or_skip("CDW_DBC_ID")


##
# Virtual Warehouse
##


def _wait_vw_stable(
    client: CdpDwClient,
    cluster_id: str,
    vw_id: str,
) -> VirtualWarehouse:
    """Poll until the Virtual Warehouse reaches a stable state, or fail."""
    timeout = int(os.getenv("CDW_VW_TIMEOUT", "3600"))
    deadline = time.time() + timeout
    while time.time() < deadline:
        vw = client.get_vw_by_id(cluster_id, vw_id)
        status = vw.status if vw is not None else None
        if status in _VW_STABLE_STATES:
            return vw
        if status in _VW_FAILED_STATES:
            raise AssertionError(f"Virtual Warehouse {vw_id} failed: {status}")
        time.sleep(15)
    raise AssertionError(
        f"Timed out waiting for Virtual Warehouse {vw_id} to stabilize",
    )


def _create_vw(
    client: CdpDwClient,
    cluster_id: str,
    dbc_id: str,
    name: str,
    vw_type: str,
) -> VirtualWarehouse:
    """Create a Virtual Warehouse and return it once stable."""
    created = client.create_vw(
        cluster_id=cluster_id,
        dbc_id=dbc_id,
        vw_type=vw_type,
        name=name,
    )
    assert created is not None
    return _wait_vw_stable(client, cluster_id, created.id)


def _provision_vw(
    request,
    dw_client: CdpDwClient,
    cluster_id: str,
    dbc_id: str,
    vw_type: str,
) -> Generator[VirtualWarehouse, None, None]:
    """Create a class-scoped Virtual Warehouse of the given type, cleaned up after.

    Uses the session-scoped C(dw_client)/C(existing_dw_*) fixtures (class scope is
    narrower than session, so this is legal). The warehouse name embeds the type
    so distinct per-type fixtures within a class never collide.
    """
    slug = re.sub(r"[^a-z0-9]", "", request.node.name.lower())[:12]
    name = f"ansible-{vw_type}-{slug}"

    existing = dw_client.get_vw_by_name(cluster_id, name)
    if existing is not None:
        warnings.warn(
            f"Virtual Warehouse {name} already exists; skipping creation and using existing VW {existing.id}",
        )
        vw = existing
    else:
        vw = _create_vw(dw_client, cluster_id, dbc_id, name, vw_type)

    try:
        yield vw
    finally:
        try:
            dw_client.delete_vw(cluster_id, vw.id)
        except Exception as e:
            warnings.warn(
                f"Failed to delete test Virtual Warehouse {vw.id} during cleanup: {e}",
            )


@pytest.fixture(scope="class")
def existing_vw_trino(
    request,
    dw_client,
    existing_dw_cluster_id,
    existing_dw_dbc_id,
) -> Generator[VirtualWarehouse, None, None]:
    """Class-scoped Trino Virtual Warehouse, shared across the suite's read/update tests."""
    yield from _provision_vw(
        request,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_dbc_id,
        "trino",
    )


@pytest.fixture(scope="class")
def existing_vw_hive(
    request,
    dw_client,
    existing_dw_cluster_id,
    existing_dw_dbc_id,
) -> Generator[VirtualWarehouse, None, None]:
    """Class-scoped Hive Virtual Warehouse, shared across the suite's read/update tests."""
    yield from _provision_vw(
        request,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_dbc_id,
        "hive",
    )


@pytest.fixture(scope="class")
def existing_vw_impala(
    request,
    dw_client,
    existing_dw_cluster_id,
    existing_dw_dbc_id,
) -> Generator[VirtualWarehouse, None, None]:
    """Class-scoped Impala Virtual Warehouse, shared across the suite's read/update tests."""
    yield from _provision_vw(
        request,
        dw_client,
        existing_dw_cluster_id,
        existing_dw_dbc_id,
        "impala",
    )


@pytest.fixture
def disposable_vw(
    request,
    dw_client,
    existing_dw_cluster_id,
    existing_dw_dbc_id,
) -> Generator[Callable[[str], VirtualWarehouse], None, None]:
    """Return a factory that creates throwaway Virtual Warehouses for destructive tests.

    Unlike the shared class-scoped C(existing_vw_*) fixtures, each warehouse
    from this factory is owned by a single test (e.g. a delete test) so removing
    it has no side effects. Any warehouse the test did not delete is cleaned up
    at teardown.
    """
    created_ids = []

    def _make(vw_type="trino") -> VirtualWarehouse:
        slug = re.sub(r"[^a-z0-9]", "", request.node.name.lower())[:12]
        name = f"ansible-{vw_type}-{slug}"
        vw = _create_vw(
            dw_client,
            existing_dw_cluster_id,
            existing_dw_dbc_id,
            name,
            vw_type,
        )
        created_ids.append(vw.id)
        return vw

    try:
        yield _make
    finally:
        for vw_id in created_ids:
            try:
                existing = dw_client.get_vw_by_id(existing_dw_cluster_id, vw_id)
                if existing:
                    dw_client.delete_vw(existing_dw_cluster_id, vw_id)
            except Exception as e:
                warnings.warn(
                    f"Failed to delete test Virtual Warehouse {vw_id} during cleanup: {e}",
                )


##
# Virtual Warehouse Secret
##


@pytest.fixture
def disposable_dw_secret(
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
            existing = dw_client.get_secret(existing_dw_cluster_id, secret_name)
            if existing:
                dw_client.delete_secret(existing_dw_cluster_id, secret_name)
        except Exception as e:
            warnings.warn(
                f"Failed to delete test secret {secret_name} during cleanup: {e}",
            )


@pytest.fixture
def existing_dw_secret_k8s(
    request,
    dw_client,
    existing_dw_cluster_id,
    disposable_dw_secret,
) -> Generator[DwSecret, None, None]:
    """Create a Kubernetes secret (gated by CDW_SECRET_VALUE) and clean it up after."""
    secret_value = os.getenv("CDW_SECRET_VALUE")
    if not secret_value:
        pytest.skip(
            "CDW_SECRET_VALUE not set; skipping Kubernetes secret creation test",
        )

    secret_name = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    secret = dw_client.create_secret(
        cluster_id=existing_dw_cluster_id,
        secret_name=secret_name,
        secret_value=secret_value,
    )

    assert isinstance(secret, DwSecret)
    disposable_dw_secret(secret_name)

    yield secret


@pytest.fixture
def existing_dw_secret_provider(
    request,
    dw_client,
    existing_dw_cluster_id,
    disposable_dw_secret,
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
    disposable_dw_secret(secret_name)

    yield secret


##
# Virtual Warehouse Connector
##


@pytest.fixture
def valid_connector_name(request):
    """Provide a unique connector name for each test, stripped to alphanumerics only."""
    return re.sub(r"[^A-Za-z0-9]", "", request.node.name)


@pytest.fixture
def existing_connector(
    test_cdp_client,
    env_context,
    valid_connector_name,
    cleanup_connector,
) -> Generator[Connector, None, None]:
    """Fixture that creates a test connector (Hive), yields it, and cleans it up after the test."""
    cluster_id = env_context.get("CDW_CLUSTER_ID")
    client = CdpDwClient(api_client=test_cdp_client)

    existing = client.get_connector_by_name(cluster_id, valid_connector_name)
    if existing is not None:
        warnings.warn(
            f"existing_connector: connector {valid_connector_name} already exists; destroying connector {existing.id}",
        )
        client.delete_connector(cluster_id, existing.id)

    connector = client.create_connector(
        cluster_id=cluster_id,
        name=valid_connector_name,
        template="hive",
        description="Ansible integration test connector",
        config=HIVE_CONNECTOR_CONFIG,
    )
    cleanup_connector(valid_connector_name)

    yield connector


@pytest.fixture
def cleanup_connector(
    test_cdp_client,
    existing_dw_cluster_id,
) -> Generator[Callable[[str], None], None, None]:
    """Fixture that registers connector names for cleanup after the test.

    Call the returned function with one or more connector names to schedule
    them for deletion in teardown, regardless of test outcome.
    """
    names = []

    def register(*connector_names):
        names.extend(connector_names)

    try:
        yield register
    finally:
        client = CdpDwClient(api_client=test_cdp_client)
        for name in names:
            existing = client.get_connector_by_name(existing_dw_cluster_id, name)
            if existing is not None:
                try:
                    client.delete_connector(existing_dw_cluster_id, existing.id)
                except Exception as exc:
                    warnings.warn(
                        f"cleanup_connector: failed to delete '{name}': {exc}",
                    )


@pytest.fixture
def disposable_connector(
    request,
    dw_client,
    existing_dw_cluster_id,
) -> Generator[Connector, None, None]:
    """Creates a test connector and ensures cleanup regardless of test outcome."""
    connector_name = re.sub(r"[^A-Za-z0-9]", "", request.node.name)
    connector_config = {
        **ICEBERG_CONNECTOR_CONFIG,
        "fs.cache.directories": "/data/trino/caches/" + connector_name,
    }

    connector = dw_client.create_connector(
        cluster_id=existing_dw_cluster_id,
        name=connector_name,
        template="iceberg",
        config=connector_config,
        description="Ansible integration test connector",
    )
    assert isinstance(connector, Connector)
    assert connector.id is not None

    yield connector

    # Cleanup — squelch any error in case test already deleted it
    try:
        dw_client.delete_connector(existing_dw_cluster_id, connector.id)
    except Exception as e:
        warnings.warn(
            f"Failed to delete test connector {connector.id} during cleanup: {e}",
        )
