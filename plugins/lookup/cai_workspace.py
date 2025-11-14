# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc.
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
    lookup: cai_workspace
    author: Ronald Suplina (@rsuplina) <rsuplina@cloudera.com>
    short_description: Get the API URL for a CDP Public Cloud CAI (Cloudera AI) Workspace
    description:
        - Allows you to retrieve the API URL for a given CDP Public Cloud CAI Workspace.
        - If the Environment is not found or is ambiguous, the lookup will return an error.
        - If the workspace is not found, the lookup will return the C(default) value.
    version_added: "3.2.0"
    options:
        _terms:
            description:
                - The name of the CAI Workspace or list of workspace names to query.
                - Returns the API endpoint URL (instanceUrl) for each workspace.
            required: True
        environment:
            description: Name of the CDP Environment where the workspace is deployed
            type: string
            required: True
            aliases:
              - env
        default:
            description: What to return when the workspace is not found
            type: raw
            default: []
    notes:
        - You can pass the C(Undefined) object as C(default) to force an undefined error.
        - Requires C(cdpy).
"""

EXAMPLES = """
- name: Retrieve the API URL for a CAI Workspace
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.cai_workspace', 'my-workspace', env='example-env') }}"

- name: Use the workspace API URL in a task
  ansible.builtin.set_fact:
    cai_api: "{{ lookup('cloudera.cloud.cai_workspace', ml_workspace, env=cdp_env) }}"

- name: Return a default value if workspace does not exist
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.cai_workspace', 'my-workspace', env='example-env', default='http://default') }}"

- name: Retrieve API URLs for multiple workspaces
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.cai_workspace', 'workspace1', 'workspace2', env='example-env') }}"

- name: Retrieve multiple workspaces specified as a list
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.cai_workspace', ['workspace1', 'workspace2'], env='example-env') }}"
"""

RETURN = """
  _list:
    description: List of API URLs for the queried CAI Workspaces
    type: list
    elements: str
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        if not terms:
            raise AnsibleError(
                "cai_workspace lookup requires at least one workspace name",
            )

        env = self.get_option("environment")
        default = self.get_option("default")

        if not env:
            raise AnsibleError("cai_workspace lookup requires 'environment' parameter")

        results = []

        try:
            cdpy = Cdpy()

            for term in LookupBase._flatten(terms):
                workspace_name = term

                workspace = cdpy.ml.describe_workspace(name=workspace_name, env=env)

                if workspace is None:
                    if isinstance(default, list):
                        results.extend(default)
                    else:
                        results.append(default)
                else:
                    instance_url = workspace.get("instanceUrl")
                    if instance_url:
                        results.append(instance_url)
                    else:
                        if isinstance(default, list):
                            results.extend(default)
                        else:
                            results.append(default)

            return results

        except CdpError as e:
            raise AnsibleError(
                "Error retrieving CAI workspace in environment '%s': %s"
                % (env, to_native(e)),
            )
