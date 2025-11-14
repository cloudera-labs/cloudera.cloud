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
import unittest.mock

from base64 import b64decode, urlsafe_b64encode

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    create_encoded_authn_params_string,
    CdpCredentialError,
)


def test_create_encoded_authn_params_string_basic():
    """Test basic authentication parameters encoding."""

    access_key = "test-access-key-123"
    auth_method = "ed25519v1"

    # Test the function
    result = create_encoded_authn_params_string(access_key, auth_method)

    # Verify function calls
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()

    assert result == expected


def test_create_encoded_authn_params_string_ordered_dict():
    """Test that function uses OrderedDict to maintain key order."""

    access_key = "my-access-key"
    auth_method = "ed25519v1"

    result = create_encoded_authn_params_string(access_key, auth_method)

    # Decode and parse the JSON to verify structure
    decoded_bytes = b64decode(result)
    json_str = decoded_bytes.decode("utf-8")
    parsed = json.loads(json_str)

    assert parsed["access_key_id"] == access_key
    assert parsed["auth_method"] == auth_method

    # Verify the expected base64 encoded result
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()
    assert result == expected


def test_create_encoded_authn_params_string_special_characters():
    """Test authentication parameters with special characters."""

    access_key = "test-key-with-special-chars!@#$%"
    auth_method = "ed25519v1"

    result = create_encoded_authn_params_string(access_key, auth_method)

    # Decode and verify the special characters are handled correctly
    decoded_bytes = b64decode(result)
    json_str = decoded_bytes.decode("utf-8")
    parsed = json.loads(json_str)

    assert parsed["access_key_id"] == access_key
    assert parsed["auth_method"] == auth_method

    # Verify the expected base64 encoded result
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()
    assert result == expected


def test_create_encoded_authn_params_string_unicode_access_key():
    """Test authentication parameters with unicode characters in access key."""

    access_key = "test-key-üñíçødé"
    auth_method = "ed25519v1"

    result = create_encoded_authn_params_string(access_key, auth_method)

    # Decode and verify UTF-8 encoding is used correctly
    decoded_bytes = b64decode(result)
    json_str = decoded_bytes.decode("utf-8")
    parsed = json.loads(json_str)

    assert parsed["access_key_id"] == access_key
    assert parsed["auth_method"] == auth_method

    # Verify the expected base64 encoded result
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()
    assert result == expected


def test_create_encoded_authn_params_string_empty_values():
    """Test authentication parameters with empty values."""

    access_key = ""
    auth_method = ""

    result = create_encoded_authn_params_string(access_key, auth_method)

    # Decode and verify empty values are handled correctly
    decoded_bytes = b64decode(result)
    json_str = decoded_bytes.decode("utf-8")
    parsed = json.loads(json_str)

    assert parsed["access_key_id"] == ""
    assert parsed["auth_method"] == ""

    # Verify the expected base64 encoded result
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()
    assert result == expected


def test_create_encoded_authn_params_string_whitespace_stripping():
    """Test that the function strips whitespace from base64 output."""

    access_key = "test-key"
    auth_method = "ed25519v1"

    result = create_encoded_authn_params_string(access_key, auth_method)

    # Verify that the result has no leading/trailing whitespace
    assert result == result.strip()

    # Decode and verify the content
    decoded_bytes = b64decode(result)
    json_str = decoded_bytes.decode("utf-8")
    parsed = json.loads(json_str)

    assert parsed["access_key_id"] == access_key
    assert parsed["auth_method"] == auth_method

    # Verify the expected base64 encoded result
    expected = urlsafe_b64encode(
        json.dumps({"access_key_id": access_key, "auth_method": auth_method}).encode(
            "utf-8",
        ),
    ).strip()
    assert result == expected


def test_create_encoded_authn_params_string_different_auth_methods():
    """Test authentication parameters with different auth methods."""

    access_key = "test-key"

    # Test with different auth method values
    for auth_method in ["ed25519v1", "rsa-sha256", "hmac-sha256"]:
        result = create_encoded_authn_params_string(access_key, auth_method)

        # Decode and verify the auth method is correctly encoded
        decoded_bytes = b64decode(result)
        json_str = decoded_bytes.decode("utf-8")
        parsed = json.loads(json_str)

        assert parsed["access_key_id"] == access_key
        assert parsed["auth_method"] == auth_method

        # Verify the expected base64 encoded result
        expected = urlsafe_b64encode(
            json.dumps(
                {"access_key_id": access_key, "auth_method": auth_method},
            ).encode("utf-8"),
        ).strip()
        assert result == expected


def test_create_encoded_authn_params_string_json_serialization_error():
    """Test authentication parameters when JSON serialization fails."""

    access_key = "test-key"
    auth_method = "ed25519v1"

    # Use unittest.mock directly with a more targeted approach
    with unittest.mock.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.json.dumps",
    ) as mock_dumps:
        mock_dumps.side_effect = TypeError("Object not JSON serializable")

        with pytest.raises(CdpCredentialError) as exc_info:
            create_encoded_authn_params_string(access_key, auth_method)

        assert "Error encoding authentication parameters" in str(exc_info.value)
        assert "Object not JSON serializable" in str(exc_info.value)


def test_create_encoded_authn_params_string_base64_error():
    """Test authentication parameters when base64 encoding fails."""

    access_key = "test-key"
    auth_method = "ed25519v1"

    # Use unittest.mock directly with a more targeted approach
    with unittest.mock.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.json.dumps",
    ) as mock_dumps, unittest.mock.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.urlsafe_b64encode",
    ) as mock_b64encode:
        mock_dumps.return_value = (
            '{"access_key_id": "test-key", "auth_method": "ed25519v1"}'
        )
        mock_b64encode.side_effect = ValueError("Invalid input for base64 encoding")

        with pytest.raises(ValueError) as exc_info:
            create_encoded_authn_params_string(access_key, auth_method)

        assert "Invalid input for base64 encoding" in str(exc_info.value)
