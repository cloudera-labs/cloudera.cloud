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
module: de_virtual_cluster_info
short_description: Gather information about CDP DE virtual clusters (within a DE service)
description:
    - Gather information about CDP DE virtual clusters (within a DE service)
author:
  - "Curtis Howard (@curtishoward)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that DE service will be described (if it exists)
      - Note that there should be only 1 or 0 (non-deleted) services with a given name
    type: str
    required: False
    aliases:
      - name
  cluster_id:
    description:
      - The ID of the service in which to find and describe the DE virtual clusters.
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

# List basic information about all DE Services
- cloudera.cloud.de_info:

# List basic information about all DE Services within a given environment
- cloudera.cloud.de_info:
    environment: example-environment

# Gather detailed information about a named DE Service
- cloudera.cloud.de_info:
    name: example-service

# Gather detailed information about a named DE Service within a particular environment
- cloudera.cloud.de_info:
    name: example-service
    environment: example-environment
'''

RETURN = r'''
services:
  description: List of DE service descriptions
  type: list
  returned: always
  elements: complex
  contains:
    clusterId:
      description: Cluster Id of the CDE Service.
      returned: always
      type: str
    creatorEmail:
      description: Email Address of the CDE creator.
      returned: always
      type: str
    enablingTime:
      description: Timestamp of service enabling.
      returned: always
      type: str
    environmentName:
      description: CDP Environment Name.
      returned: always
      type: str
    name:
      description: Name of the CDE Service.
      returned: always
      type: str
    status:
      description: Status of the CDE Service.
      returned: always
      type: str
    chartValueOverrides:
      description: Status of the CDE Service.
      returned: if full service description
      type: array
      elements: complex
      contains:
        ChartValueOverridesResponse:
          type: list
          returned: always
          contains:
            chartName:
              description: Name of the chart that has to be overridden.
              returned: always
              type: str
            overrides:
              description: Space separated key value-pairs for overriding chart values (colon separated)
              returned: always
              type: str
    cloudPlatform:
      description: The cloud platform where the CDE service is enabled.
      returned: if full service description
      type: str
    clusterFqdn:
      description: FQDN of the CDE service.
      returned: if full service description
      type: str
    creatorCrn:
      description: CRN of the creator.
      returned: if full service description
      type: str
    dataLakeAtlasUIEndpoint:
      description: Endpoint of Data Lake Atlas.E
      returned: if full service description
      type: str
    dataLakeFileSystems:
      description: The Data lake file system.
      returned: if full service description
      type: str
    environmentCrn:
      description: CRN of the environment.
      returned: if full service description
      type: str
    logLocation:
      description: Location for the log files of jobs.
      returned: if full service description
      type: str
    resources:
      description: Resources details of CDE Service.
      returned: if full service description
      type: complex
      contains:
        ServiceResources:
          description: Object to store resources for a CDE service.
          returned: always
          type: complex
          contains:
            initial_instances:
              description: Initial instances for the CDE service.
              returned: always
              type: str
            initial_spot_instances:
              description: Initial Spot Instances for the CDE Service.
              returned: always
              type: str
            instance_type:
              description: Instance type of the CDE service.
              returned: always
              type: str
            max_instances:
              description: Maximum instances for the CDE service.
              returned: always
              type: str
            max_spot_instances:
              description: Maximum Number of Spot instances.
              returned: always
              type: str
            min_instances:
              description: Minimum Instances for the CDE service.
              returned: always
              type: str
            min_spot_instances:
              description: Minimum number of spot instances for the CDE service.
              returned: always
              type: str
            root_vol_size:
              description: Root Volume Size.
              returned: always
              type: str
    tenantId:
      description: CDP tenant ID.
      returned: if full service description
      type: str
'''


class DEVirtualClusterInfo(CdpModule):
    def __init__(self, module):
        super(DEVirtualClusterInfo, self).__init__(module)

        # Set variables
        self.vc_name = self._get_param('name')
        self.service_name = self._get_param('service_name')
        self.env = self._get_param('environment')

        # Initialize return values
        self.vcs = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        cluster_id = self.cdpy.de.get_service_id_by_name(self.service_name, self.env)
        if cluster_id:
            vcs = [vc
                   for vc in self.cdpy.de.list_vcs(cluster_id) 
                   if vc['status'] not in self.cdpy.sdk.STOPPED_STATES]
            if self.vc_name:
                name_match = [self.cdpy.de.describe_vc(cluster_id=cluster_id, vc_id=vc['vcId'])
                              for vc in vcs
                              if vc['vcName'] == self.vc_name]
                self.vcs.extend(name_match)
            else:
                self.vcs.extend(vcs)

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str'),
            environment=dict(required=True, type='str', aliases=['env']),
            service_name=dict(required=True, type='str', aliases=['cluster_name'])
        ),
        supports_check_mode=True
    )

    result = DEVirtualClusterInfo(module)
    output = dict(changed=False, vcs=result.vcs)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
