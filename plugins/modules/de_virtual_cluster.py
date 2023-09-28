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
from ..module_utils.cdp_common import CdpModule


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: de_virtual_cluster
short_description: Create or delete CDP Data Engineering Virtual Clusters
description:
    - Create or delete CDP Data Engineering Virtual Clusters 
author:
  - "Curtis Howard (@curtishoward)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the CDE Virtual Cluster 
    type: str
    required: True
  cluster_id:
    description:
      - Cluster id of the CDE service where virtual cluster has to be created. 
    type: str
    required: True
  cpu_requests:
    description:
      - Cpu requests for autoscaling.
    type: str
    required: False
  memory_requests:
    description:
      - Memory requests for autoscaling - eg. 30Gi.
    type: str
    required: False
  runtime_spot_component:
    description:
      - Used to describe where the Driver and the Executors would run, on-demand or spot instances.
    type: str
    required: False
  spark_version:
    description:
      - Spark version for the virtual cluster (e.g. SPARK2 or SPARK3).
    type: str
    required: False
  acl_users:
    description:
      - Comma-separated Workload usernames of CDP users to be granted access to the Virtual Cluster.
    type: str
    required: False
  chart_value_overrides:
    description:
    - Chart overrides for creating a virtual cluster. 
    type: list
    required: False
    suboptions:
      chart_name:
        description:
          - The key/value pair for the chart_name/override
        type: str
        required: False
  state:
    description:
      - The declarative state of the CDE virtual cluster 
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the DE virtual cluster to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the DE virtual cluster to achieve the declared
        state.
    type: int
    required: False
    default: 30
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the DE virtual cluster to achieve the declared
        state.
    type: int
    required: False
    default: 600
    aliases:
      - polling_timeout
'''

EXAMPLES = r'''
# Create a CDE virtual cluster
- cloudera.cloud.de_virtual_cluster:
    name: virtual-cluster-name
    cluster_name: cde-service-name
    env: cdp-environment-name
    state: present
    wait: True
    delay: 30
    timeout: 600
'''


RETURN = r'''
---
virtual_cluster:
  description: DE virtual cluster
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
          elements: str
    chartValueOverrides:
      description: Chart overrides for the CDE virtual cluster.
      returned: always
      type: list
      elements: dict
      contains:
        ChartValueOverridesResponse:
          type: list
          elements: dict
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

class DEVirtualCluster(CdpModule):
    def __init__(self, module):
        super(DEVirtualCluster, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('env')
        self.cluster_name = self._get_param('cluster_name')

        self.cpu_requests = self._get_param('cpu_requests')
        self.memory_requests = self._get_param('memory_requests')
        self.chart_value_overrides = self._get_param('chart_value_overrides')
        self.runtime_spot_component = self._get_param('runtime_spot_component')
        self.spark_version = self._get_param('spark_version')
        self.acl_users = self._get_param('acl_users')

        self.state = self._get_param('state')
        self.force = self._get_param('force')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.virtual_cluster = None

        # Initialize virtual cluster ID
        self.cluster_id = None
        self.vc_id = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.cluster_id = self.cdpy.de.get_service_id_by_name(name=self.cluster_name, env=self.env)
        self.vc_id = self.cdpy.de.get_vc_id_by_name(name=self.name, cluster_id=self.cluster_id)
        initial_desc = self.cdpy.de.describe_vc(self.cluster_id, self.vc_id) if self.vc_id else None

        # If a VC under the name was found
        if initial_desc and initial_desc['status']:
            # Delete the VC if expected state is 'absent'
            if self.state == 'absent':
                if self.module.check_mode:
                    self.virtual_cluster = initial_desc
                else:
                    # VC is available - delete it
                    if initial_desc['status'] in self.cdpy.sdk.REMOVABLE_STATES:
                        self.virtual_cluster = self._delete_vc()
                    # VC exists but is not in a delete-able state (could be in the process of
                    # provisioning, deleting, or may be in a failed state)
                    else:
                        self.module.warn("DE virtual cluster (%s) is not in a removable state: %s" %
                                         (self.name, initial_desc['status']))
                        if self.wait:
                            self.module.warn(
                                "Waiting for DE virtual cluster (%s) to reach Active or Deleted state" %
                                self.name)
                            current_desc = self._wait_for_state(self.cdpy.sdk.REMOVABLE_STATES +
                                                                self.cdpy.sdk.STOPPED_STATES)
                            # If we just waited fo the virtual cluster to be provisioned, then delete it
                            if current_desc['status'] in self.cdpy.sdk.REMOVABLE_STATES:
                                self.virtual_cluster = self._delete_vc()
                            else:
                                self.virtual_cluster = current_desc
                                if current_desc['status'] not in self.cdpy.sdk.STOPPED_STATES:
                                    self.module.warn("DE virtual cluster (%s) did not delete successfully" %
                                           self.name) 
            elif self.state == 'present':
                # Check the existing configuration and state
                self.module.warn("DE virtual cluster (%s) already present" % self.name)
                self.virtual_cluster = initial_desc
                if self.wait:
                    current_desc = self._wait_for_state(self.cdpy.sdk.REMOVABLE_STATES +
                                                        self.cdpy.sdk.STOPPED_STATES)
                    # If we just waited for the virtual cluster to be deleted, then create it
                    if current_desc['status'] in self.cdpy.sdk.STOPPED_STATES:
                        self.virtual_cluster = self._create_vc()
                    else:
                        self.virtual_cluster = current_desc
                        if current_desc['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                            self.module.warn("DE virtual cluster (%s) did not create successfully" %
                                    self.name)
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

        # Else if the virtual cluster does not exist
        else:
            if self.state == 'absent':
                self.module.log(
                    "DE virtual cluster (%s) already absent or deleted within service ID (%s)" %
                    (self.name, self.cluster_name))
            # Create the virtual cluster
            elif self.state == 'present':
                if not self.module.check_mode:
                    self.virtual_cluster = self._create_vc()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

    def _create_vc(self):
        # set cpu/memory requests to max available if not specified
        self.cpu_requests = self.cpu_requests if self.cpu_requests else '10000000'
        self.memory_requests = self.memory_requests if self.memory_requests else '10000000Gi'
        result = self.cdpy.de.create_vc(
            name=self.name,
            cluster_id=self.cluster_id,
            cpu_requests=self.cpu_requests,
            memory_requests=self.memory_requests,
            chart_value_overrides=self.chart_value_overrides,
            runtime_spot_component=self.runtime_spot_component,
            spark_version=self.spark_version,
            acl_users=self.acl_users
        )
        return_desc = None
        if result and result['vcId']:
            self.vc_id = result['vcId']
            if self.wait:
                return_desc = self._wait_for_state(self.cdpy.sdk.REMOVABLE_STATES)
                if return_desc['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                    self.module.warn("DE virtual cluster (%s) did not create successfully" % self.name)
            else:
                return_desc = result
        else:
            self.module.warn("DE virtual cluster (%s) did not create successfully" % self.name)
        return return_desc

    def _delete_vc(self):
        self.cdpy.de.delete_vc(self.cluster_id, self.vc_id)
        if self.wait:
            current_desc = self._wait_for_state(self.cdpy.sdk.STOPPED_STATES)
            if current_desc['status'] not in self.cdpy.sdk.STOPPED_STATES:
                self.module.warn("DE virtual cluster (%s) did not delete successfully" % self.name)
            return current_desc
        else:
            current_desc = self.cdpy.de.describe_vc(self.cluster_id, self.vc_id)
            return (current_desc if current_desc not in self.cdpy.sdk.STOPPED_STATES else None)

    def _wait_for_state(self, state):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.de.describe_vc,
            params=dict(cluster_id=self.cluster_id, vc_id=self.vc_id),
            field='status', state=state, delay=self.delay,
            timeout=self.timeout
        )

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str'),
            env=dict(required=True, type='str', aliases=['environment']),
            cluster_name=dict(required=True, type='str', aliases=['service_name']),
            cpu_requests=dict(required=False, type='str', default=None),
            memory_requests=dict(required=False, type='str', default=None),
            chart_value_overrides=dict(required=False, type='list', default=None),
            runtime_spot_component=dict(required=False, type='str', default=None),
            spark_version=dict(required=False, type='str', default=None),
            acl_users=dict(required=False, type='str', default=None),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=30),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=600)
        ),
        supports_check_mode=True
    )

    result = DEVirtualCluster(module)
    output = dict(changed=False, virtual_cluster=(result.virtual_cluster if result.virtual_cluster else {}))

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
