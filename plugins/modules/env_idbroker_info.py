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
module: env_idbroker_info
short_description: Gather information about CDP ID Broker
description:
  - Gather information about the ID Broker mappings for a CDP Environment.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the Environment.
    aliases:
      - environment
    type: str
    required: True
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Gather information about the ID Broker mappings
- cloudera.cloud.env_idbroker_info:
    name: example-environment
"""

RETURN = r"""
idbroker:
    description: Returns the mappings and sync status for the ID Broker for the Environment.
    returned: when supported
    type: dict
    contains:
        mappingsVersion:
            description: The version of the mappings.
            returned: always
            type: str
            sample: AWS
        dataAccessRole:
            description: The cloud provider role to which data access services will be mapped (e.g. an ARN in AWS, a
                Resource ID in Azure).
            returned: always
            type: str
        rangerAuditRole:
            description:
              - The cloud provider role to which services that write to Ranger audit logs will be mapped (e.g. an ARN
                    in AWS, a Resource ID in Azure).
              - Note that some data access services also write to Ranger audit logs; such services will be mapped to
                    the 'dataAccessRole', not the 'rangerAuditRole'.
            returned: always
            type: str
        rangerCloudAccessAuthorizerRole:
            description: The cloud provider role to which the Ranger RAZ service will be mapped (e.g. an ARN in AWS, a
                Resource ID in Azure).
            returned: when supported
            type: str
        mappings:
            description: ID Broker mappings for individual actors and groups. Does not include mappings for data access
                services.
            returned: when supported
            type: list
            elements: dict
            contains:
              accessorCrn:
                description: The CRN of the actor (group or user) mapped to the cloud provider role.
                returned: on success
                type: str
              role:
                description: The cloud provider identitier for the role.
                returned: on success
                type: str
        syncStatus:
            description: The status of the most recent ID Broker mappings sync operation, if any. Not present if there
                is no Datalake associated with the Environment.
            returned: when supported
            type: dict
            contains:
                globalStatus:
                    description: The overall mappings sync status for all Datalake clusters in the Environment.
                    returned: always
                    type: str
                    sample:
                        - NEVER_RUN
                        - REQUESTED
                        - REJECTED
                        - RUNNING
                        - COMPLETED
                        - FAILED
                        - TIMEDOUT
                syncNeeded:
                    description: Flag indicating whether a sync is needed to bring in-cluster mappings up-to-date.
                    returned: always
                    type: bool
                statuses:
                    description: Map of Datalake cluster CRN-to-mappings sync status for each Datalake cluster in the
                        environment.
                    returned: always
                    type: dict
                    contains:
                        __datalake CRN__:
                            description: The Datalake cluster CRN
                            returned: always
                            type: dict
                            contains:
                                endDate:
                                    description: The date when the mappings sync completed or was terminated. Omitted
                                        if status is NEVER_RUN or RUNNING.
                                    returned: when supported
                                    type: str
                                errorDetail:
                                    description: The detail of the error. Omitted if status is not FAILED.
                                    returned: when supported
                                    type: str
                                startDate:
                                    description: The date when the mappings sync started executing. Omitted if status
                                        is NEVER_RUN.
                                    returned: when supported
                                    type: str
                                status:
                                    description: The mappings sync summary status.
                                    returned: always
                                    type: str
                                    sample:
                                        - NEVER_RUN
                                        - REQUESTED
                                        - REJECTED
                                        - RUNNING
                                        - COMPLETED
                                        - FAILED
                                        - TIMEDOUT
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


class EnvironmentIdBrokerInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentIdBrokerInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")

        # Initialize the return values
        self.idbroker = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.idbroker = self.cdpy.environments.gather_idbroker_mappings(self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type="str", aliases=["environment"]),
        ),
        supports_check_mode=True,
    )

    result = EnvironmentIdBrokerInfo(module)

    output = dict(
        changed=False,
        idbroker=result.idbroker,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
