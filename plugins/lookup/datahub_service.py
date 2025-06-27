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
    lookup: datahub_service
    author: Webster Mudge (@wmudge) <wmudge@cloudera.com>
    short_description: Get the URL for a CDP Public Cloud Datahub service
    description:
        - Allows you to retrieve the URL for a given CDP Public Cloud Datahub service.
        - If no service name (or optionally Knox service name) is found on the specified Datahub, the lookup returns the value of I(default).
        - Otherwise, the lookup entry will be an empty list.
        - If the Datahub is not found or is ambigious, the lookup will return an error.
    version_added: "2.0.0"
    options:
        _terms:
            description:
                - An endpoint C(serviceName) or list of them to lookup within the Datahub.
                - If I(knox_service=True), then these values will lookup against the endpoint C(knoxService).
                - For example, C(CM-API), C(CM-UI), C(RESOURCEMANAGER), C(IMPALAD), C(STREAMING_SQL_ENGINE), and C(NIFI_REGISTRY_SERVER).
            required: True
        datahub:
            description: Name of the Datahub to query
            type: string
            required: True
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
"""

EXAMPLES = """
- name: Retrieve the details for the NiFi Registry REST service API
  ansible.builtin.debug:
    msg: "{{ lookup('cloudera.cloud.datahub_service', 'NIFI_REGISTRY_SERVER', datahub='example-datahub', wantlist=True) }}"

- name: Return a generated list if the service does not exist
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_service', 'STREAMS_MESSAGING_MANAGER_SERVER', datahub='non-smm-datahub', default=['something']) }}"

- name: Return multiple services from the same Datahub
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_service', 'STREAMS_MESSAGING_MANAGER_SERVER', 'CM-API', datahub='example-datahub') }}"

- name: Return multiple services, specified as a list
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_service', ['STREAMS_MESSAGING_MANAGER_SERVER', 'CM-API'], datahub='example-datahub') }}"

- name: Look up via Knox service
  ansible.builtin.debug:
    msg: "{{ query('cloudera.cloud.datahub_service', 'NIFI_REST', datahub='example-datahub', knox_service=True) }}"
"""

RETURN = """
  _list:
    description: List of lists of service URLs
    type: list
    elements: list
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_service import (
    parse_services,
)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        try:
            datahub = Cdpy().datahub.describe_cluster(self.get_option("datahub"))
            if datahub is None:
                raise AnsibleError(
                    "No Datahub found for '%s'" % self.get_option("datahub"),
                )
            return parse_services(
                terms,
                self.get_option("datahub"),
                datahub,
                "datahub",
                self.get_option("knox_service"),
                self.get_option("default"),
            )
        except CdpError as e:
            raise AnsibleError(
                "Error connecting to service '%s': %s"
                % (self.get_option("datahub"), to_native(e)),
            )
