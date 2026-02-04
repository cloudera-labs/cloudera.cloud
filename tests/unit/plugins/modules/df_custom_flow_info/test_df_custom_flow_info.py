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
    AnsibleExitJson,
)

from ansible_collections.cloudera.cloud.plugins.modules import df_customflow_info


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

FLOW_NAME = "my-custom-flow"
FLOW_CRN = "crn:cdp:df:us-west-1:cloudera:flow:my-custom-flow-id"


def test_df_customflow_info_list_all(module_args, mocker):
    """Test df_customflow_info module with no parameters returns all flows (summary by default)."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions response
    client.list_flow_definitions.return_value = {
        "flows": [
            {
                "crn": "crn:cdp:df:us-west-1:cloudera:flow:flow1",
                "name": "Flow One",
                "artifactType": "flow",
                "versionCount": 2,
                "modifiedTimestamp": 1609459200000,
            },
            {
                "crn": "crn:cdp:df:us-west-1:cloudera:flow:flow2",
                "name": "Flow Two",
                "artifactType": "flow",
                "versionCount": 1,
                "modifiedTimestamp": 1609459300000,
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 2
    assert result.value.flows[0]["name"] == "Flow One"
    assert result.value.flows[0]["versionCount"] == 2

    # With include_details=false (default), should not have detailed fields
    assert "description" not in result.value.flows[0]
    assert "versions" not in result.value.flows[0]

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once()
    client.describe_flow.assert_not_called()


def test_df_customflow_info_list_all_with_details(module_args, mocker):
    """Test df_customflow_info module with include_details=true returns detailed flow information."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "include_details": True,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions response
    client.list_flow_definitions.return_value = {
        "flows": [
            {
                "crn": "crn:cdp:df:us-west-1:cloudera:flow:flow1",
                "name": "Flow One",
                "artifactType": "flow",
                "versionCount": 2,
                "modifiedTimestamp": 1609459200000,
            },
            {
                "crn": "crn:cdp:df:us-west-1:cloudera:flow:flow2",
                "name": "Flow Two",
                "artifactType": "flow",
                "versionCount": 1,
                "modifiedTimestamp": 1609459300000,
            },
        ],
    }

    # Mock describe_flow responses
    def describe_flow_side_effect(crn):
        if "flow1" in crn:
            return {
                "flowDetail": {
                    "crn": crn,
                    "name": "Flow One",
                    "artifactType": "flow",
                    "versionCount": 2,
                    "modifiedTimestamp": 1609459200000,
                    "description": "Detailed description of Flow One",
                    "versions": [{"version": 1}, {"version": 2}],
                },
            }
        elif "flow2" in crn:
            return {
                "flowDetail": {
                    "crn": crn,
                    "name": "Flow Two",
                    "artifactType": "flow",
                    "versionCount": 1,
                    "modifiedTimestamp": 1609459300000,
                    "description": "Detailed description of Flow Two",
                    "versions": [{"version": 1}],
                },
            }
        return None

    client.describe_flow.side_effect = describe_flow_side_effect

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 2

    # Verify detailed fields are present
    assert result.value.flows[0]["description"] == "Detailed description of Flow One"
    assert "versions" in result.value.flows[0]
    assert len(result.value.flows[0]["versions"]) == 2

    assert result.value.flows[1]["description"] == "Detailed description of Flow Two"
    assert "versions" in result.value.flows[1]
    assert len(result.value.flows[1]["versions"]) == 1

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once()
    # Should call describe_flow for each flow
    assert client.describe_flow.call_count == 2


def test_df_customflow_info_by_name(module_args, mocker):
    """Test df_customflow_info module filtering by name without details."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions response with search term
    client.list_flow_definitions.return_value = {
        "flows": [
            {
                "crn": FLOW_CRN,
                "name": FLOW_NAME,
                "artifactType": "flow",
                "versionCount": 3,
                "modifiedTimestamp": 1609459200000,
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 1
    assert result.value.flows[0]["name"] == FLOW_NAME
    assert result.value.flows[0]["crn"] == FLOW_CRN
    assert result.value.flows[0]["versionCount"] == 3

    # Without include_details, should not have detailed fields
    assert "description" not in result.value.flows[0]
    assert "versions" not in result.value.flows[0]

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once_with(search_term=FLOW_NAME)
    client.describe_flow.assert_not_called()


def test_df_customflow_info_by_name_with_details(module_args, mocker):
    """Test df_customflow_info module filtering by name with details."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": FLOW_NAME,
            "include_details": True,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions response with search term
    client.list_flow_definitions.return_value = {
        "flows": [
            {
                "crn": FLOW_CRN,
                "name": FLOW_NAME,
                "artifactType": "flow",
                "versionCount": 3,
                "modifiedTimestamp": 1609459200000,
            },
        ],
    }

    # Mock describe_flow response
    client.describe_flow.return_value = {
        "flowDetail": {
            "crn": FLOW_CRN,
            "name": FLOW_NAME,
            "artifactType": "flow",
            "versionCount": 3,
            "modifiedTimestamp": 1609459200000,
            "description": "A custom flow for data processing",
            "versions": [{"version": 1}, {"version": 2}, {"version": 3}],
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 1
    assert result.value.flows[0]["name"] == FLOW_NAME
    assert result.value.flows[0]["crn"] == FLOW_CRN
    assert result.value.flows[0]["versionCount"] == 3
    assert result.value.flows[0]["description"] == "A custom flow for data processing"
    assert "versions" in result.value.flows[0]

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once_with(search_term=FLOW_NAME)
    client.describe_flow.assert_called_once_with(FLOW_CRN)


def test_df_customflow_info_not_found_by_name(module_args, mocker):
    """Test df_customflow_info module when flow name is not found."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": "NonexistentFlow",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions returning empty list
    client.list_flow_definitions.return_value = {"flows": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 0

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once_with(search_term="NonexistentFlow")


def test_df_customflow_info_empty_catalog(module_args, mocker):
    """Test df_customflow_info module when no flows exist in catalog."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions returning empty list
    client.list_flow_definitions.return_value = {"flows": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 0

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once()


def test_df_customflow_info_with_minimal_fields(module_args, mocker):
    """Test df_customflow_info module with flows containing minimal fields."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_customflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_flow_definitions response with minimal fields
    client.list_flow_definitions.return_value = {
        "flows": [
            {
                "crn": FLOW_CRN,
                "name": FLOW_NAME,
                "artifactType": "flow",
                "versionCount": 1,
            },
        ],
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_customflow_info.main()

    assert result.value.changed is False
    assert len(result.value.flows) == 1
    assert result.value.flows[0]["crn"] == FLOW_CRN
    assert result.value.flows[0]["name"] == FLOW_NAME
    assert result.value.flows[0]["versionCount"] == 1

    # Verify optional fields are not present
    assert "modifiedTimestamp" not in result.value.flows[0]
    assert "collectionCrn" not in result.value.flows[0]
    assert "collectionName" not in result.value.flows[0]

    # Verify CdpDfClient was called correctly
    client.list_flow_definitions.assert_called_once()
