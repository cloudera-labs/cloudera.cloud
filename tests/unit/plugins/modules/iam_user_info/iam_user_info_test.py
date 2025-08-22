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

import pytest
from plugins.modules import iam_user_info

from ansible_collections.cloudera.cloud.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    setup_module_args,
)


def test_user_info_username():
    setup_module_args({"user_name": "mike01"})
    with pytest.raises(AnsibleExitJson) as e:
        iam_user_info.main()


def test_user_info_get_multiple_usernames():
    setup_module_args({"user_name": ["mike01", "john01"]})
    with pytest.raises(AnsibleExitJson) as e:
        iam_user_info.main()


def test_get_user_with_filter_by_first_name():
    setup_module_args({"filter": {"firstName": "Mike"}})
    with pytest.raises(AnsibleExitJson) as e:
        iam_user_info.main()


def test_get_user_filter_by_email():
    setup_module_args({"filter": {"email": "mike"}})
    with pytest.raises(AnsibleExitJson) as e:
        iam_user_info.main()


def test_get_all_users():
    setup_module_args({})
    with pytest.raises(AnsibleExitJson) as e:
        iam_user_info.main()
