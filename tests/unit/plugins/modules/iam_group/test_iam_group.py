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

from ansible_collections.cloudera.cloud.plugins.modules import iam_group


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

GROUP_NAME = "test-group"


def test_iam_group_default(module_args):
    """Test iam_group module with missing parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Expect the module to fail due to missing required parameter
    with pytest.raises(AnsibleFailJson, match="name"):
        iam_group.main()


def test_iam_group_absent(module_args, mocker):
    """Test iam_group module with missing parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": GROUP_NAME,
            "state": "absent",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpIamClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.iam_group.CdpIamClient",
        autospec=True,
    ).return_value
    client.get_group_details.return_value = GROUP_NAME

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        iam_group.main()

    assert result.value.changed is True
    assert result.value.group == {}

    # Verify CdpIamClient was called correctly
    client.get_group_details.assert_called_once_with(group_name=GROUP_NAME)
    client.delete_group.assert_called_once_with(group_name=GROUP_NAME)
