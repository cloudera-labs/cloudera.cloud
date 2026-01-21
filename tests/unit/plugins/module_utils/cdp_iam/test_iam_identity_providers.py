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
import uuid

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_iam import (
    CdpIamClient,
)


@pytest.mark.integration_api
class TestIamUserClientIntegration:
    """Integration tests for CdpIamClient user-related methods."""

    def test_list_saml_providers(self, test_cdp_client):
        """Test listing all SAML providers."""
        
        client = CdpIamClient(api_client=test_cdp_client)
        result = client.list_saml_providers()
        
        assert "samlProviders" in result
        assert isinstance(result["samlProviders"], list)


    def test_get_default_identity_provider(self, test_cdp_client):
        """Test getting the default identity provider."""
        
        client = CdpIamClient(api_client=test_cdp_client)
        result = client.get_default_identity_provider()
        
        assert "crn" in result
