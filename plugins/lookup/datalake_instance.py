# -*- coding: utf-8 -*-

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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    lookup: datalake_instance
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get the instances for a CDP Public Cloud Datalake
    description:
        - Allows you to retrieve the instances by one or more instance groups for a CDP Public Cloud Environment.
        - If the Environment or its Datalake is not found or is ambigious, the lookup will return an error.
        - If the instance group is not found, the lookup will return the C(default) value.
    version_added: "2.0.0"
    options:
        _terms:
            description:
                - Instance group name
            type: string
            required: True
        environment:
            description:
                - Name of the Environment to query
            required: True
            type: string
        detailed:
            description:
                - Whether to return the full entry for the matching Datalake instance group
            required: False
            type: boolean
            default: False
        default:
            description: What return when the instance group is not found on the Datalake
            type: any
            default: []
    notes:
        - Requires C(cdpy).
    seealso:
        - module: cloudera.cloud.env_info
          description: Cloudera CDP Public Cloud Environment module
        - module: cloudera.cloud.datalake_info
          description: Cloudera CDP Public Cloud Datalake module
"""

EXAMPLES = """
- name: Retrieve the instances for the ID Broker instance group for a CDP Public Cloud environment
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_instance', 'idbroker', environment='example-env') }}"

- name: Retrieve the full details for the instance
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_instance', 'idbroker', environment='example-env', detailed=True) }}"

- name: Retrieve the instance details for multiple instance groups
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datalake_instance', ['idbroker', 'master'], environment='example-env', wantlist=True) }}"
"""

RETURN = """
  _list:
    description: List of lists of instances
    type: list
    elements: complex
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native
from ansible.utils.display import Display

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError

display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        try:
            env = Cdpy().datalake.describe_all_datalakes(self.get_option("environment"))
            if not env:
                raise AnsibleError(
                    "No Environment found for '%s'" % self.get_option("environment"),
                )
            elif len(env) > 1:
                raise AnsibleError(
                    "Multiple Datalakes found for Enviroment '%s'"
                    % self.get_option("environment"),
                )

            all_instance_groups = {ig["name"]: ig for ig in env[0]["instanceGroups"]}
            results = []

            for term in LookupBase._flatten(terms):
                display.vvv(
                    "Filtering instance groups for %s[%s]"
                    % (self.get_option("environment"), term),
                )
                if term in all_instance_groups:
                    if self.get_option("detailed"):
                        results.append(all_instance_groups[term]["instances"])
                    else:
                        results.append(
                            [i["id"] for i in all_instance_groups[term]["instances"]],
                        )
                else:
                    results.append(self.get_option("default"))
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
