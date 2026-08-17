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

from typing import Callable

from ansible_collections.cloudera.cloud.plugins.modules import dw_connector
from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)
from ansible_collections.cloudera.cloud.tests.unit import (
    HIVE_CONNECTOR_CONFIG,
)


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "CDW_CLUSTER_ID",
]


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
            "template": "hive",
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
    assert result.value.connector.get("template") == "hive"
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
            "template": "hive",
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
            "template": "hive",
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
            "template": "hive",
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
            "template": "hive",
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
        "template": "hive",
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
