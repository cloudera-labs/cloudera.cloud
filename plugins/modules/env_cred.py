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
module: env_cred
short_description: Create, update, and destroy CDP credentials
description:
  - Create, update, and destroy CDP credentials.
  - The module support check_mode.
author:
  - "Webster Mudge (@wmudge)"
  - "Daniel Chaffelson (@chaffelson)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the Credential.
      - The name must conform to the CDP Credential format, which is lowercase letters, numbers, and hyphens only.
    aliases:
      - credential
    required: True
    type: str
  state:
    description:
      - Establish the state of the Credential in CDP.
    choices:
      - present
      - absent
    default: present
    type: str
  cloud:
    description:
      - The target cloud provider for the Credential.
      - Required if I(state=present).
    choices:
      - aws
      - azure
      - gcp
    required: True
    type: str
  role:
    description:
      - The CDP cross-account role for AWS
      - For I(cloud=aws), this is the Role ARN for the cross-account role.
    aliases:
      - arn
      - role_arn
    required: False
    type: str
  subscription:
    type: str
    description: The Subscription ID or URI of the Azure Subscription being used
    required: False
  tenant:
    type: str
    description: The URI of the Azure Tenant
    required: False
  application:
    type: str
    description: The ApplicationId of the Azure Application used for access
    required: False
  secret:
    type: str
    description:
        - The Secret for the Application access on Azure
        - The path to the Key File for the Service Account being used on Google
    required: False
  description:
    description:
      - Descriptive text for the Credential.
    aliases:
      - desc
    type: str
    required: False
    default: None
  retries:
    description:
      - Number of times to retry the create operation if a possible eventual consistency error is returned
      - Set to 0 to fail immediately on such errors
    default: 5
    required: False
    type: int
  delay:
    description:
      - Delay period in seconds between retries
    default: 3
    required: False
    type: int
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create a CDP Credential for AWS
- cloudera.cloud.env_cred:
    state: present
    cloud: aws
    name: example-credential
    description: This is an example Credential
    role: arn:aws:iam::123456789123:role/some-cross-account-role

# Delete a CDP Credential
- cloudera.cloud.env_cred:
    state: absent
    name: example-credential

# Create a CDP Credential for AWS and log the output of the CDP SDK in the return values
- cloudera.cloud.env_cred:
    name: example-credential
    debug: true
"""

RETURN = r"""
credential:
    description: Returns an object for the Credential.
    returned: success
    type: complex
    contains:
        cloudPlatform:
            description: The name of the cloud provider for the Credential.
            returned: always
            type: str
            sample: AWS
        credentialName:
            description: The name of the Credential.
            returned: always
            type: str
            sample: example-credential
        crn:
            description: The CDP CRN value derived from the cross-account Role ARN used during creation.
            returned: always
            type: str
            sample: crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:61eb5b97-226a-4be7-b56d-795d18a043b5
        description:
            description: The description of the Credential.
            returned: when supported
            type: str
            sample: An example Credential
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
from cdpy.common import CdpError
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class EnvironmentCredential(CdpModule):
    def __init__(self, module):
        super(EnvironmentCredential, self).__init__(module)

        # Set variables
        self.state = self._get_param("state")
        self.cloud = self._get_param("cloud")
        self.name = self._get_param("name")
        self.role = self._get_param("role")
        self.subscription = self._get_param("subscription")
        self.tenant = self._get_param("tenant")
        self.application = self._get_param("application")
        self.secret = self._get_param("secret")
        self.retries = self._get_param("retries")
        self.delay = self._get_param("delay")
        self.description = self._get_param("description")

        # Initialize the return values
        self.credential = {}

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        """Executes the module logic."""
        self.validate_credential_name()

        credential = self.cdpy.environments.describe_credential(self.name)
        if self.state == "absent":
            if credential is not None:
                self.credential = self.cdpy.environments.delete_credential(self.name)
        else:
            if credential is None:
                self.credential = self.handle_create_credential()
            else:
                if self.reconcile_credential(credential):
                    self.credential = credential
                else:
                    self.cdpy.environments.delete_credential(self.name)
                    self.credential = self.handle_create_credential()

    def validate_credential_name(self):
        """Ensures that Credential names follow required formatting and fails the module on error."""
        if (
            self.cdpy.sdk.regex_search(
                self.cdpy.environments.sdk.CREDENTIAL_NAME_PATTERN, self.name
            )
            is not None
        ):
            self.module.fail_json(
                msg='Invalid credential name, "%s". CDP credentials must contain only lowercase '
                "letters, numbers and hyphens." % self.name
            )

    def reconcile_credential(self, credential):
        """
        Tests for differences between existing credential and inputs, returning TRUE if no changes.
        Note that only 'description' is checked, as the existing credential only exposes its computed 'crn', not
        the role ARN.
        """
        self.module.warn(
            "Changes to Role ARN cannot be checked. If you need to change the Role ARN, explicitly delete"
            " and recreate the credential."
        )
        if (
            self.description is not None
            and credential["description"] != self.description
        ):
            return False
        else:
            return True

    def handle_create_credential(self):
        """Creates a Credential, returning a dictionary of the newly-created object or ClientError."""
        if not self.module.check_mode:
            if self.cloud == "aws":
                resp = self.cdpy.environments.create_aws_credential(
                    self.name, self.role, self.description, self.retries, self.delay
                )
                self.changed = True
                return resp
            elif self.cloud == "azure":
                resp = self.cdpy.environments.create_azure_credential(
                    self.name,
                    self.subscription,
                    self.tenant,
                    self.application,
                    self.secret,
                )
                self.changed = True
                return resp
            elif self.cloud == "gcp":
                resp = self.cdpy.environments.create_gcp_credential(
                    name=self.name, key_file=self.secret
                )
                self.changed = True
                return resp
            else:
                self.cdpy.sdk.throw_error(CdpError("Invalid Cloud option"))


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            cloud=dict(required=False, type="str", choices=["aws", "azure", "gcp"]),
            name=dict(required=True, type="str", aliases=["credential"]),
            subscription=dict(required=False, type="str"),
            tenant=dict(required=False, type="str"),
            application=dict(required=False, type="str"),
            secret=dict(required=False, type="str"),
            role=dict(required=False, type="str", aliases=["arn", "role_arn"]),
            description=dict(
                required=False, type="str", aliases=["desc"], default=None
            ),
            retries=dict(required=False, type="int", default=5),
            delay=dict(required=False, type="int", default=3),
        ),
        required_if=[
            ["state", "present", ("cloud", "name"), False],
            ["cloud", "aws", ("name", "role"), False],
            [
                "cloud",
                "azure",
                ("name", "subscription", "tenant", "application", "secret"),
                False,
            ],
            ["cloud", "gcp", ("name", "secret"), False],
        ],
        supports_check_mode=True,
    )

    result = EnvironmentCredential(module)

    output = dict(
        changed=result.changed,
        credential=result.credential,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
