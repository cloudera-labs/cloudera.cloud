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
module: cloudera.cloud.datalake_backup
short_description: Restore the datalake from a backup
description:
    - Restore the datalake from a backup
    - Optionally wait for the restore operation to complete
author:
    - "Jim Enright (@jimright)"
options:
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Restore the latest datalake backup
  cloudera.cloud.datalake_restore:
    datalake_name: "datalake"

- name: Restore a named datalake backup wait for it to complete
  cloudera.cloud.datalake_restore:
    datalake_name: "datalake"
    backup_name: "my_backup"
    wait: true
"""

RETURN = r"""
restore:
    description: The details of the restore
    type: list
    elements: dict
    returned: always
    contains:
        accountId:
            description: The account id
            type: str
        restoreId:
            description: The restore id
            type: str
        backupId:
            description: The backup id
            type: str
        userCrn:
            description: The crn of the user that initiated the backup operation
            type: str
        internalState:
            description: The internal state of each restore stage
            type: str
        status:
            description: The overall status of the restore operation
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
            description: Object representing the state of each service running a backup
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


class DatalakeRestore(CdpModule):
    def __init__(self, module):
        super(DatalakeRestore, self).__init__(module)

        # Set Variables
        self.datalake_name = self._get_param("datalake_name")
        self.backup_name = self._get_param("backup_name")
        self.backup_id = self._get_param("backup_id")
        self.backup_location_override = self._get_param("backup_location_override")
        self.skip_atlas_indexes = self._get_param("skip_atlas_indexes")
        self.skip_atlas_metadata = self._get_param("skip_atlas_metadata")
        self.skip_ranger_audits = self._get_param("skip_ranger_audits")
        self.skip_ranger_hms_metadata = self._get_param("skip_ranger_hms_metadata")
        self.skip_validation = self._get_param("skip_validation")
        self.wait = self._get_param("wait", False)

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
            self.module.fail_json(
                msg="Datalake {0} does not exist".format(self.datalake_name)
            )
        else:

            # If specified confirm that backup (name or id) exists
            if self.backup_location_override is None and any(
                bk is not None for bk in [self.backup_name, self.backup_id]
            ):
                datalake_backups = self.cdpy.datalake.list_datalake_backups(
                    datalake_name=self.datalake_name
                )
                if (
                    len(
                        [
                            item
                            for item in datalake_backups["backups"]
                            if item["backupName"] == self.backup_name
                            or item["backupId"] == self.backup_id
                        ]
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
                        )
                    )

            restore = self.cdpy.datalake.restore_datalake_backup(
                datalake_name=self.datalake_name,
                backup_name=self.backup_name,
                backup_id=self.backup_id,
                backup_location_override=self.backup_location_override,
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
                    datalake_name=self.datalake_name, restore_id=restore["restoreId"]
                )

        self.output = restore
        self.changed = True


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datalake_name=dict(required=True, type="str", aliases=["name"]),
            backup_name=dict(required=False, type="str"),
            backup_id=dict(required=False, type="str"),
            backup_location_override=dict(required=False, type="str"),
            skip_atlas_indexes=dict(required=False, type="bool"),
            skip_atlas_metadata=dict(required=False, type="bool"),
            skip_ranger_audits=dict(required=False, type="bool"),
            skip_ranger_hms_metadata=dict(required=False, type="bool"),
            skip_validation=dict(required=False, type="bool"),
            wait=dict(required=False, type="bool"),
        ),
        required_by={
            "backup_location_override": ("backup_id"),
        },
        mutually_exclusive=[
            ["backup_name", "backup_id"],
        ],
        supports_check_mode=True,
    )

    result = DatalakeRestore(module)

    output = dict(changed=result.changed, restore=result.output)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
