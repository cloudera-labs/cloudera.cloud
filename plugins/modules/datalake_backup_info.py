#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024 Cloudera, Inc. All Rights Reserved.
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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: cloudera.cloud.datalake_backup_info
short_description: Gather information about a Datalake backup
description:
    - Gather information about a Datalake backup
    - Optionally filter by backup name or backup id
author:
    - "Jim Enright (@jimright)"
options:
    datalake_name:
        description:
            - The name of the datalake to backup
        required: true
        type: str
    backup_name:
        description:
            - The name of the backup
        required: false
        type: str
    backup_id:
        description:
            - The id of the backup
        required: false
        type: str
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Gather information about all backups for a Datalake
  cloudera.cloud.datalake_backup_info:
    datalake_name: "datalake"
  register: backup_result

- name: Gather information about a specific backup name for a Datalake
  cloudera.cloud.datalake_backup_info:
    datalake_name: "datalake"
    backup_name: "backup"
  register: backup_result

- name: Gather information about a specific backup id for a Datalake
  cloudera.cloud.datalake_backup_info:
    datalake_name: "datalake"
    backup_id: "backup_id"
  register: backup_result
"""

RETURN = r"""
backups:
  description: Information about the backup
  type: list
  elements: dict
  returned: always
  contains:
    backupName:
      description: The name of the backup
      type: str
      returned: always
    accountId:
      description: The account id
      type: str
      returned: always
    userCrn:
      description: The user crn
      type: str
      returned: always
    backupId:
      description: The backup id
      type: str
      returned: always
    internalState:
      description: The state of each internal backup components
      type: str
      returned: always
    status:
      description: The status of the backup
      type: str
      returned: always
    startTime:
      description: The start time of the backup
      type: str
      returned: always
    endTime:
      description: The end time of the backup
      type: str
      returned: always
    backupLocation:
      description: The location of the backup
      type: str
      returned: always
"""


class DatalakeBackupInfo(CdpModule):
    def __init__(self, module):
        super(DatalakeBackupInfo, self).__init__(module)

        # Set Variables
        self.datalake_name = self._get_param("datalake_name")
        self.backup_name = self._get_param("backup_name")
        self.backup_id = self._get_param("backup_id")

        # Initialize the return values
        self.output = []
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):

        # Confirm datalake exists
        datalake_info = self.cdpy.datalake.describe_datalake(self.datalake_name)

        if datalake_info is None:
            self.module.warn("Datalake {0} not found".format(self.datalake_name))
        else:
            datalake_backups = self.cdpy.datalake.list_datalake_backups(
                datalake_name=self.datalake_name
            )

            # Filter for backup name or backup id if specified
            if self.backup_name is not None:
                named_backups = [
                    item
                    for item in datalake_backups["backups"]
                    if item["backupName"] == self.backup_name
                ]
                if len(named_backups) == 0:
                    self.module.warn(
                        "Backup name {0} not found for Datalake {1}".format(
                            self.backup_name, self.datalake_name
                        )
                    )

                self.output = named_backups

            elif self.backup_id is not None:
                single_backup = [
                    item
                    for item in datalake_backups["backups"]
                    if item["backupId"] == self.backup_id
                ]

                if len(single_backup) == 0:
                    self.module.warn(
                        "Backup id {0} not found for Datalake {1}".format(
                            self.backup_id, self.datalake_name
                        )
                    )

                self.output = single_backup
            else:
                self.output = datalake_backups["backups"]


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datalake_name=dict(required=True, type="str", aliases=["name"]),
            backup_name=dict(required=False, type="str"),
            backup_id=dict(required=False, type="str"),
        ),
        mutually_exclusive=[["backup_name", "backup_id"]],
        supports_check_mode=True,
    )

    result = DatalakeBackupInfo(module)

    output = dict(changed=False, backups=result.output)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
