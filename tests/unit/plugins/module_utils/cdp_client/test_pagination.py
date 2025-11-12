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

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    RestClient,
)


def test_paginated_decorator_single_page(mocker):
    """Test pagination decorator with single page response (no nextToken)."""

    # Mock response without nextToken
    test_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.return_value = test_data

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    assert response == test_data
    assert len(response["computeUsageRecords"]) == 2
    assert response["computeUsageRecords"][1]["id"] == "record2"

    # Should make only one request
    assert mock_func.call_count == 1


def test_paginated_decorator_multiple_pages(mocker):
    """Test pagination decorator with multiple pages."""

    # Mock multiple page responses
    page1_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
        "nextPageToken": "token123",
    }

    page2_data = {
        "computeUsageRecords": [
            {"id": "record3", "usage": 300},
            {"id": "record4", "usage": 400},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.side_effect = [page1_data, page2_data]

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    assert len(response["computeUsageRecords"]) == 4
    assert response["computeUsageRecords"][0]["id"] == "record1"
    assert response["computeUsageRecords"][3]["id"] == "record4"

    # Should make two requests
    assert mock_func.call_count == 2


def test_paginated_decorator_with_custom_page_size_single(mocker):
    """Test pagination decorator respects custom page size."""

    # Mock single page response
    test_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.return_value = test_data

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated(default_page_size=10)
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    assert response == test_data
    assert len(response["computeUsageRecords"]) == 2
    assert response["computeUsageRecords"][1]["id"] == "record2"

    # Should make only one request
    assert mock_func.call_count == 1

    # Verify that the page size is set correctly
    mock_func.assert_called_with(pageSize=10)


def test_paginated_decorator_with_custom_page_size_multiple(mocker):
    """Test pagination decorator respects custom page size."""

    # Mock single page response
    test_data1 = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
        "nextPageToken": "token123",
    }
    test_data2 = {
        "computeUsageRecords": [
            {"id": "record3", "usage": 300},
            {"id": "record4", "usage": 400},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.side_effect = [test_data1, test_data2]

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated(default_page_size=2)
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    assert len(response["computeUsageRecords"]) == 4
    assert response["computeUsageRecords"][0]["id"] == "record1"
    assert response["computeUsageRecords"][3]["id"] == "record4"

    # Should make only one request
    assert mock_func.call_count == 2

    # Verify that the page size is set correctly
    mock_func.assert_has_calls(
        [
            mocker.call(pageSize=2),
            mocker.call(pageSize=2, pageToken="token123"),
        ],
    )


def test_paginated_decorator_non_dict_response(mocker):
    """Test pagination decorator handles non-dict responses gracefully."""

    # Mock response that isn't a dict
    mock_func = mocker.Mock()
    mock_func.return_value = "Not a dict response"

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    assert response == "Not a dict response"

    # Should make only one request
    assert mock_func.call_count == 1


def test_paginated_decorator_empty_list_keys(mock_ansible_module, mocker):
    """Test pagination decorator with response that has no list fields."""

    # Mock responses with no list fields
    test_data1 = {
        "summary": "usage summary",
        "nextPageToken": "token123",
        "count": 0,
    }
    test_data2 = {
        "summary": "final summary",
        "count": 0,
    }
    mock_func = mocker.Mock()
    mock_func.side_effect = [test_data1, test_data2]

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func()

    # Should have metadata from the last page
    assert response["summary"] == "final summary"
    assert response["count"] == 0
    assert "nextToken" not in response

    # Should make two requests
    assert mock_func.call_count == 2

    # Verify that the page size is set correctly
    mock_func.assert_has_calls(
        [
            mocker.call(pageSize=100),
            mocker.call(pageSize=100, pageToken="token123"),
        ],
    )


def test_paginated_decorator_with_explicit_page_size_single(mocker):
    """Test pagination decorator respects explicit/direct page size for single pages."""

    # Mock single page response
    test_data = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.return_value = test_data

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func(pageSize=10)

    assert response == test_data
    assert len(response["computeUsageRecords"]) == 2
    assert response["computeUsageRecords"][1]["id"] == "record2"

    # Should make only one request
    assert mock_func.call_count == 1

    # Verify that the page size is set correctly
    mock_func.assert_called_with(pageSize=10)


def test_paginated_decorator_with_explicit_page_size_multiple(mocker):
    """Test pagination decorator respects explicit/direct page size for multiple pages."""

    # Mock multiple page responses
    test_data1 = {
        "computeUsageRecords": [
            {"id": "record1", "usage": 100},
            {"id": "record2", "usage": 200},
        ],
        "nextPageToken": "token123",
    }
    test_data2 = {
        "computeUsageRecords": [
            {"id": "record3", "usage": 300},
            {"id": "record4", "usage": 400},
        ],
    }
    mock_func = mocker.Mock()
    mock_func.side_effect = [test_data1, test_data2]

    # Create a function to be decorated
    class TestClient(RestClient):
        @RestClient.paginated()
        def decorated_func(self, *args, **kwargs):
            return mock_func(*args, **kwargs)

    # Call the paginated method
    response = TestClient().decorated_func(pageSize=2)

    # Should return original response since no nextToken
    assert len(response["computeUsageRecords"]) == 4
    assert response["computeUsageRecords"][0]["id"] == "record1"
    assert response["computeUsageRecords"][3]["id"] == "record4"

    # Should make only one request
    assert mock_func.call_count == 2

    # Verify that the page size is set correctly
    mock_func.assert_has_calls(
        [
            mocker.call(pageSize=2),
            mocker.call(pageSize=2, pageToken="token123"),
        ],
    )
