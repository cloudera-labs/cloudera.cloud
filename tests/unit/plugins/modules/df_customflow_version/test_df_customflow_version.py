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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import df_customflow_version


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

FLOW_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123"
VERSION_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123/v2"
FLOW_FILE_CONTENT = '{"flow": "definition"}'


def test_df_customflow_version_import_success_from_file(module_args, mocker, tmp_path):
    """Test importing a new CustomFlow version successfully from file."""

    flow_file = tmp_path / "test-flow.json"
    flow_file.write_text(FLOW_FILE_CONTENT)

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "file": str(flow_file),
            "comments": "Second version",
            "state": "present",
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "versionCount": 1,
    }

    client.import_flow_definition_version.return_value = {
        "crn": VERSION_CRN,
        "version": 2,
        "comments": "Second version",
        "timestamp": 1640000000000,
        "deploymentCount": 0,
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["crn"] == VERSION_CRN
    assert result.value.customflow_version["version"] == 2

    client.get_flow_by_crn.assert_called_once_with(FLOW_CRN)
    client.import_flow_definition_version.assert_called_once()
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["flow_crn"] == FLOW_CRN
    assert call_args["file_content"] == FLOW_FILE_CONTENT
    assert call_args["comments"] == "Second version"


def test_df_customflow_version_import_success_from_content(module_args, mocker):
    """Test importing a new CustomFlow version successfully from content string."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "content": FLOW_FILE_CONTENT,
            "comments": "Second version from content",
            "state": "present",
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "versionCount": 1,
    }

    client.import_flow_definition_version.return_value = {
        "crn": VERSION_CRN,
        "version": 2,
        "comments": "Second version from content",
        "timestamp": 1640000000000,
        "deploymentCount": 0,
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["crn"] == VERSION_CRN
    assert result.value.customflow_version["version"] == 2

    client.get_flow_by_crn.assert_called_once_with(FLOW_CRN)
    client.import_flow_definition_version.assert_called_once()
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["flow_crn"] == FLOW_CRN
    assert call_args["file_content"] == FLOW_FILE_CONTENT
    assert call_args["comments"] == "Second version from content"


def test_df_customflow_version_import_with_tags(module_args, mocker, tmp_path):
    """Test importing a CustomFlow version with tags (verifies tag format conversion)."""

    flow_file = tmp_path / "test-flow.json"
    flow_file.write_text(FLOW_FILE_CONTENT)

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "file": str(flow_file),
            "comments": "Tagged version",
            "tags": [
                {"tag_name": "production", "tag_color": "blue"},
                {"tag_name": "stable"},
            ],
            "state": "present",
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "versionCount": 1,
    }

    client.import_flow_definition_version.return_value = {
        "crn": VERSION_CRN,
        "version": 2,
        "comments": "Tagged version",
        "timestamp": 1640000000000,
        "deploymentCount": 0,
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True

    # Verify tags were converted from Ansible format (snake_case) to API format (camelCase)
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["tags"] == [
        {"tagName": "production", "tagColor": "blue"},
        {"tagName": "stable"},
    ]


def test_df_customflow_version_nonexistent_flow(module_args, mocker):
    """Test that the module fails when the referenced flow CRN does not exist."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "content": FLOW_FILE_CONTENT,
            "state": "present",
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow does not exist
    client.get_flow_by_crn.return_value = None

    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert result.value.failed is True
    assert "does not exist" in result.value.msg

    # Verify import was NOT called
    client.import_flow_definition_version.assert_not_called()


def test_df_customflow_version_check_mode(module_args, mocker, tmp_path):
    """Test check mode: reports changed=True but does not call the API."""

    flow_file = tmp_path / "test-flow.json"
    flow_file.write_text(FLOW_FILE_CONTENT)

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "file": str(flow_file),
            "comments": "Check mode version",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "versionCount": 1,
    }

    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True

    # Verify import was NOT called (check mode)
    client.import_flow_definition_version.assert_not_called()


def test_df_customflow_version_file_read_error(module_args, mocker):
    """Test handling of file read errors."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "file": "/nonexistent/file.json",
            "state": "present",
        },
    )

    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "versionCount": 1,
    }

    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert "Failed to read file" in result.value.msg
