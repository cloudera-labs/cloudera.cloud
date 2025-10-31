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
    load_cdp_config,
    create_canonical_request_string,
    create_signature_string,
)

BASE_URL = "https://cloudera.internal/api"
ACCESS_KEY = "test-access-key"
PRIVATE_KEY = "test-private-key"


def test_load_cdp_config_with_existing_credentials():
    """Test that function returns provided credentials when both are present."""
    
    access_key = "existing-access-key"
    private_key = "existing-private-key"
    
    result_access, result_private = load_cdp_config(
        access_key=access_key,
        private_key=private_key,
        credentials_path="/unused/path",
        profile="unused",
    )
    
    assert result_access == access_key
    assert result_private == private_key


def test_load_cdp_config_missing_credentials_file(mocker):
    """Test exception when credentials file doesn't exist."""

    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(Exception) as exc_info:
        load_cdp_config(
                access_key=None,
                private_key=None,
                credentials_path="/nonexistent/path",
                profile="default",
            )
        
        assert "Credentials file '/nonexistent/path' does not exist" in str(exc_info.value)


def test_load_cdp_config_missing_profile_section(mocker):
    """Test exception when profile section is not found."""
    
    config_content = "[other_profile]\ncdp_access_key_id = key1\n"

    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)
    
    with pytest.raises(Exception) as exc_info:
        load_cdp_config(
            access_key=None,
            private_key=None,
            credentials_path="/mock/path",
            profile="missing_profile",
        )
            
    assert "CDP profile 'missing_profile' not found" in str(exc_info.value)


def test_load_cdp_config_missing_access_key_option(mocker):
    """Test exception when access key option is missing from profile."""
    
    config_content = "[default]\ncdp_private_key = private123\n"
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    with pytest.raises(Exception) as exc_info:
        load_cdp_config(
            access_key=None,
            private_key="provided-key",
            credentials_path="/mock/path", 
            profile="default",
        )
    
    assert "CDP profile 'default' is missing 'cdp_access_key_id'" in str(exc_info.value)


def test_load_cdp_config_missing_private_key_option(mocker):
    """Test exception when private key option is missing from profile."""
    
    config_content = "[default]\ncdp_access_key_id = access123\n"
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    with pytest.raises(Exception) as exc_info:
        load_cdp_config(
            access_key="provided-access",
            private_key=None,
            credentials_path="/mock/path",
            profile="default",
        )
    
    assert "CDP profile 'default' is missing 'cdp_private_key'" in str(exc_info.value)


def test_load_cdp_config_reads_from_file_successfully(mocker):
    """Test successful reading of credentials from configuration file."""
    
    config_content = """[default]
cdp_access_key_id = file-access-key
cdp_private_key = file-private-key
"""
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    result_access, result_private = load_cdp_config(
        access_key=None,
        private_key=None,
        credentials_path="/mock/path",
        profile="default",
    )
    
    assert result_access == "file-access-key"
    assert result_private == "file-private-key"


def test_load_cdp_config_partial_override_access_key(mocker):
    """Test loading private key from file when access key is provided."""
    
    config_content = """[default]
cdp_access_key_id = file-access-key
cdp_private_key = file-private-key
"""
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    result_access, result_private = load_cdp_config(
        access_key="provided-access-key",
        private_key=None,
        credentials_path="/mock/path",
        profile="default",
    )
    
    assert result_access == "provided-access-key"
    assert result_private == "file-private-key"


def test_load_cdp_config_partial_override_private_key(mocker):
    """Test loading access key from file when private key is provided."""
    
    config_content = """[default]
cdp_access_key_id = file-access-key
cdp_private_key = file-private-key
"""
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    result_access, result_private = load_cdp_config(
        access_key=None,
        private_key="provided-private-key",
        credentials_path="/mock/path",
        profile="default",
    )
    
    assert result_access == "file-access-key"
    assert result_private == "provided-private-key"


def test_load_cdp_config_custom_profile(mocker):
    """Test loading credentials from custom profile section."""
    
    config_content = """[default]
cdp_access_key_id = default-access
cdp_private_key = default-private

[production]
cdp_access_key_id = prod-access-key
cdp_private_key = prod-private-key
"""
    
    mocker.patch('os.path.exists', return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch('builtins.open', mock_open_object)

    result_access, result_private = load_cdp_config(
        access_key=None,
        private_key=None, 
        credentials_path="/mock/path",
        profile="production",
    )
    
    assert result_access == "prod-access-key"
    assert result_private == "prod-private-key"


def test_create_canonical_request_string_basic():
    """Test basic canonical request string creation."""
    
    method = "GET"
    uri = "https://api.cloudera.com/api/v1/test"
    headers = {
        "Content-Type": "application/json",
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
    }
    auth_method = "ed25519v1"
    
    result = create_canonical_request_string(method, uri, headers, auth_method)
    
    expected = "GET\napplication/json\nMon, 01 Jan 2024 00:00:00 GMT\n/api/v1/test\ned25519v1"
    assert result == expected


def test_create_canonical_request_string_missing_headers():
    """Test canonical request string with missing headers."""
    
    method = "POST"
    uri = "https://api.cloudera.com/api/v1/create"
    headers = {
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "X-Altus-Date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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
        "x-altus-date": "  Mon, 01 Jan 2024 00:00:00 GMT  "
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
        "x-altus-date": "Mon, 01 Jan 2024 00:00:00 GMT"
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

