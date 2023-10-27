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

from time import time, sleep

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: datahub_cluster_repair
short_description: Repair CDP Datahub instances or instance groups
description:
    - Execute a repair (remove and/or replace) on one or more instances or instance groups within a CDP Datahub.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  datahub:
    description:
      - The name or CRN of the datahub.
    required: True
  instance_groups:
    description:
      - A list of CDP Datahub instance group names.
      - Required if I(instances) is not defined.
    type: list
    elements: str
    aliases:
      - groups
  instances:
    description:
      - A list of CDP Datahub instance IDs .
      - Required if I(instance_groups) is not defined.
    type: list
    elements: str
  restart:
    description:
      - Flag to restart (replace) removed instances.
    type: bool
    default: True
  delete_volumes:
    description:
      - Flag to recreate disk volumes on instances.
      - If C(false), the existing volumes will be reattached to the new instances.
    type: bool
    default: False
  wait:
    description:
      - Flag to wait for the repair to complete.
    type: bool
    default: True
  delay:
    description:
      - Number of seconds for the I(wait) polling interval.
    type: int
    default: 15
  timeout:
    description:
      - Number of elapsed seconds for the I(wait) polling timeout.
    type: int
    default: 1200
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
notes:
  - This module supports C(check_mode).
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Replace a single instance group
  cloudera.cloud.datahub_cluster_repair:
    datahub: example-datahub
    instance_groups: core_broker

- name: Replace multiple instance groups
  cloudera.cloud.datahub_cluster_repair:
    datahub: example-datahub
    instance_groups:
      - core_broker
      - master
      
- name: Replace a single instance
  cloudera.cloud.datahub_cluster_repair:
    datahub: example-datahub
    instances: i-08fa9ff7694dca0a8
    
- name: Replace multiple instances and remove their volumes
  cloudera.cloud.datahub_cluster_repair:
    datahub: example-datahub
    instances:
      - i-08fa9ff7694dca0a8
      - i-0ea1b60d9a103ab36
    delete_volumes: yes
      
- name: Replace multiple instances sequentially (i.e. rollout)
  cloudera.cloud.datahub_cluster_repair:
    datahub: example-datahub
    instances: "{{ instance_id }}"
    wait: yes # implied
  loop: {{ query('cloudera.cloud.datahub_instance', 'core_broker', datahub='example-datahub', detailed=True) | flatten | map(attribute='id') | list }}
  loop_control:
    loop_var: instance_id
"""

RETURN = r"""
---
datahub:
  description: The information about the Datahub
  type: dict
  returned: always
  contains:
    cloudPlatform:
      description:
        - The cloud platform.
      returned: when supported
    clouderaManager:
      description:
        - The Cloudera Manager details.
      type: dict
      contains:
        platformVersion:
          description:
            - CDP Platform version.
          returned: when supported
        version:
          description: Cloudera Manager version.
          returned: always
    clusterName:
      description:
        - The name of the cluster.
      returned: always
    clusterStatus:
      description:
        - The status of the cluster.
      returned: when supported
    clusterTemplateCrn:
      description:
        - The CRN of the cluster template used for the cluster creation.
      returned: when supported
    creationDate:
      description:
        - The date when the cluster was created.
        - Return value is a date timestamp.
      returned: when supported
    credentialCrn:
      description:
        - The CRN of the credential.
      returned: when supported
    crn:
      description:
        - The CRN of the cluster.
      returned: always
    datalakeCrn:
      description:
        - The CRN of the attached datalake.
      returned: when supported
    endpoints:
      description:
        - The exposed service API endpoints.
      type: list
      elements: dict
      returned: when supported
      contains:
        endpoint:
          description:
            - The endpoints.
          type: list
          elements: dict
          returned: always
          contains:
            displayName:
              description:
                - The more consumable name of the exposed service.
              returned: always
            knoxService:
              description:
                - The related knox entry.
              returned: always
            mode:
              description:
                - The SSO mode of the given service.
              returned: always
            open:
              description:
                - Flag of the access status of the given endpoint.
              type: bool
              returned: always
            serviceName:
              description:
                - The name of the exposed service.
              returned: always
            serviceUrl:
              description:
                - The server url for the given exposed service’s API.
              returned: always
    environmentCrn:
      description:
        - The CRN of the environment.
      returned: when supported
    environmentName:
      description:
        - The name of the environment.
      returned: when supported
    imageDetails:
      description:
        - The image details.
      type: dict
      returned: when supported
      contains:
        catalogName:
          description:
            - The image catalog name.
          returned: when supported
        catalogUrl:
          description:
            - The image catalog URL.
          returned: when supported
        id:
          description:
            - The ID of the image used for cluster instances.
            - This is internally generated by the cloud provider to uniquely identify the image.
          returned: when supported
        name:
          description:
            - The name of the image used for cluster instances.
          returned: when supported
    instanceGroups:
      description:
        - The instance details.
      type: list
      elements: dict
      returned: when supported
      contains:
        availabilityZones:
          description:
            - List of availability zones associated with the instance group.
          type: list
          elements: str
          returned: when supported
        instances:
          description:
            - List of instances in this instance group.
          type: list
          elements: dict
          returned: always
          contains:
            attachedVolumes:
              description:
                - List of volumes attached to this instance.
              type: list
              elements: dict
              returned: when supported
              contains:
                count:
                  description:
                    - The number of volumes.
                  type: int
                  returned: when supported
                size:
                  description:
                    - The size of each volume in GB.
                  type: int
                  returned: when supported
                volumeType:
                  description:
                    - The type of volumes.
                  returned: when supported
            availabilityZone:
              description:
                - The availability zone of the instance.
              returned: when supported
            clouderaManagerServer:
              description:
                - Flag indicating if Cloudera Manager has been deployed or not.
              type: bool
              returned: when supported
            fqdn:
              description:
                - The fully-qualified domain name (FQDN) of the instance.
              returned: when supported
            id:
              description:
                - The ID of the given instance.
              returned: always
            instanceGroup:
              description:
                - The name of the instance group associated with the instance.
              returned: when supported
            instanceType:
              description:
                - The type of the given instance.
                - Values are C(GATEWAY), C(GATEWAY_PRIMARY), or C(CORE).
              returned: always
            instanceVmType:
              description:
                - The VM type of the instance.
                - Supported values depend on the cloud platform.
              returned: when supported
            privateIp:
              description:
                - The private IP of the given instance.
              returned: when supported
            publicIp:
              description:
                - The public IP of the given instance.
              returned: when supported
            rackId:
              description:
                - The rack ID of the instance in Cloudera Manager.
              returned: when supported
            sshPort:
              description:
                - The SSH port for the instance.
              type: int
              returned: when supported
            state:
              description:
                - The health state of the instance. 
                - C(UNHEALTHY) represents instances with unhealthy services, lost instances, or failed operations.
              returned: always
            status:
              description:
                - The status of the instance.
                - This includes information like whether the instance is being provisioned, stopped, decommissioning failures etc.
              returned: when supported 
            statusReason:
              description:
                - The reason for the current status of this instance.
              returned: when supported
            subnetId:
              description:
                - The subnet ID of the instance.
              returned: when supported
        name:
          description:
            - The name of the instance group where the given instance is located.
          returned: always
        subnetIds:
          description:
            - The list of subnet IDs in case of multi-availability zone setup.
          type: list
          elements: str
          returned: when supported
    nodeCount:
      description:
        - The cluster node count.
      type: int
      returned: when supported
    status:
      description:
        - The status of the stack.
      returned: when supported
    statusReason:
      description:
        - The status reason.
      returned: when supported
    workloadType:
      description:
        - The workload type for the cluster.
      returned: when supported    
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


class DatahubClusterRepair(CdpModule):
    def __init__(self, module):
        super(DatahubClusterRepair, self).__init__(module)

        # Set variables
        self.datahub = self._get_param("datahub")
        self.instance_groups = self._get_param("instance_groups")
        self.instances = self._get_param("instances")
        self.restart = self._get_param("restart")
        self.delete_volumes = self._get_param("delete_volumes")
        self.wait = self._get_param("wait")
        self.delay = self._get_param("delay")
        self.timeout = self._get_param("timeout")

        # Initialize return values
        self.output = dict()
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.datahub.describe_cluster(self.datahub)

        if not existing:
            self.module.fail_json(msg=f"Datahub not found: {self.datahub}")

        if not self.module.check_mode:
            self.changed = True

            node_count = existing["nodeCount"]

            if self.wait:
                existing = self.cdpy.sdk.wait_for_state(
                    describe_func=self.cdpy.datahub.describe_cluster,
                    params=dict(name=self.datahub),
                    state=["AVAILABLE", "NODE_FAILURE"],
                    delay=self.delay,
                    timeout=self.timeout,
                )
                self._wait_for_instance_state(
                    existing, ["HEALTHY", "UNHEALTHY"], node_count
                )

            instance_payload = dict(
                deleteVolumes=self.delete_volumes,
            )

            if self.instances:
                discovered_instances = [
                    i["id"]
                    for ig in existing["instanceGroups"]
                    for i in ig["instances"]
                ]
                if set(self.instances).difference(set(discovered_instances)):
                    self.module.fail_json(
                        msg=f"Instance(s) not found in Datahub: {str(self.instances)}"
                    )

                instance_payload.update(instanceIds=self.instances)
            else:
                discovered_instances = [
                    i["id"]
                    for ig in existing["instanceGroups"]
                    if ig["name"] in self.instance_groups
                    for i in ig["instances"]
                ]
                if not discovered_instances:
                    self.module.fail_json(
                        msg=f"No instances found for instance group(s) in Datahub: {str(self.instance_groups)}"
                    )

                instance_payload.update(instanceIds=discovered_instances)

            payload = dict(
                clusterName=self.datahub,
                removeOnly=not self.restart,
                instances=instance_payload,
            )

            # Empty return
            self.cdpy.sdk.call(svc="datahub", func="repair_cluster", **payload)

            if self.wait:
                existing = self.cdpy.sdk.wait_for_state(
                    describe_func=self.cdpy.datahub.describe_cluster,
                    params=dict(name=self.datahub),
                    state="AVAILABLE",
                    delay=self.delay,
                    timeout=self.timeout,
                )
                self._wait_for_instance_state(existing, "HEALTHY", node_count)

            self.output = self.cdpy.datahub.describe_cluster(self.datahub)
        else:
            self.output = existing

    def _wait_for_instance_state(self, datahub, state, node_count):
        current = datahub
        state = state if isinstance(state, list) else [state]

        def parse_instances():
            return [
                i["id"]
                for ig in current["instanceGroups"]
                for i in ig["instances"]
                if i["state"] not in state
            ]

        start_time = time()
        while time() < start_time + self.timeout:
            outstanding_instances = parse_instances()
            if outstanding_instances or current["nodeCount"] != node_count:
                self.module.warn(
                    f"Waiting for state(s) [{str(state)}] for instances: {str(outstanding_instances)}; Node count: {str(current['nodeCount'])}/{str(node_count)}"
                )
                sleep(self.delay)
                current = self.cdpy.datahub.describe_cluster(self.datahub)
                outstanding_instances = parse_instances()
            else:
                break


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datahub=dict(required=True),
            instance_groups=dict(type="list", elements="str", aliases=["groups"]),
            instances=dict(type="list", elements="str"),
            restart=dict(type="bool", default=True),
            delete_volumes=dict(type="bool", default=False),
            wait=dict(type="bool", default=True),
            delay=dict(type="int", aliases=["polling_delay"], default=15),
            timeout=dict(type="int", aliases=["polling_timeout"], default=600),
        ),
        required_one_of=[["instance_groups", "instances"]],
        supports_check_mode=True,
    )

    result = DatahubClusterRepair(module)
    output = dict(changed=result.changed, datahub=result.output)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
