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
import warnings

from typing import Generator
from urllib.error import HTTPError

import pytest


from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CDE_SERVICE_REMOVABLE_STATUSES,
    CDE_SERVICE_STOPPED_STATUSES,
    CDE_VC_REMOVABLE_STATUSES,
    ServiceDescription,
    ServiceResources,
    ServiceSummary,
    VcDescription,
    VcSummary,
    check_service_updates,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]


# The de_client and existing_de_service fixtures are shared, defined in the
# common ancestor conftest (tests/unit/plugins/conftest.py).


@pytest.fixture(scope="class")
def existing_de_virtual_cluster(
    request,
    de_client,
    existing_de_service,
) -> Generator[VcDescription, None, None]:
    """Provide a virtual cluster for the session, provisioning if needed.

    If CDP_DE_VIRTUAL_CLUSTER is set (a VC name or id), that existing VC in
    C(existing_de_service) is described and returned as-is; it is never torn
    down. Otherwise a net-new, minimally-sized CORE VC is created, shared across
    the suite, and deleted at session teardown. Sizing is overridable via
    CDP_DE_VC_CPU_REQUESTS / CDP_DE_VC_MEMORY_REQUESTS.
    """
    cluster_id = existing_de_service.clusterId

    override = os.getenv("CDP_DE_VIRTUAL_CLUSTER")
    if override:
        vc = de_client.get_virtual_cluster_by_name(
            cluster_id,
            override,
        ) or de_client.describe_virtual_cluster(cluster_id, override)
        if vc is None:
            pytest.skip(f"CDP_DE_VIRTUAL_CLUSTER '{override}' not found")
        yield vc
        return

    name = "ansible-" + re.sub(r"[^a-z0-9]", "-", request.node.name.lower())[:20]

    # Reuse a name collision rather than clobber it, and do not tear it down.
    existing = de_client.get_virtual_cluster_by_name(cluster_id, name)
    if existing is not None:
        warnings.warn(
            f"DE virtual cluster {name} already exists; reusing {existing.vcId} without teardown",
        )
        yield existing
        return

    created = de_client.create_virtual_cluster(
        name=name,
        cluster_id=cluster_id,
        cpu_requests=os.getenv("CDP_DE_VC_CPU_REQUESTS", "20"),
        memory_requests=os.getenv("CDP_DE_VC_MEMORY_REQUESTS", "80Gi"),
        vc_tier="ALLP",
        spark_version="SPARK3_5_4",
        # spark_os_name="SECURITYHARDENED",
        # runtime_spot_component="NONE"
    )
    assert created is not None
    ready = de_client.wait_for_vc_state(
        cluster_id,
        created.vcId,
        CDE_VC_REMOVABLE_STATUSES,
    )

    try:
        yield ready
    finally:
        try:
            de_client.delete_virtual_cluster(cluster_id, created.vcId)
        except Exception as e:
            warnings.warn(
                f"Failed to delete test DE virtual cluster {created.vcId} during cleanup: {e}",
            )


# @pytest.mark.slow
class TestServiceIntegration:
    """Integration tests for CdpDeClient service management."""

    def test_list_services(self, de_client, existing_de_service):
        """list_services returns ServiceSummary instances."""
        services = de_client.list_services()

        assert isinstance(services, list)
        assert all(isinstance(s, ServiceSummary) for s in services)
        assert any(s.clusterId == existing_de_service.clusterId for s in services)

    def test_list_services_include_deleted(self, de_client, existing_de_service):
        """list_services(remove_deleted=False) still returns ServiceSummary instances."""
        services = de_client.list_services(remove_deleted=False)

        assert isinstance(services, list)
        assert all(isinstance(s, ServiceSummary) for s in services)
        assert any(s.clusterId == existing_de_service.clusterId for s in services)

    def test_describe_service(self, de_client, existing_de_service):
        """describe_service returns a populated ServiceDescription."""
        cluster_id = existing_de_service.clusterId

        result = de_client.describe_service(cluster_id)

        assert result is not None
        assert isinstance(result, ServiceDescription)
        assert result.clusterId == cluster_id
        assert result.name is not None
        assert result.status is not None

    def test_describe_nonexistent_service(self, de_client):
        """describe_service returns None for a service that doesn't exist."""
        result = de_client.describe_service("nonexistent-cluster-12345")

        assert result is None

    def test_get_service_by_name(self, de_client, existing_de_service):
        """get_service_by_name returns the matching ServiceDescription."""
        service_name = existing_de_service.name

        result = de_client.get_service_by_name(service_name)

        assert result is not None
        assert isinstance(result, ServiceDescription)
        assert result.name == service_name
        assert result.clusterId is not None

    def test_get_service_by_name_not_found(self, de_client):
        """get_service_by_name returns None when the service doesn't exist."""
        result = de_client.get_service_by_name("nonexistent-service-12345")

        assert result is None

    def test_service_details_completeness(self, de_client, existing_de_service):
        """describe_service reports all expected core fields."""
        result = de_client.describe_service(existing_de_service.clusterId)

        assert isinstance(result, ServiceDescription)
        assert result.clusterId == existing_de_service.clusterId
        assert result.name == existing_de_service.name
        assert result.environmentName == existing_de_service.environmentName
        assert result.status == existing_de_service.status

    def test_enable_existing_service_conflicts(self, de_client, existing_de_service):
        """enable_service on an already-enabled name/env raises HTTP 409 Conflict."""
        with pytest.raises(HTTPError) as exc:
            de_client.enable_service(
                name=existing_de_service.name,
                env=existing_de_service.environmentName,
                instance_type=os.getenv("CDP_DE_INSTANCE_TYPE", "m5.2xlarge"),
                minimum_instances=1,
                maximum_instances=1,
                minimum_spot_instances=0,
                maximum_spot_instances=0,
            )

        assert 409 == exc.value.code

    def test_update_service_scales_instances(self, de_client, disposable_de_service):
        """update_service changes maximum_instances and the change is observable.

        Uses C(disposable_de_service) to isolate changes.
        """
        service = disposable_de_service
        cluster_id = service.clusterId

        resources = service.resources
        if not isinstance(resources, ServiceResources):
            resources = ServiceResources()
        try:
            current_max = int(resources.max_instances)
        except (TypeError, ValueError):
            current_max = 1
        new_max = current_max + 1

        de_client.update_service(cluster_id=cluster_id, maximum_instances=new_max)
        ready = de_client.wait_for_service_state(
            cluster_id=cluster_id,
            target_statuses=CDE_SERVICE_REMOVABLE_STATUSES,
        )
        assert ready is not None

        # The new maximum is reflected on the read path.
        updated = de_client.describe_service(cluster_id)
        assert isinstance(updated, ServiceDescription)
        assert int(updated.resources.max_instances) == new_max

        # And no further update is reported for that value (idempotent).
        assert (
            check_service_updates(
                cluster_id=cluster_id,
                service_details=updated,
                maximum_instances=new_max,
            )
            == {}
        )

    def test_service_enable_disable_remove(self, de_client, disposable_de_service):
        """A freshly enabled service is readable, then disables to a removed state."""
        service = disposable_de_service
        cluster_id = service.clusterId

        # Enabled by the fixture to a removable state and visible on the read path.
        assert isinstance(service, ServiceDescription)
        assert cluster_id is not None
        assert service.status in CDE_SERVICE_REMOVABLE_STATUSES
        assert de_client.describe_service(cluster_id) is not None

        # Initiate the disable from a removable state, then wait to stopped.
        de_client.disable_service(cluster_id, force=True)
        result = de_client.wait_for_service_state(
            cluster_id=cluster_id,
            target_statuses=CDE_SERVICE_STOPPED_STATUSES,
        )

        # Either fully gone (None) or reported in a stopped status.
        if result is None:
            assert de_client.describe_service(cluster_id) is None
        else:
            assert result.status in CDE_SERVICE_STOPPED_STATUSES


class TestVirtualClusterIntegration:
    """Integration tests for CdpDeClient virtual cluster management."""

    def test_list_virtual_clusters(self, de_client, existing_de_service):
        """list_virtual_clusters returns VcSummary instances."""
        vcs = de_client.list_virtual_clusters(existing_de_service.clusterId)

        assert isinstance(vcs, list)
        assert all(isinstance(vc, VcSummary) for vc in vcs)

        if vcs:
            assert vcs[0].vcId is not None
            assert vcs[0].vcName is not None
            assert vcs[0].clusterId is not None

    def test_list_virtual_clusters_nonexistent_service(self, de_client):
        """list_virtual_clusters returns an empty list for a nonexistent service."""
        vcs = de_client.list_virtual_clusters("nonexistent-cluster-12345")

        assert isinstance(vcs, list)
        assert len(vcs) == 0

    def test_describe_virtual_cluster(
        self,
        de_client,
        existing_de_service,
        existing_de_virtual_cluster,
    ):
        """describe_virtual_cluster returns a populated VcDescription."""
        cluster_id = existing_de_service.clusterId
        vc_id = existing_de_virtual_cluster.vcId

        result = de_client.describe_virtual_cluster(cluster_id, vc_id)

        assert result is not None
        assert isinstance(result, VcDescription)
        assert result.vcId == vc_id
        assert result.clusterId == cluster_id
        assert result.vcName is not None

    def test_describe_virtual_cluster_not_found(self, de_client, existing_de_service):
        """describe_virtual_cluster returns None for a VC that doesn't exist."""
        result = de_client.describe_virtual_cluster(
            existing_de_service.clusterId,
            "nonexistent-vc-12345",
        )

        assert result is None

    def test_get_virtual_cluster_by_name(
        self,
        de_client,
        existing_de_service,
        existing_de_virtual_cluster,
    ):
        """get_virtual_cluster_by_name returns the matching VcDescription."""
        cluster_id = existing_de_service.clusterId
        vc_name = existing_de_virtual_cluster.vcName

        result = de_client.get_virtual_cluster_by_name(cluster_id, vc_name)

        assert result is not None
        assert isinstance(result, VcDescription)
        assert result.vcName == vc_name
        assert result.vcId is not None
        assert result.clusterId == cluster_id

    def test_get_virtual_cluster_by_name_not_found(
        self,
        de_client,
        existing_de_service,
    ):
        """get_virtual_cluster_by_name returns None when the VC doesn't exist."""
        result = de_client.get_virtual_cluster_by_name(
            existing_de_service.clusterId,
            "nonexistent-vc-12345",
        )

        assert result is None
