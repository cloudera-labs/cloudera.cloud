#!/usr/bin/python
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

DOCUMENTATION = r"""
module: datalake_info
short_description: Gather information about CDP Datalakes
description:
    - Gather information about CDP Datalakes
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is given, that Datalake will be described.
      - If no name is given, all Datalakes will be listed and (optionally) constrained by the C(environment) parameter.
    type: str
    required: False
    aliases:
      - datalake
  environment:
    description:
      - The name of the Environment in which to find and describe the Datalake.
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

# List basic information about all Datalakes
- cloudera.cloud.datalake_info:

# Gather detailed information about a named Datalake
- cloudera.cloud.datalake_info:
    name: example-datalake

# Gather detailed information about the Datalake in an Environment
- cloudera.cloud.datalake_info:
    environment: example-env
"""

RETURN = r"""
datalakes:
  description: The information about the named Datalake or Datalakes
  type: list
  returned: on success
  elements: complex
  contains:
    awsConfiguration:
      description: AWS-specific configuration details.
      returned: when supported
      type: dict
      contains:
        instanceProfile:
          description: The instance profile used for the ID Broker instance.
          type: str
          returned: always
    azureConfiguration:
      description: Azure-specific environment configuration information.
      returned: when supported
      type: dict
      contains:
        managedIdentity:
          description: The managed identity used for the ID Broker instance.
          type: str
          returned: always
    cloudPlatform:
      description: Cloud provider of the Datalake.
      returned: when supported
      type: str
      sample:
        - AWS
        - AZURE
    clouderaManager:
      description: The Cloudera Manager details.
      returned: when supported
      type: dict
      contains:
        clouderaManagerRepositoryURL:
          description: Cloudera Manager repository URL.
          type: str
          returned: always
        clouderaManagerServerURL:
          description: Cloudera Manager server URL.
          type: str
          returned: when supported
        version:
          description: Cloudera Manager version.
          type: str
          returned: always
          sample: 7.2.1
    creationDate:
      description: The timestamp when the Datalake was created.
      returned: when supported
      type: str
      sample: 2020-09-23T11:33:50.847000+00:00
    credentialCrn:
      description: CRN of the CDP Credential.
      returned: when supported
      type: str
    crn:
      description: CRN value for the Datalake.
      returned: always
      type: str
    datalakeName:
      description: Name of the Datalake.
      returned: always
      type: str
    endpoints:
      description: Details for the exposed service API endpoints of the Datalake.
      returned: when supported
      type: dict
      contains:
        endpoints:
          description: The exposed API endpoints.
          returned: always
          type: list
          elements: dict
          contains:
            displayName:
              description: User-friendly name of the exposed service.
              returned: always
              type: str
              sample: Atlas
            knoxService:
              description: The related Knox entry for the service.
              returned: always
              type: str
              sample: ATLAS_API
            mode:
              description: The Single Sign-On (SSO) mode for the service.
              returned: always
              type: str
              sample: PAM
            open:
              description: Flag for the access status of the service.
              returned: always
              type: bool
            serviceName:
              description: The name of the exposed service.
              returned: always
              type: str
              sample: ATLAS_SERVER
            serviceUrl:
              description: The server URL for the exposed service’s API.
              returned: always
              type: str
              sample: "https://some.domain/a-datalake/endpoint"
    environmentCrn:
      description: CRN of the associated Environment.
      returned: when supported
      type: str
    instanceGroups:
      description: The instance details of the Datalake.
      returned: when supported
      type: list
      elements: complex
      contains:
        instances:
          description: Details about the instances.
          returned: always
          type: list
          elements: dict
          contains:
            id:
              description: The identifier of the instance.
              returned: always
              type: str
              sample: i-00b58f27be4e7ab9f
            state:
              description: The state of the instance.
              returned: always
              type: str
              sample: HEALTHY
        name:
          description: Name of the instance group associated with the instances.
          returned: always
          type: str
          sample: idbroker
    productVersions:
      description: The product versions.
      returned: when supported
      type: list
      elements: dict
      contains:
        name:
          description: The name of the product.
          returned: always
          type: str
          sample: FLINK
        version:
          description: The version of the product.
          returned: always
          type: str
          sample: 1.10.0-csa1.2.1.0-cdh7.2.1.0-240-4844562
    region:
      description: The region of the Datalake.
      returned: when supported
      type: str
    status:
      description: The status of the Datalake.
      returned: when supported
      type: str
      sample:
        - EXTERNAL_DATABASE_START_IN_PROGRESS
        - START_IN_PROGRESS
        - RUNNING
        - EXTERNAL_DATABASE_START_IN_PROGRESS
        - START_IN_PROGRESS
        - EXTERNAL_DATABASE_STOP_IN_PROGRESS
        - STOP_IN_PROGRESS
        - STOPPED
        - REQUESTED
        - EXTERNAL_DATABASE_CREATION_IN_PROGRESS
        - STACK_CREATION_IN_PROGRESS
        - EXTERNAL_DATABASE_DELETION_IN_PROGRESS
        - STACK_DELETION_IN_PROGRESS
        - PROVISIONING_FAILED
    statusReason:
      description: An explanation of the status.
      returned: when supported
      type: str
      sample: Datalake is running
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


class DatalakeInfo(CdpModule):
    def __init__(self, module):
        super(DatalakeInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.env = self._get_param("environment")

        # Initialize return values
        self.datalakes = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:
            datalake_single = self.cdpy.datalake.describe_datalake(self.name)
            if datalake_single is not None:
                self.datalakes.append(datalake_single)
        else:
            self.datalakes = self.cdpy.datalake.describe_all_datalakes(self.env)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str", aliases=["datalake"]),
            environment=dict(required=False, type="str", aliases=["env"]),
        ),
        supports_check_mode=True,
    )

    result = DatalakeInfo(module)
    output = dict(changed=False, datalakes=result.datalakes)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
