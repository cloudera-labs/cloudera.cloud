#!/usr/bin/env python
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

import re
import requests
import urllib

from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: access_token
short_description: Retrieve a session token for a CDP user.
description:
  - Retrieve a session token for a CDP user and can be used to set the C(CDP_ACCESS_TOKEN) credential.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - requests
options:
  endpoint:
    description:
      - CDP Public or Private Cloud Control Plane API URL.
    type: str
    required: True
    aliases:
      - cdp_endpoint_url
  username:
    description:
      - CDP username.
    type: str
    required: True
  password:
    description:
      - CDP password.
      - This parameter is not logged.
    type: str
    required: True
  local_account:
    description:
      - Flag indicating if the CDP user is a local or IDP user.
    type: bool
    default: False
    aliases:
      - local
  verify_tls:
    description:
      - Verify the TLS certificates for the CDP endpoint.
    type: bool
    default: True
    aliases:
      - tls
'''

EXAMPLES = r'''
- name: Retrieve a Bearer access token for a local service account
  cloudera.cloud.access_token:
    endpoint: "https://my.cdp.console"
    username: example_service_acct
    password: V%rYse@ur8
    local: yes
  register: account_token  
'''

RETURN = r'''
---
token:
    description: The Bearer token for the user account.
    returned: always
    type: str
'''

ACCOUNT_ID_REGEX = re.compile('accountId=([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})&')


class AccessToken(object):
    def __init__(self, module):
        self.module = module

        # Set variables
        self.endpoint = self.module.params['endpoint'].strip('/')
        self.username = self.module.params['username']
        self.password = self.module.params['password']
        self.local_account = self.module.params['local_account'] if 'local_account' in self.module.params else None
        self.tls = self.module.params['verify_tls'] if 'verify_tls' in self.module.params else None

        # Initialize the return values
        self.token = ""
        self.changed = False

        # Execute logic process
        self.process()

    def process(self):
        acct_resp = requests.get(self.endpoint + "/authenticate/login",
                                 allow_redirects=True, verify=self.tls)
        acct_url = urllib.parse.urlparse(acct_resp.url)
        query_parts = acct_url.query.split('&')
        
        if not [p.startswith('accountId') for p in query_parts]:
            self.module.fail_json(msg="Unable to discover Account ID from endpoint.")
        
        if not self.module.check_mode:
            user_url = f"{self.endpoint}/authenticate/callback/{'local' if self.local_account else 'ldap'}?{acct_url.query}"
            user_resp = requests.post(user_url, data=dict(username=self.username, password=self.password),
                                    allow_redirects=False, verify=self.tls)
            
            if 'cdp-session-token' in user_resp.cookies:
                self.token = user_resp.cookies['cdp-session-token']
            elif 'cdp-pvt-session-token' in user_resp.cookies:
                self.token = user_resp.cookies['cdp-pvt-session-token']
            else:
                self.module.fail_json(msg="Unable to retrieve session token from endpoint.",
                                    status_code=user_resp.status_code, reason=user_resp.reason)
            self.changed = True

                
def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type=str, aliases=['cdp_endpoint_url']),
            username=dict(required=True, type=str),
            password=dict(required=True, type=str, no_log=True),
            local_account=dict(type=bool, default=False, aliases=['local']),
            verify_tls=dict(type=bool, default=True, aliases=['tls'])
        ),
        supports_check_mode=True
    )

    result = AccessToken(module)
    output = dict(
        changed=result.changed,
        token=result.token,
    )
    module.exit_json(**output)


if __name__ == '__main__':
    main()
