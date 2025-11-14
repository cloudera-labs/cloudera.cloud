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

import pytest

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    create_canonical_request_string,
)


def test_create_canonical_request_string_basic():
    """Test basic canonical request string creation."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = (
        "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    )
    assert result == expected


def test_create_canonical_request_string_missing_headers():
    """Test canonical request string with missing headers."""

    method = "POST"
    uri = "https://api.cloudera.com/api/v1/create"
    headers = {
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
        # Missing Content-Type
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    # Empty string for missing content-type
    expected = "POST\n\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/create\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_case_insensitive_headers():
    """Test canonical request string with mixed case headers."""

    method = "PUT"
    uri = "https://api.cloudera.com/api/v1/update"
    headers = {
        "CONTENT-TYPE": "application/json",
        "X-Altus-Date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = "PUT\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/update\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_with_query_params():
    """Test canonical request string with query parameters."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/list?limit=10&offset=20"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/list?limit=10&offset=20\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_root_path():
    """Test canonical request string with root path."""

    method = "GET"
    uri = "https://api.cloudera.com"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    # Should default to "/" for empty path
    expected = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_empty_path():
    """Test canonical request string with empty path."""

    method = "GET"
    uri = "https://api.cloudera.com/"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_method_case():
    """Test canonical request string converts method to uppercase."""

    method = "delete"
    uri = "https://api.cloudera.com/api/v1/resource/123"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = "DELETE\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/resource/123\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_header_whitespace():
    """Test canonical request string strips whitespace from headers."""

    method = "POST"
    uri = "https://api.cloudera.com/api/v1/create"
    headers = {
        "Content-Type": "  application/json  ",
        "x-altus-date": "  Mon, 01 Jan 2024 00:00:00 GMT  ",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    expected = "POST\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/create\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_null_headers():
    """Test canonical request string handles null header values."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {
        "Content-Type": None,
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    # Null content-type should result in empty string
    expected = "GET\n\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_all_missing_headers():
    """Test canonical request string with all headers missing."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    auth_method = "ed25519v1"

    result = create_canonical_request_string(method, uri, headers, auth_method)

    # Both headers missing should result in empty strings
    expected = "GET\n\n\n/api/v1/test\ned25519v1"
    assert result == expected
