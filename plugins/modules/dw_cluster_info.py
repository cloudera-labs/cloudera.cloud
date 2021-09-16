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
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
      - Mutually exclusive with I(environment).
    type: str
    aliases:
      - id
  environment:
    description:
      - The name or CRN of the Environment in which to find and describe Data Warehouse Clusters.
      - Mutually exclusive with I(cluster_id).
    type: str
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List information about all Data Warehouse Clusters
- cloudera.cloud.dw_cluster_info:

# Gather information about all Data Warehouse Clusters within an Environment
- cloudera.cloud.dw_cluster_info:
    env: example-environment
    
# Gather information about an identified Cluster
- cloudera.cloud.dw_cluster_info:
    cluster_id: env-xyzabc
'''

RETURN = r'''
---
clusters:
  description: The information about the named Cluster or Clusters
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The cluster identifier.
      returned: always
      type: str
    environmentCrn:
      description: The CRN of the cluster's Environment
      returned: always
      type: str
    crn:
      description: The cluster's CRN.
      returned: always
      type: str
    creationDate:
      description: The creation timestamp of the cluster in UTC.
      returned: always
      type: str
    status:
      description: The status of the cluster
      returned: always
      type: str
    creator:
      description: The cluster creator details.
      returned: always
      type: dict
      contains:
        crn:
          description: The Actor CRN.
          type: str
          returned: always
        email:
          description: Email address (users).
          type: str
          returned: when supported
        workloadUsername:
          description: Username (users).
          type: str
          returned: when supported
        machineUsername:
          description: Username (machine users).
          type: str
          returned: when supported
    cloudPlatform:
      description: The cloud platform of the environment that was used to create this cluster.
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
        self.cluster_id = self._get_param('cluster_id')
        self.environment = self._get_param('environment')

        # Initialize return values
        self.clusters = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.cluster_id is not None:
            cluster_single = self.cdpy.dw.describe_cluster(self.cluster_id)
            if cluster_single is not None:
                self.clusters.append(cluster_single)
        elif self.environment is not None:
            env_crn = self.cdpy.environments.resolve_environment_crn(self.environment)
            if env_crn:
                self.clusters = self.cdpy.dw.list_clusters(env_crn=env_crn)
        else:
            self.clusters = self.cdpy.dw.list_clusters()


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            cluster_id=dict(type='str', aliases=['id']),
            environment=dict(type='str', aliases=['env'])
        ),
        mutually_exclusive=[
          ['cluster_id', 'environment']
        ],
        supports_check_mode=True
    )

    result = DwClusterInfo(module)
    output = dict(changed=False, clusters=result.clusters)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
