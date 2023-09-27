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
    lookup: datahub_instance
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get the instances for a CDP Public Cloud Datahub
    description:
        - Allows you to retrieve the instances by one or more instance groups for a CDP Public Cloud Datahub.
        - If the Datahub is not found or is ambigious, the lookup will return an error.
        - If the instance group is not found, the lookup will return the C(default) value.
    options:
        _terms:
            description:
                - Instance group name
            type: string
            required: True
        datahub:
            description:
                - Name of the Datahub
            required: True
            type: string
        detailed:
            description:
                - Whether to return the full entry for the matching Datahub instance group
            required: False
            type: boolean
            default: False
        default:
            description: What return when the instance group is not found on the Datahub
            type: any
            default: []
    notes:
        - Requires C(cdpy).
    seealso:
        - module: cloudera.cloud.datahub_cluster_info
          description: Cloudera CDP Public Cloud Datahub cluster module
'''

EXAMPLES = '''
- name: Retrieve the instances for the NiFi instance group for a CDP Public Cloud Flow Management datahub
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_instance', 'nifi', datahub='example-flow-dh') }}"
    
- name: Retrieve the full details for the instance
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_instance', 'nifi', datahub='example-flow-dh', detailed=True) }}"
  
- name: Retrieve the instance details for multiple instance groups
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datahub_instance', ['nifi', 'management'], datahub='example-flow-dh', wantlist=True) }}"
'''

RETURN = '''
  _list:
    description: List of lists of instances
    type: list
    elements: complex
'''

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native
from ansible.utils.display import Display

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_service import parse_environment

display = Display()

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        try:
            datahub = Cdpy().datahub.describe_cluster(self.get_option('datahub'))
            if datahub is None:
                raise AnsibleError("No Datahub found for '%s'" % self.get_option('datahub'))
            
            all_instance_groups = {ig['name']:ig for ig in datahub['instanceGroups']}
            results = []
            flattened_terms = LookupBase._flatten(terms)
            
            if flattened_terms:
                for term in flattened_terms:
                    display.vvv("Filtering instance groups for %s[%s]" % (self.get_option('datahub'), term))
                    if term in all_instance_groups:
                        if self.get_option('detailed'):
                            results.append(all_instance_groups[term]['instances'])
                        else:
                            results.append([i['fqdn'] for i in all_instance_groups[term]['instances']])
                    else:
                        results.append(self.get_option('default'))
            else:
                if self.get_option('detailed'):
                    results.append([all_instance_groups[group]['instances'] for group in all_instance_groups])
                else:
                    results.append([i['fqdn'] for group in all_instance_groups for i in all_instance_groups[group]['instances']])
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
