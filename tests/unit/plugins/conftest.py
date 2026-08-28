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

"""Shared fixtures for Cloudera Data Warehouse (CDW) and Data Engineering (DE)
integration tests.

These are used by both the module_utils client tests (cdp_dw, cdp_de) and the
module tests (dw_secret_info, dw_connector, de) and therefore live in the common
ancestor conftest so they need not be duplicated per test file.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import os
import re
import time
import warnings

from typing import Callable, Generator
from urllib.error import HTTPError

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
    ServiceDescription,
    ServiceResources,
)
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


##
# Data Engineering (DE) Service
##


# Session-scoped and self-contained (reads os.environ via required_or_skip
# rather than the function-scoped env_context) so the narrower-scoped DE
# fixtures can depend on it. Does no network I/O; the value is the shared client.
@pytest.fixture(scope="session")
def de_client() -> CdpDeClient:
    """Provide a live Data Engineering client, skipping when credentials are absent."""
    api_client = CdpTestClient(
        endpoint=required_or_skip("CDP_API_ENDPOINT"),
        access_key=required_or_skip("CDP_ACCESS_KEY_ID"),
        private_key=required_or_skip("CDP_PRIVATE_KEY"),
    )
    return CdpDeClient(api_client=api_client)


@pytest.fixture(scope="session")
def existing_de_service(de_client) -> Generator[ServiceDescription, None, None]:
    """Provide a Data Engineering service for the session, provisioning if needed.

    If CDP_DE_SERVICE is set (a service name or cluster id), that existing
    service is described and returned as-is; it is never torn down. Otherwise a
    net-new, minimally-sized service is enabled in CDP_DE_ENVIRONMENT (using
    a single, non-spot instance), shared across the suite, and disabled at
    session teardown.

    Enabling a DE service is slow and costly, so the create path is gated on
    CDP_DE_ENVIRONMENT being present; instance sizing is overridable via
    CDP_DE_INSTANCE_TYPE.
    """
    override = os.getenv("CDP_DE_SERVICE")
    if override:
        service = de_client.get_service_by_name(
            override,
        ) or de_client.get_service_by_cluster_id(override)
        if service is None:
            pytest.skip(f"CDP_DE_SERVICE '{override}' not found")
        yield service
        return

    env_name = required_or_skip("CDP_DE_ENVIRONMENT")
    # subnets = required_or_skip("CDP_DE_SUBNETS").split(",")
    name = "ansible-de-inttest"

    # Reuse a name collision rather than clobber it, and do not tear it down
    # since this run did not create it.
    existing = de_client.get_service_by_name(name, env_name=env_name)
    if existing is not None:
        warnings.warn(
            f"DE service {name} already exists; reusing {existing.clusterId} without teardown",
        )
        yield existing
        return

    try:
        created = de_client.enable_service(
            name=name,
            env=env_name,
            instance_type=os.getenv("CDP_DE_INSTANCE_TYPE", "r5.2xlarge"),
            minimum_instances=1,
            maximum_instances=2,
            minimum_spot_instances=0,
            maximum_spot_instances=0,
            # subnets=subnets,
            enable_public_endpoint=True,
        )
        assert created is not None
        ready = de_client.wait_for_service_state(
            created.clusterId,
            CdpDeClient.REMOVABLE_STATUSES,
        )

        yield ready
    except HTTPError as e:
        response = e.fp.read().decode("utf-8") if e.fp else ""
        error_response = json.loads(response) if response else {}
        warnings.warn(
            f"Failed to enable test DE service: {e.code} {e.msg}; Code: {error_response.get('code')}, Msg: {error_response.get('message')}",
        )
    finally:
        try:
            # Targeting a stopped status initiates the disable from a removable state.
            de_client.wait_for_service_state(
                created.clusterId,
                CdpDeClient.STOPPED_STATUSES,
                force=True,
            )
        except Exception as e:
            warnings.warn(
                f"Failed to disable test DE service {created.clusterId} during cleanup: {e}",
            )


def _resource_int(value):
    """Coerce a DE resource count (string/None/NULLABLE) to int, or None."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@pytest.fixture
def cleanup_de_service(
    de_client,
) -> Generator[Callable[[str], None], None, None]:
    """Register DE service cluster ids for disable/removal after the test.

    Call the returned function with one or more cluster ids to schedule them
    for teardown regardless of test outcome. Each is disabled (from a removable
    state) and waited to a stopped status; ids that no longer exist are skipped.
    """
    cluster_ids = []

    def register(cluster_id):
        cluster_ids.append(cluster_id)

    try:
        yield register
    finally:
        for cluster_id in cluster_ids:
            existing = de_client.get_service_by_cluster_id(cluster_id)
            if existing is None:
                continue
            try:
                # Targeting a stopped status initiates the disable from a
                # removable state.
                de_client.wait_for_service_state(
                    cluster_id=cluster_id,
                    target_statuses=CdpDeClient.STOPPED_STATUSES,
                    force=True,
                )
            except Exception as e:
                warnings.warn(
                    f"cleanup_de_service: failed to disable '{cluster_id}': {e}",
                )


@pytest.fixture
def disposable_de_service(
    request,
    de_client,
) -> Generator[ServiceDescription, None, None]:
    """Provision a net-new, minimally-sized DE service owned by a single test.

    Unlike the shared C(existing_de_service), this service is created for the
    test that requests it, so disabling it has no side effects. It is enabled in
    CDP_DE_ENVIRONMENT (single, non-spot instance; sizing overridable via
    CDP_DE_INSTANCE_TYPE) and, if the test did not already remove it, disabled at
    teardown.

    Enabling a DE service is slow and costly, so this is gated on
    CDP_DE_ENVIRONMENT being present.
    """
    env_name = required_or_skip("CDP_DE_ENVIRONMENT")
    name = "ansible-" + re.sub(r"[^a-z0-9]", "", request.node.name.lower())[:20]

    existing = de_client.get_service_by_name(name)
    if existing is not None:
        warnings.warn(
            f"Test DE service {existing.clusterId} already exists; will reuse and then teardown.",
        )

        ready = de_client.wait_for_service_state(
            existing.clusterId,
            CdpDeClient.REMOVABLE_STATUSES,
        )
    else:
        created = de_client.enable_service(
            name=name,
            env=env_name,
            instance_type=os.getenv("CDP_DE_INSTANCE_TYPE", "r5.2xlarge"),
            minimum_instances=1,
            maximum_instances=2,
            minimum_spot_instances=0,
            maximum_spot_instances=0,
        )
        assert created is not None

        ready = de_client.wait_for_service_state(
            created.clusterId,
            CdpDeClient.REMOVABLE_STATUSES,
        )

    try:
        yield ready
    finally:
        if de_client.get_service_by_cluster_id(ready.clusterId) is not None:
            try:
                # Targeting a stopped status initiates the disable from a
                # removable state.
                de_client.wait_for_service_state(
                    cluster_id=ready.clusterId,
                    target_statuses=CdpDeClient.STOPPED_STATUSES,
                    force=True,
                )
            except Exception as e:
                warnings.warn(
                    f"Failed to disable test DE service {ready.clusterId} during cleanup: {e}",
                )


@pytest.fixture
def resettable_de_service(
    de_client,
    existing_de_service,
) -> Generator[ServiceDescription, None, None]:
    """Snapshot a DE service's reconcilable configuration, yield it, then restore it.

    Captures the service's instance counts (and whitelist/load balancer CIDRs)
    before the test mutates them, then updates the service back to those values
    at teardown and waits for it to settle. Use with C(existing_de_service) for
    update/reconcile tests so they leave the shared service as they found it.
    """
    service = existing_de_service
    cluster_id = service.clusterId

    resources = service.resources
    if not isinstance(resources, ServiceResources):
        resources = ServiceResources()

    original = {
        "minimum_instances": _resource_int(resources.min_instances),
        "maximum_instances": _resource_int(resources.max_instances),
        "minimum_spot_instances": _resource_int(resources.min_spot_instances),
        "maximum_spot_instances": _resource_int(resources.max_spot_instances),
    }

    whitelist = service.whitelistIps
    if isinstance(whitelist, str) and whitelist:
        original["whitelist_ips"] = [c.strip() for c in whitelist.split(",")]
    loadbalancer = service.loadbalancerAllowlist
    if isinstance(loadbalancer, str) and loadbalancer:
        original["loadbalancer_allowlist"] = [
            c.strip() for c in loadbalancer.split(",")
        ]

    yield service

    restore = {k: v for k, v in original.items() if v is not None}
    if not restore:
        return
    try:
        de_client.update_service(cluster_id=cluster_id, **restore)
        de_client.wait_for_service_state(
            cluster_id=cluster_id,
            target_statuses=CdpDeClient.REMOVABLE_STATUSES,
        )
    except Exception as e:
        warnings.warn(
            f"Failed to restore DE service {cluster_id} config during cleanup: {e}",
        )
