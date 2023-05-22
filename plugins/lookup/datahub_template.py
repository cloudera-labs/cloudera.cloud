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
    lookup: datahub_template
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get a Datahub template for a CDP Public Cloud Environment
    description:
        - Allows you to retrieve the Datahub templates matching the Datalake CDH Runtime for one or more CDP Public Cloud Environments.
        - If an Environment is not found or is ambigious, the lookup will return an error.
    options:
        _terms:
            description:
                - A CDP Public Cloud Environment name
            type: string
            required: True
        template:
            description:
                - Name (substring) of the Datahub template to filter the resulting matches
            required: False
            type: string
        detailed:
            description:
                - Whether to return the full entry for the matching Datahub templates
            required: False
            type: boolean
            default: False
        status:
            description:
                - Category of the Datahub templates to filter
            choices:
                - USER_MANAGED
                - DEFAULT
            required: False
            type: string
    notes:
        - Requires C(cdpy).
    seealso:
        - module: cloudera.cloud.datahub_template_info
          description: Cloudera CDP Public Cloud Datahub template module
'''

EXAMPLES = '''
- name: Retrieve the Datahub templates for a single CDP Public Cloud Environment
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_template', 'example-env') }}"
    
- name: Retrieve the Datahub templates that match the given substring
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_template', 'example-env', template='Flow Management Light Duty') }}"
    
- name: Retrieve the only user-managed Datahub templates
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_template', 'example-env', status='USER_MANAGED') }}"

- name: Retrieve the full details for the Datahub templates
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_template', 'example-env', detailed=True) }}"
  
- name: Retrieve the Datahub template details for multiple CDP Public Cloud Environments
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datahub_template', ['example-env', 'another-env'], wantlist=True) }}"
'''

RETURN = '''
  _list:
    description: List of lists of Datahub templates
    type: list
    elements: complex
'''

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native
from ansible.utils.display import Display

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError

from ansible_collections.cloudera.cloud.plugins.lookup.cdp_service import parse_environment

display = Display()

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        try:
            all_templates = Cdpy().datahub.list_cluster_templates()
            results = []
            for term in terms:
                cloud_platform, raw_version, semantic_version = parse_environment(term)
                display.vvv("Filtering templates for %s[%s]" % (term, semantic_version))
                
                for t in all_templates:
                    if t['productVersion'] == 'CDH %s' % semantic_version:
                        if (self.get_option('status') is not None and self.get_option('status') != t['status']) or \
                           (self.get_option('template') is not None and self.get_option('template') not in t['clusterTemplateName']):
                            continue                        
                        results.append([t if self.get_option('detailed') else t['clusterTemplateName']])
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
