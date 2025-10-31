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

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.cloudera.runtime.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)


def pytest_collection_modifyitems(items):
    """
    Skips tests marked 'integration_api' if CDP_ACCESS_KEY and CDP_PRIVATE_KEY
    and skips tests marked 'integration_token' if CDP_TOKEN environment variable is not set.
    """
    # Initialize skip markers
    skip_api = None
    skip_token = None
    
    # Check if the environment variables are *not* set
    if "CDP_ACCESS_KEY" not in os.environ or "CDP_PRIVATE_KEY" not in os.environ:
        # Create a skip marker for API credentials
        skip_api = pytest.mark.skip(
            reason="CDP API credentials not set in env vars. Skipping integration tests."
        )
    
    if "CDP_TOKEN" not in os.environ:
        skip_token = pytest.mark.skip(
            reason="CDP token not set in env vars. Skipping integration tests."
        )

    # Apply the marker to all tests with the 'integration' mark
    for item in items:
        if "integration_api" in item.keywords and skip_api:
            item.add_marker(skip_api)
        elif "integration_token" in item.keywords and skip_token:
            item.add_marker(skip_token)


@pytest.fixture(autouse=True)
def skip_python():
    if sys.version_info < (3, 6):
        pytest.skip(
            "Skipping on Python %s. cloudera.cloud supports Python 3.6 and higher."
            % sys.version,
        )


@pytest.fixture
def module_args():
    """Prepare module arguments"""

    def prep_args(args=dict()):
        args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
        basic._ANSIBLE_ARGS = to_bytes(args)

    return prep_args


@pytest.fixture(autouse=True)
def patch_module(monkeypatch):
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
def mock_ansible_module(mocker):
    """Fixture for mock AnsibleModule."""
    module = mocker.MagicMock()
    module.params = {}
    module.fail_json = mocker.MagicMock(side_effect=Exception("fail_json called"))
    module.exit_json = mocker.MagicMock(side_effect=Exception("exit_json called"))
    return module
