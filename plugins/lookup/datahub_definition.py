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
    lookup: datahub_definition
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get a Datahub definition for a CDP Public Cloud Environment
    description:
        - Allows you to retrieve the Datahub definition matching the Datalake CDH cloud platform and Runtime for one or more CDP Public Cloud Environments.
        - If an Environment is not found or is ambigious, the lookup will return an error.
    options:
        _terms:
            description:
                - A CDP Public Cloud Environment name
            type: string
            required: True
        definition:
            description:
                - Name (substring) of the Datahub definition to filter the resulting matches
            required: False
            type: string
        detailed:
            description:
                - Whether to return the full entry for the matching Datahub definitions
            required: False
            type: boolean
            default: False
        type:
            description:
                - Category of the Datahub definition to filter
            choices:
                - OPERATIONALDATABASE
                - FLOW_MANAGEMENT
                - DATAMART
                - DISCOVERY_DATA_AND_EXPLORATION
                - DATAENGINEERING
                - STREAMING
                - OTHER
            required: False
            type: string
    notes:
        - Requires C(cdpy).
        - If you encounter I(worker found in a dead state) and are running OSX, set the environment variable, C(OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES).
    seealso:
        - module: cloudera.cloud.datahub_definition_info
          description: Cloudera CDP Public Cloud Datahub definition module
'''

EXAMPLES = '''
- name: Retrieve the Datahub definition for a single CDP Public Cloud Environment
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_definition', 'example-env') }}"
    
- name: Retrieve the Datahub definition that match the given substring
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_definition', 'example-env', definition='Flow Management Light Duty') }}"
    
- name: Retrieve the only streaming Datahub definition
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_definition', 'example-env', type='STREAMING') }}"

- name: Retrieve the full details for the Datahub definition
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_definition', 'example-env', detailed=True) }}"
  
- name: Retrieve the Datahub definition details for multiple CDP Public Cloud Environments
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datahub_definition', ['example-env', 'another-env'], wantlist=True) }}"
'''

RETURN = '''
  _list:
    description: List of lists of Datahub definition
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
            all_definitions = Cdpy().datahub.list_cluster_definitions()
            results = []
            for term in terms:
                cloud_platform, raw_version, semantic_version = parse_environment(term)
                display.vvv("Filtering definitions for %s[%s][%s]" % (term, cloud_platform, semantic_version))
                
                for d in all_definitions:
                    if d['cloudPlatform'] == cloud_platform and d['productVersion'] == 'CDH %s' % semantic_version:
                        if (self.get_option('type') is not None and self.get_option('type') != d['type']) or \
                           (self.get_option('definition') is not None and self.get_option('definition') not in d['clusterDefinitionName']):
                            continue
                        results.append([d if self.get_option('detailed') else d['clusterDefinitionName']])
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
