# -*- coding: utf-8 -*-

# Copyright 2025 Cloudera, Inc. All Rights Reserved.
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

import json

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
)


BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


def test_paginated_decorator_single_page(mock_ansible_module, mocker):
    """Test pagination decorator with single page response (no nextToken)."""

    # Mock response without nextToken
    test_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200}
        ],
        "totalRecords": 2
    }
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")

    # Mock the request function
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    # Call the paginated method
    response = client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Should return original response since no nextToken
    assert response == test_data
    assert len(response["computeUsageRecords"]) == 2
    assert response["totalRecords"] == 2

    # Should make only one request
    assert mock_fetch_url.call_count == 1


def test_paginated_decorator_multiple_pages(mock_ansible_module, mocker):
    """Test pagination decorator with multiple pages."""

    # Mock multiple page responses
    page1_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200}
        ],
        "nextToken": "token123",
        "totalRecords": 4
    }
    
    page2_data = {
        "computeUsageRecords": [
            {"id": "record3", "usage": 300},
            {"id": "record4", "usage": 400}
        ],
        "totalRecords": 4  # Final count
    }

    responses = [page1_data, page2_data]
    current_response = [0]

    def mock_response(*args, **kwargs):
        mock_resp = mocker.Mock()
        mock_resp.read.return_value = json.dumps(responses[current_response[0]]).encode("utf-8")
        current_response[0] += 1
        return mock_resp, {"status": 200}

    # Mock the request function
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
        side_effect=mock_response
    )

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    # Call the paginated method
    response = client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Should combine all records from both pages
    assert len(response["computeUsageRecords"]) == 4
    assert response["computeUsageRecords"][0]["id"] == "record1"
    assert response["computeUsageRecords"][3]["id"] == "record4"
    assert response["totalRecords"] == 4  # Should have latest metadata

    # Should make two requests
    assert mock_fetch_url.call_count == 2


def test_paginated_decorator_with_custom_page_size(mock_ansible_module, mocker):
    """Test pagination decorator respects custom page size."""

    # Mock single page response
    test_data = {
        "computeUsageRecords": [{"id": "record1", "usage": 100}],
        "totalRecords": 1
    }
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")

    # Mock the request function and capture the request body
    captured_requests = []
    
    def capture_request(module, url, **kwargs):
        captured_requests.append(kwargs.get('data'))
        return mock_resp, {"status": 200}

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
        side_effect=capture_request
    )

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    # Create client with custom default page size
    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
        default_page_size=50
    )

    # Call the paginated method
    client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Verify that the default page size is set correctly
    assert client.default_page_size == 50


def test_paginated_decorator_three_pages(mock_ansible_module, mocker):
    """Test pagination decorator with three pages to verify proper token handling."""

    # Mock three page responses
    page1_data = {
        "computeUsageRecords": [{"id": "record1"}],
        "nextToken": "token1",
        "metadata": {"page": 1}
    }
    
    page2_data = {
        "computeUsageRecords": [{"id": "record2"}],
        "nextToken": "token2",
        "metadata": {"page": 2}
    }
    
    page3_data = {
        "computeUsageRecords": [{"id": "record3"}],
        "metadata": {"page": 3}  # No nextToken = last page
    }

    responses = [page1_data, page2_data, page3_data]
    current_response = [0]
    captured_requests = []

    def mock_response(*args, **kwargs):
        # Capture the request data to verify pagination parameters
        captured_requests.append(kwargs.get('data'))
        mock_resp = mocker.Mock()
        mock_resp.read.return_value = json.dumps(responses[current_response[0]]).encode("utf-8")
        current_response[0] += 1
        return mock_resp, {"status": 200}

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
        side_effect=mock_response
    )

    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    response = client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Should combine all records from three pages
    assert len(response["computeUsageRecords"]) == 3
    assert response["computeUsageRecords"][0]["id"] == "record1"
    assert response["computeUsageRecords"][1]["id"] == "record2"
    assert response["computeUsageRecords"][2]["id"] == "record3"
    
    # Should have metadata from last page
    assert response["metadata"]["page"] == 3

    # Should make three requests
    assert mock_fetch_url.call_count == 3

    # Verify pagination tokens were sent correctly
    request1 = json.loads(captured_requests[0])
    assert "startingToken" not in request1  # First request has no token
    
    request2 = json.loads(captured_requests[1])
    assert request2["startingToken"] == "token1"
    
    request3 = json.loads(captured_requests[2])
    assert request3["startingToken"] == "token2"


def test_paginated_decorator_non_dict_response(mock_ansible_module, mocker):
    """Test pagination decorator handles non-dict responses gracefully."""

    # Mock response that's not a dict
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b"Not a JSON object"

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    response = client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Should return the non-dict response as-is
    assert response == {"response": "Not a JSON object"}
    assert mock_fetch_url.call_count == 1


def test_paginated_decorator_empty_list_keys(mock_ansible_module, mocker):
    """Test pagination decorator with response that has no list fields."""

    # Mock responses with no list fields
    page1_data = {
        "summary": "usage summary",
        "nextToken": "token123",
        "count": 0
    }
    
    page2_data = {
        "summary": "final summary",
        "count": 0
    }

    responses = [page1_data, page2_data]
    current_response = [0]

    def mock_response(*args, **kwargs):
        mock_resp = mocker.Mock()
        mock_resp.read.return_value = json.dumps(responses[current_response[0]]).encode("utf-8")
        current_response[0] += 1
        return mock_resp, {"status": 200}

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
        side_effect=mock_response
    )

    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    response = client.list_compute_usage_records("2024-01-01", "2024-01-31")

    # Should have metadata from the last page
    assert response["summary"] == "final summary"
    assert response["count"] == 0
    assert "nextToken" not in response

    # Should make two requests
    assert mock_fetch_url.call_count == 2


def test_single_page_method_no_pagination(mock_ansible_module, mocker):
    """Test that the non-decorated single page method works correctly."""

    # Mock response with nextToken that should NOT be handled
    test_data = {
        "computeUsageRecords": [{"id": "record1"}],
        "nextToken": "token123",  # This should be returned as-is
        "totalRecords": 10
    }
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    # Call the non-paginated method
    response = client.list_compute_usage_records_single_page("2024-01-01", "2024-01-31")

    # Should return original response including nextToken
    assert response == test_data
    assert "nextToken" in response
    assert response["nextToken"] == "token123"
    assert len(response["computeUsageRecords"]) == 1

    # Should make only one request
    assert mock_fetch_url.call_count == 1


def test_paginated_decorator_with_explicit_page_size(mock_ansible_module, mocker):
    """Test pagination decorator when pageSize is explicitly provided."""

    # Mock single page response
    test_data = {
        "computeUsageRecords": [{"id": "record1"}],
        "totalRecords": 1
    }
    
    captured_requests = []
    
    def capture_request(module, url, **kwargs):
        captured_requests.append(kwargs.get('data'))
        mock_resp = mocker.Mock()
        mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")
        return mock_resp, {"status": 200}

    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
        side_effect=capture_request
    )

    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
        default_page_size=100
    )

    # Call with explicit pageSize parameter (this should be used instead of default)
    response = client.list_compute_usage_records(
        "2024-01-01", 
        "2024-01-31", 
        pageSize=25
    )

    # Verify the request contains the explicit page size
    request_data = json.loads(captured_requests[0])
    assert request_data["pageSize"] == 25
    assert request_data["fromTimestamp"] == "2024-01-01"
    assert request_data["toTimestamp"] == "2024-01-31"