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
module: opdb_info
short_description: Gather information about CDP OpDB Databases
description:
    - Gather information about CDP OpDB Databases
author:
  - "Webster Mudge (@wmudge)"
  - "Dan Chaffelson (@chaffelson)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a C(name) is provided, that OpDB Database will be described.
      - C(environment) must be provided if using C(name) to retrieve a Database
    type: str
    required: False
    aliases:
      - database
  environment:
    description:
      - The name of the Environment in which to find and describe the OpDB Databases.
      - Required with name to retrieve a Database
    type: str
    required: False
    aliases:
      - env
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# List basic information about all OpDB Databases
- cloudera.cloud.opdb_info:

# Gather detailed information about a named Database
- cloudera.cloud.opdb_info:
    name: example-database
    env: example-environment
"""

RETURN = r"""
databases:
  description: The information about the named Database or Databases
  type: list
  returned: always
  elements: complex
  contains:
    databaseName:
      description: The name of the database.
      returned: always
      type: str
    environmentCrn:
      description: The crn of the database's environment.
      returned: always
      type: str
    crn:
      description: The database's crn.
      returned: always
      type: str
    creationDate:
      description: The creation time of the database in UTC.
      returned: always
      type: str
    status:
      description: The status of the Database
      returned: always
      type: str
    creatorCrn:
      description: The CRN of the database creator.
      returned: always
      type: str
    k8sClusterName:
      description: The Kubernetes cluster name.
      returned: always
      type: str
    dbVersion:
      description: The version of the Database.
      returned: always
      type: str
    hueEndpoint:
      description: The Hue endpoint for the Database.
      returned: always
      type: str
    environmentName:
      description: The name of the Database's environment
      returned: always
      type: bool
    storageLocation:
      description: HBase cloud storage location
      returned: always
      type: str
    internalName:
      description: Internal cluster name for this database
      returned: always
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class OpdbDatabaseInfo(CdpModule):
    def __init__(self, module):
        super(OpdbDatabaseInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.env = self._get_param("environment")

        # Initialize return values
        self.databases = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        if self.name and self.env:  # Note that both None and '' will trigger this
            database_single = self.cdpy.opdb.describe_database(
                name=self.name, env=self.env
            )
            if database_single is not None:
                self.databases.append(database_single)
        else:
            self.databases = self.cdpy.opdb.describe_all_databases(self.env)


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str", aliases=["database"]),
            environment=dict(required=False, type="str", aliases=["env"]),
        ),
        required_by={"name": ("environment")},
        supports_check_mode=True,
    )

    result = OpdbDatabaseInfo(module)
    output = dict(changed=False, databases=result.databases)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
