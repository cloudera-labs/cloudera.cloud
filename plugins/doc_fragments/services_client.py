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


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    client_cert:
        description:
            - The path to a client certificate for authenticating to the API endpoint.
        type: path
    client_key:
        description:
            - The path to a client key for authenticating to the API endpoint.
        type: path
    debug:
        description:
            - A flag to enable debug logging of the module's execution.
        type: bool
        default: false
        required: false
        aliases:
            - debug_endpoints
    force:
        description:
            - A flag to force a refresh of the API request, ignoring any cached results.
        type: bool
        default: false
    force_basic_auth:
        description:
            - A flag to force basic authentication for API requests.
        type: bool
        default: false
    http_agent:
        description:
            - The User-Agent string to send with API requests.
        type: str
        default: cloudera-services-module
        required: false
        aliases:
            - user_agent
    page_size:
        description:
            - The number of items to return per page in a paginated API response.
        type: int
        default: 100
        required: false
        aliases:
            - default_page_size
    timeout:
        description:
            - The timeout in seconds for any API requests.
        type: int
        default: 60
        required: false
        aliases:
            - timeout_seconds
    url:
        description:
            - The base URL of the API endpoint, including the port if necessary.
        type: str
        required: true
        aliases:
            - endpoint
            - endpoint_url
    url_username:
        description:
            - The username for authenticating to the API endpoint.
        type: str
    url_password:
        description:
            - The password for authenticating to the API endpoint.
        type: str
    use_proxy:
        description:
            - A flag to enable or disable the use of a proxy for API requests.
        type: bool
        default: true
    use_gssapi:
        description:
            - A flag to enable or disable GSSAPI authentication for API requests.
        type: bool
        default: false
    validate_certs:
        description:
            - A flag to enable or disable SSL certificate validation for API requests.
        type: bool
        default: true
"""
