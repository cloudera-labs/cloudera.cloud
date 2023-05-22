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
    lookup: datalake_service
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get the URL for a CDP Public Cloud Datalake service
    description:
        - Allows you to retrieve the URL for a given CDP Public Cloud Datalake service.
        - If no service name (or optionally Knox service name) is found on the specified Datalake, the lookup returns the value of I(default).
        - Otherwise, the lookup entry will be an empty list.
        - If the Datalake is not found or is ambigious, the lookup will return an error.
    options:
        _terms:
            description:
                - An endpoint C(serviceName) or list of them to lookup within the Datalake.
                - If I(knox_service=True), then these values will lookup against the endpoint C(knoxService).
            required: True
            sample:
                - CM-API
                - CM-UI
                - ATLAS_SERVER
                - RANGER_ADMIN
        environment:
            description: Name of the Environment of the Datalake to query
            type: string
        datalake:
            description: Name of the Datalake to query
            type: string
        default:
            description: What return when the service name is not found on the Datahub
            type: raw
            default: []
        knox_service:
            description: Whether the terms are C(serviceName) or C(knoxService) values.
            type: boolean
            default: False
    notes:
        - You can pass the C(Undefined) object as C(default) to force an undefined error.
        - Requires C(cdpy).
'''

EXAMPLES = '''
- name: Retrieve the details for the Ranger Admin service, via Environment reference
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datalake_service', 'RANGER_ADMIN', environment='example-env', wantlist=True) }}"
    
- name: Retrieve the details for the Ranger Admin service, via explicit Datalake reference
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datalake_service', 'RANGER_ADMIN', datalake='example-dl', wantlist=True) }}"
    
- name: Return a generated list if the service does not exist
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_service', 'NO_SERVICE', environment='example-env', default=['something', 'else']) }}"
    
- name: Return multiple services from the same Datalake
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_service', 'RANGER_ADMIN', 'ATLAS_SERVER', 'CM-API', environment='example-env') }}"
    
- name: Return multiple services, specified as a list
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_service', ['RANGER_ADMIN', 'ATLAS_SERVER', 'CM-API'], environment='example-env') }}"
    
- name: Look up via Knox service
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_service', 'ATLAS_API', environment='example-env', knox_service=True) }}"
'''

RETURN = '''
  _list:
    description: List of lists of service URLs
    type: list
    elements: list
'''

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError

from ansible_collections.cloudera.cloud.plugins.lookup.cdp_service import parse_services


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        if not self.get_option('datalake') and not self.get_option('environment'):
            raise AnsibleError("One of 'environment' or 'datalake' parameters must be present")

        try:
            dl = None
            if self.get_option('datalake'):
                dl = Cdpy().datalake.describe_datalake(self.get_option('datalake'))
                if dl is None:
                    raise AnsibleError("No Datalake found for '%s'" % self.get_option('datalake'))
            else:
                env = Cdpy().datalake.describe_all_datalakes(self.get_option('environment'))                
                if not env:
                    raise AnsibleError("No Environment found for '%s'" % self.get_option('environment'))
                elif len(env) > 1:
                    raise AnsibleError("Multiple Datalakes found for Enviroment '%s'" % self.get_option('environment'))
                dl = env[0]
            return parse_services(terms, dl['datalakeName'], dl, 'datalake', self.get_option('knox_service'), self.get_option('default'))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
