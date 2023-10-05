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

import json

import jmespath
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: datahub_cluster
short_description: Manage CDP Datahubs
description:
    - Create and delete CDP Datahubs.
author:
  - "Webster Mudge (@wmudge)"
  - "Daniel Chaffelson (@chaffelson)"
  - "Chris Perro (@cmperro)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the datahub.
      - This name must be unique, must have between 5 and 20 characters, and must contain only lowercase letters,
        numbers, and hyphens.
      - Names are case-sensitive.
    type: str
    required: True
    aliases:
      - datahub
  state:
    description:
      - The declarative state of the datahub.
      - If creating a datahub, the associate Environment and Datalake must be started as well.
    type: str
    required: False
    default: present
    choices:
      - present
      - started
      - stopped
      - absent
  environment:
    description:
      - The CDP environment name or CRN to which the datahub will be attached.
    type: str
    required: False
    aliases:
      - env
  definition:
    description:
      - The name or CRN of the cluster definition to use for cluster creation.
    type: str
    required: False
  template:
    description:
      - Name or CRN of the cluster template to use for cluster creation.
    type: str
    required: False
  subnet:
    description:
      - The subnet ID in AWS, or the Subnet Name on Azure or GCP
      - Mutually exclusive with the subnet and subnets options 
    type: str
    required: False
  subnets:
    description:
      - List of subnet IDs in case of multi availability zone setup.
      - Mutually exclusive with the subnet and subnets options 
    type: list
    required: False
  subnets_filter:
    description:
      - L(JMESPath,https://jmespath.org/) expression to filter the subnets to be used for the load balancer
      - The expression will be applied to the full list of subnets for the specified environment
      - Each subnet in the list is an object with the following attributes - subnetId, subnetName, availabilityZone, cidr
      - The filter expression must only filter the list, but not apply any attribute projection
      - Mutually exclusive with the subnet and subnets options 
    type: list
    required: False
  image:
    description: ID of the image used for cluster instances
    type: str
    required: False
  catalog:
    description: Name of the image catalog to use for cluster instances
    type: str
    required: False
  groups:
    description:
      - Instance group details.
    type: list
    elements: dict
    required: False
    suboptions:
      nodeCount:
        description: tktk
        type: int
      instanceGroupName:
        description: tktk
        type: str
      instanceGroupType:
        description: tktk
        type: str
      instanceType:
        description: tktk
        type: str
      rootVolumeSize:
        description: tktk
        type: int
      recoveryMode:
        description: tktk
        type: str
      volumeEncryption:
        description: tktk
        type: dict
        suboptions:
          enableEncryption:
            description: tktk
            type: bool
          encryptionKey:
            description: tktk
            type: str
      recipeNames:
        description: tktk
        type: list
        suboptions:
          recipeName:
            description: tktk
            type: string
      attachedVolumeConfiguration:
        description: tktk
        type: list
        suboptions:
          volumeSize:
            description: tktk
            type: int
          volumeCount:
            description: tktk
            type: int
          volumeType:
            description: tktk
            type: str
  tags:
    description:
      - Tags associated with the datahub and its resources.
    type: dict
    required: False
    aliases:
      - datahub_tags
  extension:
    description:
      - Cluster extensions for Data Hub cluster.
    type: str
    required: False
  multi_az:
    description:
      - (AWS) Flag indicating whether to defer to the CDP Environment for availability zone/subnet placement.
      - Useful for when you are not sure which subnet is available to the datahub cluster.
    type: bool
    required: False
    default: True
  force:
    description:
      - Flag indicating if the datahub should be force deleted.
      - This option can be used when cluster deletion fails.
      - This removes the entry from Cloudera Datahub service.
      - Any lingering resources have to be deleted from the cloud provider manually.
    type: bool
    required: False
    default: False
  wait:
    description:
      - Flag to enable internal polling to wait for the datahub to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the datahub to achieve the declared state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the datahub to achieve the declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create a datahub specifying instance group details (and do not wait for status change)
- cloudera.cloud.datahub_cluster:
    name: datahub-name
    env: name-or-crn
    state: present
    subnet: subnet-id-for-cloud-provider
    image: image-uuid-from-catalog
    catalog: name-of-catalog-for-image
    template: template-name
    groups:
      - nodeCount: 1
        instanceGroupName: master
        instanceGroupType: GATEWAY
        instanceType: instance-type-for-cloud-provider
        rootVolumeSize: 100
        recoveryMode: MANUAL
        recipeNames: []
        attachedVolumeConfiguration:
          - volumeSize: 100
            volumeCount: 1
            volumeType: volume-type-for-cloud-provider
    tags:
      project: Arbitrary content
    wait: no

# Create a datahub specifying only a definition name
- cloudera.cloud.datahub_cluster:
    name: datahub-name
    env: name-or-crn
    definition: definition-name
    tags:
      project: Arbitrary content
    wait: no

# Stop the datahub (and wait for status change)
- cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: stopped

# Start the datahub (and wait for status change)
- cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: started

# Delete the datahub (and wait for status change)
  cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: absent
'''

RETURN = r'''
---
datahub:
  description: The information about the Datahub
  type: dict
  returned: on success
  contains:
    clusterName:
      description: tktk
      type: str
    crn:
      description: tktk
      type: str
    creationDate:
      description: tktk
      type: str
    status:
      description: tktk
      type: str
    clusterStatus:
      description: tktk
      type: str
    nodeCount:
      description: tktk
      type: int
    instanceGroups:
      description: tktk
      type: list
      contains:
        instanceGroup:
          description: tktk
          type: dict
          contains:
            name:
              description: tktk
              type: str
            id:
              description: tktk
              type: str
            state:
              description: tktk
              type: str
            privateIp:
              description: tktk
              type: str
            publicIp:
              description: tktk
              type: str
            fqdn:
              description: tktk
              type: str
            status:
              description: tktk
              type: str
    workdloadType:
      description: tktk
      type: str
    cloudPlatform:
      description: tktk
      type: str
    imageDetails:
      description: tktk
      type: list
      contains:
        name:
          description: tktk
          type: str
        id:
          description:
            - This is the unique ID generated by the cloud provider for the image
          type: str
        catalogUrl:
          description: tktk
          type: str
        catalogName:
          description: tktk
          type: str
    environmentCrn:
      description: tktk
      type: str
    credentialCrn:
      description: tktk
      type: str
    datalakeCrn:
      description: tktk
      type: str
    clusterTemplateCrn:
      description: tktk
      type: str
    statusReason:
      description: tktk
      type: str
    clouderaManager:
      description: tktk
      type: dict
      contains:
        version:
          description: tktk
          type: str
        platformVersion:
          description: tktk
          type: str
    endpoints:
      description: tktk
      type: list
      contains:
        endpoint:
          description: tktk
          type: dict
          contains:
            serviceName:
              description: tktk
              type: str
            serviceUrl:
              description: tktk
              type: str
            displayName:
              description: tktk
              type: str
            knoxService:
              description: tktk
              type: str
            mode:
              description: tktk
              type: str
            open:
              description: tktk
              type: bool
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


class DatahubCluster(CdpModule):
    def __init__(self, module):
        super(DatahubCluster, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.state = self._get_param('state').lower()
        self.cloud = self._get_param('cloud')

        self.environment = self._get_param('environment')
        self.definition = self._get_param('definition')
        self.subnet = self._get_param('subnet')
        self.subnets = self._get_param('subnets')
        self.subnets_filter = self._get_param('subnets_filter')
        self.image_id = self._get_param('image')
        self.image_catalog = self._get_param('catalog')
        self.template = self._get_param('template')
        self.groups = self._get_param('groups')
        self.tags = self._get_param('tags')
        self.extension = self._get_param('extension')
        self.multi_az = self._get_param('multi_az')

        self.wait = self._get_param('wait')
        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')
        self.force = self._get_param('force')

        self.host_env = None

        # Initialize the return values
        self.datahub = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.datahub.describe_cluster(self.name)
        if self.state in ['present', 'started']:
            # If the datahub exists
            if existing is not None:
                self.datahub = existing
                if 'status' in existing and existing['status'] not in self.cdpy.sdk.CREATION_STATES:
                    # Reconcile and error if specifying invalid cloud parameters
                    if self.environment is not None:
                        self.host_env = self.cdpy.environments.describe_environment(self.environment)
                        if self.host_env['crn'] != existing['environmentCrn']:
                            self.module.fail_json(
                                msg="Datahub exists in a different Environment: %s" % existing['environmentCrn'])
                        # Check for changes
                        mismatch = self._reconcile_existing_state(existing)
                        if mismatch:
                            msg = ''
                            for m in mismatch:
                                msg += "Parameter '%s' found to be '%s'\n" % (m[0], m[1])
                            self.module.fail_json(msg='Datahub exists and differs from expected:\n' + msg,
                                                  violations=mismatch)
                # Attempt to start the datahub
                if 'status' in existing and existing['status'] not in self.cdpy.sdk.STARTED_STATES:
                    self.cdpy.datahub.start_cluster(self.name)
                    
                if self.wait and not self.module.check_mode:
                    self.datahub = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.datahub.describe_cluster,
                        params=dict(name=self.name),
                        state='AVAILABLE',
                        delay=self.delay,
                        timeout=self.timeout
                    )
            # Else not exists already, therefore create the datahub
            else:
                self.host_env = self.cdpy.environments.describe_environment(self.environment)
                if self.host_env is not None:
                    if self.cdpy.datalake.is_datalake_running(self.environment) is True:
                        self.create_cluster()
                    else:
                        self.module.fail_json(msg="Unable to find datalake or not Running, '%s'" % self.environment)
                else:
                    self.module.fail_json(msg="Unable to find environment, '%s'" % self.environment)
        elif self.state == 'stopped':
            # If the datahub exists
            if existing is not None:
                
              # Warn if attempting to stop an already stopped/stopping datahub
              if existing['status'] in self.cdpy.sdk.STOPPED_STATES:
                  self.module.warn('Attempting to stop a datahub already stopped or in stopping cycle')
                  self.datahub = existing
              # Warn if attempting to stop an already terminated/terminating datahub
              elif existing['status'] in self.cdpy.sdk.TERMINATION_STATES:
                self.module.warn('Attempting to stop an datahub during the termination cycle')
                self.datahub = existing
              # Otherwise, stop the datahub
              else:
                if not self.module.check_mode:
                  self.cdpy.datahub.stop_cluster(self.name)
                  self.changed = True
                  if self.wait:
                    self.datahub = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.datahub.describe_cluster,
                        params=dict(name=self.name),
                        state='STOPPED',
                        delay=self.delay,
                        timeout=self.timeout
                    )
            
            else:
              self.module.fail_json(msg='Datahub %s does not exist' % self.name)

        elif self.state == 'absent':
            # If the datahub exists
            if existing is not None:
                # Warn if attempting to delete an already terminated/terminating datahub
                if not self.module.check_mode:
                    if existing['status'] in self.cdpy.sdk.TERMINATION_STATES:
                        self.module.warn('Attempting to delete an datahub during the termination cycle')
                        self.datahub = existing
                    # Otherwise, delete the datahub
                    else:
                        self.cdpy.datahub.delete_cluster(self.name)
                        self.changed = True
                    if self.wait:
                        self.datahub = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.datahub.describe_cluster,
                            params=dict(name=self.name),
                            field=None,
                            delay=self.delay,
                            timeout=self.timeout,
                            ignore_failures=True
                        )
        else:
            self.module.fail_json(msg='Invalid state: %s' % self.state)

    def create_cluster(self):
        self._validate_datahub_name()

        payload = self._configure_payload()

        if self.host_env['cloudPlatform'] == 'AWS':
            self.datahub = self.cdpy.sdk.call('datahub', 'create_aws_cluster', **payload)
        elif self.host_env['cloudPlatform'] == 'AZURE':
            self.datahub = self.cdpy.sdk.call('datahub', 'create_azure_cluster', **payload)
        elif self.host_env['cloudPlatform'] == 'GCP':
            self.datahub = self.cdpy.sdk.call('datahub', 'create_gcp_cluster', **payload)
        else:
            self.module.fail_json(
                msg="cloudPlatform %s datahub deployment not implemented" % self.host_env['cloudPlatform'])

        self.changed = True

        if self.wait and not self.module.check_mode:
            self.datahub = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.datahub.describe_cluster,
                params=dict(name=self.name),
                state='AVAILABLE',
                delay=self.delay,
                timeout=self.timeout
            )

    def _configure_payload(self):
        payload = dict(
            clusterName=self.name,
            environmentName=self.environment
        )

        if self.definition is not None:
            if self.host_env['cloudPlatform'] == 'AWS':
                payload["clusterDefinition"] = self.definition
            else:
                payload["clusterDefinitionName"] = self.definition
        else:
            payload["image"] = {"id": self.image_id, "catalogName": self.image_catalog}
            if self.host_env['cloudPlatform'] == 'AWS':
                payload["clusterTemplate"] = self.template
            else:
                payload["clusterTemplateName"] = self.template
            payload["instanceGroups"] = self.groups

        if self.subnets_filter:
            try:
                env_info = self.cdpy.environments.describe_environment(self.environment)
                subnet_metadata = list(env_info['network']['subnetMetadata'].values())
            except Exception:
                subnet_metadata = []
            if not subnet_metadata:
                self.module.fail_json(
                    msg="Could not retrieve subnet metadata for CDP Environment %s" % self.env_crn)

            subnets = self._filter_subnets(self.subnets_filter, subnet_metadata)
            self.module.warn("Found subnets: %s" % ", ".join(subnets))
            if len(subnets) == 1:
                self.subnet = subnets[0]
            else:
                self.subnets = subnets

        if self.subnet:
            if self.host_env['cloudPlatform'] == 'GCP':
                payload['subnetName'] = self.subnet
            else:
                payload['subnetId'] = self.subnet
        elif self.subnets:
            payload['subnetIds'] = self.subnets

        if self.extension is not None:
            payload['clusterExtension'] = self.extension

        if self.host_env['cloudPlatform'] == 'AWS':
            payload['multiAz'] = self.multi_az

        if self.tags is not None:
            payload['tags'] = list()
            for k in self.tags:
                payload['tags'].append(dict(key=k, value=str(self.tags[k])))

        return payload

    def _filter_subnets(self, query, subnets):
        """Apply a JMESPath to an array of subnets and return the id of the selected subnets.
        The query must only filter the array, without applying any projection. The query result must also be an
        array of subnet objects.

        :param query: JMESpath query to filter the subnet array.
        :param subnets: An array of subnet objects. Each subnet in the array is an object with the following attributes:
        subnetId, subnetName, availabilityZone, cidr.
        :return: An array of subnet ids.
        """
        filtered_subnets = []
        try:
            filtered_subnets = jmespath.search(query, subnets)
        except Exception:
            self.module.fail_json(msg="The specified subnet filter is an invalid JMESPath expression: " % query)
        try:
            return [s['subnetId'] for s in filtered_subnets]
        except Exception:
            self.module.fail_json(msg='The subnet filter "%s" should return an array of subnet objects '
                                      'but instead returned this: %s' % (query, json.dumps(filtered_subnets)))

    def _reconcile_existing_state(self, existing):
        mismatched = list()

        if existing['cloudPlatform'] == 'AWS':
            self.module.warn("Datahub configuration reconciliation not implemented on AWS")

        if existing['cloudPlatform'].upper() == 'AZURE':
            self.module.warn("Datahub configuration reconciliation not implemented on Azure")

        if existing['cloudPlatform'].upper() == 'GCP':
            self.module.warn("Datahub configuration reconciliation not implemented on GCP")

        if self.tags:
            self.module.warn("Updating an existing Datahub's 'tags' "
                             "directly are not supported at this time. If you "
                             "need to change the tags, explicitly delete "
                             "and recreate the Datahub.")
        return mismatched

    def _validate_datahub_name(self):
        if len(self.name) < 5 or len(self.name) > 100:
            self.module.fail_json(msg="Invalid datahub name, '%s'. Names must be between 5-100 characters." % self.name)
        elif self.cdpy.sdk.regex_search(self.cdpy.sdk.DATAHUB_NAME_PATTERN, self.name) is not None:
            self.module.fail_json(msg="Invalid datahub name, '%s'. Names must contain only lowercase "
                                      "letters, numbers and hyphens." % self.name)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['datahub']),
            state=dict(required=False, type='str', choices=['present', 'started', 'stopped', 'absent'], default='present'),
            definition=dict(required=False, type='str'),
            subnet=dict(required=False, type='str', default=None),
            subnets=dict(required=False, type='list', elements='str', default=None),
            subnets_filter=dict(required=False, type='str', default=None),
            image=dict(required=False, type='str', default=None),
            catalog=dict(required=False, type='str', default=None),
            template=dict(required=False, type='str', default=None),
            groups=dict(required=False, type='list', default=None),
            environment=dict(required=False, type='str', aliases=['env'], default=None),
            tags=dict(required=False, type='dict', aliases=['datahub_tags']),
            extension=dict(required=False, type='dict'),
            multi_az=dict(required=False, type='bool', default=True),
            force=dict(required=False, type='bool', default=False),
            wait=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600)
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ('subnet', 'subnets', 'subnets_filter'),
        ],
        #Punting on additional checks here. There are a variety of supporting datahub invocations that can make this more complex
        #required_together=[
        #    ['subnet', 'image', 'catalog', 'template', 'groups', 'environment'],
        #]
    )

    result = DatahubCluster(module)
    output = dict(changed=result.changed, datahub=result.datahub)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
