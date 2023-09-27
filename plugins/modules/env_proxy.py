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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: env_proxy
short_description: Create, update, or destroy CDP Environment Proxies
description:
    - Create, update, and destroy CDP Environment Proxies
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the proxy config
    type: str
    required: True
    aliases:
      - proxyConfigName
  description:
    description:
      - A description for the proxy config
    type: str
    required: False
  host:
    description:
      - The proxy host
      - Required when state=present
    type: str
    required: False
  port:
    description:
      - The proxy port
      - Required when state=present
    type: int
    required: False
  protocol:
    description:
      - The protocol
      - Required when state=present
    type: str
    required: False
    choices:
      - http
      - https
  noProxyHosts:
    description:
      - List of hosts that should note be proxied.
      - Format can be CIDR, [.]host[:port] (can be a subdomain) or IP[:port]. Wildcards are not accepted
    type: list
    required: False
  user:
    description:
      - The proxy user
      - NOTE - Defining this parameter will always force an proxy configuration update
    type: str
    required: False
  password:
    description:
      - The proxy password
      - NOTE - Defining this parameter will always force an proxy configuration update.
    type: str
    required: False
  state:
    description:
      - The state of the proxy
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create a proxy with a user and password
- cloudera.cloud.env_proxy:
    name: proxy-example
    host: example.cloudera.com
    port: 8443
    protocol: https
    user: foo
    password: barbazgaz

# Delete a proxy
- cloudera.cloud.env_info:
    state: absent
    name: proxy-example
'''

RETURN = r'''
---
proxy:
  description: Details on the proxy
  type: dict
  returned: on success
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
'''


class EnvironmentProxy(CdpModule):
    def __init__(self, module):
        super(EnvironmentProxy, self).__init__(module)

        # Set variables
        self.state = self._get_param('state')
        self.name = self._get_param('name')
        self.host = self._get_param('host')
        self.port = self._get_param('port')
        self.protocol = self._get_param('protocol')

        self.description = self._get_param('description')
        self.no_proxy_hosts = self._get_param('noProxyHosts')
        self.user = self._get_param('user')
        self.password = self._get_param('password')

        self._payload = dict()

        # Initialize return values
        self.proxy_config = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.environments.describe_proxy_config(self.name)

        if existing is None or len(existing) == 0:
            if self.state == 'present':
                self._create_core_payload()
                self.changed = True
                self._create_auth_payload()
                self.proxy_config = self.cdpy.environments.create_proxy_config(**self._payload)
        else:
            if self.state == 'present':
                self._create_core_payload()

                test = existing
                del test['crn']

                if self._payload != test:
                    self.changed = True

                if self.user is not None or self.password is not None:
                    self.changed = True
                    self._create_auth_payload()
                    self.module.warn('Proxy authentication details are set. Forcing update.')

                if self.changed:
                    self.cdpy.environments.delete_proxy_config(self.name)
                    self.proxy_config = self.cdpy.environments.create_proxy_config(**self._payload)
                else:
                    self.proxy_config = existing
            else:
                self.changed = True
                self.cdpy.environments.delete_proxy_config(self.name)

    def _create_core_payload(self):
        self._payload = dict(
            proxyConfigName=self.name,
            host=self.host,
            port=self.port,
            protocol=self.protocol
        )

        if self.description is not None:
            self._payload.update(description=self.description)

        if self.no_proxy_hosts is not None:
            # convert no_proxy_hosts list to a comma separated string
            self._payload.update(noProxyHosts=(','.join(self.no_proxy_hosts)))

    def _create_auth_payload(self):
        if self.user is not None:
            self._payload.update(user=self.user)

        if self.password is not None:
            self._payload.update(password=self.password)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['proxyConfigName']),
            description=dict(required=False, type='str', aliases=['desc']),
            host=dict(required=False, type='str'),
            port=dict(required=False, type='int'),
            protocol=dict(required=False, type='str'),
            noProxyHosts=dict(required=False, type='list', elements='str'),
            user=dict(required=False, type='str'),
            password=dict(required=False, type='str', no_log=True),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present')
        ),
        required_if=[
            ['state', 'present', ('host', 'port', 'protocol'), False],
        ],
        # TODO Support check mode
        supports_check_mode=False
    )

    result = EnvironmentProxy(module)

    output = dict(
        changed=result.changed,
        proxy=result.proxy_config,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
