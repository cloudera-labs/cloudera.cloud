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
import pytest

from ansible_collections.cloudera.cloud.tests.unit import AnsibleFailJson

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    AnsibleCdpClient,
    CdpError,
)

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


def test_url_string(mock_ansible_module):
    """Test that URL strings are constructed correctly."""

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    url = client._url("/some/path")
    expected_url = f"{BASE_URL}/some/path"

    assert url == expected_url


def test_url_string_trailing_slash(mock_ansible_module):
    """Test that URL strings are constructed correctly with trailing slashes."""

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    url = client._url("/some/path/")
    expected_url = f"{BASE_URL}/some/path"

    assert url == expected_url


def test_cdp_client_init(mock_ansible_module):
    """Test listing compute usage records."""

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url="https://api.us-west-1.cdp.cloudera.com/",
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    assert client.base_url == "https://api.us-west-1.cdp.cloudera.com"
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Accept"] == "application/json"


def test_cdp_client_init_proxy(mock_ansible_module):
    """Test listing compute usage records."""

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url="https://api.us-west-1.cdp.cloudera.com/",
        proxy_context_path="/proxy/path",
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    assert client.base_url == "https://api.us-west-1.cdp.cloudera.com"
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Accept"] == "application/json"
    assert client.proxy_context_path == "/proxy/path"


def test_make_request_http_200(mock_ansible_module, mocker):
    """Test processing 200 OK responses."""

    # Set up the mock response data
    test_data = {"success": True}
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")

    # Mock the request function to return the test data (200 OK)
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

    response = client._make_request("GET", "/test/path")

    assert "success" in response
    assert response["success"] is True

    assert mock_fetch_url.call(
        mock_ansible_module,
        f"{BASE_URL}/test/path",
        method="GET",
        headers=client.headers,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_204(mock_ansible_module, mocker):
    """Test processing 204 No Content responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b""

    # Mock the request function to return 204 No Content
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 204})

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

    response = client._make_request("DELETE", "/test/path")

    assert response is None


def test_make_request_http_401(mock_ansible_module, mocker):
    """Test processing 401 Unauthorized responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = (
        b'{"errorMessage": "Unauthorized", "errorCode": "401"}'
    )

    # Mock the request function to return 401 Unauthorized
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 401})

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

    with pytest.raises(AnsibleFailJson):
        client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(msg="Unauthorized access to /test/path")


def test_make_request_http_403(mock_ansible_module, mocker):
    """Test processing 403 Forbidden responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b'{"errorMessage": "Forbidden", "errorCode": "403"}'

    # Mock the request function to return 403 Forbidden
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 403})

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

    with pytest.raises(AnsibleFailJson):
        client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(msg="Forbidden access to /test/path")


def test_make_request_http_404(mock_ansible_module, mocker):
    """Test processing 404 Not Found responses."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 404 Not Found
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {
            "status": 404,
            "body": '{"errorMessage": "Not Found", "errorCode": "404"}',
            "msg": "Not Found",
        },
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

    with pytest.raises(AnsibleFailJson):
        client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(msg="Not Found [404] for https://cloudera.internal/api/test/path")


def test_make_request_http_500_with_retry(mock_ansible_module, mocker):
    """Test processing 500 Internal Server Error with retry logic."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 500 Internal Server Error
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {"status": 500, "msg": "Internal Server Error"},
    )

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.time.sleep",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    with pytest.raises(AnsibleFailJson):
        client._make_request("GET", "/test/path", max_retries=2)

    mock_ansible_module.fail_json.assert_called_once_with(msg="Internal Server Error [500] for https://cloudera.internal/api/test/path") 
    
    # Should retry once (2 total attempts)
    assert mock_fetch_url.call_count == 2
    assert mock_sleep.call_count == 1


def test_make_request_http_429_with_retry(mock_ansible_module, mocker):
    """Test processing 429 Too Many Requests with retry logic."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 429 Too Many Requests
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {"status": 429, "msg": "Too Many Requests"},
    )

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.time.sleep",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    with pytest.raises(AnsibleFailJson):
        client._make_request("GET", "/test/path", max_retries=3)

    mock_ansible_module.fail_json.assert_called_once_with(msg="Too Many Requests [429] for https://cloudera.internal/api/test/path")

    # Should retry 2 times (3 total attempts)
    assert mock_fetch_url.call_count == 3
    assert mock_sleep.call_count == 2


def test_make_request_connection_error_with_retry(mock_ansible_module, mocker):
    """Test processing connection errors with retry logic."""

    # Mock the request function to raise a connection error
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.fetch_url",
    )
    mock_fetch_url.side_effect = Exception("Connection refused")

    # Mock the signature header generation
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.make_signature_header",
        return_value="mock_signature",
    )

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.time.sleep",
    )

    client = AnsibleCdpClient(
        module=mock_ansible_module,
        base_url=BASE_URL,
        access_key=ACCESS_KEY,
        private_key=PRIVATE_KEY,
    )

    with pytest.raises(AnsibleFailJson) as exc_info:
        client._make_request("GET", "/test/path", max_retries=2)

    mock_ansible_module.fail_json.assert_called_once_with(msg="Request failed after 2 attempts for https://cloudera.internal/api/test/path: Connection refused")

    # Should retry once (2 total attempts)
    assert mock_fetch_url.call_count == 2
    assert mock_sleep.call_count == 1


def test_make_request_empty_response(mock_ansible_module, mocker):
    """Test processing 200 OK responses with empty body."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b""

    # Mock the request function to return empty response (200 OK)
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

    response = client._make_request("GET", "/test/path")

    assert response == {}


def test_make_request_json_decode_error(mock_ansible_module, mocker):
    """Test processing responses with invalid JSON."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b"invalid json {"

    # Mock the request function to return invalid JSON (200 OK)
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

    response = client._make_request("GET", "/test/path")

    assert "response" in response
    assert response["response"] == "invalid json {"
