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
module: datahub_template_info
short_description: Gather information about CDP Datahub Cluster Templates
description:
    - Gather information about CDP Datahub Cluster Templates
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that Template will be described.
      - If no name provided, all Templates will be listed.
    type: str
    required: False
    aliases:
      - template
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all Datahubs
- cloudera.cloud.datahub_template_info:

# Gather detailed information about a named Datahub
- cloudera.cloud.datahub_template_info:
    name: example-template
'''

RETURN = r'''
---
templates:
  description: The information about the named Template or Templates
  type: list
  returned: on success
  elements: complex
  contains:
    clusterTemplateName:
      description: The name of the cluster template.
      returned: always
      type: str
    crn:
      description:  The CRN of the cluster template.
      returned: always
      type: str
    description:
      description: The description of the cluster template.
      returned: always
      type: str
    productVersion:
      description: The product version.
      returned: always
      type: str
    instanceGroupCount:
      description: The instance group count of the cluster.
      returned: always
      type: str
    status:
      description: The status of the cluster template.
      returned: always
      type: str
    tags:
      description: Tags added to the cluster template
      type: dict
      returned: always
      contains:
        key:
          description: The key of the tag.
          returned: always
          type: str
        value:
          description: The value of the tag.
          returned: always
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


class DatahubTemplateInfo(CdpModule):
    def __init__(self, module):
        super(DatahubTemplateInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')

        # Initialize return values
        self.templates = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:  # Note that both None and '' will trigger this
            template_single = self.cdpy.datahub.describe_cluster(self.name)
            if template_single is not None:
                self.templates.append(template_single)
        else:
            self.templates = self.cdpy.datahub.list_cluster_templates()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['template'])
        ),
        supports_check_mode=True
    )

    result = DatahubTemplateInfo(module)
    output = dict(changed=False, templates=result.templates)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
