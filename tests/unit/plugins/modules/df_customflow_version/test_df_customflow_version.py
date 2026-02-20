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
import tempfile

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

FLOW_NAME = "test-flow"
FLOW_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123"
FLOW_VERSION_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123:version:2"
FLOW_FILE_CONTENT = '{"flow": "definition"}'


@pytest.fixture
def temp_flow_file():
    """Create a temporary flow file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(FLOW_FILE_CONTENT)
        temp_path = f.name
    yield temp_path
    # Cleanup handled by OS


def test_df_customflow_version_import_by_name(module_args, mocker, temp_flow_file):
    """Test importing a new version by flow name."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_name": FLOW_NAME,
            "file": temp_flow_file,
            "comments": "Version 2",
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 1,
    }

    # Mock import_flow_definition_version response
    client.import_flow_definition_version.return_value = {
        "crn": FLOW_VERSION_CRN,
        "version": 2,
        "comments": "Version 2",
        "timestamp": 1640000000000,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["crn"] == FLOW_VERSION_CRN
    assert result.value.customflow_version["version"] == 2

    # Verify CdpDfClient was called correctly
    client.get_flow_by_name.assert_called_once_with(FLOW_NAME)
    client.import_flow_definition_version.assert_called_once()
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["flow_crn"] == FLOW_CRN
    assert call_args["file_content"] == FLOW_FILE_CONTENT
    assert call_args["comments"] == "Version 2"


def test_df_customflow_version_import_by_crn(module_args, mocker, temp_flow_file):
    """Test importing a new version by flow CRN."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": FLOW_CRN,
            "file": temp_flow_file,
            "comments": "Version 3",
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_crn.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 2,
    }

    # Mock import_flow_definition_version response
    client.import_flow_definition_version.return_value = {
        "crn": "crn:cdp:df:us-west-1:tenant:flow:flow-123:version:3",
        "version": 3,
        "comments": "Version 3",
        "timestamp": 1640000000000,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["version"] == 3

    # Verify CdpDfClient was called correctly
    client.get_flow_by_crn.assert_called_once_with(FLOW_CRN)
    client.import_flow_definition_version.assert_called_once()


def test_df_customflow_version_flow_not_found_by_name(
    module_args,
    mocker,
    temp_flow_file,
):
    """Test error when flow doesn't exist (by name)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_name": "nonexistent-flow",
            "file": temp_flow_file,
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist
    client.get_flow_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert "does not exist" in result.value.msg


def test_df_customflow_version_flow_not_found_by_crn(
    module_args,
    mocker,
    temp_flow_file,
):
    """Test error when flow doesn't exist (by CRN)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_crn": "crn:cdp:df:us-west-1:tenant:flow:nonexistent",
            "file": temp_flow_file,
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist
    client.get_flow_by_crn.return_value = None

    # Test module execution
    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert "does not exist" in result.value.msg


def test_df_customflow_version_check_mode(module_args, mocker, temp_flow_file):
    """Test check mode for importing a version."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_name": FLOW_NAME,
            "file": temp_flow_file,
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
    }

    # Test module execution
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
            "flow_name": FLOW_NAME,
            "file": "/nonexistent/path/to/flow.json",
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
    }

    # Test module execution
    with pytest.raises(AnsibleFailJson) as result:
        df_customflow_version.main()

    assert "Failed to read file" in result.value.msg


def test_df_customflow_version_import_with_tags(module_args, mocker, temp_flow_file):
    """Test importing a new version with tags."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_name": FLOW_NAME,
            "file": temp_flow_file,
            "comments": "Version 2 with tags",
            "tags": [
                {"tag_name": "production", "tag_color": "blue"},
                {"tag_name": "stable", "tag_color": "green"},
            ],
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 1,
    }

    # Mock import_flow_definition_version response
    client.import_flow_definition_version.return_value = {
        "crn": FLOW_VERSION_CRN,
        "version": 2,
        "comments": "Version 2 with tags",
        "timestamp": 1640000000000,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True
    assert result.value.customflow_version["crn"] == FLOW_VERSION_CRN
    assert result.value.customflow_version["version"] == 2

    # Verify CdpDfClient was called correctly with tags
    client.get_flow_by_name.assert_called_once_with(FLOW_NAME)
    client.import_flow_definition_version.assert_called_once()
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["flow_crn"] == FLOW_CRN
    assert call_args["file_content"] == FLOW_FILE_CONTENT
    assert call_args["comments"] == "Version 2 with tags"
    assert call_args["tags"] == [
        {"tagName": "production", "tagColor": "blue"},
        {"tagName": "stable", "tagColor": "green"},
    ]


def test_df_customflow_version_import_with_partial_tags(
    module_args,
    mocker,
    temp_flow_file,
):
    """Test importing a new version with tags that have only tag_name (no color)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "flow_name": FLOW_NAME,
            "file": temp_flow_file,
            "comments": "Version 3 with partial tags",
            "tags": [
                {"tag_name": "development"},
                {"tag_name": "testing", "tag_color": "yellow"},
            ],
            "state": "present",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_version.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 2,
    }

    # Mock import_flow_definition_version response
    client.import_flow_definition_version.return_value = {
        "crn": "crn:cdp:df:us-west-1:tenant:flow:flow-123:version:3",
        "version": 3,
        "comments": "Version 3 with partial tags",
        "timestamp": 1640000000000,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_version.main()

    assert result.value.changed is True

    # Verify tags were converted correctly (omitting None values)
    call_args = client.import_flow_definition_version.call_args[1]
    assert call_args["tags"] == [
        {"tagName": "development"},
        {"tagName": "testing", "tagColor": "yellow"},
    ]
