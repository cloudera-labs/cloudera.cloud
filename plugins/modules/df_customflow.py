#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
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
module: df_customflow
short_description: Import or Delete CustomFlows into the DataFlow Catalog
description:
  - Import or Delete CustomFlows into the DataFlow Catalog
author:
  - "Andre Araujo (@asdaraujo)"
  - "Ronald Suplina (@rsuplina)"
version_added: "2.0.0"
options:
  name:
    description:
      - The name of the CustomFlow to be acted upon.
    type: str
    required: True
    aliases:
      - flow_name
  file:
    description:
      - The path to the JSON file containing the CustomFlow definition to be imported.
      - Required when I(state=present).
    type: path
    default: None
  description:
    description:
      - The description of the CustomFlow.
    type: str
    default: None
    required: False
  comments:
    description:
      - Comments associated to the initial version of the CustomFlow.
    type: str
    default: None
    required: False
  collection_crn:
    description:
      - The CRN of the collection into which the flow definition will be imported.
      - If unspecified, the flow will not be assigned to a collection.
    type: str
    default: None
    required: False
  tags:
    description:
      - The list of tags for the initial flow definition version.
      - Each tag should have a C(tag_name) (required) and optionally a C(tag_color).
    type: list
    elements: dict
    required: False
    suboptions:
      tag_name:
        description:
          - The name of the version tag.
        type: str
        required: True
      tag_color:
        description:
          - The color of the version tag.
        type: str
        required: False
  state:
    description:
      - The declarative state of the CustomFlow
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.


# Import a CustomFlow into the DataFlow Catalog
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    file: /tmp/my-custom-flow.json
    description: My sample CDF flow
    comments: Initial version

# Import a CustomFlow into the DataFlow Catalog with collection assignment
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    file: /tmp/my-custom-flow2.json
    collection_crn: crn:cdp:df:us-west-1:tenant:collection:col-123

# Import a CustomFlow with tags
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    file: /tmp/my-custom-flow3.json
    description: My tagged flow
    comments: Initial version with tags
    tags:
      - tag_name: production
        tag_color: blue
      - tag_name: stable
        tag_color: green

# Delete a CustomFlow from the DataFlow Catalog
- cloudera.cloud.df_customflow:
    name: my-customflow-name
    state: absent
"""

RETURN = r"""
customflow:
  description: The CustomFlow Definition
  type: dict
  returned: when supported
  contains:
    crn:
      description:
        - The DataFlow CustomFlow's CRN.
        - Use this crn to address this object
      returned: always
      type: str
    name:
      description: The DataFlow CustomFlow's name.
      returned: always
      type: str
    versionCount:
      description: Number of versions contained in this CustomFlow.
      returned: always
      type: int
    createdTimestamp:
      description: The timestamp the entry was created.
      returned: always
      type: int
    modifiedTimestamp:
      description: The timestamp the entry was last modified.
      returned: always
      type: int
    description:
      description: The flow description.
      returned: when available
      type: str
    versions:
      description: The list of artifactDetail versions.
      returned: always
      type: list
      elements: dict
      contains:
        crn:
          description: The artifact version CRN.
          returned: always
          type: str
        bucketIdentifier:
          description: The bucketIdentifier of the flow.
          returned: always
          type: str
        author:
          description: The author of the artifact.
          returned: always
          type: str
        version:
          description: The version of the artifact.
          returned: always
          type: int
        timestamp:
          description: The timestamp of the artifact.
          returned: always
          type: int
        deploymentCount:
          description: The number of deployments of the artifact.
          returned: always
          type: int
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient


class DFCustomFlow(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=True, type="str", aliases=["flow_name"]),
                file=dict(required=False, type="path"),
                description=dict(required=False, type="str"),
                comments=dict(required=False, type="str"),
                collection_crn=dict(required=False, type="str"),
                tags=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        tag_name=dict(required=True, type="str"),
                        tag_color=dict(required=False, type="str"),
                    ),
                ),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            required_if=[
                ("state", "present", ("file",)),
            ],
            supports_check_mode=True,
        )

        # Initialize parameters
        self.name: str = self.get_param("name")
        self.file: Optional[str] = self.get_param("file")
        self.description: Optional[str] = self.get_param("description")
        self.comments: Optional[str] = self.get_param("comments")
        self.collection_crn: Optional[str] = self.get_param("collection_crn")
        self.tags: Optional[list] = self.get_param("tags")
        self.state: str = self.get_param("state")

        # Initialize the DataFlow client
        self.df_client = CdpDfClient(self.api_client)

        # Initialize return values
        self.flow = {}
        self.changed = False

    def process(self):
        existing_flow = self.df_client.get_flow_by_name(self.name)

        if self.state == "present":
            if existing_flow:
                self.flow = existing_flow  # Flow already exists, no update operation for CustomFlows (import only)
            else:
                self.changed = True
                if not self.module.check_mode:
                    try:
                        with open(self.file, "r") as f:
                            file_content = f.read()
                    except Exception as e:
                        self.module.fail_json(
                            msg=f"Failed to read file '{self.file}': {str(e)}",
                        )

                    # Convert tags format from Ansible to API format
                    api_tags = None
                    if self.tags:
                        api_tags = [
                            {
                                k: v
                                for k, v in {
                                    "tagName": tag.get("tag_name"),
                                    "tagColor": tag.get("tag_color"),
                                }.items()
                                if v is not None
                            }
                            for tag in self.tags
                        ]

                    self.flow = self.df_client.import_flow_definition(
                        name=self.name,
                        file_content=file_content,
                        description=self.description,
                        comments=self.comments,
                        collection_crn=self.collection_crn,
                        tags=api_tags,
                    )

        elif self.state == "absent":
            if existing_flow:
                self.changed = True
                if not self.module.check_mode:
                    flow_crn = existing_flow.get("crn")
                    self.flow = self.df_client.delete_flow(flow_crn)
                else:
                    self.flow = existing_flow


def main():
    result = DFCustomFlow()

    output = dict(
        changed=result.changed,
        customflow=result.flow,
    )

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
