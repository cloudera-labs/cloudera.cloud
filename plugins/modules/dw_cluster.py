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
module: dw_cluster
short_description: Create or Delete CDP Data Warehouse Clusters
description:
    - Create or Delete CDP Data Warehouse Clusters
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  id:
    description:
      - If an ID is provided, that Data Warehouse Cluster will be deleted if C(state=absent)
    type: str
    required: When state is absent
    aliases:
      - name
  env:
    description: The name of the target environment
    type: str
    required: when state is present
    aliases:
      - environment
      - env_crn
  aws_public_subnets:
    description: List of zero or more Public AWS Subnet IDs to deploy to
    type: list
    required: when state is present for AWS deployment 
  aws_private_subnets:
    description: List of zero or more Private AWS Subnet IDs to deploy to
    type: list
    required: when state is present for AWS deployment
  az_subnet:
    description: Azure Subnet Name, not URI
    type: str
    required: when state is present for Azure deploymnet
  az_enable_az:
    description: Whether to enable AZ mode or not
    type: bool
    required: when state is present for Azure deployment
  state:
    description: The declarative state of the Data Warehouse Cluster
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared
        state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Delete a Data Warehouse Cluster
- cloudera.cloud.dw_cluster:
    state: absent
    id: my-id

# Request Azure Cluster creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    az_subnet: my-subnet-name
    az_enable_az: yes

# Request AWS Cluster Creation
- cloudera.cloud.dw_cluster:
    env_crn: crn:cdp:environments...
    aws_public_subnets: [subnet-id-1, subnet-id-2]
    aws_private_subnets: [subnet-id-3, subnet-id-4]
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
      tyoe: dict
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


class DwCluster(CdpModule):
    def __init__(self, module):
        super(DwCluster, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('env')
        self.overlay = self._get_param('overlay')
        self.az_subnet = self._get_param('az_subnet')
        self.az_enable_az = self._get_param('az_enable_az')
        self.aws_public_subnets = self._get_param('aws_public_subnets')
        self.aws_private_subnets = self._get_param('aws_private_subnets')
        self.force = self._get_param('force')
        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.clusters = []

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
                self.module.fail_json(
                    msg="Got ambiguous listing result for DW Clusters in Environment %s" % self.env)
        else:
            self.target = None
        if self.target is not None:
            # Cluster Exists
            if self.state == 'absent':
                # Begin Delete
                if self.module.check_mode:
                    self.clusters.append(self.target)
                else:
                    if self.target['status'] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.warn(
                            "DW Cluster not in valid state for Delete operation: %s" % self.target['status'])
                    else:
                        _ = self.cdpy.dw.delete_cluster(cluster_id=self.name, force=self.force)
                    if self.wait:
                        self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.dw.describe_cluster,
                            params=dict(cluster_id=self.name),
                            field=None, delay=self.delay, timeout=self.timeout
                        )
                    else:
                        self.cdpy.sdk.sleep(3)  # Wait for consistency sync
                        self.target = self.cdpy.dw.describe_cluster(cluster_id=self.name)
                        self.clusters.append(self.target)
                # Drop Done
            elif self.state == 'present':
                # Being Config check
                self.module.warn("DW Cluster already present and config validation is not implemented")
                if self.wait:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.dw.describe_cluster,
                        params=dict(cluster_id=self.name),
                        state='Running', delay=self.delay, timeout=self.timeout
                    )
                    self.clusters.append(self.target)
                # End Config check
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)
            # End handling Cluster exists
        else:
            # Begin handling Cluster not found
            if self.state == 'absent':
                self.module.warn("DW CLuster %s already absent in Environment %s" % (self.name, self.env))
            elif self.state == 'present':
                if self.module.check_mode:
                    pass
                else:
                    # Being handle Cluster Creation
                    if env_crn is None:
                        self.module.fail_json(msg="Could not retrieve CRN for CDP Environment %s" % self.env)
                    else:
                        self.name = self.cdpy.dw.create_cluster(
                            env_crn=env_crn, overlay=self.overlay, aws_public_subnets=self.aws_public_subnets,
                            aws_private_subnets=self.aws_private_subnets, az_subnet=self.az_subnet,
                            az_enable_az=self.az_enable_az
                        )
                        if self.wait:
                            self.target = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.dw.describe_cluster,
                                params=dict(cluster_id=self.name),
                                state='Running', delay=self.delay, timeout=self.timeout
                            )
                        else:
                            self.target = self.cdpy.dw.describe_cluster(cluster_id=self.name)
                        self.clusters.append(self.target)
            else:
                self.module.fail_json(msg="State %s is not valid for this module" % self.state)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['id']),
            env=dict(required=False, type='str', aliases=['environment', 'env_crn']),
            overlay=dict(required=False, type='bool', default=False),
            az_subnet=dict(required=False, type='str', default=None),
            az_enable_az=dict(required=False, type='bool', default=None),
            aws_public_subnets=dict(required=False, type='list', default=None),
            aws_private_subnets=dict(required=False, type='list', default=None),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            force=dict(required=False, type='bool', default=False),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        required_together=[
            ['az_subnet', 'az_enable_az'],
            ['aws_public_subnets', 'aws_private_subnets']
        ],
        required_one_of=[['name', 'env'], ],
        supports_check_mode=True
    )

    result = DwCluster(module)
    output = dict(changed=False, clusters=result.clusters)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
