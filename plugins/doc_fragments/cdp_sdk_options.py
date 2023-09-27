#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Cloudera, Inc. All Rights Reserved.
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

class ModuleDocFragment(object):
    DOCUMENTATION = r'''
    options:
        verify_endpoint_tls:
            description:
                - Verify the TLS certificates for the CDP endpoint.
            type: bool
            required: False
            default: True
            aliases:
                - endpoint_tls
        debug:
            description:
                - Capture the CDP SDK debug log.
            type: bool
            required: False
            default: False
            aliases:
                - debug_endpoints
    '''

    RETURN = r'''
    sdk_out:
        description: Returns the captured CDP SDK log.
        returned: when supported
        type: str
    sdk_out_lines:
        description: Returns a list of each line of the captured CDP SDK log.
        returned: when supported
        type: list
        elements: str
    '''
