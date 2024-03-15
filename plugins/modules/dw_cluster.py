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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: dw_cluster
short_description: Create or Delete CDP Data Warehouse Clusters
description:
    - Create or Delete CDP Data Warehouse Clusters
author:
  - "Dan Chaffelson (@chaffelson)"
  - "Saravanan Raju (@raju-saravanan)"
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  cluster_id:
    description:
      - The identifier of the Data Warehouse Cluster.
      - Required if I(state=absent) and I(env) is not specified.
    type: str
    aliases:
      - id
      - name
  env:
    description:
      - The name of the target environment.
      - Required if I(state=present).
      - Required if I(state=absent) and I(cluster_id) is not specified.
    type: str
    aliases:
      - environment
      - env_crn
  overlay:
    description: 
      - Flag to use private IP addresses for Pods within the cluster. 
      - Otherwise, use IP addresses within the VPC.
    type: bool
    default: False    
  private_load_balancer:
    description: Flag to set up a load balancer for private subnets.
    type: bool
    default: False    
  aws_lb_subnets:
    description:
      - List of zero or more AWS Subnet IDs where the cluster load balancer should be deployed.
      - Required if I(state=present) and the I(env) is deployed to AWS.
    type: list
    elements: str
  aws_worker_subnets:
    description:
      - List of zero or more AWS Subnet IDs where the cluster worker nodes should be deployed.
      - Required if I(state=present) and the I(env) is deployed to AWS.
    type: list
    elements: str
  az_subnet:
    description:
      - The Azure Subnet Name.
      - Required if I(state=present) and the I(env) is deployed to Azure.
    type: str
  az_enable_az:
    description: 
      - Flag to enable Availability Zone mode.
      - Required if I(state=present) and the I(env) is deployed to Azure.
    type: bool
  az_managed_identity:
    description:
      - Resource ID of the managed identity used by AKS.
      - Required if I(state=present) and the I(env) is deployed to Azure.
    type: str
  az_enable_private_aks:
    description:
      - Flag to enable Azure Private AKS mode.
    type: bool
  az_enable_private_sql:
    description:
      - Flag to enable private SQL for the cluster deployment.
    type: bool  
  az_enable_spot_instances:
    description:
      - Flag to enable spot instances for Virtual warehouses.
    type: bool
  az_log_analytics_workspace_id:
    description:
      - Workspace ID for Azure log analytics.
      - Used to monitor the Azure Kubernetes Service (AKS) cluster.
    type: str  
  az_network_outbound_type:
    description:
      - Network outbound type. 
      - This setting controls the egress traffic for cluster nodes in Azure Kubernetes Service
    type: str
    choices:
      - LoadBalancer
      - UserAssignedNATGateway
      - UserDefinedRouting
  az_aks_private_dns_zone:
    description:
      - ID for the private DNS zone used by AKS.
    type: str
  az_compute_instance_types:
    description:
      - List of Azure Compute Instance Types that the AKS environment is restricted to use.
      - Only a single instance type can be listed.
    type: list
    elements: str
  state:
    description: The state of the Data Warehouse Cluster
    type: str
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    default: True
  force:
    description:
      - Flag to enable force deletion of the Data Warehouse Cluster.
      - This will not destroy the underlying cloud provider assets.
    type: bool
    default: False
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Request Azure Cluster creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    az_subnet: my-subnet-name
    az_enable_az: yes
    az_managed_identity: my-aks-managed-identity

# Request AWS Cluster Creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    aws_lb_subnets: [subnet-id-1, subnet-id-2]
    aws_worker_subnets: [subnet-id-3, subnet-id-4]

# Delete a Data Warehouse Cluster
- cloudera.cloud.dw_cluster:
    state: absent
    cluster_id: my-id
    
# Delete the Data Warehouse Cluster within the Environment
- cloudera.cloud.dw_cluster:
    state: absent
    env: crn:cdp:environments...
'''

RETURN = r'''
---
cluster:
  description: Details for the Data Warehouse cluster
  type: dict
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


class DwCluster(CdpModule):
    def __init__(self, module):
        super(DwCluster, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('env')
        self.overlay = self._get_param('overlay')
        self.private_load_balancer = self._get_param('private_load_balancer')
        self.az_subnet = self._get_param('az_subnet')
        self.az_enable_az = self._get_param('az_enable_az')
        self.az_managed_identity = self._get_param('az_managed_identity')
        self.az_enable_private_aks = self._get_param('az_enable_private_aks')
        self.az_enable_private_sql = self._get_param('az_enable_private_sql')
        self.az_enable_spot_instances = self._get_param('az_enable_spot_instances')
        self.az_log_analytics_workspace_id = self._get_param('az_log_analytics_workspace_id')
        self.az_network_outbound_type = self._get_param('az_network_outbound_type')
        self.az_aks_private_dns_zone = self._get_param('az_aks_private_dns_zone')
        self.az_compute_instance_types = self._get_param('az_compute_instance_types')
        self.aws_lb_subnets = self._get_param('aws_lb_subnets')
        self.aws_worker_subnets = self._get_param('aws_worker_subnets')
        self.force = self._get_param('force')
        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.cluster = {}
        self.changed = False

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        env_crn = self.cdpy.environments.resolve_environment_crn(self.env)
        
        # Check if Cluster exists
        if self.name is not None:
            self.target = self.cdpy.dw.describe_cluster(cluster_id=self.name)
        elif env_crn is not None:
            listing = self.cdpy.dw.list_clusters(env_crn)  # Always returns a list
            if len(listing) == 1:
                self.name = listing[0]['id']
                self.target = self.cdpy.dw.describe_cluster(cluster_id=self.name)
            elif len(listing) == 0:
                self.target = None
            else:
                self.module.fail_json(msg="Received multiple (i.e. ambiguous) Clusters in Environment %s" % self.env)
        else:
            self.target = None
            
        if self.target is not None:
            # Begin Cluster Exists
            if self.state == 'absent':
                # Begin Delete
                if self.module.check_mode:
                    self.cluster = self.target
                else:
                    self.changed = True
                    if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.warn("Cluster is not in a valid state for Delete operations: %s" % self.target['status'])
                    else:
                        _ = self.cdpy.dw.delete_cluster(cluster_id=self.name, force=self.force)
                    
                    if self.wait:
                        self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_cluster,
                            params=dict(cluster_id=self.name),
                            field=None, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.cdpy.sdk.sleep(self.delay)  # Wait for consistency sync
                        self.cluster = self.cdpy.dw.describe_cluster(cluster_id=self.name)
                # End Delete
            elif self.state == 'present':
                # Begin Config Check
                self.module.warn("Cluster is already present and reconciliation is not yet implemented")
                if self.wait:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.dw.describe_cluster,
                        params=dict(cluster_id=self.name),
                        state='Running', delay=self.delay, timeout=self.timeout
                    )
                self.cluster = self.target
                # End Config Check
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End Cluster Exists
        else:
            # Begin Cluster Not Found
            if self.state == 'absent':
                self.module.warn("Cluster %s already absent in Environment %s" % (self.name, self.env))
            elif self.state == 'present':
                if not self.module.check_mode:
                    # Begin Cluster Creation
                    self.changed = True
                    if env_crn is None:
                        self.module.fail_json(msg="Could not retrieve CRN for CDP Environment %s" % self.env)
                    else:
                        self.name = self.cdpy.dw.create_cluster(
                            env_crn=env_crn, overlay=self.overlay, private_load_balancer=self.private_load_balancer,
                            aws_lb_subnets=self.aws_lb_subnets, aws_worker_subnets=self.aws_worker_subnets,
                            az_subnet=self.az_subnet, az_enable_az=self.az_enable_az, az_managed_identity=self.az_managed_identity,
                            az_enable_private_aks=self.az_enable_private_aks, az_enable_private_sql=self.az_enable_private_sql,
                            az_enable_spot_instances=self.az_enable_spot_instances, az_log_analytics_workspace_id=self.az_log_analytics_workspace_id,
                            az_network_outbound_type=self.az_network_outbound_type, az_aks_private_dns_zone=self.az_aks_private_dns_zone,
                            az_compute_instance_types=self.az_compute_instance_types
                        )

                        if self.wait:
                            self.cluster = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.describe_cluster,
                                params=dict(cluster_id=self.name),
                                state='Running', delay=self.delay, timeout=self.timeout
                            )
                        else:
                            self.cluster = self.cdpy.dw.describe_cluster(cluster_id=self.name)
                # End Cluster Creation
            else:
                self.module.fail_json(msg="Invalid state: %s" % self.state)
            # End Cluster Not Found


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            cluster_id=dict(type='str', aliases=['id', 'name']),
            env=dict(type='str', aliases=['environment', 'env_crn']),
            overlay=dict(type='bool', default=False),
            private_load_balancer=dict(type='bool', default=False),
            az_subnet=dict(type='str'),
            az_enable_az=dict(type='bool'),
            az_managed_identity=dict(type='str'),
            az_enable_private_aks=dict(type='bool'),
            az_enable_private_sql=dict(type='bool'),
            az_enable_spot_instances=dict(type='bool'),
            az_log_analytics_workspace_id=dict(type='str'),
            az_network_outbound_type=dict(type='str', choices=['LoadBalancer','UserAssignedNATGateway','UserDefinedRouting']),
            az_aks_private_dns_zone=dict(type='str'),
            az_compute_instance_types=dict(type='list'),
            aws_lb_subnets=dict(type='list', aliases=['aws_public_subnets']),
            aws_worker_subnets=dict(type='list', aliases=['aws_private_subnets']),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            force=dict(type='bool', default=False),
            wait=dict(type='bool', default=True),
            delay=dict(type='int', aliases=['polling_delay'], default=15),
            timeout=dict(type='int', aliases=['polling_timeout'], default=3600)
        ),
        required_together=[
            ['az_subnet', 'az_enable_az', 'az_managed_identity'],
            ['aws_lb_subnets', 'aws_worker_subnets']
        ],
        required_if=[
            ['state', 'absent', ['cluster_id', 'env'], True],
            ['state', 'present', ['env']]
        ],
        supports_check_mode=True
    )

    result = DwCluster(module)
    output = dict(changed=result.changed, cluster=result.cluster)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
