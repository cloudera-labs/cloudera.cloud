#!/usr/bin/env python
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: env_proxy_info
short_description: Gather information about CDP Environment Proxies
description:
    - Gather information about CDP Environment Proxy Configurations
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that proxy configuration will be described
      - If no name is provided, all proxy configurations will be listed
    type: str
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all Proxy Configurations
- cloudera.cloud.env_proxy_info:

# Gather detailed information about a named Proxy Configuration
- cloudera.cloud.env_proxy_info:
    name: example-proxy
"""

RETURN = r"""
proxies:
    description: Details on the proxies.
    type: list
    returned: on success
    elements: dict
    contains:
        crn:
            description: The CRN of the proxy config.
            returned: always
            type: str
            sample: crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:eb6c5fc8-38fe-4c3c-8194-1a0f05edc010
        description:
            description: A description for the proxy config.
            returned: when supported
            type: str
            sample: Example proxy configuration
        host:
            description: The proxy host.
            returned: always
            type: str
            sample: example.cloudera.com
        port:
            description: The proxy port.
            returned: always
            type: int
            sample: 8443
        protocol:
            description: The proxy protocol.
            returned: always
            type: str
            sample: https
        proxyConfigName:
            description: The name of the proxy config.
            returned: always
            type: str
            sample: example-proxy-config
        user:
            description: The proxy user.
            returned: when supported
            type: str
            sample: proxy_username
sdk_out:
    description: Returns the captured CDP SDK log.
    returned: when supported
    type: str
sdk_out_lines:
    description: Returns a list of each line of the captured CDP SDK log.
    returned: when supported
    type: list
    elements: str
"""


class EnvironmentProxyInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentProxyInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")

        # Initialize return values
        self.proxy_configs = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:
            result = self.cdpy.environments.describe_proxy_config(self.name)
            if result is not None:
                self.proxy_configs = [result]
        else:
            self.proxy_configs = self.cdpy.environments.list_proxy_configs()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str", aliases=["proxyConfigName"])
        ),
        supports_check_mode=True,
    )

    result = EnvironmentProxyInfo(module)
    output = dict(
        changed=False,
        proxies=result.proxy_configs,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
