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
)


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