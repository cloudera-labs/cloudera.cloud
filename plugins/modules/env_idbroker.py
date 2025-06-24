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
module: env_idbroker
short_description: Update ID Broker for CDP Environments
description:
  - Update ID Broker mappings for CDP Environments for data access.
  - The module supports C(check_mode).
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
    required: True
    type: str
  data_access:
    description:
      - The cloud provider IAM role for data access.
      - Must be the cloud provider resource identifier
      - For AWS, it should be the ARN
      - For Azure, it should be the Resource ID
      - for GCP, it should be the Service Account fully qualified name
      - When creating a new set of data access mappings, this parameter is required.
    aliases:
      - data_access_arn
      - data
    required: False
    type: str
  ranger_audit:
    description:
      - The cloud provider role to which services that write to Ranger audit logs will be mapped
      - For AWS, it should be the ARN
      - For Azure, it should be the Resource ID
      - for GCP, it should be the Service Account fully qualified name
      - Note that some data access services also write to Ranger audit logs; such services will be mapped to the C(data_access) role, not the C(ranger_audit) role.
      - When creating a new set of data access mappings, this parameter is required.
    aliases:
      - ranger_audit_arn
      - audit
    required: False
    type: str
  ranger_cloud_access:
    description:
      - The cloud provider role to which the Ranger RAZ service will be mapped
      - For AWS, it should be the ARN
      - For Azure, it should be the Resource ID
      - for GCP, it should be the Service Account fully qualified name
      - This is required in RAZ-enabled environments.
    aliases:
      - ranger_cloud_access_arn
      - cloud
    required: False
    type: str
  mappings:
    description:
      - ID Broker mappings for individual users and groups.
      - Does not include mappings for data access services.
      - Mutually exclusive with C(clear_mappings).
    required: False
    type: list
    elements: dict
    suboptions:
      accessor:
        description:
          - The CRN of the actor or group.
        aliases:
          - accessorCrn
        required: True
        type: str
      role:
        description:
          - The cloud provider role (e.g., ARN in AWS, Resource ID in Azure, Service Account in GCP) to which the actor or group is mapped.
        aliases:
          - roleCrn
        required: True
        type: str
  clear_mappings:
    description:
      - Flag to install an empty set of individual mappings, deleting any existing mappings.
      - Mutually exclusive with C(mappings).
    aliases:
      - set_empty_mappings
    required: False
    type: bool
    default: False
  sync:
    description:
      - Flag to sync mappings to the Environment's Datalake(s).
      - If the mappings do not need to be synced or there is no Datalake associated with the Environment, the flag will be ignored.
    aliases:
      - sync_mappings
    required: False
    type: bool
    default: True
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a fresh set of data access mappings for ID Broker
- cloudera.cloud.env_idbroker:
    name: example-environment
    data_access: arn:aws:iam::654468598544:role/some-data-access-role
    ranger_audit: arn:aws:iam::654468598544:role/some-ranger-audit-role

# Set the data access role for ID Broker on an existing environment
- cloudera.cloud.env_idbroker:
    name: example-environment
    data_access: arn:aws:iam::654468598544:role/some-data-access-role

# Set the Ranger audit role for ID Broker on an existing environment
- cloudera.cloud.env_idbroker:
    name: example-environment
    ranger_audit: arn:aws:iam::654468598544:role/some-ranger-audit-role

# Set some actor-to-role mappings for ID Broker on an existing environment
- cloudera.cloud.env_idbroker:
    name: example-environment
    mappings:
      - accessor: crn:altus:iam:us-west-1:1234:group:some-group/abcd-1234-efghi
        role: arn:aws:iam::654468598544:role/another-data-access-role

# Clear the actor-to-role mappings for ID Broker on an existing environment
- cloudera.cloud.env_idbroker:
    name: example-environment
    clear_mappings: true

# Don't sync the mappings for ID Broker to the environment's datalakes
- cloudera.cloud.env_idbroker:
    name: example-environment
    mappings:
      - accessor: crn:altus:iam:us-west-1:1234:group:some-group/abcd-1234-efghi
        role: arn:aws:iam::654468598544:role/another-data-access-role
    sync: false

# Now sync the mappings for the ID Broker once the environment has a datalake
- cloudera.cloud.env_idbroker:
    name: example-environment
    sync: true
"""

RETURN = r"""
idbroker:
    description: Returns the mappings and sync status for the ID Broker for the Environment.
    returned: always
    type: dict
    contains:
        mappingsVersion:
            description: The version of the mappings.
            returned: always
            type: str
            sample: AWS
        dataAccessRole:
            description: The cloud provider role to which data access services will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).
            returned: always
            type: str
        rangerAuditRole:
            description:
              - The cloud provider role to which services that write to Ranger audit logs will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).
              - Note that some data access services also write to Ranger audit logs; such services will be mapped to the 'dataAccessRole', not the 'rangerAuditRole'.
            returned: always
            type: str
        rangerCloudAccessAuthorizerRole:
            description: The cloud provider role to which the Ranger RAZ service will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).
            returned: when supported
            type: str
        mappings:
            description: ID Broker mappings for individual actors and groups. Does not include mappings for data access services.
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
            description: The status of the most recent ID Broker mappings sync operation, if any. Not present if there is no Datalake associated with the Environment.
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
                    description: Map of Datalake cluster CRN-to-mappings sync status for each Datalake cluster in the environment.
                    returned: always
                    type: dict
                    contains:
                        __datalake CRN__:
                            description: The Datalake cluster CRN
                            returned: always
                            type: dict
                            contains:
                                endDate:
                                    description: The date when the mappings sync completed or was terminated. Omitted if status is NEVER_RUN or RUNNING.
                                    returned: when supported
                                    type: str
                                errorDetail:
                                    description: The detail of the error. Omitted if status is not FAILED.
                                    returned: when supported
                                    type: str
                                startDate:
                                    description: The date when the mappings sync started executing. Omitted if status is NEVER_RUN.
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


class EnvironmentIdBroker(CdpModule):
    def __init__(self, module):
        super(EnvironmentIdBroker, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.data_access = self._get_param("data_access")
        self.ranger_audit = self._get_param("ranger_audit")
        self.ranger_cloud_access = self._get_param("ranger_cloud_access")
        self.mappings = self._get_param("mappings")
        self.clear_mappings = self._get_param("clear_mappings")
        self.sync = self._get_param("sync")

        # Initialize the return values
        self.idbroker = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.environments.gather_idbroker_mappings(self.name)

        if existing is None:
            delta = self.reconcile_mappings(list())
            if "mappings" not in delta or self.clear_mappings:
                delta["setEmptyMappings"] = True
            self.set_mappings(delta)
        else:
            delta = self.reconcile_mappings(existing)

            if delta or (self.clear_mappings and existing["mappings"]):
                payload = existing.copy()
                payload.update(delta)

                if (
                    self.clear_mappings
                    or "mappings" not in payload
                    or not payload["mappings"]
                ):
                    _ = payload.pop("mappings", None)
                    payload["setEmptyMappings"] = True

                _ = [
                    payload.pop(x, None)
                    for x in ["mappingsVersion", "baselineRole", "syncStatus"]
                ]

                self.set_mappings(payload)

        if self.sync:
            sync_status = self.cdpy.environments.get_id_broker_mapping_sync(self.name)
            if sync_status is not None and sync_status["syncNeeded"]:
                self.sync_mappings()

        if self.changed:
            self.idbroker = self.cdpy.environments.gather_idbroker_mappings(self.name)
        else:
            self.idbroker = existing

    def reconcile_mappings(self, existing):
        reconciled = dict()

        if self.mappings:

            def normalize_accessor(mapping):
                if "accessor" in mapping:
                    mapping["accessorCrn"] = mapping["accessor"]
                    _ = mapping.pop("accessor", None)
                return mapping

            list(map(normalize_accessor, self.mappings))

        def update_parameter(expected, parameter):
            if expected is not None and (
                (parameter in existing and expected != existing[parameter])
                or parameter not in existing
            ):
                reconciled[parameter] = expected

        parameters = [
            [self.data_access, "dataAccessRole"],
            [self.ranger_audit, "rangerAuditRole"],
            [self.ranger_cloud_access, "rangerCloudAccessAuthorizerRole"],
            [self.mappings, "mappings"],
        ]

        for p in parameters:
            update_parameter(*p)

        return reconciled

    def set_mappings(self, mappings):
        self.changed = True
        if not self.module.check_mode:
            return self.cdpy.sdk.call(
                "environments",
                "set_id_broker_mappings",
                environmentName=self.name,
                **mappings
            )

    def sync_mappings(self):
        self.changed = True
        if not self.module.check_mode:
            self.cdpy.sdk.call(
                "environments", "sync_id_broker_mappings", environmentName=self.name
            )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type="str", aliases=["environment"]),
            data_access=dict(
                required=False, type="str", aliases=["data_access_arn", "data"]
            ),
            ranger_audit=dict(
                required=False, type="str", aliases=["ranger_audit_arn", "audit"]
            ),
            ranger_cloud_access=dict(
                required=False, type="str", aliases=["ranger_cloud_access_arn", "cloud"]
            ),
            mappings=dict(
                required=False,
                type="list",
                elements=dict,
                options=dict(
                    accessor=dict(required=True, type="str", aliases=["accessorCrn"]),
                    role=dict(required=True, type="str", aliases=["roleCrn"]),
                ),
            ),
            clear_mappings=dict(
                required=False,
                type="bool",
                default=False,
                aliases=["set_empty_mappings"],
            ),
            sync=dict(
                required=False, type="bool", default=True, aliases=["sync_mappings"]
            ),
        ),
        mutually_exclusive=[["mappings", "clear_mappings"]],
        supports_check_mode=True,
    )

    result = EnvironmentIdBroker(module)

    output = dict(
        changed=result.changed,
        idbroker=result.idbroker,
        mappings=result.idbroker,  # TODO: Remove this legacy key
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
