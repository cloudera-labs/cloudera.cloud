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

from cdpy.common import Squelch

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: datahub_recipe
short_description: Manage a CDP Datahub recipe
description:
    - Create, update, and delete a CDP Datahub recipe.
    - A recipe is a script that runs on all nodes of a specified instance group of a Datahub.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  state:
    description:
      - State of the recipe.
    required: False
    choices:
      - present
      - absent
    default: present
  name:
    description:
      - The name of the recipe.
    required: True
    aliases:
      - recipe
      - recipe_name
  description:
    description:
      - The description of the recipe.
    required: False
    aliases:
      - desc
  content:
    description:
      - The content of the recipe.
      - Required if I(state=present).
    required: False
    aliases:
      - recipe_content
  type:
    description:
      - Execution hook for the recipe.
      - Required if I(state=present).
    required: False
    choices:
      - POST_CLOUDERA_MANAGER_START
      - PRE_TERMINATION
      - PRE_SERVICE_DEPLOYMENT
      - POST_SERVICE_DEPLOYMENT
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
notes:
  - This module supports C(check_mode).
  - If the existing recipe is different than the declared state, the recipe is recreated and assigned a new CRN.
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Create a recipe
  cloudera.cloud.datahub_recipe:
    name: example-recipe
    type: PRE_TERMINATION
    content: |
      #!/bin/bash
      echo "Done"

- name: Delete a recipe
  cloudera.cloud.datahub_recipe:
    name: example-recipe
    state: absent
"""

RETURN = r"""
---
recipe:
  description: The information about the recipe.
  type: dict
  returned: always
  contains:
    creatorCrn:
      description: The CRN of the creator of the recipe.
      returned: when supported
      type: str
    crn:
      description: The CRN of the recipe.
      returned: always
      type: str
    description:
      description: The description of the recipe.
      returned: when supported
      type: str
    recipeContent:
      description: The content of the recipe.
      returned: when supported
      type: str
    recipeName:
      description: The name of the recipe.
      returned: always
      type: str
    type:
      description: 
        - The type of recipe. 
        - "Supported values are: C(POST_CLOUDERA_MANAGER_START), C(PRE_TERMINATION), C(PRE_SERVICE_DEPLOYMENT), C(POST_SERVICE_DEPLOYMENT)."
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
"""

TYPES = [
    "POST_CLOUDERA_MANAGER_START",
    "PRE_TERMINATION",
    "PRE_SERVICE_DEPLOYMENT",
    "POST_SERVICE_DEPLOYMENT",
]


class DatahubRecipe(CdpModule):
    def __init__(self, module):
        super(DatahubRecipe, self).__init__(module)

        # Set variables
        self.state = self._get_param("state")
        self.name = self._get_param("name")
        self.description = self._get_param("description")
        self.content = self._get_param("content")
        self.type = self._get_param("type")

        # Initialize return values
        self.recipe = {}
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.sdk.call(
            svc="datahub",
            func="describe_recipe",
            squelch=[Squelch("NOT_FOUND", default=None)],
            ret_field="recipe",
            recipeName=self.name,
        )

        if self.state == "present":
            payload = dict(
                recipeName=self.name,
                recipeContent=self.content,
                type=self.type,
            )

            if self.description:
                payload.update(description=self.description)

            if existing is None:
                if not self.module.check_mode:
                    self.changed = True
                    self.recipe = self.cdpy.sdk.call(
                        svc="datahub",
                        func="create_recipe",
                        ret_field="recipe",
                        **payload
                    )
                else:
                    self.recipe = existing
            else:
                tmp = dict(existing)
                del tmp["creatorCrn"]
                del tmp["crn"]
                if tmp != payload and not self.module.check_mode:
                    self.changed = True
                    self.module.warn(
                        "Existing recipe is different from input. Recreating recipe."
                    )
                    self.cdpy.sdk.call(
                        svc="datahub",
                        func="delete_recipes",
                        recipeNames=[self.name],
                    )
                    self.recipe = self.cdpy.sdk.call(
                        svc="datahub",
                        func="create_recipe",
                        ret_field="recipe",
                        **payload
                    )
                else:
                    self.recipe = existing
        else:
            if existing is not None and not self.module.check_mode:
                self.changed = True
                self.cdpy.sdk.call(
                    svc="datahub",
                    func="delete_recipes",
                    recipeNames=[self.name],
                )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            state=dict(
                required=False, choices=["present", "absent"], default="present"
            ),
            name=dict(required=True, aliases=["recipe", "recipe_name"]),
            description=dict(required=False, aliases=["desc"]),
            content=dict(required=False, aliases=["recipe_content"]),
            type=dict(required=False, choices=TYPES),
        ),
        required_if=[
            ["state", "present", ["content", "type"], False],
        ],
        supports_check_mode=True,
    )

    result = DatahubRecipe(module)
    output = dict(changed=result.changed, recipe=result.recipe)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
