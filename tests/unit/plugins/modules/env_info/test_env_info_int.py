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

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import env_info


# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


@pytest.fixture
def env_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common Environment module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}
        args.update(
            {
                # "endpoint": env_context["CDP_API_ENDPOINT"],
                # "access_key": env_context["CDP_ACCESS_KEY_ID"],
                # "private_key": env_context["CDP_PRIVATE_KEY"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.mark.slow
def test_env_info_list_all(env_module_args):
    """Test listing all Environments"""

    env_module_args()

    with pytest.raises(AnsibleExitJson) as result:
        env_info.main()

    assert result.value.changed is False
    assert result.value.environments is not None
    assert isinstance(result.value.environments, list)
    assert len(result.value.environments) > 0

    first_environment = result.value.environments[0]
    assert "environmentName" in first_environment
    assert "crn" in first_environment
    assert "status" in first_environment
