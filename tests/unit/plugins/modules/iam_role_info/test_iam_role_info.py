# Copyright 2024 Cloudera, Inc. All Rights Reserved.
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
from plugins.modules import iam_role_info

from ansible_collections.cloudera.cloud.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    setup_module_args,
)


def test_get_single_role_details():
    setup_module_args({"name": "crn:iam:us-west-1:role:ClassicClustersCreator"})

    with pytest.raises(AnsibleExitJson) as e:
        iam_role_info.main()


def test_get_multiple_role_details():

    setup_module_args(
        {
            "name": [
                "crn:iam:us-west-1:role:ClassicClustersCreator",
                "crn:iam:us-west-1:role:EnvironmentCreator",
            ]
        }
    )

    with pytest.raises(AnsibleExitJson) as e:
        iam_role_info.main()


def test_get_all_role_details():
    setup_module_args({})

    with pytest.raises(AnsibleExitJson) as e:
        iam_role_info.main()
