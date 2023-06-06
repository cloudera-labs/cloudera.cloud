# Copyright 2023 Cloudera, Inc.
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

DOCUMENTATION = '''
    lookup: env_domain
    author: Ronald Suplina (@rsuplina) <rsuplina@cloudera.com>
    short_description: Get infromation about Freeipa CDP domain and freeipa host private ips for selected Environment
    description:
        - Allows you to retrieve information about Freeipa Domain for a given CDP Public Cloud Environment.
        - If the Environment is not found or is ambigious, the lookup will return an error.
    options:
        _terms:
            description:
                - A CDP Public Cloud Environment name
            type: string
            required: True
        detailed:
            description:
                -  Whether to return private ip's of Freeipa hosts for selected CDP Public Clouder Environment.
            required: False
            type: boolean
            default: False

    notes:
        - Requires C(cdpy).
'''


EXAMPLES = '''
- name: Retrieve the Freeipa domain for a single CDP Public Cloud Environment
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.env_domain', 'example-env') }}"

- name: Retrieve the Freeipa domain and Private Freeipa host ips for a CDP Public Cloud Environment
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.env_domain', 'example-env' , detailed=True  ) }}"
    
 
'''

RETURN = '''
  _list:
    description: List of Freeipa domains for selected Environments
    type: list
    elements: list
'''
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_text, to_native
from ansible.utils.display import Display
from cdpy.cdpy import Cdpy
from cdpy.common import CdpError


display = Display()
class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)    
        try: 
            results = []
            for term in LookupBase._flatten(terms):
                environment = Cdpy().environments.describe_environment(term)
                freeipa_client_domain = environment['freeipa']['domain']
                results = [{'domain': freeipa_client_domain}]

            if self.get_option('detailed'):
                for term in LookupBase._flatten(terms):
                    environment = Cdpy().environments.describe_environment(term)   
                    server_ips = environment['freeipa']['serverIP']
                    results = [{'domain': freeipa_client_domain,'server_ips' : server_ips}]     
            return results

        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
