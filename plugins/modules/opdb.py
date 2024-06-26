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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: opdb
short_description: Create or destroy CDP OpDB Databases
description:
    - Create or destroy CDP OpDB Databases
author:
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that OpDB Database will be created or dropped.
      - environment must be provided
    type: str
    required: True
    aliases:
      - database
  environment:
    description:
      - The name of the Environment in which to find or place the OpDB Databases.
      - Required with name
    type: str
    required: True
    aliases:
      - env
  state:
    description:
      - The declarative state of the OpDB Database
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the Opdb Database to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the OpDB Database to achieve the declared
        state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the OpDB Database to achieve the declared
        state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Create an OpDB Database
- cloudera.cloud.opdb:
    name: example-database
    env: example-environment

# Remove an OpDB Database
- cloudera.cloud.opdb:
    name: example-database
    env: example-environment
    state: absent
"""

RETURN = r"""
---
database:
  description: The information about the Created Database
  type: dict
  returned: always
  elements: complex
  contains:
    databaseName:
      description: The name of the database.
      returned: present
      type: str
    environmentCrn:
      description: The crn of the database's environment.
      returned: present
      type: str
    crn:
      description: The database's crn.
      returned: present
      type: str
    creationDate:
      description: The creation time of the database in UTC.
      returned: present
      type: str
    status:
      description: The status of the Database
      returned: always
      type: str
    creatorCrn:
      description: The CRN of the database creator.
      returned: present
      type: str
    dbVersion:
      description: The version of the Database.
      returned: present
      type: str
    hueEndpoint:
      description: The Hue endpoint for the Database.
      returned: present
      type: str
    environmentName:
      description: The name of the Database's environment
      returned: present
      type: bool
    storageLocation:
      description: HBase cloud storage location
      returned: present
      type: str
    internalName:
      description: Internal cluster name for this database
      returned: present
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
"""


class OpdbDatabase(CdpModule):
    def __init__(self, module):
        super(OpdbDatabase, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.env = self._get_param("environment")
        self.state = self._get_param("state")
        self.wait = self._get_param("wait")
        self.delay = self._get_param("delay")
        self.timeout = self._get_param("timeout")

        # Initialize return values
        self.databases = []

        # Initialize internal values
        self.target = None

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        # Check if Database exists
        self.target = self.cdpy.opdb.describe_database(name=self.name, env=self.env)
        if self.target is not None:
            # Database Exists
            if self.state == "absent":
                # Begin Drop
                if self.module.check_mode:
                    self.databases.append(self.target)
                else:
                    if self.target["status"] not in self.cdpy.sdk.REMOVABLE_STATES:
                        self.module.warn(
                            "OpDB Database not in valid state for Drop operation: %s"
                            % self.target["status"]
                        )
                    else:
                        drop_status = self.cdpy.opdb.drop_database(
                            name=self.name, env=self.env
                        )
                        self.target[
                            "status"
                        ] = drop_status  # Drop command only returns status, not full object
                    if self.wait:
                        self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.opdb.describe_database,
                            params=dict(name=self.name, env=self.env),
                            field=None,
                            delay=self.delay,
                            timeout=self.timeout,
                        )
                    else:
                        self.databases.append(self.target)
                # Drop Done
            elif self.state == "present":
                # Being Config check
                self.module.warn(
                    "OpDB Database already present and config validation is not implemented"
                )
                if self.wait:
                    self.target = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.opdb.describe_database,
                        params=dict(name=self.name, env=self.env),
                        state="AVAILABLE",
                        delay=self.delay,
                        timeout=self.timeout,
                    )
                    self.databases.append(self.target)
                # End Config check
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state
                )
            # End handling Database exists
        else:
            # Begin handling Database not found
            if self.state == "absent":
                self.module.warn(
                    "OpDB Database %s already absent in Environment %s"
                    % (self.name, self.env)
                )
            elif self.state == "present":
                if self.module.check_mode:
                    pass
                else:
                    # Being handle Database Creation
                    create_status = self.cdpy.opdb.create_database(
                        name=self.name, env=self.env
                    )
                    if self.wait:
                        self.target = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.opdb.describe_database,
                            params=dict(name=self.name, env=self.env),
                            state="AVAILABLE",
                            delay=self.delay,
                            timeout=self.timeout,
                        )
                        self.databases.append(self.target)
                    else:
                        self.databases.append(create_status)
            else:
                self.module.fail_json(
                    msg="State %s is not valid for this module" % self.state
                )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type="str", aliases=["database"]),
            environment=dict(required=True, type="str", aliases=["env"]),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            wait=dict(required=False, type="bool", default=True),
            delay=dict(
                required=False, type="int", aliases=["polling_delay"], default=15
            ),
            timeout=dict(
                required=False, type="int", aliases=["polling_timeout"], default=3600
            ),
        ),
        supports_check_mode=True,
    )

    result = OpdbDatabase(module)
    output = dict(changed=False, databases=result.databases)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
