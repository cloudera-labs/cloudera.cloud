# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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

import json
import os
import sys
import pytest

from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from typing import Callable
from unittest.mock import MagicMock, Mock

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
    TestCdpClient,
)

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """
    Adds an 'all' alias to run all tests.
    Skips all tests if not running Python 3.6 or higher.
    Skips tests marked 'integration_api' if CDP_ACCESS_KEY_ID and CDP_PRIVATE_KEY
    are missing, and skips 'integration_token' if CDP_TOKEN is missing.
    """

    if sys.version_info < (3, 6):
        skip_python = pytest.mark.skip(
            reason=f"Skipping on Python {sys.version}. cloudera.cloud supports Python 3.6 and higher.",
        )
        for item in items:
            item.add_marker(skip_python)
        return

    marker_expr = config.getoption("-m")
    if marker_expr == "all":
        config.option.markexpr = ""

    # Initialize skip markers
    skip_api = None
    skip_token = None

    # Check if the environment variables are *not* set
    if "CDP_ACCESS_KEY_ID" not in os.environ or "CDP_PRIVATE_KEY" not in os.environ:
        skip_api = pytest.mark.skip(
            reason="CDP API credentials not set in env vars. Skipping integration tests.",
        )

    if "CDP_TOKEN" not in os.environ:
        skip_token = pytest.mark.skip(
            reason="CDP token not set in env vars. Skipping integration tests.",
        )

    for item in items:
        if skip_api and item.get_closest_marker("integration_api"):
            item.add_marker(skip_api)
        if skip_token and item.get_closest_marker("integration_token"):
            item.add_marker(skip_token)


@pytest.fixture
def module_args() -> Callable[[dict], None]:
    """Prepare module arguments"""

    def prep_args(args=dict()):
        args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
        basic._ANSIBLE_ARGS = to_bytes(args)

    return prep_args


@pytest.fixture
def module_creds() -> dict[str, str]:
    """Prepare module credentials"""

    return {
        "access_key": os.getenv("CDP_ACCESS_KEY_ID", "test-access-key"),
        "private_key": os.getenv("CDP_PRIVATE_KEY", "test-private-key"),
        "token": os.getenv("CDP_TOKEN", "test-token"),
        "endpoint": os.getenv("CDP_API_ENDPOINT", "https://cloudera.internal/api"),
    }


@pytest.fixture(scope="module")
def env_context(request) -> dict[str, str]:
    """
    Validates and provides required environment variables for integration tests.
    Set REQUIRED_ENV_VARS in the test module to specify required variables.
    Returns a dictionary of environment variable names to their values.
    """

    required_vars = getattr(request.module, "REQUIRED_ENV_VARS", [])

    missing = [var for var in required_vars if var not in os.environ]
    if missing:
        pytest.skip(
            f"Skipping module {request.module.__name__}: "
            f"Missing required env vars: {', '.join(missing)}",
        )

    return {var: os.environ[var] for var in required_vars}


@pytest.fixture(autouse=True)
def patch_module(monkeypatch: MonkeyPatch):
    """Patch AnsibleModule to raise exceptions on success and failure"""

    def exit_json(*args, **kwargs):
        if "changed" not in kwargs:
            kwargs["changed"] = False
        raise AnsibleExitJson(kwargs)

    def fail_json(*args, **kwargs):
        kwargs["failed"] = True
        raise AnsibleFailJson(kwargs)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)


@pytest.fixture
def mock_ansible_module(mocker: MockerFixture) -> Mock:
    """Fixture for mock AnsibleModule."""
    module = mocker.Mock()
    module.params = {}
    module.fail_json = mocker.Mock(
        side_effect=AnsibleFailJson({"msg": "fail_json called"}),
    )
    module.exit_json = mocker.Mock(
        side_effect=AnsibleExitJson({"msg": "exit_json called"}),
    )
    return module


@pytest.fixture()
def mock_load_cdp_config(mocker: MockerFixture) -> MagicMock:
    """Mock the load_cdp_config function."""
    return mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
        return_value=("test-access-key", "test-private-key", "test-region"),
    )


@pytest.fixture()
def unset_cdp_env_vars(monkeypatch: MonkeyPatch):
    """Fixture to unset any prior CDP-related environment variables."""
    monkeypatch.delenv("CDP_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("CDP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("CDP_CREDENTIALS_PATH", raising=False)
    monkeypatch.delenv("CDP_PROFILE", raising=False)
    monkeypatch.delenv("CDP_REGION", raising=False)


@pytest.fixture()
def ansible_cdp_client(
    module_creds: dict[str, str],
    mock_ansible_module: Mock,
) -> AnsibleCdpClient:
    """Fixture for creating an Ansible API client instance."""

    return AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=module_creds["endpoint"],
        access_key=module_creds["access_key"],
        private_key=module_creds["private_key"],
    )


@pytest.fixture(scope="session")
def test_cdp_client() -> TestCdpClient:
    if "CDP_ACCESS_KEY_ID" not in os.environ or "CDP_PRIVATE_KEY" not in os.environ:
        pytest.skip(
            "CDP API credentials not set in env vars. Skipping integration tests.",
        )

    return TestCdpClient(
        endpoint=os.getenv("CDP_API_ENDPOINT"),  # pyright: ignore[reportArgumentType]
        access_key=os.getenv(
            "CDP_ACCESS_KEY_ID",
        ),  # pyright: ignore[reportArgumentType]
        private_key=os.getenv("CDP_PRIVATE_KEY"),  # pyright: ignore[reportArgumentType]
    )
