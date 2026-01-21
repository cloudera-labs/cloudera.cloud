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

from ansible_collections.cloudera.cloud.plugins.modules import df_readyflow_info



BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"
FILE_ACCESS_KEY = "file-access-key"
FILE_PRIVATE_KEY = "file-private-key"
FILE_REGION = "default"

READYFLOW_NAME = "Kafka to S3 Avro"
READYFLOW_CRN = "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro"


def test_df_readyflow_info_list_all(module_args, mocker):
    """Test df_readyflow_info module with no parameters returns all ReadyFlows."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows response
    client.list_readyflows.return_value = {
        "readyflows": [
            {
                "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro",
                "name": "Kafka to S3 Avro",
                "author": "Cloudera",
                "summary": "Ingest Kafka messages to S3 as Avro files",
            },
            {
                "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-s3",
                "name": "S3 to S3",
                "author": "Cloudera",
                "summary": "Move data from S3 to S3",
            },
        ],
    }

    # Mock describe_readyflow responses
    def mock_describe_readyflow(readyflow_crn):
        if "kafka-to-s3-avro" in readyflow_crn:
            return {
                "readyflowDetail": {
                    "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro",
                    "name": "Kafka to S3 Avro",
                    "author": "Cloudera",
                    "summary": "Ingest Kafka messages to S3 as Avro files",
                    "description": "This ReadyFlow consumes messages from Kafka and writes them to S3 in Avro format",
                    "source": "Kafka",
                    "sourceDataFormat": "JSON",
                    "destination": "S3",
                    "destinationDataFormat": "Avro",
                    "documentationLink": "https://docs.cloudera.com/readyflows/kafka-to-s3-avro",
                    "imported": False,
                    "modifiedTimestamp": 1609459200000,
                },
            }
        else:
            return {
                "readyflowDetail": {
                    "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-s3",
                    "name": "S3 to S3",
                    "author": "Cloudera",
                    "summary": "Move data from S3 to S3",
                    "description": "This ReadyFlow moves data from one S3 bucket to another",
                    "source": "S3",
                    "sourceDataFormat": "Any",
                    "destination": "S3",
                    "destinationDataFormat": "Any",
                    "documentationLink": "https://docs.cloudera.com/readyflows/s3-to-s3",
                    "imported": True,
                    "modifiedTimestamp": 1609459300000,
                },
            }

    client.describe_readyflow.side_effect = mock_describe_readyflow

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 2
    assert result.value.readyflows[0]["name"] == "Kafka to S3 Avro"
    assert result.value.readyflows[0]["source"] == "Kafka"
    assert result.value.readyflows[0]["destination"] == "S3"
    assert result.value.readyflows[1]["name"] == "S3 to S3"
    assert result.value.readyflows[1]["imported"] is True

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once_with(search_term=None)
    assert client.describe_readyflow.call_count == 2


def test_df_readyflow_info_by_search_term(module_args, mocker):
    """Test df_readyflow_info module filtering by search term."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": "Kafka",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows response with filtered results
    client.list_readyflows.return_value = {
        "readyflows": [
            {
                "readyflowCrn": READYFLOW_CRN,
                "name": READYFLOW_NAME,
                "author": "Cloudera",
                "summary": "Ingest Kafka messages to S3 as Avro files",
            },
        ],
    }

    # Mock describe_readyflow response
    client.describe_readyflow.return_value = {
        "readyflowDetail": {
            "readyflowCrn": READYFLOW_CRN,
            "name": READYFLOW_NAME,
            "author": "Cloudera",
            "summary": "Ingest Kafka messages to S3 as Avro files",
            "description": "This ReadyFlow consumes messages from Kafka and writes them to S3 in Avro format",
            "source": "Kafka",
            "sourceDataFormat": "JSON",
            "destination": "S3",
            "destinationDataFormat": "Avro",
            "documentationLink": "https://docs.cloudera.com/readyflows/kafka-to-s3-avro",
            "imported": False,
            "modifiedTimestamp": 1609459200000,
            "notes": "Supports various Kafka authentication mechanisms",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 1
    assert result.value.readyflows[0]["name"] == READYFLOW_NAME
    assert result.value.readyflows[0]["readyflowCrn"] == READYFLOW_CRN
    assert result.value.readyflows[0]["source"] == "Kafka"
    assert result.value.readyflows[0]["destination"] == "S3"

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once_with(search_term="Kafka")
    client.describe_readyflow.assert_called_once_with(readyflow_crn=READYFLOW_CRN)


def test_df_readyflow_info_by_name_alias(module_args, mocker):
    """Test df_readyflow_info module using name alias for search_term."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "name": READYFLOW_NAME,
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows response
    client.list_readyflows.return_value = {
        "readyflows": [
            {
                "readyflowCrn": READYFLOW_CRN,
                "name": READYFLOW_NAME,
                "author": "Cloudera",
                "summary": "Ingest Kafka messages to S3 as Avro files",
            },
        ],
    }

    # Mock describe_readyflow response
    client.describe_readyflow.return_value = {
        "readyflowDetail": {
            "readyflowCrn": READYFLOW_CRN,
            "name": READYFLOW_NAME,
            "author": "Cloudera",
            "summary": "Ingest Kafka messages to S3 as Avro files",
            "description": "This ReadyFlow consumes messages from Kafka and writes them to S3 in Avro format",
            "source": "Kafka",
            "sourceDataFormat": "JSON",
            "destination": "S3",
            "destinationDataFormat": "Avro",
            "imported": False,
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 1
    assert result.value.readyflows[0]["name"] == READYFLOW_NAME

    # Verify CdpDfClient was called correctly with the search term
    client.list_readyflows.assert_called_once_with(search_term=READYFLOW_NAME)


def test_df_readyflow_info_no_matches(module_args, mocker):
    """Test df_readyflow_info module when search term yields no results."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": "NonexistentReadyFlow",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows returning empty list
    client.list_readyflows.return_value = {"readyflows": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 0

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once_with(search_term="NonexistentReadyFlow")
    client.describe_readyflow.assert_not_called()


def test_df_readyflow_info_empty_catalog(module_args, mocker):
    """Test df_readyflow_info module when no ReadyFlows exist in catalog."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows returning empty list
    client.list_readyflows.return_value = {"readyflows": []}

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 0

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once_with(search_term=None)
    client.describe_readyflow.assert_not_called()


def test_df_readyflow_info_multiple_matches(module_args, mocker):
    """Test df_readyflow_info module with multiple ReadyFlows matching search term."""

    module_args(
        {
            "endpoint": BASE_URL,
            "access_key": ACCESS_KEY,
            "private_key": PRIVATE_KEY,
            "search_term": "S3",
        },
    )

    # Patch load_cdp_config to avoid reading real config files
    config = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
    )
    config.return_value = (FILE_ACCESS_KEY, FILE_PRIVATE_KEY, FILE_REGION)

    # Patch CdpDfClient to avoid real API calls
    client = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows response with multiple S3-related ReadyFlows
    client.list_readyflows.return_value = {
        "readyflows": [
            {
                "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro",
                "name": "Kafka to S3 Avro",
                "author": "Cloudera",
            },
            {
                "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-s3",
                "name": "S3 to S3",
                "author": "Cloudera",
            },
            {
                "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-kafka",
                "name": "S3 to Kafka",
                "author": "Cloudera",
            },
        ],
    }

    # Mock describe_readyflow responses
    def mock_describe_readyflow(readyflow_crn):
        readyflows = {
            "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro": {
                "readyflowDetail": {
                    "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:kafka-to-s3-avro",
                    "name": "Kafka to S3 Avro",
                    "author": "Cloudera",
                    "source": "Kafka",
                    "destination": "S3",
                },
            },
            "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-s3": {
                "readyflowDetail": {
                    "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-s3",
                    "name": "S3 to S3",
                    "author": "Cloudera",
                    "source": "S3",
                    "destination": "S3",
                },
            },
            "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-kafka": {
                "readyflowDetail": {
                    "readyflowCrn": "crn:cdp:df:us-west-1:cloudera:readyflow:s3-to-kafka",
                    "name": "S3 to Kafka",
                    "author": "Cloudera",
                    "source": "S3",
                    "destination": "Kafka",
                },
            },
        }
        return readyflows[readyflow_crn]

    client.describe_readyflow.side_effect = mock_describe_readyflow

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 3

    # Verify all ReadyFlows contain S3 in source or destination
    for readyflow in result.value.readyflows:
        assert "S3" in readyflow["source"] or "S3" in readyflow["destination"]

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once_with(search_term="S3")
    assert client.describe_readyflow.call_count == 3


def test_df_readyflow_info_with_minimal_fields(module_args, mocker):
    """Test df_readyflow_info module with ReadyFlows containing minimal fields."""

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
        "ansible_collections.cloudera.cloud.plugins.modules.df_readyflow_info.CdpDfClient",
        autospec=True,
    ).return_value

    # Mock list_readyflows response
    client.list_readyflows.return_value = {
        "readyflows": [
            {
                "readyflowCrn": READYFLOW_CRN,
                "name": READYFLOW_NAME,
                "author": "Cloudera",
            },
        ],
    }

    # Mock describe_readyflow response with minimal fields
    client.describe_readyflow.return_value = {
        "readyflowDetail": {
            "readyflowCrn": READYFLOW_CRN,
            "name": READYFLOW_NAME,
            "author": "Cloudera",
        },
    }

    # Test module execution
    with pytest.raises(AnsibleExitJson) as result:
        df_readyflow_info.main()

    assert result.value.changed is False
    assert len(result.value.readyflows) == 1
    assert result.value.readyflows[0]["readyflowCrn"] == READYFLOW_CRN
    assert result.value.readyflows[0]["name"] == READYFLOW_NAME
    assert result.value.readyflows[0]["author"] == "Cloudera"

    # Verify optional fields are not present
    assert "description" not in result.value.readyflows[0]
    assert "source" not in result.value.readyflows[0]
    assert "destination" not in result.value.readyflows[0]

    # Verify CdpDfClient was called correctly
    client.list_readyflows.assert_called_once()
    client.describe_readyflow.assert_called_once_with(readyflow_crn=READYFLOW_CRN)
