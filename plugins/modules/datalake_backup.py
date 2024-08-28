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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: cloudera.cloud.datalake_backup
short_description: Create a backup of a datalake
description:
    - Create a backup of a datalake
    - Optionally wait for the backup to complete
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
    wait:
        description:
            - Whether to wait for the backup to complete
        required: false
        type: bool
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

- name: Create a datalake backup
  cloudera.cloud.datalake_backup:
    datalake_name: "datalake"
    backup_name: "backup"
  register: backup_result

- name: Create a datalake backup and wait for it to complete
  cloudera.cloud.datalake_backup:
    datalake_name: "datalake"
    backup_name: "backup"
    wait: true
  register: backup_result
'''


RETURN = r'''
backup:
    description: The details of the backup
    type: list
    elements: dict
    returned: always
    contains:
        backupName:
            description: The name of the backup
            type: str
        accountId:
            description: The account id
            type: str
        userCrn:
            description: The crn of the user that initiated the backup operation 
            type: str
        backupId:
            description: The backup id
            type: str
        internalState:
            description: The internal state of each backup stage
            type: str
        status:
            description: The overall status of the backup operation
            type: str
        startTime:
            description: The start time
            type: str
        endTime:
            description: The end time
            type: str
        backupLocation:
            description: The backup location
            type: str
'''

class DatalakeBackup(CdpModule):
    def __init__(self, module):
        super(DatalakeBackup, self).__init__(module)

        # Set Variables
        self.datalake_name = self._get_param('datalake_name')
        self.backup_name = self._get_param('backup_name')
        self.wait = self._get_param('wait', False)

        # Initialize the return values
        self.output = dict()
        self.changed = False
        # Execute logic process
        self.process()
        
    @CdpModule._Decorators.process_debug
    def process(self):

        # Confirm datalake exists
        datalake_info = self.cdpy.datalake.describe_datalake(self.datalake_name)

        if datalake_info is None:
            self.module.fail_json(msg='Datalake {0} does not exist'.format(self.datalake_name))
        else:
            backup = self.cdpy.datalake.create_datalake_backup(datalake_name=self.datalake_name, backup_name=self.backup_name)

            if self.wait:
                self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.datalake.check_datalake_backup_status,
                params=dict(datalake_name=self.datalake_name, backup_id=backup['backupId']),
                state=["SUCCESSFUL"])
       
        datalake_backups = self.cdpy.datalake.list_datalake_backups(datalake_name=self.datalake_name)
        self.output = [item for item in datalake_backups['backups'] if item['backupId'] == backup['backupId']] 
        self.changed = True

def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datalake_name=dict(required=True, type='str',aliases=['name']),
            backup_name=dict(required=False, type='str'),
            wait=dict(required=False, type='bool'),
        ),
        supports_check_mode=True
    )

    result = DatalakeBackup(module)

    output = dict(
        changed=result.changed,
        backup=result.output
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines
        )

    module.exit_json(**output)


if __name__ == '__main__':
    main()
