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
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: datahub_cluster_recipe
short_description: Manage CDP Datahub recipes on an instance group
description:
    - Create, update, and delete CDP Datahub recipes to an instance group of a CDP Datahub.
    - A recipe is a script that runs on all nodes of a specified instance group of a Datahub.
    - See the L(Cloudera documentation on recipes,https://docs.cloudera.com/data-hub/cloud/recipes/topics/mc-creating-custom-scripts-recipes.html) for details.
author:
  - "Webster Mudge (@wmudge)"
requirements:
  - cdpy
options:
  datahub:
    description:
      - The name or CRN of the datahub.
    required: True
  name:
    description:
      - The name of the CDP Datahub instance group.
    required: True
    aliases:
      - instance_group
      - group
  recipes:
    description:
      - A list of recipes for the CDP Datahub instance group.
      - To remove all recipes from the instance group, declare an empty list.
    required: True
    type: list
    elements: str
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
notes:
  - This module supports C(check_mode).
  - If the existing recipe is different than the declared state, the recipe is recreated and assigned a new CRN.
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Set a couple of recipes to an instance group
  cloudera.cloud.datahub_cluster_recipe:
    datahub: example-datahub
    name: core_broker
    recipes:
      - recipe01
      - recipe02

- name: Reset the recipes to an instance group (will remove recipe01 from above)
  cloudera.cloud.datahub_cluster_recipe:
    datahub: example-datahub
    name: core_broker
    recipes:
      - recipe02

- name: Remove all recipes of an instance group
  cloudera.cloud.datahub_cluster_recipe:
    datahub: example-datahub
    name: core_broker
    recipes: []
"""

RETURN = r"""
---
instance_group:
  description: The recipe state for the CDP Datahub instance group.
  type: dict
  returned: always
  contains:
    attached_recipes:
      description: List of recipes attached to the instance group.
      returned: always
      type: list
      elements: str
    datahub:
      description: Name of the CDP Datahub.
      returned: always
      type: str
    detached_recipes:
      description: List of recipes detached from the instance group.
      returned: always
      type: list
      elements: str
    name:
      description: Name of the instance group in the CDP Datahub.
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


class DatahubClusterRecipe(CdpModule):
    def __init__(self, module):
        super(DatahubClusterRecipe, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.datahub = self._get_param("datahub")
        self.recipes = self._get_param("recipes")

        # Initialize return values
        self.instance_group = dict(
            name=self.name,
            datahub=self.datahub,
            attached_recipes=list(),
            detached_recipes=list(),
        )
        self.changed = False

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        assignments = dict(instanceGroupName=self.name)

        if self.recipes:
            assignments.update(recipeNames=self.recipes)
        else:
            assignments.update(recipeNames=list())

        payload = dict(datahub=self.datahub, instanceGroupRecipes=[assignments])

        if not self.module.check_mode:
            results = camel_dict_to_snake_dict(
                self.cdpy.sdk.call(svc="datahub", func="replace_recipes", **payload)
            )

            for r in ["attached_recipes", "detached_recipes"]:
                delta = results.get(r, list())
                if delta:
                    self.instance_group[r] = [
                        r for d in delta for r in d["recipe_names"]
                    ]
                    self.changed = True


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            datahub=dict(required=True),
            name=dict(required=True, aliases=["instance_group", "group"]),
            recipes=dict(required=False, type="list", elements="str"),
        ),
        supports_check_mode=True,
    )

    result = DatahubClusterRecipe(module)
    output = dict(changed=result.changed, instance_group=result.instance_group)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
