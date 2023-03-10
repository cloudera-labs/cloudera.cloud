#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 Cloudera, Inc. All Rights Reserved.
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
module: env
short_description: Manage CDP Environments
description:
    - Create, update, and delete CDP Environments
    - Note that changing states, in particular, creating a new environment, can take several minutes.
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the target environment.
      - Names must begin with a lowercase alphanumeric, contain only lowercase alphanumerics and hyphens, and be
        between 5 to 28 characters in length.
    type: str
    required: True
    aliases:
      - environment
  state:
    description:
      - The declarative state of the environment
      - If I(state=present), one of I(cloud) or I(credential) must be present.
    type: str
    required: False
    default: present
    choices:
      - present
      - started
      - stopped
      - absent
  cloud:
    description:
      - The cloud provider or platform for the environment.
      - Requires I(region), I(credential), I(log_location), and I(log_identity).
      - If I(cloud=aws), one of I(public_key) or I(public_key_id) must be present.
      - If I(cloud=aws), one of I(network_cidr) or I(vpc_id) must be present.
      - If I(cloud=aws), one of I(inbound_cidr) or I(default_sg) and I(knox_sg) must be present.
    type: str
    required: False
    choices:
      - aws
      - azure
      - gcp
  region:
    description:
      - The cloud platform specified region
    type: str
    required: False
  credential:
    description:
      - The CDP credential associated with the environment
    type: str
    required: False
  project:
    description: Name of Project when deploying environment on GCP
    type: str
    required: false
  inbound_cidr:
    description:
      - CIDR range which is allowed for inbound traffic. Either IPv4 or IPv6 is allowed.
      - Mutually exclusive with I(default_sg) and I(knox_sg).
    type: str
    required: False
    aliases:
      - security_cidr
  default_sg:
    description:
      - Security group where all other hosts are placed.
      - Mutually exclusive with I(inbound_cidr).
    type: str
    required: False
    aliases:
      - default
      - default_security_group
  knox_sg:
    description:
      - Security group where Knox-enabled hosts are placed.
      - Mutually exclusive with I(inbound_cidr).
    type: str
    required: False
    aliases:
      - knox
      - knox_security_group
  public_key_text:
    description:
      - The content of a public SSH key.
      - Mutually exclusive with I(public_key_id).
    type: str
    required: False
    aliases:
      - ssh_key_text
  public_key_id:
    description:
      - The public SSH key ID already registered in the cloud provider.
      - Mutually exclusive with I(public_key_text).
    type: str
    required: False
    aliases:
      - public_key
      - ssh_key
      - ssh_key_id
  log_location:
    description:
      - (AWS) The base location to store logs in S3. This should be an s3a:// url.
    type: str
    required: False
    aliases:
      - storage_location_base
  log_identity:
    description:
      - (AWS) The instance profile ARN assigned the necessary permissions to access the S3 storage location, i.e.
        I(log_location).
    type: str
    required: False
    aliases:
      - instance_profile
  network_cidr:
    description:
      - (AWS) The network CIDR. This will create a VPC along with subnets in multiple Availability Zones.
      - Mutually exclusive with I(vpc_id) and I(subnet_ids).
    type: str
    required: False
  vpc_id:
    description:
      - (AWS) The VPC ID.
      - Mutually exclusive with I(network_cidr) and requires I(subnet_ids).
    type: str
    required: False
    aliases:
      - vpc
  subnet_ids:
    description:
      - (AWS) One or more subnet identifiers within the VPC.
      - Mutually exclusive with I(network_cidr) and requires I(vpc_id).
    type: list
    elements: str
    required: False
    aliases:
      - subnets
  tags:
    description:
      - Tags associated with the environment and its resources.
    type: dict
    required: False
    aliases:
      - environment_tags
  workload_analytics:
    description:
      - Flag to enable diagnostic information about job and query execution to be sent to Workload Manager for Data Hub
        clusters created within the environment.
    type: bool
    required: False
    default: True
  description:
    description:
      - A description for the environment.
    type: str
    required: False
    aliases:
      - desc
  tunnel:
    description:
      - Flag to enable SSH tunnelling for the environment.
    type: bool
    required: False
    default: False
    aliases:
      - enable_tunnel
      - ssh_tunnel
  freeipa:
    description:
      - The FreeIPA service for the environment.
    type: dict
    required: False
    contains:
      instanceCountByGroup:
        description:
          - The number of FreeIPA instances to create per group when creating FreeIPA in the environment.
          - For high-availability, provide a number greater than 2.
        type: int
        required: False
        default: 2
      multiAZ:
        description:
          - Flag to specify that the FreeIPA instances will be deployed across multi-availability zones.
          - Only applies to AWS environments.
        type: bool
        required: False
        default: False        
  proxy:
    description:
      - The name of the proxy config to use for the environment.
    type: str
    required: False
    aliases:
      - proxy_config
      - proxy_config_name
  force:
    description:
      - Flag to remove CDP and cloud provider resources, but ignore cloud provider resources deletion errors.
      - NOTE: this option might leave cloud provider resources after deletion.
    type: bool
    required: False
    default: False
  cascade:
    description:
      - Flag to delete all connected resources, e.g. Data Services and Data Hubs.
    type: bool
    required: False
    default: False
    aliases:
      - cascading
  wait:
    description:
      - Flag to enable internal polling to wait for the environment to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  datahub_start:
    description:
      - Also starts datahubs within this environment when starting the environment
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the environment to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the environment to achieve the declared
        state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
  endpoint_access_scheme:
    description:
      - (AWS)The scheme for the workload endpoint gateway. PUBLIC creates an external endpoint that can be accessed over the Internet. 
        Defaults to PRIVATE which restricts the traffic to be internal to the VPC / Vnet. Relevant in Private Networks.
    type: str
    choices:
      - PRIVATE
      - PUBLIC
    required: False
  endpoint_access_subnets:
    description:
      - (AWS) The list of subnet IDs to use for endpoint access gateway.
    type: list
    elements: str
    required: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# Create an environment
- cloudera.cloud.env:
    name: example-environment
    state: present
    credential: example-credential
    cloud: aws
    region: us-east-1
    log_location: s3a://example-bucket/datalake/logs
    log_identity: arn:aws:iam::981304421142:instance-profile/example-log-role
    public_key_id: example-sshkey
    network_cidr: 10.10.0.0/16
    inbound_cidr: 0.0.0.0/0
    tags:
      project: Arbitrary content

# Create an environment with multiAZ FreeIPA, but don't wait for completion (see env_info)
- cloudera.cloud.env:
    name: example-environment
    state: present
    wait: no
    credential: example-credential
    cloud: aws
    region: us-east-1
    log_location: s3a://example-bucket/datalake/logs
    log_identity: arn:aws:iam::981304421142:instance-profile/example-log-role
    public_key_id: example-sshkey
    network_cidr: 10.10.0.0/16
    inbound_cidr: 0.0.0.0/0
    freeipa:
      instanceCountByGroup: 3
      multiAZ: yes
    tags:
      project: Arbitrary content

# Update the environment's CDP credential
- cloudera.cloud.env:
    name: example-module
    credential: another-credential

# Stop the environment (and wait for status change)
- cloudera.cloud.env:
    name: example-module
    state: stopped

# Start the environment (and wait for status change)
- cloudera.cloud.env:
    name: example-module
    state: started

# Delete the environment (and wait for status change)
  cloudera.cloud.env:
    name: example-module
    state: absent
'''

RETURN = r'''
---
environment:
  description: The information about the Environment
  type: dict
  returned: on success
  contains:
    authentication:
      description: Additional SSH key authentication configuration for accessing cluster node instances of the
        Environment.
      returned: always
      type: dict
      contains:
        loginUserName:
          description: SSH user name created on the node instances for SSH access.
          type: str
          returned: always
          sample: cloudbreak
        publicKey:
          description: SSH Public key string
          type: str
          returned: when supported
          sample: ssh-rsa AAAAB3NzaC...BH example-public-key
        publicKeyId:
          description: Public SSH key ID registered in the cloud provider.
          type: str
          returned: when supported
          sample: a_labeled_public_key
    cloudPlatform:
      description: Cloud provider of the Environment.
      returned: always
      type: str
      sample:
        - AWS
        - AZURE
        - GCP
    credentialName:
      description: Name of the CDP Credential of the Environment.
      returned: always
      type: str
      sample: a-cdp-credential
    crn:
      description: CDP CRN value for the Environment.
      returned: always
      type: str
      sample: crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:61eb5b97-226a-4be7-b56d-795d18a043b5
    description:
      description: Description of the Environment.
      returned: always
      type: str
      sample: An example Environment
    environmentName:
      description: Name of the Environment.
      returned: always
      type: str
      sample: a-cdp-environment-name
    freeipa:
      description: Details of a FreeIPA instance in the Environment.
      returned: always
      type: complex
      contains:
        crn:
          description: CRN of the FreeIPA instance.
          returned: always
          type: str
          sample: crn:cdp:freeipa:us-west-1:558bc1d2-8867-4357-8524-311d51259233:freeipa:cbab8ee3-00f2-4958-90c1-6f7cc06b4937
        domain:
          description: Domain name of the FreeIPA instance.
          returned: always
          type: str
          sample: example.012345-abcd.cloudera.site
        hostname:
          description: Hostname of the FreeIPA instance.
          returned: always
          type: str
          sample: ipaserver
        serverIP:
          description: IP addresses of the FreeIPA instance.
          returned: always
          type: list
          elements: str
          sample:
            - ['10.10.2.40']
    logStorage:
      description: Storage configuration for cluster and audit logs for the Environment.
      returned: always
      type: complex
      contains:
        awsDetails:
          description: AWS-specific log storage configuration details.
          returned: when supported
          type: dict
          contains:
            instanceProfile:
              description: AWS instance profile that contains the necessary permissions to access the S3 storage
                location.
              returned: always
              type: str
              sample: arn:aws:iam::381358652250:instance-profile/EXAMPLE-LOG_ROLE
            storageLocationBase:
              description: Base location to store logs in S3.
              returned: always
              type: str
              sample: s3a://example-bucket/datalake/logs
        azureDetails:
          description: Azure-specific log storage configuration details.
          returned: when supported
          type: dict
          contains:
            managedIdentity:
              description:
                - Azure managing identity associated with the logger.
                - This identify should have the Storage Blob Data Contributor role on the given storage account.
              returned: always
              type: str
              sample: /subscriptions/01234-56789-abcd/resourceGroups/example-environment-name/providers/
                Microsoft.ManagedIdentity/userAssignedIdentities/loggerIdentity
            storageLocationBase:
              description: Base location to store logs in Azure Blob Storage.
              returned: always
              type: str
              sample: abfs://logs@example_location.dfs.core.windows.net
        enabled:
          description: Flag for external log storage.
          returned: always
          type: bool
    network:
      description: Network details for the Environment
      returned: always
      type: complex
      contains:
        aws:
          description: AWS networking specifics for the Environment.
          returned: when supported
          type: dict
          contains:
            vpcId:
              description: VPC identifier.
              returned: always
              type: str
              sample: vpc-08785c81e888251df
        azure:
          description: Azure networking specifics for the Environment.
          returned: when supported
          type: dict
          contains:
            networkId:
              description: VNet identifier.
              returned: always
              type: str
              sample: example-vnet
            resourceGroupName:
              description: Resource Group name.
              returned: always
              type: str
              sample: example-rg
            usePublicIp:
              description: Flag for associating public IP addresses to the resources within the network.
              returned: always
              type: bool
        networkCidr:
          description: Range of private IPv4 addresses that resources will use for the Environment.
          returned: always
          type: str
          sample: 10.10.0.0/16
        subnetIds:
          description: Subnet identifiers for the Environment.
          returned: always
          type: list
          elements: str
          sample:
            - ['subnet-04a332603a269535f', 'subnet-07bbea553ca667b66', 'subnet-0aad7d6d9aa66d1e7']
        subnetMetadata:
          description: Additional subnet metadata for the Environment.
          returned: always
          type: complex
          contains:
            __subnetId__:
              description: Keyed subnet identifier.
              returned: always
              type: dict
              contains:
                availabilityZone:
                  description: Availability zone (AWS only)
                  returned: when supported
                  type: str
                  sample: us-west-2a
                subnetId:
                  description: Identifier for the subnet
                  returned: always
                  type: str
                  sample: subnet-04a332603a269535f
                subnetName:
                  description: Name of the subnet
                  returned: always
                  type: str
                  sample: subnet-04a332603a269535f
    proxyConfig:
      description: Proxy configuration of the Environment.
      returned: when supported
      type: dict
      contains:
        proxyConfigName:
          description: Name of the proxy configuration.
          returned: always
          type: str
          sample: the-proxy-config
        crn:
          description: CDP CRN for the proxy configuration.
          returned: always
          type: str
          sample: crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:38eeb2b9-6e57-4d10-ad91-f6d9bceecb54
        description:
          description: Description of the proxy.
          returned: always
          type: str
          sample: The proxy configuration description
        host:
          description: Proxy host.
          returned: always
          type: str
          sample: some.host.example.com
        password:
          description: Proxy user password.
          returned: always
          type: str
          sample: secret_password
        port:
          description: Proxy port.
          returned: always
          type: str
          sample: 8443
        protocol:
          description: Proxy protocol.
          returned: always
          type: str
          sample: https
        user:
          description: Proxy user name.
          returned: always
          type: str
          sample: the_username
    region:
      description: Cloud provider region of the Environment.
      returned: always
      type: str
      sample: us-east-1
    securityAccess:
      description: Security control configuration for FreeIPA and Datalake deployment in the Environment.
      returned: always
      type: dict
      contains:
        cidr:
          description: CIDR range which is allowed for inbound traffic. Either IPv4 or IPv6 is allowed.
          returned: when supported
          type: str
          sample: 0.0.0.0/0
        defaultSecurityGroupId:
          description: Security group associated with Knox-enabled hosts.
          returned: when supported
          type: str
          sample: /subscriptions/01234-56789-abcd/resourceGroups/example-environment/providers/Microsoft.Network/
            networkSecurityGroups/example-default-nsg
        securityGroupIdForKnox:
          description: Security group associated with all other hosts (non-Knox).
          returned: when supported
          type: str
          sample: /subscriptions/01234-56789-abcd/resourceGroups/example-environment/providers/Microsoft.Network/
            networkSecurityGroups/example-knox-nsg
    status:
      description: Status of the Environment.
      returned: always
      type: str
      sample:
        - AVAILABLE
        - CREATE_FAILED
        - CREATION_INITIATED
        - ENV_STOPPED
        - FREEIPA_CREATION_IN_PROGRESS
        - FREEIPA_DELETE_IN_PROGRESS
        - FREEIPA_DELETED_ON_PROVIDER_SIDE
        - START_FREEIPA_FAILED
        - STOP_FREEIPA_STARTED
    statusReason:
      description: Description for the status code of the Environment.
      returned: when supported
      type: str
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


class Environment(CdpModule):
    def __init__(self, module):
        super(Environment, self).__init__(module)

        self.name = self._get_param('name')
        self.state = self._get_param('state').lower()
        self.cloud = self._get_param('cloud')
        if self.cloud is not None:
            self.cloud = self.cloud.lower()
        self.region = self._get_param('region')
        self.credential = self._get_param('credential')
        self.inbound_cidr = self._get_param('inbound_cidr')
        self.default_sg = self._get_param('default_sg')
        self.knox_sg = self._get_param('knox_sg')
        self.public_ip = self._get_param('public_ip')
        self.public_key_text = self._get_param('public_key_text')
        self.public_key_id = self._get_param('public_key_id')
        self.log_location = self._get_param('log_location')
        self.log_identity = self._get_param('log_identity')
        self.network_cidr = self._get_param('network_cidr')
        self.vpc_id = self._get_param('vpc_id')
        self.resource_gp = self._get_param('resource_gp')
        self.subnet_ids = self._get_param('subnet_ids')
        self.s3_guard_name = self._get_param('s3_guard_name')
        self.tags = self._get_param('tags')
        self.workload_analytics = self._get_param('workload_analytics')
        self.description = self._get_param('description')
        self.tunnel = self._get_param('tunnel')
        self.freeipa = self._get_param('freeipa')
        self.proxy = self._get_param('proxy')
        self.project = self._get_param('project')

        self.delay = self._get_param('delay')
        self.timeout = self._get_param('timeout')
        self.force = self._get_param('force', False)
        self.cascade = self._get_param('cascade', False)
        self.wait = self._get_param('wait', False)

        self.datahub_start = self._get_param('datahub_start')

        self.endpoint_access_scheme = self._get_param('endpoint_access_scheme')
        self.endpoint_access_subnets = self._get_param('endpoint_access_subnets')

        self.use_single_resource_group=self._get_param('use_single_resource_group')

        # Initialize the return values
        self.environment = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.environments.describe_environment(self.name)

        # TODO SetTelemetryFeaturesRequest

        if self.state in ['present', 'started']:

            # If the environment exists
            if existing is not None:
                self.environment = existing

                # Reconcile if specifying cloud parameters
                if self.cloud is not None:
                    # Check to make sure environment state is the same
                    # TODO Delete environment and rebuild if different
                    if existing['cloudPlatform'].lower() != self.cloud:
                        self.module.fail_json(msg="Environment exists in a different cloud platform. "
                                                  "Platform: '%s'" % existing['cloudPlatform'])

                    # Check for changes (except for credentials and cloud platform)
                    mismatch = self._reconcile_existing_state(existing)
                    if mismatch:
                        msg = ''
                        for m in mismatch:
                            msg += "Parameter '%s' found to be '%s'\n" % (m[0], m[1])
                        self.module.fail_json(msg='Environment exists and differs from expected:\n' + msg,
                                              violations=mismatch)

                # Else, only update the credential
                elif self.credential is not None and existing['credentialName'] != self.credential:
                    self.update_credential()

                # Fail if attempting to restart a failed environment
                if existing['status'] in self.cdpy.sdk.FAILED_STATES:
                    self.module.fail_json(msg='Attempting to restart a failed environment')

                # Warn if attempting to start an environment amidst the creation cycle
                elif existing['status'] in self.cdpy.sdk.CREATION_STATES:
                    self.module.warn('Skipping attempt to start an environment during its creation cycle')

                # Otherwise attempt to start the environment
                elif existing['status'] not in self.cdpy.sdk.STARTED_STATES:
                    if not self.module.check_mode:
                        self.environment = self.cdpy.environments.start_environment(self.name, self.datahub_start)
                else:
                    self.module.warn('Environment state %s is unexpected' % existing['status'])

                if self.wait:
                    self.environment = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.environments.describe_environment,
                        params=dict(name=self.name),
                        state='AVAILABLE',
                        delay=self.delay,
                        timeout=self.timeout
                    )

            # Else create the environment
            else:
                # Catch errors for updating the credential
                if self.cloud is None:
                    self.module.fail_json(msg="Environment does not exist, or 'cloud' is not defined.")

                self._validate_environment_name()

                payload = self._configure_payload()

                if not self.module.check_mode:
                    if self.cloud not in ['aws', 'azure', 'gcp']:
                        self.module.fail_json(msg='Cloud %s is not yet implemented' % self.cloud)
                    elif self.cloud == 'aws':
                        self.environment = self.cdpy.environments.create_aws_environment(**payload)
                    elif self.cloud == 'gcp':
                        self.environment = self.cdpy.environments.create_gcp_environment(**payload)
                    else:
                        self.environment = self.cdpy.environments.create_azure_environment(**payload)
                    self.changed = True
                    if self.wait:
                        self.environment = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.environments.describe_environment,
                            params=dict(name=self.name),
                            state='AVAILABLE',
                            delay=self.delay,
                            timeout=self.timeout
                        )

        elif self.state == 'stopped':
            # If the environment exists
            if existing is not None:

                # Warn if attempting to stop an already stopped/stopping environment
                if existing['status'] in self.cdpy.sdk.STOPPED_STATES:
                    if not self.wait:
                        self.module.warn('Attempting to stop an environment already stopped or in stopping cycle')
                    self.environment = existing

                # Warn if attempting to stop a terminated/terminating environment
                elif existing['status'] in self.cdpy.sdk.TERMINATION_STATES:
                    self.module.fail_json(msg='Attempting to stop a terminating environment', **existing)

                # Fail if attempting to stop a failed environment
                elif existing['status'] in self.cdpy.sdk.FAILED_STATES:
                    self.module.fail_json(msg='Attempting to stop a failed environment', **existing)

                # Otherwise, stop the environment
                else:
                    if not self.module.check_mode:
                        self.environment = self.cdpy.environments.stop_environment(self.name)
                        if self.wait:
                            self.environment = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.environments.describe_environment,
                                params=dict(name=self.name),
                                state='ENV_STOPPED',
                                delay=self.delay,
                                timeout=self.timeout
                            )

            else:
                self.module.fail_json(msg='Environment does not exist.')

        elif self.state == 'absent':
            # If the environment exists
            if existing is not None:
                # Warn if attempting to delete an already terminated/terminating environment
                if not self.wait and existing['status'] in self.cdpy.sdk.TERMINATION_STATES:
                    self.module.warn('Attempting to delete an environment during the termination cycle')
                    self.environment = existing
                # Otherwise, delete the environment
                # TODO: Check that no CML or DWX etc. are attached to environment
                else:
                    if not self.module.check_mode:
                        self.cdpy.environments.delete_environment(self.name, self.cascade, self.force)
                        self.changed = True

                        if self.wait:
                            self.environment = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.environments.describe_environment,
                                params=dict(name=self.name),
                                field=None,
                                delay=self.delay,
                                timeout=self.timeout
                            )

        else:
            self.module.fail_json(msg='Invalid state: %s' % self.state)

    def update_credential(self):
        if not self.module.check_mode:
            self.cdpy.sdk.call('environments', 'change_environment_credential',
                               environmentName=self.name, credentialName=self.credential)
        self.environment = self.cdpy.environments.describe_environment(self.name)
        self.changed = True

    def _validate_environment_name(self):
        if self.cdpy.sdk.regex_search(self.cdpy.sdk.ENV_NAME_PATTERN, self.name) is not None:
            self.module.fail_json(msg="Invalid environment name, '%s'. Names must contain only lowercase "
                                      "letters, numbers, and hyphens, must start with a lowercase letter "
                                      "or a number, and be between 5 and 28 characters" % self.name)

    def _configure_payload(self):
        payload = dict(environmentName=self.name, credentialName=self.credential, region=self.region,
                       enableTunnel=self.tunnel, workloadAnalytics=self.workload_analytics)

        if self.tags is not None:
            payload['tags'] = list()
            for k in self.tags:
                payload['tags'].append(dict(key=k, value=str(self.tags[k])))
        if self.description is not None:
            payload['description'] = self.description

        if self.cloud not in ['aws', 'azure', 'gcp']:
            self.module.fail_json(msg='Cloud %s is not yet implemented' % self.cloud)
        elif self.cloud == 'aws':
            payload['logStorage'] = dict(instanceProfile=self.log_identity, storageLocationBase=self.log_location)

            if self.public_key_id is not None:
                payload['authentication'] = dict(publicKeyId=self.public_key_id)
            else:
                payload['authentication'] = dict(publicKey=self.public_key_text)

            if self.freeipa is not None:
                payload['freeIpa'] = dict()
                if self.freeipa['instanceCountByGroup'] is not None:
                    payload['freeIpa'].update(dict(instanceCountByGroup=self.freeipa['instanceCountByGroup']))
                if self.freeipa['multiAZ'] is not None:
                    payload['freeIpa'].update(dict(multiAZ=self.freeipa['multiAZ']))

            if self.vpc_id is not None:
                payload['vpcId'] = self.vpc_id
                payload['subnetIds'] = self.subnet_ids
            else:
                payload['networkCidr'] = self.network_cidr

            if self.proxy is not None:
                payload['proxyConfigName'] = self.proxy

            if self.s3_guard_name is not None:
                self.module.warn('As of CDP Runtime 7.2.10 (and given consistent s3), s3Guard is no longer needed. '
                                  'Proceeding without s3Guard.')

            if self.inbound_cidr is not None:
                payload['securityAccess'] = dict(cidr=self.inbound_cidr)
            else:
                payload['securityAccess'] = dict(defaultSecurityGroupId=self.default_sg,
                                                 securityGroupIdForKnox=self.knox_sg)

            if self.endpoint_access_scheme == 'PUBLIC':
                payload['endpointAccessGatewayScheme'] = self.endpoint_access_scheme
                payload['endpointAccessGatewaySubnetIds'] = self.endpoint_access_subnets
        elif self.cloud == 'gcp':
            payload['publicKey'] = self.public_key_text
            payload['existingNetworkParams'] = dict(
                networkName=self.vpc_id,
                subnetNames=self.subnet_ids,
                sharedProjectId=self.project
            )
            payload['usePublicIp'] = self.public_ip
            payload['logStorage'] = dict(serviceAccountEmail=self.log_identity, storageLocationBase=self.log_location)
            if self.freeipa is not None:
                payload['freeIpa'] = dict(instanceCountByGroup=self.freeipa['instanceCountByGroup'])
        else:
            # For Azure
            payload['securityAccess'] = dict(defaultSecurityGroupId=self.default_sg,
                                             securityGroupIdForKnox=self.knox_sg)
            payload['publicKey'] = self.public_key_text
            payload['usePublicIp'] = self.public_ip
            payload['logStorage'] = dict(managedIdentity=self.log_identity, storageLocationBase=self.log_location)
            if self.vpc_id:
                payload['existingNetworkParams'] = dict(
                    networkId=self.vpc_id, resourceGroupName=self.resource_gp, subnetIds=self.subnet_ids
                )
            if self.freeipa is not None:
                payload['freeIpa'] = dict(instanceCountByGroup=self.freeipa['instanceCountByGroup'])
            if self.use_single_resource_group:
                payload['resourceGroupName'] = self.resource_gp

        return payload

    def _reconcile_existing_state(self, existing):
        mismatch = list()

        if self.region is not None and existing['region'] != self.region:
            mismatch.append(['region', existing['region']])

        if self.tunnel is not None:
            self.module.warn('Environment SSH tunneling specified. Currently, the SSH tunnel setting cannot be '
                             'reconciled. To update the tunneling setting, explicitly delete and recreate the '
                             'environment.')

        if self.workload_analytics is not None:
            self.module.warn('Environment workload analytics specified. Currently, the environment\'s workload '
                             'analytics setting cannot be reconciled. To update the workload analytics setting for the'
                             'environment, explicitly delete and recreate the environment.')

        if self.tags is not None:
            self.module.warn('Environment tags specified. Currently, tags cannot be reconciled. To update tags, '
                             'explicitly delete and recreate the environment.')

        if self.cloud == 'aws':
            if self.log_identity is not None and \
                    existing['logStorage']['awsDetails']['instanceProfile'] != self.log_identity:
                mismatch.append(['log_identity', existing['logStorage']['awsDetails']['instanceProfile']])

            if self.log_location is not None and \
                    existing['logStorage']['awsDetails']['storageLocationBase'] != self.log_location:
                mismatch.append(['log_location', existing['logStorage']['awsDetails']['storageLocationBase']])

            if self.public_key_id is not None or self.public_key_text is not None:
                auth = existing['authentication']
                if self.public_key_id is not None and auth.get('publicKeyId') != self.public_key_id:
                    mismatch.append(['public_key_id', auth.get('publicKeyId')])
                elif auth.get('publicKey') != self.public_key_text:
                    mismatch.append(['public_key_text', auth.get('publicKey')])

            if self.description is not None and existing['description'] != self.description:
                mismatch.append(['description', existing['description']])

            if self.freeipa is not None and len(existing['freeipa']['serverIP']) != self.freeipa['instanceCountByGroup']:
                mismatch.append(['freeipa', len(existing['freeipa']['serverIP'])])

            if self.vpc_id is not None and existing['network']['aws']['vpcId'] != self.vpc_id:
                mismatch.append(['vpc_id', existing['network']['aws']['vpcId']])

            if self.subnet_ids is not None and set(existing['network']['subnetIds']) != set(self.subnet_ids):
                mismatch.append(['subnetIds', existing['network']['subnetIds']])

            if self.network_cidr is not None and existing['network']['networkCidr'] != self.network_cidr:
                mismatch.append(['network_cidr', existing['network']['networkCidr']])

            if self.inbound_cidr is not None and existing['securityAccess']['cidr'] != self.inbound_cidr:
                mismatch.append(['inbound_cidr', existing['securityAccess']['cidr']])

            if self.default_sg is not None or self.knox_sg is not None:
                access = existing['securityAccess']
                if self.default_sg is not None and access.get('defaultSecurityGroupId') != self.default_sg:
                    mismatch.append(['default_sg', access.get('defaultSecurityGroupId')])
                if self.knox_sg is not None and access.get('securityGroupIdForKnox') != self.knox_sg:
                    mismatch.append(['knox_sg', access.get('securityGroupIdForKnox')])

            if self.proxy is not None:
                if 'proxyConfig' in existing:
                    if existing['proxyConfig']['proxyConfigName'] != self.proxy:
                        mismatch.append(['proxy', existing['proxyConfig']['proxyConfigName']])
                else:
                    mismatch.append(['proxy', 'n/a'])
            elif 'proxyConfig' in existing:
                mismatch.append(['proxy', existing['proxyConfig']['proxyConfigName']])
        elif self.cloud == 'gcp':
            self.module.warn("Environment configuration reconciliation not implemented on GCP")
        else:
            # For Azure
            self.module.warn("Environment configuration reconciliation not implemented on Azure")

        return mismatch


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type='str', aliases=['environment']),
            state=dict(required=False, type='str', choices=['present', 'started', 'stopped', 'absent'],
                       default='present'),
            cloud=dict(required=False, type='str', choices=['aws', 'azure', 'gcp']),
            region=dict(required=False, type='str'),
            credential=dict(required=False, type='str'),
            inbound_cidr=dict(required=False, type='str', aliases=['security_cidr']),
            default_sg=dict(required=False, type='str', aliases=['default', 'default_security_group']),
            knox_sg=dict(required=False, type='str', aliases=['knox', 'knox_security_group']),
            public_key_text=dict(required=False, type='str', aliases=['ssh_key_text']),
            public_key_id=dict(required=False, type='str', aliases=['public_key', 'ssh_key', 'ssh_key_id']),
            log_location=dict(required=False, type='str', aliases=['storage_location_base']),
            log_identity=dict(required=False, type='str', aliases=['instance_profile']),
            network_cidr=dict(required=False, type='str'),
            vpc_id=dict(required=False, type='str', aliases=['vpc', 'network']),  # TODO: Update Docs
            subnet_ids=dict(required=False, type='list', elements='str', aliases=['subnets']),
            public_ip=dict(required=False, type='bool'),  # TODO: add to docs
            s3_guard_name=dict(required=False, type='str', aliases=['s3_guard', 's3_guard_table_name']),
            resource_gp=dict(required=False, type='str', aliases=['resource_group_name']),
            tags=dict(required=False, type='dict', aliases=['environment_tags']),
            workload_analytics=dict(required=False, type='bool', default=True),
            description=dict(required=False, type='str', aliases=['desc']),
            tunnel=dict(required=False, type='bool', aliases=['enable_tunnel', 'ssh_tunnel'], default=False),
            freeipa=dict(required=False, type='dict', options=dict(
              instanceCountByGroup=dict(required=False, type='int')
            ), default=dict(instanceCountByGroup=2,multiAz=False)),
            project=dict(required=False, type='str'),
            proxy=dict(required=False, type='str', aliases=['[proxy_config', 'proxy_config_name']),
            cascade=dict(required=False, type='bool', default=False, aliases=['cascading']),
            force=dict(required=False, type='bool', default=False),
            wait=dict(required=False, type='bool', default=True),
            datahub_start=dict(required=False, type='bool', default=True),
            delay=dict(required=False, type='int', aliases=['polling_delay'], default=15),
            timeout=dict(required=False, type='int', aliases=['polling_timeout'], default=3600),
            endpoint_access_subnets=dict(required=False, type='list', elements='str'),
            endpoint_access_scheme=dict(required=False, type='str', choices=['PUBLIC', 'PRIVATE']),
            use_single_resource_group=dict(required=False, type='bool', default=False),

        ),
        # TODO: Update for Azure
        required_if=[
            ['state', 'present', ('cloud', 'credential'), True],
            ['cloud', 'aws', ('public_key_text', 'public_key_id'), True],
            ['cloud', 'aws', ('network_cidr', 'vpc_id'), True],
            ['cloud', 'aws', ('inbound_cidr', 'default_sg', 'knox_sg'), True]
        ],
        required_by={
            'cloud': ('region', 'credential', 'log_location', 'log_identity'),
        },
        mutually_exclusive=[
            ['network_cidr', 'vpc_id'],
            ['network_cidr', 'subnet_ids'],
            ['public_key_id', 'public_key_text'],
            ['inbound_cidr', 'default_sg'],
            ['inbound_cidr', 'knox_sg']
        ],
        required_together=[
            ['vpc_id', 'subnet_ids'],
            ['default_sg', 'knox_sg']
        ],
        supports_check_mode=True
    )

    result = Environment(module)
    output = dict(changed=result.changed, environment=result.environment)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
