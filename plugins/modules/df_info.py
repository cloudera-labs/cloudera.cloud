#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Cloudera, Inc. All Rights Reserved.
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: df_info
short_description: Gather information about CDP DataFlow Services
description:
    - Gather information about CDP DataFlow Services
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that DataFlow Service will be described.
    type: str
    required: False
    aliases:
      - crn
notes:
  - This feature this module is for is in Technical Preview
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all DataFlow Services
- cloudera.cloud.df_info:

# Gather detailed information about a named DataFlow Service using a name
- cloudera.cloud.df_info:
    name: example-service

# Gather detailed information about a named DataFlow Service using a CRN
- cloudera.cloud.df_info:
    crn: example-service-crn
'''

RETURN = r'''
---
environments:
  description: The information about the named DataFlow Service or DataFlow Services
  type: list
  returned: always
  elements: complex
  contains:
    crn:
      description:  The DataFlow Service's parent environment CRN.
      returned: always
      type: str
    name:
      description: The DataFlow Service's parent environment name.
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform of the environment.
      returned: always
      type: str
    region:
      description: The region of the environment.
      returned: always
      type: str
    deploymentCount:
      description: The deployment count.
      returned: always
      type: str
    minK8sNodeCount:
      description: The  minimum  number  of Kubernetes nodes that need to be provisioned in the environment.
      returned: always
      type: int
    maxK8sNodeCount:
      description:  The maximum number of  kubernetes  nodes  that  environment  may scale up under high-demand situations.
      returned: always
      type: str
    status:
      description: The status of a DataFlow enabled environment.
      returned: always
      type: dict
      contains:
        state:
          description: The state of the environment.
          returned: always
          type: str
        message:
          description: A status message for the environment.
          returned: always
          type: str
    k8sNodeCount:
      description: The  number of kubernetes nodes currently in use by DataFlow for this environment.
      returned: always
      type: int
    instanceType:
      description: The instance type of the kubernetes nodes currently  in  use  by DataFlow for this environment.
      returned: always
      type: str
    dfLocalUrl:
      description: The URL of the environment local DataFlow application.
      returned: always
      type: str
    authorizedIpRanges:
      description:  The authorized IP Ranges.
      returned: always
      type: list
    activeWarningAlertCount:
      description: Current count of active alerts classified as a warning.
      returned: always
      type: int
    activeErrorAlertCount:
      description: Current count of active alerts classified as an error.
      returned: always
      type: int
    clusterId:
      description: Cluster id of the environment.
      returned: if enabled
      type: str
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when supported
  type: list
  elements: str
'''


class DFInfo(CdpModule):
    def __init__(self, module):
        super(DFInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')

        # Initialize return values
        self.services = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:  # Note that both None and '' will trigger this
            service_single = self.cdpy.df.describe_environment(name=self.name)
            if service_single is not None:
                self.services.append(service_single)
        else:
            self.services = self.cdpy.df.list_environments()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['crn']),
        ),
        supports_check_mode=True,
    )

    result = DFInfo(module)
    output = dict(changed=False, services=result.services)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
