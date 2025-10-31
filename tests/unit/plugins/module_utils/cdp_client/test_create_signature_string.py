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
    create_signature_string,
)


def test_create_signature_string_basic(mocker):
    """Test basic signature string creation."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    # Valid base64-encoded 32-byte Ed25519 private key
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="  # 32 bytes of zeros
    
    # Mock the cryptography components
    mock_private_key = mocker.Mock()
    mock_signature = b"mock_signature_bytes_here_32_chars_"
    mock_private_key.sign.return_value = mock_signature
    
    mock_ed25519_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.ed25519.Ed25519PrivateKey"
    )
    mock_ed25519_class.from_private_bytes.return_value = mock_private_key
    
    # Mock base64 functions
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"\x00" * 32  # 32 bytes
    
    mock_urlsafe_b64encode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.urlsafe_b64encode"
    )
    mock_urlsafe_b64encode.return_value = b"mock_encoded_signature"
    
    result = create_signature_string(canonical_string, private_key)
    
    # Verify the function calls
    mock_b64decode.assert_called_once_with(private_key)
    mock_ed25519_class.from_private_bytes.assert_called_once_with(b"\x00" * 32)
    mock_private_key.sign.assert_called_once_with(canonical_string.encode("utf-8"))
    mock_urlsafe_b64encode.assert_called_once_with(mock_signature)
    
    assert result == "mock_encoded_signature"


def test_create_signature_string_invalid_key_length(mocker):
    """Test signature string creation with invalid private key length."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    private_key = "invalid_short_key"
    
    # Mock b64decode to return wrong length
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"short"  # Not 32 bytes
    
    with pytest.raises(Exception) as exc_info:
        create_signature_string(canonical_string, private_key)
    
    assert "Not an Ed25519 private key!" in str(exc_info.value)
    mock_b64decode.assert_called_once_with(private_key)


def test_create_signature_string_empty_canonical_string(mocker):
    """Test signature string creation with empty canonical string."""
    
    canonical_string = ""
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    # Mock the cryptography components
    mock_private_key = mocker.Mock()
    mock_signature = b"signature_for_empty_string"
    mock_private_key.sign.return_value = mock_signature
    
    mock_ed25519_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.ed25519.Ed25519PrivateKey"
    )
    mock_ed25519_class.from_private_bytes.return_value = mock_private_key
    
    # Mock base64 functions
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"\x00" * 32
    
    mock_urlsafe_b64encode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.urlsafe_b64encode"
    )
    mock_urlsafe_b64encode.return_value = b"empty_string_signature"
    
    result = create_signature_string(canonical_string, private_key)
    
    # Should still work with empty string
    mock_private_key.sign.assert_called_once_with(b"")
    assert result == "empty_string_signature"


def test_create_signature_string_unicode_canonical_string(mocker):
    """Test signature string creation with unicode characters in canonical string."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test/üñíçødé\ned25519v1"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    # Mock the cryptography components
    mock_private_key = mocker.Mock()
    mock_signature = b"unicode_signature"
    mock_private_key.sign.return_value = mock_signature
    
    mock_ed25519_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.ed25519.Ed25519PrivateKey"
    )
    mock_ed25519_class.from_private_bytes.return_value = mock_private_key
    
    # Mock base64 functions
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"\x00" * 32
    
    mock_urlsafe_b64encode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.urlsafe_b64encode"
    )
    mock_urlsafe_b64encode.return_value = b"unicode_encoded_sig"
    
    result = create_signature_string(canonical_string, private_key)
    
    # Verify UTF-8 encoding is used
    expected_bytes = canonical_string.encode("utf-8")
    mock_private_key.sign.assert_called_once_with(expected_bytes)
    assert result == "unicode_encoded_sig"


def test_create_signature_string_whitespace_handling(mocker):
    """Test that signature string strips whitespace from base64 output."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    # Mock the cryptography components
    mock_private_key = mocker.Mock()
    mock_signature = b"signature_bytes"
    mock_private_key.sign.return_value = mock_signature
    
    mock_ed25519_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.ed25519.Ed25519PrivateKey"
    )
    mock_ed25519_class.from_private_bytes.return_value = mock_private_key
    
    # Mock base64 functions
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"\x00" * 32
    
    mock_urlsafe_b64encode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.urlsafe_b64encode"
    )
    # Return bytes with whitespace to test strip()
    mock_urlsafe_b64encode.return_value = b"  signature_with_whitespace  "
    
    result = create_signature_string(canonical_string, private_key)
    
    # Should strip whitespace
    assert result == "signature_with_whitespace"


def test_create_signature_string_b64decode_error(mocker):
    """Test signature string creation when base64 decode fails."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    private_key = "invalid_base64!"
    
    # Mock b64decode to raise an exception
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.side_effect = ValueError("Invalid base64")
    
    with pytest.raises(ValueError) as exc_info:
        create_signature_string(canonical_string, private_key)
    
    assert "Invalid base64" in str(exc_info.value)


def test_create_signature_string_crypto_error(mocker):
    """Test signature string creation when cryptographic operation fails."""
    
    canonical_string = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    private_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    # Mock base64 decode
    mock_b64decode = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.b64decode"
    )
    mock_b64decode.return_value = b"\x00" * 32
    
    # Mock Ed25519 to raise an exception during key creation
    mock_ed25519_class = mocker.patch(
        "ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client.ed25519.Ed25519PrivateKey"
    )
    mock_ed25519_class.from_private_bytes.side_effect = ValueError("Invalid key material")
    
    with pytest.raises(ValueError) as exc_info:
        create_signature_string(canonical_string, private_key)
    
    assert "Invalid key material" in str(exc_info.value)