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
from ..module_utils.cdp_common import CdpModule


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ml
short_description: Create or Destroy CDP Machine Learning Workspaces
description:
    - Create or Destroy CDP Machine Learning Workspaces
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the ML Workspace
    type: str
    required: True
    aliases:
      - workspace
  environment:
    description:
      - The name of the Environment for the ML Workspace
    type: str
    required: True
    aliases:
      - env
  state:
    description:
      - The declarative state of the ML Workspace
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  tls:
    description:
      - The flag to manage TLS for the ML Workspace.
    type: bool
    required: False
    default: True
    aliases:
      - enable_tls
  monitoring:
    description:
      - The flag to manage monitoring for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_monitoring
  governance:
    description:
      - The flag to enable governance by integrating with Cloudera Atlas for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_governance
  metrics:
    description:
      - The flag to enable the exporting of model metrics to a metrics store for the ML Workspace.
    type: bool
    required: False
    default: False
    aliases:
      - enable_metrics
  database:
    description:
      - Configuration for exporting model metrics to an existing Postgres database.
    type: dict
    required: False
    contains:
      existingDatabaseHost:
        description:
          - The Postgres hostname
        type: str
        required: False
      existingDatabaseName:
        description:
          - The Postgres database name
        type: str
        required: False
      existingDatabasePort:
        description:
          - The Postgres port
        type: str
        required: False
      existingDatabaseUser:
        description:
          - The Postgres user
        type: str
        required: False
      existingDatabasePassword:
        description:
          - The Postgres password
        type: str
        required: False
    aliases:
      - existing_database
      - database_config
  nfs:
    description:
      - An existing NFS mount (hostname and desired path).
      - Applicable to I(Azure) and I(Private Cloud) deployments only.
    type: str
    required: False
    aliases:
      - existing_nfs
  nfs_version:
    description:
      - The NFS Protocol version of the NFS server as declared in C(nfs).
      - Applicable to I(Azure) and I(Private Cloud) deployments only.
    type: str
    required: False
  k8s_request:
    description:
      - Configuration for the Kubernetes provisioning of the ML Workspace.
    type: dict
    required: False
    contains:
      environmentName:
        description:
          - The Environment for the ML Workspace
        type: str
        required: True
      instanceGroups:
        description:
          - The instance groups for the ML Workspace provisioning request
        type: array
        elements: dict
        required: True
        contains:
          autoscaling:
            description:
              - The autoscaling configuration for the instance group
            type: dict
            required: False
            contains:
              enabled:
                description:
                  - The flag enabling autoscaling
                type: bool
                required: False
                default: True
              maxInstance:
                description:
                  - The maximum number of instances
                type: int
                required: True
              minInstance:
                description:
                  - The minimum number of instances
                type: int
                required: True
          ingressRules:
            description:
              - The networking rules for the ingress
            type: array
            elements: str
            required: False
          instanceCount:
            description:
              - The initial number of instances
            type: int
            required: False
            default: 0
          instanceTier:
            description:
              - The provision tier of the instances
            type: str
            required: False
            sample: ON_DEMAND
          instanceType:
            description:
              - The cloud provider instance type for the instance
            type: str
            required: True
            sample:
              - (AWS) m5.2xlarge
          name:
            description:
              - A unique name of the instance group
            type: str
            required: False
          rootVolume:
            description:
              - Configuration of the root volume for each instance
            type: dict
            required: False
            contains:
              size:
                description:
                  - The volume size (in GB)
                type: int
                required: True
      network:
        description:
          - The overlay network for the Container Network Interface (CNI).
          - I(AWS) only.
        type: dict
        required: False
        contains:
          plugin:
            description:
              - The identifier for the specific Container Network Interface (CNI) vendor
            type: str
            required: False
            sample:
              - calico,
              - weave
          topology:
            description:
              - The options for overlay topology
            type: dict
            required: False
            contains:
              subnets:
                description:
                  - Configuration for the topology subnets
                type: list
                elements: str
                required: False
      tags:
        description:
          - Tags to add to the cloud provider resources
        type: dict
        required: False
        contains:
          key:
            description:
              - The key/value pair for the tag
            type: str
            required: False
    aliases:
      - provision_k8s
  ip_addresses:
    description:
      - List of allowed CIDR blocks for the load balancer.
    type: list
    elements: str
    required: False
    aliases:
      - loadbalancer_access_ips
  public_loadbalancer:
    description:
      - Flag to manage the usage of a public load balancer.
    type: bool
    required: False
    default: False
    aliases:
      - enable_public_loadbalancer
  force:
    description:
      - Flag to force delete a workspace even if errors occur during deletion.
      - Force delete removes the guarantee that the cloud provider resources are destroyed.
      - Applicable to C(state=absent) only.
    type: bool
    required: False
    default: False
    aliases:
      - force_delete
  storage:
    description:
      - Flag to delete the ML Workspace backing storage during delete operations.
      - Applicable to C(state=absent) only.
    type: bool
    required: False
    default: True
    aliases:
      - remove_storage
  wait:
    description:
      - Flag to enable internal polling to wait for the ML Workspace to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the ML Workspace to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the ML Workspace to achieve the declared
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

# Create a ML Workspace with TLS turned off and wait for setup completion
- cloudera.cloud.ml:
    name: ml-example
    env: cdp-env
    tls: no
    wait: yes

# Create a ML Workspace (in AWS) with a custom Kubernetes request configuration
- cloudera.cloud.ml:
    name: ml-k8s-example
    env: cdp-env
    k8s_request:
      environmentName: cdp-env
      instanceGroups:
        - name: default_settings
          autoscaling:
            maxInstances: 10
            minInstances: 1
          instanceType: m5.2xlarge
        - name: cpu_settings
          autoscaling:
            maxInstances: 10
            minInstances: 1
          instanceCount: 0
          instanceTier: "ON_DEMAND"
          instanceType: m5.2xlarge
          rootVolume:
            size: 60
        - name: gpu_settings
          autoscaling:
            maxInstances: 1
            minInstances: 0
          instanceCount: 0
          instanceTier: "ON_DEMAND"
          instanceType: "p2.8xlarge"
          rootVolume:
            size: 40
      wait: yes

# Remove a ML Workspace, but return immediately
- cloudera.cloud.ml:
    name: ml-example
    env: cdp-env
    state: absent
    wait: no
'''

RETURN = r'''
---
workspace:
  description: The information about the ML Workspace
  type: dict
  returned: when supported
  contains:
    cloudPlatform:
      description: The cloud platform of the environment that was used to create this workspace.
      returned: always
      type: str
    clusterBaseDomain:
      description: The basedomain of the cluster.
      returned: when supported
      type: str
    creationDate:
      description: Creation date of workspace (date-time).
      returned: always
      type: str
      sample: "2021-05-19T15:35:17.997000+00:00"
    creatorCrn:
      description: The CRN of the creator of the workspace.
      returned: always
      type: str
    crn:
      description: The CRN of the workspace.
      returned: always
      type: str
    endpointPublicAccess:
      description: Flag indicating if the cluster is publicly accessible.
      returned: always
      type: bool
    environmentCrn:
      description: CRN of the environment.
      returned: always
      type: str
    environmentName:
      description: The name of the workspace's environment.
      returned: always
      type: str
    failureMessage:
      description: Failure message from the most recent failure that has occurred during workspace provisioning.
      returned: during failure
      type: str
    filesystemID:
      description: A filesystem ID referencing the filesystem that was created on the cloud provider environment that this workspace uses.
      returned: always
      type: str
    governanceEnabled:
      description: Flag indicating if Cloudera Atlas governance is enabled for the cluster.
      returned: when supported
      type: bool
    healthInfoLists:
      description: The health info information of the workspace.
      type: list
      contains:
        HealthInfo:
          description: Healthinfo  object  contains  the health information of a resource.
          type: array
          returned: always
          contains:
            details:
              description: The detail of the health info.
              returned: always
              type: array
            isHealthy:
              description: The boolean that indicates the health status.
              returned: always
              type: bool
            message:
              description: The message to show for the health info.
              returned: always
              type: str
            resourceName:
              description: The resource name being checked.
              returned: always
              type: str
            updatedAt:
              description: The unix timestamp for the heartbeat.
              returned: always
              type: str
    httpsEnabled:
      description: Indicates if HTTPS communication was enabled on this workspace when provisioned.
      returned: always
      type: bool
    instanceGroups:
      description: The instance groups details for the cluster.
      returned: always
      type: array
      elements: dict
      contains:
        instanceCount:
          description: The initial number of instance nodes.
          returned: always
          type: int
        instanceGroupName: 
          description: The unique name of the instance group.
          returned: always
          type: str
        instanceType:
          description: The cloud provider instance type for the node instances.
          returned: always
          type: str
        instances:
          description: Instances in the instance group.
          returned: always
          type: list
          elements: dict
          contains:
            availabilityZone:
              description: Availability zone of the instance.
              returned: always
              type: str
            instanceId:
              description: Unique instance Id generated by the cloud provider.
              returned: always
              type: str
        maxInstances:
          description: The maximum number of instances that can be deployed to this instance group.
          returned: always
          type: int
        minInstances: 
          description: The minimum number of instances that can be deployed to this instance group. If the value is 0, the group might be empty.
          returned: always
          type: int
        tags:
          description: Key/value pairs applied to all applicable resources deployed in cloud provider.
          returned: always
          type: list
          elements: dict
          contains:
            key:
              description: Tag name
              returned: always
              type: str
            value:
              description: Tag value
              returned: always
              type: str
    instanceName:
      description: The name of the workspace.
      returned: always
      type: str
    instanceStatus:
      description: The workspace's current status.
      returned: always
      type: str
    instanceUrl:
      description: URL of the workspace's user interface.
      returned: always
      type: str
    k8sClusterName:
      description: The Kubernetes cluster name.
      returned: always
      type: str
    loadBalancerIPWhitelists:
      description: The whitelist of ips for loadBalancer.
      returned: always
      type: array
    modelMetricsEnabled:
      description: Flag indicating if model metrics export is enabled for the cluster.
      returned: when supported
      type: bool
    monitoringEnabled:
      description: If usage monitoring is enabled or not on this workspace.
      returned: always
      type: bool
    tags:
      description: Tags provided by the user at the time of workspace creation.
      returned: always
      type: list
      elements: dict
      contains:
        key:
          description: Tag name
          returned: always
          type: str
        value:
          description: Tag value
          returned: always
          type: str
    version:
      description: The version of Cloudera Machine Learning that was installed on the workspace.
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


class MLWorkspace(CdpModule):
    def __init__(self, module):
        super(MLWorkspace, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.env = self._get_param('environment')

        self.tls = self._get_param('tls')
        self.monitoring = self._get_param('monitoring')
        self.governance = self._get_param('governance')
        self.metrics = self._get_param('metrics')
        self.database = self._get_param('database')
        self.nfs = self._get_param('nfs')
        self.nfs_version = self._get_param('nfs_version')
        self.ip_addresses = self._get_param('ip_addresses')
        self.public_loadbalancer = self._get_param('public_loadbalancer')
        self.k8s_request = self._get_param('k8s_request')

        self.force = self._get_param('force')
        self.storage = self._get_param('storage')

        self.state = self._get_param('state')
        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')

        # Initialize return values
        self.workspace = {}

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):        
        self.target = self.cdpy.ml.describe_workspace(
            name=self.name, env=self.env)

        # If the Workspace exists
        if self.target is not None:
            # Delete the Workspace
            if self.state == 'absent':
                if self.module.check_mode:
                    self.workspace = self.target
                else:
                    if self.target['instanceStatus'] in self.cdpy.sdk.REMOVABLE_STATES:
                        self._delete_workspace()
                    elif self.target['instanceStatus'] in self.cdpy.sdk.TERMINATION_STATES:
                        self.module.log(
                            "ML Workspace already performing Delete operation: %s" % self.target['instanceStatus'])
                    else:
                        self.module.warn(
                            "ML Workspace not in valid state to perform Delete operation: %s" % self.target['instanceStatus'])
                        if self.wait:
                            self.module.warn(
                                "Waiting for ML Workspace to reach Active state before performing Delete operation")
                            self._wait_ready_state()
                            self._delete_workspace()

                    if self.wait:
                        self._wait_delete_state()
                    else:
                        self.workspace = self.target
            elif self.state == 'present':
                # Check the existing configuration
                self.module.warn("ML Workspace already present and configuration validation and reconciliation is not supported;" +
                                 "to change a ML Workspace, explicitly destroy and recreate the Workspace")
                if self.wait:
                    self.workspace = self._wait_ready_state()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

        # Else if the Workspace does not exist
        else:
            if self.state == 'absent':
                self.module.log(
                    "ML Workspace %s already absent in Environment %s" % (self.name, self.env))
            # Create the Workspace
            elif self.state == 'present':
                if not self.module.check_mode:
                    payload = dict(
                        workspaceName=self.name,
                        environmentName=self.env,
                        disableTLS=not self.tls,
                        enableMonitoring=self.monitoring,
                        enableGovernance=self.governance,
                        enableModelMetrics=self.metrics,
                        existingDatabaseConfig=self.database,
                        existingNFS=self.nfs,
                        nfsVersion=self.nfs_version,
                        loadBalancerIPWhitelists=self.ip_addresses,
                        usePublicLoadBalancer=self.public_loadbalancer,
                        provisionK8sRequest=self.k8s_request
                    )
                    if self.k8s_request and self.k8s_request['tags'] is not None:
                        tag_items = []
                        for k, v in self.k8s_request['tags'].items():
                            tag_items.append(dict(key=k, value=v))
                        payload['provisionK8sRequest']['tags'] = tag_items

                    normalized_payload = MLWorkspace._normalize_payload(
                        payload)
                    self.cdpy.sdk.call(
                        'ml', 'create_workspace', **normalized_payload)
                    if self.wait:
                        self.workspace = self._wait_ready_state()
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state)

    def _delete_workspace(self):
        payload = dict(force=self.force, removeStorage=self.storage)
        if self.env is not None:
            payload.update(workspaceName=self.name, environmentName=self.env)
        else:
            payload.update(workspaceCrn=self.name)
        self.cdpy.sdk.call('ml', 'delete_workspace', **payload)

    def _wait_ready_state(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.ml.describe_workspace,
            params=dict(name=self.name, env=self.env), field='instanceStatus',
            state='installation:finished', delay=self.delay, timeout=self.timeout
        )

    def _wait_delete_state(self):
        return self.cdpy.sdk.wait_for_state(
            describe_func=self.cdpy.ml.describe_workspace,
            params=dict(name=self.name, env=self.env),
            field=None, delay=self.delay, timeout=self.timeout, ignore_failures=self.force
        )

    @staticmethod
    def _normalize_payload(payload):
        normalized = dict()
        for k, v in payload.items():
            if isinstance(v, dict):
                normalized[k] = MLWorkspace._normalize_payload(v)
            elif isinstance(v, (list, set, tuple)):
                normalized[k] = type(v)(MLWorkspace._normalize_payload(el)
                                        if isinstance(el, dict) else el for el in v)
            elif v is not None:
                normalized[k] = v
        return normalized


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            # TODO - Handle CRN as separate parameter with tests
            name=dict(required=True, type='str', aliases=[
                      'workspace', 'crn', 'workspace_crn']),
            environment=dict(required=False, type='str', aliases=['env']),
            tls=dict(required=False, type='bool',
                     default=True, aliases=['enable_tls']),
            monitoring=dict(required=False, type='bool',
                            default=False, aliases=['enable_monitoring']),
            governance=dict(required=False, type='bool',
                            default=False, aliases=['enable_governance']),
            metrics=dict(required=False, type='bool',
                            default=False, aliases=['enable_metrics']),
            database=dict(required=False, type='dict', options=dict(
                existingDatabaseHost=dict(required=False, type='str'),
                existingDatabaseName=dict(required=False, type='str'),
                existingDatabasePort=dict(required=False, type='str'),
                existingDatabaseUser=dict(required=False, type='str'),
                existingDatabasePassword=dict(required=False, type='str')
            ), aliases=['existing_database', 'database_config']),
            nfs=dict(required=False, type='str', aliases=['existing_nfs']),
            nfs_version=dict(required=False, type='str'),
            k8s_request=dict(required=False, type='dict', options=dict(
                environmentName=dict(required=True, type='str'),
                instanceGroups=dict(required=True, type='list', elements='dict', options=dict(
                    autoscaling=dict(required=False, type='dict', options=dict(
                        enabled=dict(required=False,
                                     type='bool', default=True),
                        maxInstances=dict(required=True, type='int'),
                        minInstances=dict(required=True, type='int')
                    )),
                    ingressRules=dict(
                        required=False, type='list', elements='str'),
                    instanceCount=dict(required=False, type='int', default=0),
                    instanceTier=dict(required=False, type='str'),
                    instanceType=dict(required=True, type='str'),
                    name=dict(required=False, type='str'),
                    rootVolume=dict(required=False, type='dict', options=dict(
                        size=dict(required=True, type='int')
                    ))
                )),
                network=dict(required=False, type='dict', options=dict(
                    plugin=dict(required=False, type='str'),
                    topology=dict(required=False, type='dict', options=dict(
                        subnets=dict(required=False,
                                     type='list', elements='str')
                    ))
                )),
                tags=dict(required=False, type='dict')
            ), aliases=['provision_k8s']),
            ip_addresses=dict(required=False, type='list', elements='str', aliases=[
                              'loadbalancer_access_ips']),
            public_loadbalancer=dict(required=False, type='bool', default=False, aliases=[
                                     'enable_public_loadbalancer']),
            force=dict(required=False, type='bool',
                       default=False, aliases=['force_delete']),
            storage=dict(required=False, type='bool',
                         default=True, aliases=['remove_storage']),
            state=dict(required=False, type='str', choices=[
                       'present', 'absent'], default='present'),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=[
                       'polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=[
                         'polling_timeout'], default=3600)
        ),
        supports_check_mode=True
    )

    result = MLWorkspace(module)
    output = dict(changed=False, workspace=result.workspace)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
