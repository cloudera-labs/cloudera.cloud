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
import random
from typing import Callable, Generator

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import CdpDeClient
from ansible_collections.cloudera.cloud.plugins.modules import de

# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
    "DE_ENV_NAME",
]

DEFAULT_INSTANCE_TYPE = "r5.2xlarge"

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def de_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common DE module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def de_client(test_cdp_client) -> CdpDeClient:
    """Fixture to provide a Data Engineering client for tests."""
    return CdpDeClient(api_client=test_cdp_client)


@pytest.fixture
def de_service_disable(de_client) -> Generator[Callable[[str, str], None], None, None]:
    """
    Fixture to clean up CDE services created during integration tests.

    Registers a (name, env_name) pair for cleanup and disables + waits after the test.
    """
    services_to_cleanup = []

    def _register(name: str, env_name: str):
        services_to_cleanup.append((name, env_name))

    yield _register

    for name, env_name in services_to_cleanup:
        try:
            result = de_client.get_service_by_name(name, env_name=env_name)
            if result:
                cluster_id = result.get("service", {}).get("clusterId")
                if cluster_id:
                    de_client.wait_for_service_state(
                        cluster_id=cluster_id,
                        target_statuses=CdpDeClient.STOPPED_STATUSES,
                        timeout=7200,
                        delay=60,
                    )
        except Exception:
            pass


@pytest.fixture
def de_service_enable(
    de_client,
    de_service_disable,
    env_context,
) -> Callable[[str], dict]:
    """
    Fixture to create a CDE service for tests that need an existing service.

    Creates the service (or reuses an existing one) and registers it for cleanup.
    Returns the service details dict.
    """

    def _de_service_enable(service_name: str) -> dict:
        env_name = env_context["DE_ENV_NAME"]
        instance_type = env_context.get("DE_INSTANCE_TYPE", DEFAULT_INSTANCE_TYPE)
        de_service_disable(service_name, env_name)

        # Check if service already exists
        existing = de_client.get_service_by_name(service_name, env_name=env_name)
        if existing:
            service = existing.get("service", existing)
            current_status = service.get("status")

            # Wait for it to reach a usable state if it's transitioning
            if current_status not in CdpDeClient.REMOVABLE_STATUSES:
                cluster_id = service.get("clusterId")
                if cluster_id:
                    result = de_client.wait_for_service_state(
                        cluster_id=cluster_id,
                        target_statuses=CdpDeClient.REMOVABLE_STATUSES,
                        timeout=7200,
                        delay=60,
                    )
                    return result if result else service
            return service

        # Create a new service
        result = de_client.enable_service(
            name=service_name,
            env=env_name,
            instance_type=instance_type,
            minimum_instances=1,
            maximum_instances=2,
            minimum_spot_instances=0,
            maximum_spot_instances=0,
        )
        service = result.get("service") if result else None
        if not service:
            pytest.skip(f"Failed to create CDE service '{service_name}'")

        cluster_id = service.get("clusterId")
        if cluster_id:
            wait_result = de_client.wait_for_service_state(
                cluster_id=cluster_id,
                target_statuses=CdpDeClient.REMOVABLE_STATUSES,
                timeout=7200,
                delay=60,
            )
            return wait_result if wait_result else service

        return service

    return _de_service_enable


@pytest.mark.data_service
def test_de_service_enable(de_module_args, env_context, de_service_disable):
    """Test enabling a CDE service and verify idempotency on second run."""

    random_suffix = random.randint(100000, 999999)
    service_name = f"test-cde-{random_suffix}"
    env_name = env_context["DE_ENV_NAME"]
    instance_type = env_context.get("DE_INSTANCE_TYPE", DEFAULT_INSTANCE_TYPE)

    de_service_disable(service_name, env_name)

    # First run — enable
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("name") == service_name
    assert result.value.service.get("status") in CdpDeClient.REMOVABLE_STATUSES

    # Second run — idempotent (no config changes)
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service.get("name") == service_name


@pytest.mark.data_service
def test_de_service_update(de_module_args, env_context, de_service_disable):
    """Test updating an existing CDE service's instance counts."""

    random_suffix = random.randint(100000, 999999)
    service_name = f"test-cde-update-{random_suffix}"
    env_name = env_context["DE_ENV_NAME"]
    instance_type = env_context.get("DE_INSTANCE_TYPE", DEFAULT_INSTANCE_TYPE)

    de_service_disable(service_name, env_name)

    # First run — create service with initial config
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("name") == service_name
    assert result.value.service.get("status") in CdpDeClient.REMOVABLE_STATUSES

    # Second run — update maximum_instances
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 3,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service is not None

    # Verify idempotency after update
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 3,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False


@pytest.mark.data_service
def test_de_service_disable(de_module_args, env_context, de_service_enable):
    """Test disabling a CDE service and verify idempotency."""

    random_suffix = random.randint(100000, 999999)
    service_name = f"test-cde-disable-{random_suffix}"
    env_name = env_context["DE_ENV_NAME"]
    instance_type = env_context.get("DE_INSTANCE_TYPE", DEFAULT_INSTANCE_TYPE)

    # Ensure service exists
    existing = de_service_enable(service_name)
    assert existing is not None

    # First run — disable
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "absent",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True

    # Second run — idempotent (service already gone)
    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "absent",
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is False
    assert result.value.service == {}


@pytest.mark.data_service
def test_de_service_enable_check_mode(de_module_args, env_context, de_service_disable):
    """Test that check mode reports changed but does not create the service."""

    random_suffix = random.randint(100000, 999999)
    service_name = f"test-cde-checkmode-{random_suffix}"
    env_name = env_context["DE_ENV_NAME"]
    instance_type = env_context.get("DE_INSTANCE_TYPE", DEFAULT_INSTANCE_TYPE)

    de_module_args(
        {
            "name": service_name,
            "environment": env_name,
            "instance_type": instance_type,
            "minimum_instances": 1,
            "maximum_instances": 2,
            "minimum_spot_instances": 0,
            "maximum_spot_instances": 0,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        de.main()

    assert result.value.changed is True
    assert result.value.service == {}

    # Verify the service was NOT actually created
    from ansible_collections.cloudera.cloud.tests.unit import TestCdpClient

    test_client = TestCdpClient(
        endpoint=env_context["CDP_API_ENDPOINT"],
        access_key=env_context["CDP_ACCESS_KEY_ID"],
        private_key=env_context["CDP_PRIVATE_KEY"],
    )
    de_client = CdpDeClient(api_client=test_client)
    assert de_client.get_service_by_name(service_name, env_name=env_name) is None
