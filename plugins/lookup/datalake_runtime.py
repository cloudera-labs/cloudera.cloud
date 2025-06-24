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
    lookup: datalake_runtime
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get the Datalake Runtime for CDP Public Cloud Environments
    description:
        - Allows you to retrieve the Datalake CDH Runtime for one or more CDP Public Cloud Environments.
        - If an Environment is not found or is ambigious, the lookup will return an error.
    version_added: "2.0.0"
    options:
        _terms:
            description:
                - A CDP Public Cloud Environment name.
            required: True
    notes:
        - Requires C(cdpy).
    seealso:
        - module: cloudera.cloud.datalake_runtime_info
          description: Cloudera CDP Public Cloud Datalake Runtime module
"""

EXAMPLES = """
- name: Retrieve the details for a single CDP Public Cloud Environment
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datalake_runtime', 'example-env') }}"

- name: Retrieve the details for multiple CDP Public Cloud Environments as a list
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datalake_runtime', ['example-env', 'another-env']) }}"
"""

RETURN = """
  _list:
    description: List of Runtime versions
    type: list
    elements: string
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
            results = []
            for term in terms:
                env = Cdpy().datalake.describe_all_datalakes(term)
                if not env:
                    raise AnsibleError("No Datalake found for Environment '%s'" % term)
                elif len(env) > 1:
                    raise AnsibleError(
                        "Multiple Datalakes found for Environment '%s'" % term
                    )
                results.append(env[0]["productVersions"][0]["version"])
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result: %s" % to_native(e))
        except CdpError as e:
            raise AnsibleError("Error connecting to CDP: %s" % to_native(e))
