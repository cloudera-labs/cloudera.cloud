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
module: df_customflow_version
short_description: Import CustomFlow versions into the DataFlow Catalog
description:
    - Import CustomFlow versions into the DataFlow Catalog
author:
  - "Andre Araujo (@asdaraujo)"
  - "Ronald Suplina (@rsuplina)"
version_added: "2.0.0"
options:
  flow_crn:
    description:
      - The CRN of the CustomFlow into which the version will be imported.
    type: str
    required: False
  flow_name:
    description:
      - The name of the CustomFlow into which the version will be imported.
      - Either I(flow_crn) or I(flow_name) must be provided.
    type: str
    required: False
  file:
    description:
      - The path to the JSON file containing the CustomFlow definition to be imported as a new version.
    type: path
    required: True
  comments:
    description:
      - Comments associated to the version of the CustomFlow being imported.
    type: str
    default: None
    required: False
  tags:
    description:
      - The list of tags for the flow definition version.
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
      - The declarative state of the CustomerFlow version
    type: str
    required: False
    default: present
    choices:
      - present
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.


# Import a CustomFlow version into the DataFlow Catalog by CRN
- cloudera.cloud.df_customflow_version:
    flow_crn: crn:cdp:df:us-west-1:558bc1d2-8867-4357-8524-311d51259233:flow:my-flow
    file: /tmp/my-custom-flow-v2.json
    comments: Second version

# Import a CustomFlow version by name
- cloudera.cloud.df_customflow_version:
    flow_name: my-customflow-name
    file: /tmp/my-custom-flow-v2.json
    comments: Second version

# Import a CustomFlow version with tags
- cloudera.cloud.df_customflow_version:
    flow_name: my-customflow-name
    file: /tmp/my-custom-flow-v3.json
    comments: Third version with tags
    tags:
      - tag_name: production
        tag_color: blue
      - tag_name: stable
        tag_color: green
"""

RETURN = r"""
customflow_version:
  description: The CustomFlow Version Definition
  type: dict
  returned: always
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
    comments:
      description: Comments about the flow version.
      returned: when available
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_df import CdpDfClient


class DFCustomFlowVersion(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                flow_crn=dict(required=False, type="str"),
                flow_name=dict(required=False, type="str"),
                file=dict(required=True, type="path"),
                comments=dict(required=False, type="str"),
                tags=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    options=dict(
                        tag_name=dict(required=True, type="str"),
                        tag_color=dict(required=False, type="str"),
                    ),
                ),
                state=dict(type="str", choices=["present"], default="present"),
            ),
            required_one_of=[["flow_crn", "flow_name"]],
            mutually_exclusive=[["flow_crn", "flow_name"]],
            supports_check_mode=True,
        )

        # Initialize parameters
        self.flow_crn: Optional[str] = self.get_param("flow_crn")
        self.flow_name: Optional[str] = self.get_param("flow_name")
        self.file: str = self.get_param("file")
        self.comments: Optional[str] = self.get_param("comments")
        self.tags: Optional[list] = self.get_param("tags")
        self.state: str = self.get_param("state")

        # Initialize the DataFlow client
        self.df_client = CdpDfClient(self.api_client)

        # Initialize return values
        self.flow_version: Optional[Dict[str, Any]] = None
        self.changed = False

    def process(self):
        if self.flow_name:
            flow = self.df_client.get_flow_by_name(self.flow_name)
            if not flow:
                self.module.fail_json(
                    msg=f"Flow definition with name '{self.flow_name}' does not exist",
                )
            self.flow_crn = flow.get("crn")
        else:
            flow = self.df_client.get_flow_by_crn(self.flow_crn)
            if not flow:
                self.module.fail_json(
                    msg=f"Flow definition with CRN '{self.flow_crn}' does not exist",
                )

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

            self.flow_version = self.df_client.import_flow_definition_version(
                flow_crn=self.flow_crn,
                file_content=file_content,
                comments=self.comments,
                tags=api_tags,
            )


def main():
    result = DFCustomFlowVersion()

    output = dict(
        changed=result.changed,
        customflow_version=result.flow_version,
    )

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
