# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import pprint
import pytest
import unittest

from ansible_collections.cloudera.cloud.plugins.modules import env_info 
from ansible_collections.cloudera.cloud.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, setup_module_args

ENV_NAME = "foobarbaz"


@unittest.skipUnless(os.getenv('CDP_PROFILE'), "CDP access parameters not set")
class TestEnvironmentIntegration(ModuleTestCase):
    
    #@unittest.skip("Focus focus focus")
    def test_list_all_environments(self):
        setup_module_args({
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleExitJson) as e:
            env_info.main()
            
        pprint.pp(e.value)

    def test_describe_environment(self):
        setup_module_args({
            "name": ENV_NAME,
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleExitJson) as e:
            env_info.main()
            
        assert len(e.value.args[0]['environments']) == 0
        pprint.pp(e.value)

if __name__ == '__main__':
    unittest.main()