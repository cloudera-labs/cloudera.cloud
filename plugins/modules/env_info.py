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
module: env_info
short_description: Gather information about CDP Environments
description:
    - Gather information about CDP Environments
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
  - "Christian Leroy (cleroy@cloudera.com)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that environment will be described
      - If no name is provided, all environments will be listed
    type: str
    required: False
  descendants:
    description: Gather information about descendant deployments such as Datahubs and Experiences
    type: bool
    required: False
    default: False
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details.

# List basic information about all Environments
- cloudera.cloud.env_info:

# Gather detailed information about a named Environment
- cloudera.cloud.env_info:
    name: example-environment
    descendants: True
'''

RETURN = r'''
environments:
  description: The information about the named Environment or Environments
  type: list
  returned: on success
  elements: complex
  contains:
    descendants:
      description:
        - Additional descriptions of all descendant Datahub or Experience Services
        - Contains a list of zero or more description objects for descendants found
        - Note that resolving this may be very slow, especially for a large list of environments
      returned: when requested
      type: dict
      contains:
        datahub:
          type: list
          description: List of descriptions of zero or more Datahubs in this Environment
        dw:
          type: list
          description: List of descriptions of zero or more Datawarehouse Experiences in this Environment
        ml:
          type: list
          description: List of descriptions of zero or more Machine learning Workspaces in this Environment
        opdb:
          type: list
          description: List of descriptions of zero or more Operational Database Experiences in this Environment
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
    awsDetails:
      description: AWS-specific environment configuration information.
      returned: when supported
      type: dict
      contains:
        s3GuardTableName:
          description: The name for the DynamoDB table backing S3Guard.
          type: str
          returned: always
          sample: table_name
    cloudPlatform:
      description: Cloud provider of the Environment.
      returned: always
      type: str
      sample:
        - AWS
        - AZURE
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
        gcp:
          description: Google networking specifics for the Environment.
          returned: when supported
          type: dict
          contains:
            networkName:
              description: VNet identifier.
              returned: always
              type: str
              sample: example-vnet
            sharedProjectId:
              description: The Id of the Google project associated with the VPC.
              returned: always
              type: str
              sample: my-project
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
          description: Description of the proxy..
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


class EnvironmentInfo(CdpModule):
    def __init__(self, module):
        super(EnvironmentInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param('name')
        self.descendants = self._get_param('descendants')

        # Initialize return values
        self.environments = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name:
            env_single = self.cdpy.environments.describe_environment(self.name)
            if env_single is not None:
                self.environments.append(env_single)
        else:
            self.environments = self.cdpy.environments.describe_all_environments()
        if self.descendants and self.environments:
            updated_envs = []
            for this_env in self.environments:
                df = None
                # Removing until DF is GA so we are not dependent on Beta functionality
                # df = self.cdpy.df.describe_environment(this_env['crn'])
                this_env['descendants'] = {
                    'datahub': self.cdpy.datahub.describe_all_clusters(this_env['environmentName']),
                    'dw': self.cdpy.dw.gather_clusters(this_env['crn']),
                    'ml': self.cdpy.ml.describe_all_workspaces(this_env['environmentName']),
                    'opdb': self.cdpy.opdb.describe_all_databases(this_env['environmentName']),
                    'df': df if df is not None else []
                }
                updated_envs.append(this_env)
            self.environments = updated_envs


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type='str', aliases=['environment']),
            descendants=dict(required=False, type='bool', default=False)
        ),
        supports_check_mode=True
    )

    result = EnvironmentInfo(module)
    output = dict(changed=False, environments=result.environments)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == '__main__':
    main()
