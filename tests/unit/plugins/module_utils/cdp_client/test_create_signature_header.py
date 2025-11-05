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
    create_signature_header,
)


def test_create_signature_header_basic():
    """Test basic signature header creation."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = "mock_signature_string"

    result = create_signature_header(encoded_authn_params, signature)

    # Should combine with a dot separator
    expected = "eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==.mock_signature_string"
    assert result == expected


def test_create_signature_header_empty_signature():
    """Test signature header creation with empty signature."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = ""

    result = create_signature_header(encoded_authn_params, signature)

    # Should still include the dot separator even with empty signature
    expected = "eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==."
    assert result == expected


def test_create_signature_header_empty_encoded_params():
    """Test signature header creation with empty encoded parameters."""

    encoded_authn_params = b""
    signature = "mock_signature_string"

    result = create_signature_header(encoded_authn_params, signature)

    # Should handle empty encoded params
    expected = ".mock_signature_string"
    assert result == expected


def test_create_signature_header_special_characters():
    """Test signature header creation with special characters in signature."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = "signature_with_special-chars!@#$%^&*()_+={}[]|\\:;\"'<>,.?/"

    result = create_signature_header(encoded_authn_params, signature)

    # Should handle special characters in signature
    expected = f"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==.{signature}"
    assert result == expected


def test_create_signature_header_unicode_signature():
    """Test signature header creation with unicode characters in signature."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = "signature_with_üñíçødé_chars"

    result = create_signature_header(encoded_authn_params, signature)

    # Should handle unicode characters in signature
    expected = f"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==.{signature}"
    assert result == expected


def test_create_signature_header_long_values():
    """Test signature header creation with very long values."""

    # Long base64 encoded parameters
    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoibG9uZy1hY2Nlc3Mta2V5LXRoYXQtaXMtdmVyeS1sb25nLWFuZC1jb250YWlucy1tYW55LWNoYXJhY3RlcnMtdG8tdGVzdC1sb25nLXZhbHVlcy1oYW5kbGluZy1pbi1zaWduYXR1cmUtaGVhZGVyLWNyZWF0aW9uIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    # Long signature
    signature = "very_long_signature_string_" + "x" * 1000

    result = create_signature_header(encoded_authn_params, signature)

    # Should handle long values correctly
    decoded_params = encoded_authn_params.decode("utf-8")
    expected = f"{decoded_params}.{signature}"
    assert result == expected
    assert len(result) > 1000  # Verify it's actually long


def test_create_signature_header_whitespace_in_signature():
    """Test signature header creation with whitespace in signature."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = "  signature_with_whitespace  "

    result = create_signature_header(encoded_authn_params, signature)

    # Should preserve whitespace in signature (no trimming expected)
    expected = f"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==.{signature}"
    assert result == expected


def test_create_signature_header_both_empty():
    """Test signature header creation with both parameters empty."""

    encoded_authn_params = b""
    signature = ""

    result = create_signature_header(encoded_authn_params, signature)

    # Should still include the dot separator
    expected = "."
    assert result == expected


def test_create_signature_header_realistic_values():
    """Test signature header creation with realistic base64 and signature values."""

    # Realistic base64 encoded auth params
    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoiMTc3ZTlhNDMtMjY3Zi00YjRlLWI0N2UtMDhiZTBlMTAzYWRlIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ"
    # Realistic Ed25519 signature (base64 encoded)
    signature = "yGHoq4b0t_T5J3KhRPqelQjLq5qzhyty-935cwWLgRw"

    result = create_signature_header(encoded_authn_params, signature)

    expected = "eyJhY2Nlc3Nfa2V5X2lkIjoiMTc3ZTlhNDMtMjY3Zi00YjRlLWI0N2UtMDhiZTBlMTAzYWRlIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ.yGHoq4b0t_T5J3KhRPqelQjLq5qzhyty-935cwWLgRw"
    assert result == expected


def test_create_signature_header_decode_error(mocker):
    """Test signature header creation when decode fails."""

    # Create a mock bytes object that will fail to decode
    mock_encoded_params = mocker.Mock()
    mock_encoded_params.decode.side_effect = UnicodeDecodeError(
        "utf-8",
        b"",
        0,
        1,
        "invalid start byte",
    )
    signature = "test_signature"

    with pytest.raises(UnicodeDecodeError) as exc_info:
        create_signature_header(mock_encoded_params, signature)

    assert "invalid start byte" in str(exc_info.value)
    mock_encoded_params.decode.assert_called_once_with("utf-8")


def test_create_signature_header_none_signature():
    """Test signature header creation with None signature."""

    encoded_authn_params = b"eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ=="
    signature = None

    # The % formatting will convert None to "None"
    result = create_signature_header(encoded_authn_params, signature)

    expected = "eyJhY2Nlc3Nfa2V5X2lkIjoidGVzdC1hY2Nlc3Mta2V5IiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ==.None"
    assert result == expected


def test_create_signature_header_none_encoded_params():
    """Test signature header creation with None encoded parameters."""

    encoded_authn_params = None
    signature = "test_signature"

    # This should raise an AttributeError since None doesn't have decode method
    with pytest.raises(AttributeError):
        create_signature_header(encoded_authn_params, signature)


def test_create_signature_header_format_string():
    """Test that function uses % formatting correctly."""

    encoded_authn_params = b"test_params"
    signature = "test_signature"

    result = create_signature_header(encoded_authn_params, signature)

    # Verify the format is exactly: {decoded_params}.{signature}
    assert result == "test_params.test_signature"
    assert "." in result
    assert result.count(".") == 1  # Should have exactly one dot

    parts = result.split(".")
    assert len(parts) == 2
    assert parts[0] == "test_params"
    assert parts[1] == "test_signature"
