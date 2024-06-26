#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: datalake_runtime_info
short_description: Gather information about CDP Datalake Runtimes
description:
    - Gather information about CDP Datalake Runtimes
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  default:
    description:
      - Flag to return only the C(default) Runtime.
      - Otherwise, all available Runtimes will be listed.
    type: bool
    required: False
    default: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about available Datalake Runtimes
- cloudera.cloud.datalake_runtime_info:

# List basic information about the default Datalake Runtime
- cloudera.cloud.datalake_runtime_info:
    default: yes

"""

RETURN = r"""
---
versions:
  description: Details on available CDP Datalake Runtimes
  type: list
  returned: on success
  elements: dict
  contains:
    runtimeVersion:
      description: The version number of the Runtime.
      returned: always
      type: str
      sample: "7.2.6"
    defaultRuntimeVersion:
      description: Flag designating default status.
      returned: always
      type: bool
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when supported
  type: list
  elements: str
"""


class DatalakeRuntimeInfo(CdpModule):
    def __init__(self, module):
        super(DatalakeRuntimeInfo, self).__init__(module)

        # Set variables
        self.default = self._get_param("default")

        # Initialize return values
        self.versions = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        retrieved_versions = self.cdpy.sdk.call(
            svc="datalake", func="list_runtimes", ret_field="versions"
        )
        if self.default:
            self.versions = list(
                filter(lambda r: r["defaultRuntimeVersion"], retrieved_versions)
            )
        else:
            self.versions = retrieved_versions


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            default=dict(required=False, type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    result = DatalakeRuntimeInfo(module)
    output = dict(changed=False, versions=result.versions)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
