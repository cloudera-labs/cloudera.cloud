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
module: datahub_recipe_info
short_description: Gather information about CDP Datahub recipes
description:
    - Gather information about CDP Datahub recipes.
    - A recipe is a script that runs on all nodes of a specified instance group of a Datahub.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  name:
    description:
      - If a name is provided, that recipe will be described.
      - If no name provided, all recipes will be listed.
    type: str
    required: False
    aliases:
      - recipe
  return_content:
    description: Flag dictating if recipe content is returned
    type: bool
    required: False
    default: False
    aliases:
     - recipe_content
     - content
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: List all Datahub recipes
  cloudera.cloud.datahub_recipe_info:

- name: Gather information about a named recipe
  cloudera.cloud.datahub_recipe_info:
    name: example-recipe
    
- name: Gather detailed information about a named recipe
  cloudera.cloud.datahub_recipe_info:
    name: example-recipe
    return_content: yes
  register: my_recipe
"""

RETURN = r"""
---
recipes:
  description: The information about the named recipe or recipes
  type: list
  returned: on success
  elements: dict
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


class DatahubRecipeInfo(CdpModule):
    def __init__(self, module):
        super(DatahubRecipeInfo, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.content = self._get_param("return_content")

        # Initialize return values
        self.recipes = []

        # Initialize internal values
        self.all_recipes = []

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        self.all_recipes = self.cdpy.sdk.call(
            svc="datahub", func="list_recipes", ret_field="recipes"
        )

        if self.name:
            recipe = next(
                (
                    r
                    for r in self.all_recipes
                    if r["crn"] == self.name or r["recipeName"] == self.name
                ),
                None,
            )
            if recipe is not None:
                if self.content:
                    self.recipes.append(self._describe_recipe(recipe))
                else:
                    self.recipes.append(recipe)
            else:
                self.module.warn("Recipe not found, '%s'" % self.name)
        else:
            if self.content:
                for recipe in self.all_recipes:
                    self.recipes.append(self._describe_recipe(recipe))
            else:
                self.recipes = self.all_recipes

    def _describe_recipe(self, recipe):
        full = self.cdpy.datahub.describe_cluster_template(recipe["crn"])
        full = self.cdpy.sdk.call(
            svc="datahub", func="describe_recipe", recipeName=recipe["crn"]
        )
        if full is not None:
            return full
        else:
            self.module.fail_json(
                msg="Failed to retrieve recipe content, '%s'" % recipe["recipeName"]
            )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=False, type="str", aliases=["recipe", "crn"]),
            return_content=dict(
                required=False,
                type="bool",
                default=False,
                aliases=["recipe_content", "content"],
            ),
        ),
        supports_check_mode=True,
    )

    result = DatahubRecipeInfo(module)
    output = dict(changed=False, recipes=result.recipes)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
