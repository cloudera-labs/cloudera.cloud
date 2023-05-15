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

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_text, to_native
from ansible.utils.display import Display

display = Display()

class CdpServiceLookupModule(LookupBase):
    def parse_services(self, terms:list, name:str, entity:dict, service:str):
        lookup = 'knoxService' if self.get_option('knox_service') else 'serviceName'
        results = []
        try: 
            for term in LookupBase._flatten(terms):
                display.vvv("%s_service lookup connecting to '%s[%s]'" % (service, name, term))
                services = [s for s in entity['endpoints']['endpoints'] if s[lookup] == term and 'serviceUrl' in s]
                if services:
                    results.append([to_text(s['serviceUrl']) for s in services])
                else:
                    results.append(self.get_option('default'))
            return results
        except KeyError as e:
            raise AnsibleError("Error parsing result for '%s':'" % (name, to_native(e)))
