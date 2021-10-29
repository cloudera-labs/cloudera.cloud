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
      - If a name is provided, that DE virtual cluster will be described (if it exists)
      - Note that there should be only 1 or 0 (non-deleted) virtual clusters with a given CDE service 
    type: str
    required: False
    aliases:
      - name
  cluster_name:
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

# List basic information about all CDE virtual clusters within a CDE service
- cloudera.cloud.de_virtual_cluster_info:
    cluster_name: example-cluster-name
    environment: example-environment

# Gather detailed information about a specific CDE virtual cluster
- cloudera.cloud.de_info:
    cluster_name: example-cluster-name
    environment: example-environment
    name: example-virtual-cluster-name
'''

RETURN = r'''
virtual_cluster:
  description: DE virtual cluste
  type: complex
  returned: always
  contains:
    VcUiUrl:
      description: URL of the CDE Virtual Cluster UI
      returned: always
      type: str
    accessControl:
      description: Access control object for the Virtual Cluster
      returned: always
      type: dict
      contains:
        users:
          description: Workload usernames of CDP users granted access to the Virtual Cluster. 
          returned: always
          type: list
          contains:
            description: Workload username
            returned: always
            type: str
    chartValueOverrides:
      description: Chart overrides for the CDE virtual cluster.
      returned: always
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
    clusterId:
      description: Cluster ID of the CDE service that contains the Virtual Cluster
      returned: always
      type: str
    creationTime:
      description: Time of creation of the virtual Cluster
      returned: always
      type: str
    creatorEmail:
      description: Email address of the creator of Virtual Cluster
      returned: always
      type: str
    creatorID:
      description: ID of the creator of Virtual Cluster
      returned: always
      type: str
    creatorName:
      description: Name of the creator of the Virtual Cluster
      returned: always
      type: str
    historyServerUrl:
      description: Spark History Server URL for the Virtual Cluster
      returned: always
      type: str
    livyServerUrl:
      description: Livy Server URL for the Virtual Cluster
      returned: always
      type: str
    resources:
      description: Resources details of CDE virtual cluster.
      returned: always
      type: complex
      contains:
        VcResources:
          description: Object to store resources for a CDE service.
          returned: always
          type: complex
          contains:
            actualCpuRequests:
              description: Actual CPU request for the VC. This accounts for other dex apps(eg. livy, airflow), that run in the virtual cluster.
              returned: always
              type: str
            actualMemoryRequests:
              description: Actual Memory request for the VC. This accounts for other dex apps(eg. livy, airflow), that run in the virtual cluster.
              returned: always
              type: str
            cpuRequests:
              description: The CPU requests for VC for running spark jobs.
              returned: always
              type: str
            memRequests:
              description: The Memory requests for VC for running spark jobs.
              returned: always
              type: str
    safariUrl:
      description: Safari URL for the Virtual Cluster
      returned: always
      type: str
    sparkVersion:
      description: Spark version for the virtual cluster
      returned: always
      type: str
    status:
      description: Status of the Virtual Cluster
      returned: always
      type: str
    vcApiUrl:
      description: Url for the Virtual Cluster APIs
      returned: always
      type: str
    vcId:
      description: Virtual Cluster ID
      returned: always
      type: str
    vcName:
      description: Name of the CDE Virtual Cluster
      returned: always
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
