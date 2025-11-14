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
    CdpCredentialError,
    make_signature_header,
)


def test_make_signature_header_basic(mocker):
    """Test basic signature header creation."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT",
    }
    access_key = "test-access-key-123"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="  # 44 chars

    canonical_string = (
        "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    )

    # Mock the sub-functions
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = canonical_string

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "mock_signature_value"

    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.return_value = b"mock_encoded_params"

    mock_create_header = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
    )
    mock_create_header.return_value = "mock_encoded_params.mock_signature_value"

    result = make_signature_header(method, uri, headers, access_key, private_key)

    # Verify all sub-functions were called correctly
    mock_create_canonical.assert_called_once_with(method, uri, headers, "ed25519v1")
    mock_create_signature.assert_called_once_with(canonical_string, private_key)
    mock_create_encoded_params.assert_called_once_with(access_key, "ed25519v1")
    mock_create_header.assert_called_once_with(
        b"mock_encoded_params",
        "mock_signature_value",
    )

    assert result == "mock_encoded_params.mock_signature_value"


def test_make_signature_header_invalid_key_length():
    """Test signature header creation with invalid private key length."""

    method = "POST"
    uri = "https://api.cloudera.com/api/v1/create"
    headers = {"Content-Type": "application/json"}
    access_key = "test-access-key"
    private_key = "short_key"  # Not 44 characters

    with pytest.raises(Exception) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Only ed25519v1 keys are supported!" in str(exc_info.value)


def test_make_signature_header_exactly_44_chars(mocker):
    """Test signature header creation with exactly 44 character private key."""

    method = "PUT"
    uri = "https://api.cloudera.com/api/v1/update"
    headers = {"x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"}
    access_key = "test-access-key"
    private_key = "A" * 44  # Exactly 44 characters

    # Mock the sub-functions
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = (
        "PUT\n\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/update\ned25519v1"
    )

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "signature_44chars"

    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.return_value = b"encoded_44chars"

    mock_create_header = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
    )
    mock_create_header.return_value = "encoded_44chars.signature_44chars"

    result = make_signature_header(method, uri, headers, access_key, private_key)

    # Should work with exactly 44 characters
    assert result == "encoded_44chars.signature_44chars"


def test_make_signature_header_too_long_key():
    """Test signature header creation with private key too long."""

    method = "DELETE"
    uri = "https://api.cloudera.com/api/v1/delete/123"
    headers = {}
    access_key = "test-access-key"
    private_key = "A" * 45  # Too long (45 characters)

    with pytest.raises(CdpCredentialError) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Only ed25519v1 keys are supported!" in str(exc_info.value)


def test_make_signature_header_empty_key():
    """Test signature header creation with empty private key."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    access_key = "test-access-key"
    private_key = ""  # Empty key

    with pytest.raises(CdpCredentialError) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Only ed25519v1 keys are supported!" in str(exc_info.value)


def test_make_signature_header_auth_method_fixed(mocker):
    """Test that auth_method is always 'ed25519v1'."""

    method = "POST"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {"Content-Type": "application/json"}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Mock the sub-functions
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = "canonical_string"

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "signature_value"

    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.return_value = b"encoded_params"

    mock_create_header = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
    )
    mock_create_header.return_value = "final_header"

    make_signature_header(method, uri, headers, access_key, private_key)

    # Verify that "ed25519v1" is passed to both functions that need auth_method
    mock_create_canonical.assert_called_once_with(method, uri, headers, "ed25519v1")
    mock_create_encoded_params.assert_called_once_with(access_key, "ed25519v1")


def test_make_signature_header_function_call_order(mocker):
    """Test that functions are called in the correct order."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {"Content-Type": "application/json"}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Create call tracking
    call_order = []

    def track_canonical(*args, **kwargs):
        call_order.append("canonical")
        return "canonical_result"

    def track_signature(*args, **kwargs):
        call_order.append("signature")
        return "signature_result"

    def track_encoded(*args, **kwargs):
        call_order.append("encoded")
        return b"encoded_result"

    def track_header(*args, **kwargs):
        call_order.append("header")
        return "header_result"

    # Mock the sub-functions with tracking
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
        side_effect=track_canonical,
    )
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
        side_effect=track_signature,
    )
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
        side_effect=track_encoded,
    )
    mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
        side_effect=track_header,
    )

    make_signature_header(method, uri, headers, access_key, private_key)

    # Verify the order: canonical -> signature -> encoded -> header
    expected_order = ["canonical", "signature", "encoded", "header"]
    assert call_order == expected_order


def test_make_signature_header_realistic_values(mocker):
    """Test signature header creation with realistic values."""

    method = "POST"
    uri = "https://console.cdp.cloudera.com/api/v1/iam/listUsers"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-altus-date": "Tue, 05 Nov 2024 12:00:00 GMT",
    }
    access_key = "177e9a43-267f-4b4e-b47e-08be0e103ade"
    private_key = "yGHoq4b0t_T5J3KhRPqelQjLq5qzhyty-935cwWLgRw="  # 44 chars

    # Mock the sub-functions with realistic returns
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = "POST\napplication/json\nTue, 05 Nov 2024 12:00:00 GMT\n/api/v1/iam/listUsers\ned25519v1"

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "kJ8VH2aM9p1Qz7X3nR5tY8uI2oP6wE4rT1yU9iO7pA"

    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.return_value = b"eyJhY2Nlc3Nfa2V5X2lkIjoiMTc3ZTlhNDMtMjY3Zi00YjRlLWI0N2UtMDhiZTBlMTAzYWRlIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ"

    mock_create_header = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
    )
    mock_create_header.return_value = "eyJhY2Nlc3Nfa2V5X2lkIjoiMTc3ZTlhNDMtMjY3Zi00YjRlLWI0N2UtMDhiZTBlMTAzYWRlIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ.kJ8VH2aM9p1Qz7X3nR5tY8uI2oP6wE4rT1yU9iO7pA"

    result = make_signature_header(method, uri, headers, access_key, private_key)

    # Verify realistic signature header format
    assert (
        result
        == "eyJhY2Nlc3Nfa2V5X2lkIjoiMTc3ZTlhNDMtMjY3Zi00YjRlLWI0N2UtMDhiZTBlMTAzYWRlIiwiYXV0aF9tZXRob2QiOiJlZDI1NTE5djEifQ.kJ8VH2aM9p1Qz7X3nR5tY8uI2oP6wE4rT1yU9iO7pA"
    )
    assert "." in result  # Should contain the separator


def test_make_signature_header_canonical_error_propagation(mocker):
    """Test that errors from create_canonical_request_string propagate correctly."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Mock canonical function to raise an error
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.side_effect = ValueError("Canonical creation failed")

    with pytest.raises(ValueError) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Canonical creation failed" in str(exc_info.value)


def test_make_signature_header_signature_error_propagation(mocker):
    """Test that errors from create_signature_string propagate correctly."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Mock canonical to succeed
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = "canonical_string"

    # Mock signature function to raise an error
    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.side_effect = Exception("Not an Ed25519 private key!")

    with pytest.raises(Exception) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Not an Ed25519 private key!" in str(exc_info.value)


def test_make_signature_header_encoded_params_error_propagation(mocker):
    """Test that errors from create_encoded_authn_params_string propagate correctly."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Mock canonical and signature to succeed
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = "canonical_string"

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "signature_value"

    # Mock encoded params function to raise an error
    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.side_effect = TypeError("Object not JSON serializable")

    with pytest.raises(TypeError) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "Object not JSON serializable" in str(exc_info.value)


def test_make_signature_header_final_header_error_propagation(mocker):
    """Test that errors from create_signature_header propagate correctly."""

    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {}
    access_key = "test-access-key"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

    # Mock all functions to succeed except the last one
    mock_create_canonical = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_canonical_request_string",
    )
    mock_create_canonical.return_value = "canonical_string"

    mock_create_signature = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_string",
    )
    mock_create_signature.return_value = "signature_value"

    mock_create_encoded_params = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_encoded_authn_params_string",
    )
    mock_create_encoded_params.return_value = b"encoded_params"

    # Mock final header function to raise an error
    mock_create_header = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.create_signature_header",
    )
    mock_create_header.side_effect = UnicodeDecodeError(
        "utf-8",
        b"",
        0,
        1,
        "invalid start byte",
    )

    with pytest.raises(UnicodeDecodeError) as exc_info:
        make_signature_header(method, uri, headers, access_key, private_key)

    assert "invalid start byte" in str(exc_info.value)
