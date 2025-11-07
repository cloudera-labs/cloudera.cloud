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
module: cloudera.cloud.datalake_backup
short_description: Create a backup of a datalake
description:
    - Create a backup of a datalake
    - Optionally wait for the backup to complete
author:
    - "Jim Enright (@jimright)"
version_added: "3.0.0"
options:
    datalake_name:
        description:
            - The name of the datalake to backup
        required: true
        type: str
    backup_name:
        description:
            - The name of the backup
            - If I(state=backup) this is the name of the backup to create
            - If I(state=restore) this is the name of the backup to restore
        required: false
        type: str
    backup_id:
        description:
            - The Id of the backup to restore
            - Only applicable when I(state=restore)
        required: false
        type: str
    backup_location:
        description:
            - The location of the backup to use during the restore
            - When not specified the location used will be the backup storage of the environment
            - The I(backup_id) parameter is required when provided with I(state=restore),
        required: false
        type: str
    skip_atlas_indexes:
        description:
            - Skips the restore of the Atlas indexes
            - Only applicable when I(state=restore)
        required: false
        type: bool
    skip_atlas_metadata:
        description:
            - Skips the restore of the Atlas metadata
            - Only applicable when I(state=restore)
        required: false
        type: bool
    skip_ranger_audits:
        description:
            - Skips the restore of the Ranger audits
            - Only applicable when I(state=restore)
        required: false
        type: bool
    skip_ranger_hms_metadata:
        description:
            - Skips the restore of the databases backing HMS/Ranger services
            - Only applicable when I(state=restore)
        required: false
        type: bool
    skip_validation:
        description:
            - Skips the validation steps that run prior to the restore
            - Only applicable when I(state=restore)
        required: false
        type: bool
    state:
        description:
        - The declarative state of the datalake backup.
        type: str
        required: False
        default: backup
        choices:
        - backup
        - restore
    wait:
        description:
            - Whether to wait for the backup to complete
        required: false
        type: bool
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Create a datalake backup
  cloudera.cloud.datalake_backup:
    datalake_name: "datalake"
    backup_name: "my_backup"
    state: "backup"
  register: backup_result

- name: Create a datalake backup and wait for it to complete
  cloudera.cloud.datalake_backup:
    datalake_name: "datalake"
    state: "backup"
    wait: true
  register: backup_result

- name: Restore a named datalake backup wait for it to complete
  cloudera.cloud.datalake_backup:
    datalake_name: "datalake"
    backup_name: "my_backup"
    state: "restore"
    wait: true
"""

RETURN = r"""
backup:
    description: The details of the backup or restore operation
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
        restoreId:
            description:
                - The restore id
                - Only returned when I(state=restore)
            type: str
        backupId:
            description: The backup id
            type: str
        internalState:
            description: The internal state of each backup or restore stage
            type: str
        status:
            description: The overall status of the backup or restore operation
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
        operationStates:
            description: Object representing the state of each service running a backup or restore
            type: dict
            contains:
                adminOperations:
                    description: The state of Cloudera Manager admin operations
                    type: dict
                    contains:
                        stopServices:
                            description: Details of the stop services admin operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        startServices:
                            description: Details of the start services admin operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        precheckStoragePermission:
                            description: Details of the pre check storage permission admin operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        rangerAuditCollectionValidation:
                            description: Details of the Ranger Audit Collection Validation admin operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        dryRunValidation:
                            description: Details of the dry run validation admin operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                hbase:
                    description: The state of each HBase backup/restore operation
                    type: dict
                    contains:
                        atlasEntityAuditEventTable:
                            description: Details of the Atlas entity audit event table HBase operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        atlasJanusTable:
                            description: Details of the Atlas Janus HBase operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                solr:
                    description: The state of each Solr backup/restore operation
                    type: dict
                    contains:
                        edgeIndexCollection:
                            description: Details of the edge index collection Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        fulltextIndexCollection:
                            description: Details of the full text index collection Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        rangerAuditsCollection:
                            description: Details of the ranger audits collection Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        vertexIndexCollection:
                            description: Details of the vertex index collection Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        edgeIndexCollectionDelete:
                            description: Details of the edge index collection delete Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        fulltextIndexCollectionDelete:
                            description: Details of the full text index collection delete Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        rangerAuditsCollectionDelete:
                            description: Details of the ranger audits collection delete Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                        vertexIndexCollectionDelete:
                            description: Details of the vertex index collection delete Solr operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
                database:
                    description: The state of each database backup/restore operation
                    type: dict
                    contains:
                        database:
                            description: Details of the database operation
                            type: dict
                            contains:
                                status:
                                    description: The status of the backup or restore operation
                                    type: str
                                failureReason:
                                    description: The failure reason if the operation was not successful
                                    type: str
                                durationInMinutes:
                                    description: The duration of the operation, in minutes
                                    type: str
                                predictedDurationInMinutes:
                                    description: Predicted duration of the operation, in minutes
                                    type: str
        runtimeVersion:
            description: Datalake runtime version
            type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class DatalakeBackup(CdpModule):
    def __init__(self, module):
        super(DatalakeBackup, self).__init__(module)

        # Set Variables
        self.datalake_name = self._get_param("datalake_name")
        self.backup_name = self._get_param("backup_name")
        self.state = self._get_param("state").lower()
        self.wait = self._get_param("wait", False)
        self.backup_location = self._get_param("backup_location")
        # ...variables for restore only
        self.backup_id = self._get_param("backup_id")
        self.skip_atlas_indexes = self._get_param("skip_atlas_indexes")
        self.skip_atlas_metadata = self._get_param("skip_atlas_metadata")
        self.skip_ranger_audits = self._get_param("skip_ranger_audits")
        self.skip_ranger_hms_metadata = self._get_param("skip_ranger_hms_metadata")
        self.skip_validation = self._get_param("skip_validation")

        # Initialize the return values
        self.output = dict()
        self.changed = False
        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):

        # Check parameters that should only specified with state=restore
        if self.state == "backup" and (
            self.backup_id
            or self.skip_atlas_indexes
            or self.skip_atlas_metadata
            or self.skip_ranger_audits
            or self.skip_ranger_hms_metadata
            or self.skip_validation
        ):
            self.module.fail_json(
                msg="Unable to use 'state=backup' with args 'backup_id', 'skip_atlas_indexes', 'skip_atlas_metadata', 'skip_ranger_audits', 'skip_ranger_hms_metadata' or 'skip_validation'",
            )

        # Validate that backup_location requires backup_id only when state=restore
        if self.state == "restore" and self.backup_location and not self.backup_id:
            self.module.fail_json(
                msg="backup_location requires backup_id when state=restore",
            )

        # Confirm datalake exists
        datalake_info = self.cdpy.datalake.describe_datalake(self.datalake_name)

        if datalake_info is None:
            self.module.fail_json(
                msg="Datalake {0} does not exist".format(self.datalake_name),
            )
        else:
            if self.state == "backup":

                backup = self.cdpy.datalake.create_datalake_backup(
                    datalake_name=self.datalake_name,
                    backup_name=self.backup_name,
                    backup_location=self.backup_location,
                )

                if self.wait:
                    self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.datalake.check_datalake_backup_status,
                        params=dict(
                            datalake_name=self.datalake_name,
                            backup_id=backup["backupId"],
                        ),
                        state=["SUCCESSFUL"],
                    )

                datalake_backups = self.cdpy.datalake.list_datalake_backups(
                    datalake_name=self.datalake_name,
                )
                self.output = [
                    item
                    for item in datalake_backups["backups"]
                    if item["backupId"] == backup["backupId"]
                ]
                self.changed = True

            elif self.state == "restore":
                # If specified confirm that backup (name or id) exists
                if self.backup_location is None and any(
                    bk is not None for bk in [self.backup_name, self.backup_id]
                ):
                    datalake_backups = self.cdpy.datalake.list_datalake_backups(
                        datalake_name=self.datalake_name,
                    )
                    if (
                        len(
                            [
                                item
                                for item in datalake_backups["backups"]
                                if item["backupName"] == self.backup_name
                                or item["backupId"] == self.backup_id
                            ],
                        )
                        == 0
                    ):
                        self.module.fail_json(
                            msg="Specified backup {0} does not exist for datalake {1}".format(
                                next(
                                    bk
                                    for bk in [self.backup_name, self.backup_id]
                                    if bk is not None
                                ),
                                self.datalake_name,
                            ),
                        )

                restore = self.cdpy.datalake.restore_datalake_backup(
                    datalake_name=self.datalake_name,
                    backup_name=self.backup_name,
                    backup_id=self.backup_id,
                    backup_location_override=self.backup_location,
                    skip_atlas_indexes=self.skip_atlas_indexes,
                    skip_atlas_metadata=self.skip_atlas_metadata,
                    skip_ranger_audits=self.skip_ranger_audits,
                    skip_ranger_hms_metadata=self.skip_ranger_hms_metadata,
                    skip_validation=self.skip_validation,
                )

                if self.wait:
                    self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.datalake.check_datalake_restore_status,
                        params=dict(
                            datalake_name=self.datalake_name,
                            restore_id=restore["restoreId"],
                        ),
                        state=["SUCCESSFUL"],
                    )
                    restore = self.cdpy.datalake.check_datalake_restore_status(
                        datalake_name=self.datalake_name,
                        restore_id=restore["restoreId"],
                    )

                self.output = restore
                self.changed = True
            else:
                self.module.fail_json(msg="Invalid state: %s" % self.state)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datalake_name=dict(required=True, type="str", aliases=["name"]),
            backup_name=dict(required=False, type="str"),
            state=dict(
                required=False,
                type="str",
                choices=["backup", "restore"],
                default="backup",
            ),
            wait=dict(required=False, type="bool"),
            backup_id=dict(required=False, type="str"),
            backup_location=dict(required=False, type="str"),
            skip_atlas_indexes=dict(required=False, type="bool"),
            skip_atlas_metadata=dict(required=False, type="bool"),
            skip_ranger_audits=dict(required=False, type="bool"),
            skip_ranger_hms_metadata=dict(required=False, type="bool"),
            skip_validation=dict(required=False, type="bool"),
        ),
        mutually_exclusive=[
            ["backup_name", "backup_id"],
        ],
        supports_check_mode=True,
    )

    result = DatalakeBackup(module)

    output = dict(changed=result.changed, backup=result.output)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
