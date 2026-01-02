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

import os
import pytest

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import ml_info

BASE_URL = os.getenv("CDP_API_ENDPOINT", "not set")
ACCESS_KEY = os.getenv("CDP_ACCESS_KEY_ID", "not set")
PRIVATE_KEY = os.getenv("CDP_PRIVATE_KEY", "not set")


@pytest.mark.integration_api
@pytest.mark.slow
def test_ml_info_integration(module_args):
    """Integration test for ml_info module.
    Lists all ML workspaces.
    """

    module_args(
        {
            "endpoint": os.getenv("CDP_API_ENDPOINT", BASE_URL),
            "access_key": os.getenv("CDP_ACCESS_KEY_ID", ACCESS_KEY),
            "private_key": os.getenv("CDP_PRIVATE_KEY", PRIVATE_KEY),
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        ml_info.main()

    assert hasattr(result.value, "workspaces")
    assert isinstance(result.value.workspaces, list)
    assert result.value.changed is False
