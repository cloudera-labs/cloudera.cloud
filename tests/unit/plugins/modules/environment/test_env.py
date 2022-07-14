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
__metaclass__ = type

import pytest
import unittest

from mock import patch

from ansible_collections.cloudera.cloud.plugins.modules import env
from ansible_collections.cloudera.cloud.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase, setup_module_args
      

class TestEnvironment(ModuleTestCase):
    
    def test_freeipa_specified(self):
        setup_module_args({
            'name': "unit-test",
            'cloud': 'aws',
            'region': 'fake_region',
            'credential': 'fake_credential',
            'public_key_id': 'fake_key',
            'vpc_id': 'fake_vpc',
            'subnet_ids': [ 'fake_subnet' ],
            'default_sg': 'fake_default_sg',
            'knox_sg': 'fake_knox_sg',
            'log_location': 'fake_log_location',
            'log_identity': 'fake_log_identity',
            'wait': False,
            'freeipa': { 'instanceCountByGroup': 3 }
        })
        
        expected = dict(
            environmentName='unit-test',
            credentialName='fake_credential',
            region='fake_region',
            enableTunnel=False,
            workloadAnalytics=True,
            logStorage=dict(
                instanceProfile='fake_log_identity',
                storageLocationBase='fake_log_location'
            ),
            authentication=dict(
                publicKeyId='fake_key'
            ),
            vpcId='fake_vpc',
            subnetIds=['fake_subnet'],
            securityAccess=dict(
                defaultSecurityGroupId='fake_default_sg',
                securityGroupIdForKnox='fake_knox_sg'
            ),
            freeIpa=dict(instanceCountByGroup=3)
        )
        
        with patch('cdpy.cdpy.CdpyEnvironments') as mocked_cdp:   
            mocked_cdp.return_value.describe_environment.return_value = None
            mocked_cdp.return_value.create_aws_environment.return_value = { 'name': 'Successful test' }
            
            with pytest.raises(AnsibleExitJson) as e:
                env.main()
                
            print("Returned: ", str(e.value))
            
            mocked_cdp.return_value.describe_environment.assert_called_once_with('unit-test')
            mocked_cdp.return_value.create_aws_environment.assert_called_once_with(**expected)
            
    def test_freeipa_default(self):
        setup_module_args({
            'name': "unit-test",
            'cloud': 'aws',
            'region': 'fake_region',
            'credential': 'fake_credential',
            'public_key_id': 'fake_key',
            'vpc_id': 'fake_vpc',
            'subnet_ids': [ 'fake_subnet' ],
            'default_sg': 'fake_default_sg',
            'knox_sg': 'fake_knox_sg',
            'log_location': 'fake_log_location',
            'log_identity': 'fake_log_identity',
            'wait': False
        })
        
        expected = dict(
            environmentName='unit-test',
            credentialName='fake_credential',
            region='fake_region',
            enableTunnel=False,
            workloadAnalytics=True,
            logStorage=dict(
                instanceProfile='fake_log_identity',
                storageLocationBase='fake_log_location'
            ),
            authentication=dict(
                publicKeyId='fake_key'
            ),
            vpcId='fake_vpc',
            subnetIds=['fake_subnet'],
            securityAccess=dict(
                defaultSecurityGroupId='fake_default_sg',
                securityGroupIdForKnox='fake_knox_sg'
            ),
            freeIpa=dict(instanceCountByGroup=2)
        )
        
        with patch('cdpy.cdpy.CdpyEnvironments') as mocked_cdp:   
            mocked_cdp.return_value.describe_environment.return_value = None
            mocked_cdp.return_value.create_aws_environment.return_value = { 'name': 'Successful test' }
            
            with pytest.raises(AnsibleExitJson) as e:
                env.main()
                
            print("Returned: ", str(e.value))
            
            mocked_cdp.return_value.describe_environment.assert_called_once_with('unit-test')
            mocked_cdp.return_value.create_aws_environment.assert_called_once_with(**expected)
        
if __name__ == '__main__':
    unittest.main()