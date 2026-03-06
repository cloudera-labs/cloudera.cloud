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
import os

from ansible_collections.cloudera.cloud.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import df_customflow


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

FLOW_NAME = "test-flow"
FLOW_CRN = "crn:cdp:df:us-west-1:tenant:flow:flow-123"
FLOW_FILE_CONTENT = '{"flow": "definition"}'


@pytest.fixture
def temp_flow_file():
    """Create a temporary flow definition file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write(FLOW_FILE_CONTENT)
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_df_customflow_import_success(module_args, mocker, temp_flow_file):
    """Test importing a new CustomFlow successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "description": "Test flow description",
            "comments": "Initial version",
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist yet
    client.get_flow_by_name.return_value = None

    # Mock import_flow_definition response
    client.import_flow_definition.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "description": "Test flow description",
        "versionCount": 1,
        "createdTimestamp": 1640000000000,
        "modifiedTimestamp": 1640000000000,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True
    assert result.value.customflow["crn"] == FLOW_CRN
    assert result.value.customflow["name"] == FLOW_NAME

    # Verify CdpDfClient was called correctly
    client.get_flow_by_name.assert_called_once_with(FLOW_NAME)
    client.import_flow_definition.assert_called_once()
    call_args = client.import_flow_definition.call_args[1]
    assert call_args["name"] == FLOW_NAME
    assert call_args["file_content"] == FLOW_FILE_CONTENT
    assert call_args["description"] == "Test flow description"
    assert call_args["comments"] == "Initial version"


def test_df_customflow_import_with_collection(module_args, mocker, temp_flow_file):
    """Test importing a CustomFlow with collection assignment."""

    collection_crn = "crn:cdp:df:us-west-1:tenant:collection:col-123"

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "collection_crn": collection_crn,
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    client.get_flow_by_name.return_value = None
    client.import_flow_definition.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "collectionCrn": collection_crn,
        "versionCount": 1,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    # Verify collection_crn was passed
    call_args = client.import_flow_definition.call_args[1]
    assert call_args["collection_crn"] == collection_crn


def test_df_customflow_present_idempotent(module_args, mocker, temp_flow_file):
    """Test that existing flow is not reimported (idempotent)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow already exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 1,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is False
    assert result.value.customflow["crn"] == FLOW_CRN

    # Verify import was NOT called
    client.import_flow_definition.assert_not_called()


def test_df_customflow_delete_success(module_args, mocker, temp_flow_file):
    """Test deleting an existing CustomFlow successfully."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "state": "absent",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "versionCount": 1,
    }

    # Mock delete_flow response
    client.delete_flow.return_value = {
        "flow": {
            "crn": FLOW_CRN,
            "name": FLOW_NAME,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    # Verify delete was called
    client.delete_flow.assert_called_once_with(FLOW_CRN)


def test_df_customflow_delete_idempotent(module_args, mocker, temp_flow_file):
    """Test deleting non-existent flow is idempotent."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "state": "absent",
        },
    )

    # Patch load_cdp_config
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist
    client.get_flow_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is False

    # Verify delete was NOT called
    client.delete_flow.assert_not_called()


def test_df_customflow_import_with_tags(module_args, mocker, temp_flow_file):
    """Test importing a CustomFlow with tags."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "description": "Flow with tags",
            "comments": "Initial version",
            "tags": [
                {"tag_name": "production", "tag_color": "blue"},
                {"tag_name": "stable"},
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist yet
    client.get_flow_by_name.return_value = None

    # Mock import_flow_definition response
    client.import_flow_definition.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
        "description": "Flow with tags",
        "versionCount": 1,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    # Verify tags were passed correctly (converted to API format)
    call_args = client.import_flow_definition.call_args[1]
    assert call_args["tags"] == [
        {"tagName": "production", "tagColor": "blue"},
        {"tagName": "stable"},
    ]


def test_df_customflow_check_mode_import(module_args, mocker, temp_flow_file):
    """Test check mode for importing a flow."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist
    client.get_flow_by_name.return_value = None

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    # Verify import was NOT called (check mode)
    client.import_flow_definition.assert_not_called()


def test_df_customflow_check_mode_delete(module_args, mocker, temp_flow_file):
    """Test check mode for deleting a flow."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": temp_flow_file,
            "state": "absent",
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow exists
    client.get_flow_by_name.return_value = {
        "crn": FLOW_CRN,
        "name": FLOW_NAME,
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow.main()

    assert result.value.changed is True

    # Verify delete was NOT called (check mode)
    client.delete_flow.assert_not_called()


def test_df_customflow_file_read_error(module_args, mocker):
    """Test handling of file read errors."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "file": "/nonexistent/file.json",
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
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock: Flow doesn't exist
    client.get_flow_by_name.return_value = None

    # Test module execution - should fail
    with pytest.raises(AnsibleFailJson) as result:
        df_customflow.main()

    assert "Failed to read file" in result.value.msg
