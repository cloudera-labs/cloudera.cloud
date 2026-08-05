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
import re
import warnings

from typing import Callable

from ansible_collections.cloudera.cloud.plugins.modules import dw_connector
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_dw import CdpDwClient
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

HIVE_CONNECTOR_TEMPLATE = "hive"  # A valid connector template for testing
HIVE_CONNECTOR_CONFIG = {
    "connector.name": "hive",
    "fs.cache.directories": "/data/trino/caches/hive",
    "fs.cache.enabled": "true",
    "fs.cache.max-disk-usage-percentages": "30",
    "fs.cache.preferred-hosts-count": "2",
    "fs.cache.ttl": "7d",
    "hive.allow-drop-table": "true",
    "hive.collect-column-statistics-on-write": "false",
    "hive.metastore.uri": "thrift://metastore-service.{{ .Values.warehouseId }}.svc.cluster.local:9083",
    "hive.non-managed-table-writes-enabled": "true",
    "hive.security": "{{ .Values.authorizationMode }}",
    "hive.temporary-staging-directory-enabled": "{{ if and .Values.isPrivateCloud .Values.ozone .Values.ozone.enabled }}false{{ else }}true{{ end }}",
    "ranger.audit_config": "/etc/trino/ranger-hive-audit.xml",
    "ranger.hadoop_config": "/etc/trino/core-site.xml",
    "ranger.policy_mgr_ssl_config": "/etc/trino/ranger-policymgr-ssl.xml",
    "ranger.security_config": "/etc/trino/ranger-hive-security.xml",
    "ranger.service_name": "{{ .Values.rangerHiveSvcName }}",
}


@pytest.fixture
def dw_connector_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common dw_connector module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context.get("CDP_ACCESS_KEY_ID"),
                "private_key": env_context.get("CDP_PRIVATE_KEY"),
                "cluster_id": env_context.get("CDW_CLUSTER_ID"),
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def cleanup_connector(test_cdp_client, env_context):
    """Fixture that registers connector names for cleanup after the test.

    Call the returned function with one or more connector names to schedule
    them for deletion in teardown, regardless of test outcome.
    """
    names = []

    def register(*connector_names):
        names.extend(connector_names)

    yield register

    cluster_id = env_context.get("CDW_CLUSTER_ID")
    if not cluster_id:
        warnings.warn(
            f"cleanup_connector: no Data Warehouse Cluster ID: {cluster_id}. Skipping cleanup of connectors: {names}",
        )
        return
    client = CdpDwClient(api_client=test_cdp_client)
    for name in names:
        existing = client.get_connector_by_name(cluster_id, name)
        if existing is not None:
            try:
                client.delete_connector(cluster_id, existing.id)
            except Exception as exc:
                warnings.warn(
                    f"cleanup_connector: failed to delete '{name}': {exc}",
                )


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
):
    """Fixture that creates a test connector, yields it, and cleans it up after the test."""
    cluster_id = env_context.get("CDW_CLUSTER_ID")
    client = CdpDwClient(api_client=test_cdp_client)

    connector = client.create_connector(
        cluster_id=cluster_id,
        name=valid_connector_name,
        template=HIVE_CONNECTOR_TEMPLATE,
        description="Ansible integration test connector",
        config=HIVE_CONNECTOR_CONFIG,
    )
    cleanup_connector(valid_connector_name)

    yield connector


def test_present_creates_connector(
    dw_connector_module_args,
    valid_connector_name,
    cleanup_connector,
):
    """Test state=present creates a new connector and returns its details."""
    cleanup_connector(valid_connector_name)

    dw_connector_module_args(
        {
            "name": valid_connector_name,
            "template": HIVE_CONNECTOR_TEMPLATE,
            "description": "Ansible integration test connector",
            "config": HIVE_CONNECTOR_CONFIG,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True
    assert result.value.connector != {}
    assert result.value.connector.get("name") == valid_connector_name
    assert result.value.connector.get("template") == HIVE_CONNECTOR_TEMPLATE
    assert result.value.connector.get("id") is not None


def test_present_idempotent(
    dw_connector_module_args,
    valid_connector_name,
    cleanup_connector,
):
    """Test state=present is idempotent when connector already matches."""
    cleanup_connector(valid_connector_name)

    # First run: create
    dw_connector_module_args(
        {
            "name": valid_connector_name,
            "template": HIVE_CONNECTOR_TEMPLATE,
            "description": "Ansible integration test connector",
            "config": HIVE_CONNECTOR_CONFIG,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True

    # Second run: idempotent
    dw_connector_module_args(
        {
            "name": valid_connector_name,
            "template": HIVE_CONNECTOR_TEMPLATE,
            "description": "Ansible integration test connector",
            "config": HIVE_CONNECTOR_CONFIG,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is False
    assert result.value.connector.get("name") == valid_connector_name


def test_present_updates_connector(
    dw_connector_module_args,
    existing_connector,
):
    """Test state=present updates a mutable field (description)."""
    dw_connector_module_args(
        {
            "name": existing_connector.name,
            "template": existing_connector.template,
            "description": "Updated description by Ansible",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True
    assert result.value.connector.get("name") == existing_connector.name
    assert result.value.connector.get("description") == "Updated description by Ansible"


def test_tested_state_creates_and_tests(
    request,
    dw_connector_module_args,
    valid_connector_name,
    cleanup_connector,
):
    """Test state=tested creates the connector when absent, then runs a test job."""
    cleanup_connector(valid_connector_name)

    dw_connector_module_args(
        {
            "name": valid_connector_name,
            "template": HIVE_CONNECTOR_TEMPLATE,
            "state": "tested",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True
    assert result.value.connector.get("name") == valid_connector_name
    assert result.value.connector.get("id") is not None
    assert hasattr(result.value, "test_job")
    assert "jobId" in result.value.test_job
    assert result.value.test_job["jobId"] != ""


def test_tested_state_existing(dw_connector_module_args, existing_connector):
    """Test state=tested runs a test job against an existing connector."""
    dw_connector_module_args(
        {
            "name": existing_connector.name,
            "template": HIVE_CONNECTOR_TEMPLATE,
            "state": "tested",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True
    assert result.value.connector.get("name") == existing_connector.name
    assert hasattr(result.value, "test_job")
    assert "jobId" in result.value.test_job
    assert result.value.test_job["jobId"] != ""


def test_tested_state_produces_unique_job_ids(
    dw_connector_module_args,
    existing_connector,
):
    """Test that each execution of state=tested produces a distinct jobId."""
    args = {
        "name": existing_connector.name,
        "template": HIVE_CONNECTOR_TEMPLATE,
        "state": "tested",
    }

    dw_connector_module_args(args)
    with pytest.raises(AnsibleExitJson) as first:
        dw_connector.main()

    dw_connector_module_args(args)
    with pytest.raises(AnsibleExitJson) as second:
        dw_connector.main()

    first_job_id = first.value.test_job.get("jobId")
    second_job_id = second.value.test_job.get("jobId")

    assert first_job_id != ""
    assert second_job_id != ""
    assert first_job_id != second_job_id


def test_absent_deletes_connector(
    dw_connector_module_args,
    existing_connector,
):
    """Test state=absent removes an existing connector and is then idempotent."""
    # First run: delete
    dw_connector_module_args(
        {
            "name": existing_connector.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is True
    assert result.value.connector == {}

    # Second run: idempotent
    dw_connector_module_args(
        {
            "name": existing_connector.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        dw_connector.main()

    assert result.value.changed is False
    assert result.value.connector == {}
