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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: env_auth_info
short_description: Gather information about CDP environment authentication details
description:
  - Gather information about CDP environment authentication details, notably the FreeIPA root certificate and 
        user keytabs.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - A target list of environments or a single environment string.
      - If no environments are specified, all environments are targeted.
    type: list
    elements: str
    required: False
    aliases:
      - environment
  root_certificate:
    description:
      - A flag indicating whether to retrieve the given environment's FreeIPA root certificate.
    type: bool
    required: False
    default: True
    aliases:
      - root_ca
      - cert
  keytab:
    description:
      - A flag to retrieve the keytabs for the given environment or environments, governed by the value of C(user).
      - If no environments are declared, all environments will be queried.
    type: bool
    required: False
    default: True
    aliases:
      - keytabs
      - user_keytabs
  user:
    description:
      - A list of user IDs or a single user ID for retrieving the keytabs from the specified environment(s).
      - If no user ID is declared, the current CDP user will be used.
    type: list
    elements: str
    required: False
    aliases:
      - users
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Retrieve only the root certificate for a single environment
- cloudera.cloud.env_auth_info:
    name: the-environment
    root_certificate: yes
    keytab: no

# Retrieve the root certificate for multiple environments
- cloudera.cloud.env_auth_info:
    name:
      - one-environment
      - two-environment
    root_certificate: yes
    keytab: no

# Retrieve the keytab details for the current CDP user for selected environments
- cloudera.cloud.env_auth_info:
    name:
      - one-environment
      - two-environment
    keytab: yes
    root_certificate: no

# Retrieve the keytab details for the specified users for selected environments
- cloudera.cloud.env_auth_info:
    name:
      - one-environment
      - two-environment
    user:
      - UserA
      - UserB
    keytab: yes
    root_certificate: no
'''

RETURN = r'''
authentication:
    description: Returns a dictionary of the environment authentication details.
    returned: always
    type: dict
    contains:
        certificates:
            description: A dictionary of environment-to-FreeIPA root certificate
            returned: when supported
            type: dict
            contains:
              _environment name_:
                description: The FreeIPA root certificate for the environment
                returned: always
                type: str
        keytabs:
            description: A dictionary of the keytabs for each specified environment by user.
            returned: when supported
            type: dict
            contains:
              _workload username_:
                description: The user's workload username.
                returned: always
                type: dict
                contains:
                  _environment name_:
                    description: The keytab for the environment. The keytab is encoded in base64.
                    returned: always
                    type: str
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


class EnvironmentAuthentication(CdpModule):
    def __init__(self, module):
        super(EnvironmentAuthentication, self).__init__(module)

        # Set Variables
        self.name = self._get_param('name')
        self.user = self._get_param('user')
        self.root_cert = self._get_param('root_certificate')
        self.keytab = self._get_param('keytab')

        # Initialize the return values
        self.auth = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.root_cert:
            certs = self.get_certificates()
            self.auth.update(certificates=certs)

        if self.keytab:
            keytabs = dict()
            actors = list()

            if self.user is None:
                actors.append(self.cdpy.iam.get_user())
            else:
                for user in self.user:
                    actor = self.cdpy.iam.get_user(user)
                    if actor is None:
                        self.module.fail_json(msg='Invalid user: %s' % user)
                    actors.append(actor)

            for actor in actors:
                user_keytabs = self.get_keytabs_for_user(actor['crn'])
                keytabs[actor['workloadUsername']] = user_keytabs

            self.auth.update(keytabs=keytabs)

    def get_certificates(self):
        certs = dict()

        if self.name is None:
            env_list = self._list_all_crns()
        else:
            env_list = self._discover_crns()

        for env in env_list:
            result = self.cdpy.environments.get_root_cert(env['crn'])
            certs[env['name']] = result

        return certs

    def get_keytabs_for_user(self, workload_user_crn):
        keytabs = dict()

        if self.name:
            for name in self.name:
                result = self.cdpy.environments.get_keytab(workload_user_crn, name)
                keytabs[name] = result
        else:
            all_envs = self.cdpy.environments.list_environments()
            for env in all_envs:
                result = self.cdpy.environments.get_keytab(workload_user_crn, env['crn'])
                keytabs[env['environmentName']] = result

        return keytabs

    def _discover_crns(self):
        converted = []
        for name in self.name:
            env = self.cdpy.environments.describe_environment(name)
            if env is not None:
                converted.append(dict(name=name, crn=env['crn']))
            else:
                self.module.fail_json(msg="Environment '%s' not found" % name)
        return converted

    def _list_all_crns(self):
        converted = []
        discovered = self.cdpy.environments.list_environments()
        for env in discovered:
            converted.append(dict(name=env['environmentName'], crn=env['crn']))
        return converted


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='list', elements='str', aliases=['environment']),
            user=dict(required=False, type='list', elements='str', aliases=['users']),
            root_certificate=dict(required=False, type='bool', aliases=['root_ca', 'cert'], default=True),
            keytab=dict(required=False, type='bool', aliases=['keytabs', 'user_keytabs'], default=True)
        ),
        supports_check_mode=True
    )

    result = EnvironmentAuthentication(module)

    output = dict(
        changed=False,
        authentication=result.auth,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
