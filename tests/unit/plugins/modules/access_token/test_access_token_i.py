# -*- coding: utf-8 -*-

# Copyright 2022 Cloudera, Inc. All Rights Reserved.
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
from tokenize import String
__metaclass__ = type

import os
import pytest
import unittest

from ansible_collections.cloudera.cloud.plugins.modules import access_token 
from ansible_collections.cloudera.cloud.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, setup_module_args


@unittest.skipUnless(os.getenv('CDP_ENDPOINT_URL'), "CDP Private Cloud API URL parameter not set")
class TestAccessToken(ModuleTestCase):
    
    def test_local(self):
        setup_module_args({
            "endpoint": os.getenv('CDP_ENDPOINT_URL'),
            "username": os.getenv('PVC_LOCAL_USER'),
            "password": os.getenv('PVC_LOCAL_PASSWORD'),
            "local": True,
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleExitJson) as e:
            access_token.main()
            
        self.assertIsInstance(e.value.args[0]['token'], str)
        self.assertGreater(len(e.value.args[0]['token']), 0)
        
    def test_local_invalid(self):
        setup_module_args({
            "endpoint": os.getenv('CDP_ENDPOINT_URL'),
            "username": os.getenv('PVC_LOCAL_USER'),
            "password": "nope",
            "local": True,
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleFailJson) as e:
            access_token.main()
            
        self.assertEquals(e.value.args[0]['status_code'], 303)

    def test_idp(self):
        setup_module_args({
            "endpoint": os.getenv('CDP_ENDPOINT_URL'),
            "username": os.getenv('PVC_IDP_USER'),
            "password": os.getenv('PVC_IDP_PASSWORD'),
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleExitJson) as e:
            access_token.main()
            
        self.assertIsInstance(e.value.args[0]['token'], str)
        self.assertGreater(len(e.value.args[0]['token']), 0)
  
    def test_idp_invalid(self):
        setup_module_args({
            "endpoint": os.getenv('CDP_ENDPOINT_URL'),
            "username": os.getenv('PVC_IDP_USER'),
            "password": "nope",
            "verify_tls": False
        })
        
        with pytest.raises(AnsibleFailJson) as e:
            access_token.main()
            
        self.assertEqual(e.value.args[0]['status_code'], 303)

if __name__ == '__main__':
    unittest.main()