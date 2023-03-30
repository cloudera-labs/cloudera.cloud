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
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: datalake
short_description: Manage CDP Datalakes
description:
    - Create and delete CDP Datalakes.
    - To start and stop a datalake, use the M(env) module to change the associated CDP Environment's state.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the datalake.
      - This name must be unique, must have between 5 and 100 characters, and must contain only lowercase letters, 
            numbers, and hyphens.
      - Names are case-sensitive.
    type: str
    required: True
    aliases:
      - datalake
  state:
    description:
      - The declarative state of the datalake.
      - If creating a datalake, the associate environment must be started as well.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  environment:
    description:
      - The CDP environment name or CRN to which the datalake will be attached.
      - If the environment is AWS-based, I(instance_profile) and I(storage) must be present.
    type: str
    required: False
    choices:
      - env
  instance_profile:
    description:
      - (AWS) The IAM instance profile of the ID Broker role, which can assume the Datalake Admin S3 role.
      - (Azure) The URI of the Identity of the ID Broker Role, which can assume the Datalake Admin ADLS role.
      - (GCP) The Service Account email of the ID Broker Role, which can assume the Datalake Admin GCS role.
    type: str
    required: False
  storage:
    description:
      - (AWS) The S3 bucket (and optional path) for the Storage Location Base for the datalake, starting with C(s3a://)
      - (Azure) The ADLS bucket URI (and optional path) for the Datalake storage
      - (GCP) The bucket name and optional path for the GCS Storage Location Base for the Datalake, starting with C(gs://)
    type: str
    required: False
    aliases:
      - storage_location
      - storage_location_base
  runtime:
    description:
      - The Cloudera Runtime version for the datalake, when supported
    type: str
    required: False
  scale:
    description:
      - The scale of the datalake.
    type: str
    required: False
    choices:
      - LIGHT_DUTY
      - MEDIUM_DUTY_HA
    default: LIGHT_DUTY
  tags:
    description:
      - Tags associated with the datalake and its resources.
    type: dict
    required: False
    aliases:
      - datalake_tags
  force:
    description:
      - Flag indicating if the datalake should be force deleted.
      - This option can be used when cluster deletion fails.
      - This removes the entry from Cloudera Datalake service.
      - Any lingering resources have to be deleted from the cloud provider manually.
    type: bool
    required: False
    default: False
  wait:
    description:
      - Flag to enable internal polling to wait for the datalake to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the datalake to reach the declared state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the datalake to achieve the declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
  raz:
    description:
      - Flag indicating if Ranger RAZ fine grained access should be enabled for the datalake
    type: bool
    required: False
    default: False
  multi_az:
    description:
      - Flag indicating if the datalake is deployed across multi-availability zones.
      - Only applies to AWS datalakes.
    type: bool
    required: False
    default: False    
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create a datalake in AWS
- cloudera.cloud.datalake:
    name: example-datalake
    state: present
    environment: an-aws-environment-name-or-crn
    instance_profile: arn:aws:iam::1111104421142:instance-profile/example-role
    storage: s3a://example-bucket/datalake/data
    tags:
      project: Arbitrary content

# Create a datalake in AWS, but don't wait for completion (see datalake_info for datalake status)
- cloudera.cloud.datalake:
    name: example-datalake
    state: present
    wait: no
    environment: an-aws-environment-name-or-crn
    instance_profile: arn:aws:iam::1111104421142:instance-profile/example-role
    storage: s3a://example-bucket/datalake/data
    tags:
      project: Arbitrary content

# Delete the datalake (and wait for status change)
  cloudera.cloud.datalake:
    name: example-datalake
    state: absent
'''

RETURN = r'''
---
datalake:
  description: The information about the Datalake
  type: dict
  returned: on success
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
    gcpConfiguration:
      description: GCP-specific environment configuration information.
      returned: when supported
      type: dict
      contains:
        serviceAccountEmail:
          description: The email id of the service account used for  the  ID  Broker instance.
          type: str
          returned: always
    cloudPlatform:
      description: Cloud provider of the Datalake.
      returned: when supported
      type: str
      sample:
        - AWS
        - AZURE
    enableRangerRaz:
      description: Whether or not RAZ is enabled
      returned: always
      type: bool
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
'''


class Datalake(CdpModule):
    def __init__(self, module):
        super(Datalake, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.state = self._get_param('state').lower()
        self.cloud = self._get_param('cloud')

        # ID Broker Role
        self.instance_profile = self._get_param('instance_profile')
        # Storage Location Base
        self.storage = self._get_param('storage')

        self.environment = self._get_param('environment')
        self.runtime = self._get_param('runtime')
        self.scale = self._get_param('scale')
        self.tags = self._get_param('tags')

        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')
        self.force = self._get_param('force')
        self.raz = self._get_param("raz")
        self.multi_az = self._get_param("multi_az")

        # Initialize the return values
        self.datalake = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.datalake.describe_datalake(self.name)

        if self.state in ['present']:

            # If the datalake exists
            if existing is not None:
                self.datalake = existing
                # Fail if attempting to restart a failed datalake
                if 'status' in existing:
                    if existing['status'] in self.cdpy.sdk.FAILED_STATES:
                        self.module.fail_json(msg='Attempting to restart a failed datalake')

                    # Check for Datalake actions during create or started
                    elif existing['status'] in self.cdpy.sdk.CREATION_STATES + self.cdpy.sdk.STARTED_STATES:
                        # Reconcile and error if specifying invalid cloud parameters
                        if self.environment is not None:
                            env = self.cdpy.environments.describe_environment(self.environment)
                            if env['crn'] != existing['environmentCrn']:
                                self.module.fail_json(
                                    msg="Datalake exists in a different Environment: %s" % existing['environmentCrn'])
                        # Check for changes
                        mismatch = self._reconcile_existing_state(existing)
                        if mismatch:
                            msg = ''
                            for m in mismatch:
                                msg += "Parameter '%s' found to be '%s'\n" % (m[0], m[1])
                            self.module.fail_json(
                                msg='Datalake exists and differs from expected:\n' + msg, violations=mismatch)
                        # Wait
                        if not self.wait:
                            self.module.warn('Datalake already creating or started, changes may not be possible')
                        else:
                            # Wait for creation to complete if previously requested and still running
                            self.datalake = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.datalake.describe_datalake,
                                params=dict(name=self.name),
                                field='status',
                                state='RUNNING',
                                delay=self.delay,
                                timeout=self.timeout
                            )
            # Else create the datalake if not exists already
            else:
                if self.environment is not None:
                    env = self.cdpy.environments.describe_environment(self.environment)
                    if env is not None:
                        self.create_datalake(env)
                    else:
                        self.module.fail_json(msg="Unable to find environment, '%s'" % self.environment)
                else:
                    self.module.fail_json(msg="Datalake creation failed, required parameter 'environment' missing")

        elif self.state == 'absent':
            # If the datalake exists
            if existing is not None:

                # Warn if attempting to delete an already terminated/terminating datalake
                if not self.wait and existing['status'] in self.cdpy.sdk.TERMINATION_STATES:
                    self.module.warn('Attempting to delete an datalake during the termination cycle')
                    self.datalake = existing

                # Otherwise, delete the datalake
                else:
                    self.delete_datalake()
        else:
            self.module.fail_json(msg='Invalid state: %s' % self.state)

    def create_datalake(self, environment):
        self._validate_datalake_name()

        payload = self._configure_payload(environment)

        if environment['cloudPlatform'] == 'AWS':
            if self.instance_profile is None or self.storage is None:
                self.module.fail_json(msg="One of the following are missing: instance_profile, storage")

            payload.update(cloudProviderConfiguration=dict(
                instanceProfile=self.instance_profile,
                storageBucketLocation=self.storage
            ))

            self.datalake = self.cdpy.sdk.call('datalake', 'create_aws_datalake', **payload)
        elif environment['cloudPlatform'] == 'AZURE':
            payload.update(cloudProviderConfiguration=dict(
                managedIdentity=self.instance_profile,
                storageLocation=self.storage
            ))
            self.datalake = self.cdpy.sdk.call('datalake', 'create_azure_datalake', **payload)
        elif environment['cloudPlatform'] == 'GCP':
            payload.update(cloudProviderConfiguration=dict(
                serviceAccountEmail=self.instance_profile,
                storageLocation=self.storage
            ))
            self.datalake = self.cdpy.sdk.call('datalake', 'create_gcp_datalake', **payload)
        else:
            self.module.fail_json(msg='Datalakes not yet implemented for this Environment Type')
        self.changed = True

        if self.wait and not self.module.check_mode:
            self.datalake = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.datalake.describe_datalake,
                params=dict(name=self.name),
                field='status',
                state='RUNNING',
                delay=self.delay,
                timeout=self.timeout
            )

    def delete_datalake(self):
        if not self.module.check_mode:
            self.datalake = self.cdpy.datalake.delete_datalake(self.name, self.force)
        self.changed = True

        if self.wait and not self.module.check_mode:
            self.datalake = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.datalake.describe_datalake,
                params=dict(name=self.name),
                field=None,
                delay=self.delay,
                timeout=self.timeout
            )

    def _configure_payload(self, environment):
        payload = dict(
            datalakeName=self.name,
            environmentName=self.environment,
        )

        if self.runtime:
            payload.update(runtime=self.runtime)

        if self.scale:
            payload.update(scale=self.scale)

        if self.raz:
            if environment['cloudPlatform'] == 'AWS' or environment['cloudPlatform'] == 'AZURE':
                payload.update(enableRangerRaz=self.raz)
            else:
                self.module.fail_json(msg='GCP Datalakes do not currently support RAZ')
        elif environment['cloudPlatform'] != 'GCP' :
            payload.update(enableRangerRaz=self.raz)

        if self.multi_az:
            if environment['cloudPlatform'] == 'AWS':
                payload.update(multiAz=self.multi_az)
            else:
                self.module.fail_json(msg='Multi-AZ Datalakes are not supported on GCP and Azure')
        elif environment['cloudPlatform'] == 'AWS':
            payload.update(multiAz=self.multi_az)

        if self.tags is not None:
            payload['tags'] = list()
            for k in self.tags:
                payload['tags'].append(dict(key=k, value=str(self.tags[k])))

        return payload

    def _reconcile_existing_state(self, existing):
        mismatched = list()

        if 'cloudPlatform' in existing and existing['cloudPlatform'] == 'AWS':
            if self.instance_profile is not None and \
                    self.instance_profile != existing['awsConfiguration']['instanceProfile']:
                mismatched.append(['instance_profile', existing['awsConfiguration']['instanceProfile']])

        if self.storage is not None:
            self.module.warn("Updating an existing Datalake's 'storage' "
                             "directly is not supported at this time. If "
                             "you need to change the storage, explicitly "
                             "delete and recreate the Datalake.")

        if self.runtime:
            self.module.warn("Updating an existing Datalake's 'runtime' "
                             "directly is not supported at this time. If you "
                             "need to change the runtime, either use the "
                             "'upgrade' state or explicitly delete and "
                             "recreate the Datalake.")
        if self.scale:
            self.module.warn("Updating an existing Datalake's 'scale' "
                             "directly is not supported at this time. If you "
                             "need to change the scale, explicitly delete "
                             "and recreate the Datalake.")

        if self.tags:
            self.module.warn("Updating an existing Datalake's 'tags' "
                             "directly are not supported at this time. If you "
                             "need to change the tags, explicitly delete "
                             "and recreate the Datalake.")

        if self.raz:
            self.module.warn("Updating an existing Datalake's 'enableRangerRaz' "
                             "directly is not supported at this time. If you "
                             "need to change the enableRangerRaz, explicitly delete "
                             "and recreate the Datalake.")

        if self.multi_az:
            self.module.warn("Updating an existing Datalake's 'multiAz' "
                             "directly is not supported at this time. If you "
                             "need to change the multiAz, explicitly delete "
                             "and recreate the Datalake.")

        return mismatched

    def _validate_datalake_name(self):
        if len(self.name) < 5 or len(self.name) > 100:
            self.module.fail_json(
                msg="Invalid datalake name, '%s'. Names must be between 5-100 characters." % self.name)
        elif self.cdpy.sdk.regex_search(self.cdpy.sdk.DATALAKE_NAME_PATTERN, self.name) is not None:
            self.module.fail_json(msg="Invalid datalake name, '%s'. Names must contain only lowercase "
                                      "letters, numbers and hyphens." % self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['datalake']),
            state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
            instance_profile=dict(required=False, type='str', aliases=['managed_identity']),
            storage=dict(required=False, type='str', aliases=['storage_location', 'storage_location_base']),

            environment=dict(required=False, type='str', aliases=['env']),
            runtime=dict(required=False, type='str'),
            scale=dict(required=False, type='str', choices=['LIGHT_DUTY', 'MEDIUM_DUTY_HA']),
            tags=dict(required=False, type='dict', aliases=['datalake_tags']),

            force=dict(required=False, type='bool', default=False),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600),
            raz=dict(required=False, type="bool", default=False),
            multi_az=dict(required=False, type="bool", default=False)
        ),
        supports_check_mode=True
    )

    result = Datalake(module)
    output = dict(changed=result.changed, datalake=result.datalake)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
