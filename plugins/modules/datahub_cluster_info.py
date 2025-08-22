#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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

DOCUMENTATION = r"""
module: datahub_cluster_info
short_description: Gather information about CDP Datahubs
description:
    - Gather information about CDP Datahub Clusters
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that Datahub will be described.
      - If no name provided, all Datahubs will be listed and (optionally) constrained by the C(environment) parameter.
    type: str
    required: False
    aliases:
      - datahub
  environment:
    description:
      - The name of the Environment in which to find and describe the Datahubs.
    type: str
    required: False
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all Datahubs
- cloudera.cloud.datahub_cluster_info:

# Gather detailed information about a named Datahub
- cloudera.cloud.datahub_cluster_info:
    name: example-datahub

# Gather detailed information about a Datahub in an Environment
- cloudera.cloud.datahub_cluster_info:
    environment: example-env-name
"""

RETURN = r"""
datahubs:
  description: The information about the named Datahub or Datahubs
  type: list
  returned: on success
  elements: dict
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class DatahubClusterInfo(CdpModule):
    def __init__(self, module):
        super(DatahubClusterInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.env = self._get_param("environment")

        # Initialize return values
        self.datahubs = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:  # Note that both None and '' will trigger this
            datahub_single = self.cdpy.datahub.describe_cluster(self.name)
            if datahub_single is not None:
                self.datahubs.append(datahub_single)
        else:
            self.datahubs = self.cdpy.datahub.describe_all_clusters(self.env)
            # The sdk will ignore env = None and list all Datahubs, making this a shortcut


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str", aliases=["datahub"]),
            environment=dict(required=False, type="str", aliases=["env"]),
        ),
        supports_check_mode=True,
    )

    result = DatahubClusterInfo(module)
    output = dict(changed=False, datahubs=result.datahubs)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
