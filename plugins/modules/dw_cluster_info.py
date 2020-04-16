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
module: dw_cluster_info
short_description: Gather information about CDP Data Warehouse Clusters
description:
    - Gather information about CDP Data Warehouse Clusters
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  id:
    description:
      - If a name is provided, that Data Warehouse Cluster will be described.
      - environment must be provided if using name to retrieve a Cluster
    type: str
    required: False
    aliases:
      - name
  environment:
    description:
      - The name of the Environment in which to find and describe the Data Warehouse Clusters.
      - Required with name to retrieve a Cluster
    type: str
    required: False
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all Data Warehouse Clusters
- cloudera.cloud.dw_cluster_info:

# Gather detailed information about a named Cluster
- cloudera.cloud.dw_cluster_info:
    name: example-cluster
    env: example-environment
'''

RETURN = r'''
---
clusters:
  description: The information about the named Cluster or Clusters
  type: list
  returned: always
  elements: complex
  contains:
    cluster:
      type: dict
      contains:
        name:
          description: The name of the cluster.
          returned: always
          type: str
        environmentCrn:
          description: The crn of the cluster's environment.
          returned: always
          type: str
        crn:
          description: The cluster's crn.
          returned: always
          type: str
        creationDate:
          description: The creation time of the cluster in UTC.
          returned: always
          type: str
        status:
          description: The status of the Cluster
          returned: always
          type: str
        creator:
          description: The CRN of the cluster creator.
          returned: always
          type: dict
          contains:
            crn:
              type: str
              description: Actor CRN
            email:
              type: str
              description: Email address for users
            workloadUsername:
              type: str
              description: Username for users
            machineUsername:
              type: str
              description: Username for machine users
        cloudPlatform:
          description: The  cloud  platform  of the environment that was used to create this cluster
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


class DwClusterInfo(CdpModule):
    def __init__(self, module):
        super(DwClusterInfo, self).__init__(module)

        # Set variables
        self.id = self._get_param('name')
        self.env = self._get_param('env')

        # Initialize return values
        self.clusters = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.id is not None:
            cluster_single = self.cdpy.dw.describe_cluster(name=self.id)
            if cluster_single is not None:
                self.clusters.append(cluster_single)
        if self.env is not None:
            env_crn = self.cdpy.environments.resolve_environment_crn(self.env)
            if env_crn is not None:
                self.clusters = self.cdpy.dw.gather_clusters(env_crn)
        else:
            self.clusters = self.cdpy.dw.gather_clusters()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            id=dict(required=False, type='str', aliases=['name']),
            env=dict(required=False, type='str', aliases=['environment'])
        ),
        supports_check_mode=True
    )

    result = DwClusterInfo(module)
    output = dict(changed=False, clusters=result.clusters)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
