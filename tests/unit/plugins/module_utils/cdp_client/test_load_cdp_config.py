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
    CdpCredentialError,
)


def test_load_cdp_config_reads_from_file_successfully(mocker):
    """Test successful reading of credentials from configuration file."""

    config_content = """[default]
cdp_access_key_id = file-access-key
cdp_private_key = file-private-key
"""

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    result_access, result_private, result_region = load_cdp_config(
        credentials_path="/mock/path",
        profile="default",
    )

    assert result_access == "file-access-key"
    assert result_private == "file-private-key"
    assert result_region == "us-west-1"


def test_load_cdp_config_reads_from_file_successfully_region(mocker):
    """Test successful reading of credentials from configuration file with cdp_region."""

    config_content = """[default]
cdp_access_key_id = file-access-key
cdp_private_key = file-private-key
cdp_region = file-region
"""

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    result_access, result_private, result_region = load_cdp_config(
        credentials_path="/mock/path",
        profile="default",
    )

    assert result_access == "file-access-key"
    assert result_private == "file-private-key"
    assert result_region == "file-region"


def test_load_cdp_config_missing_credentials_file(mocker):
    """Test exception when credentials file doesn't exist."""

    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(CdpCredentialError) as exc_info:
        load_cdp_config(
            credentials_path="/nonexistent/path",
            profile="default",
        )

    assert "Credentials file '/nonexistent/path' does not exist" in str(exc_info.value)


def test_load_cdp_config_missing_profile_section(mocker):
    """Test exception when profile section is not found."""

    config_content = "[other_profile]\ncdp_access_key_id = key1\n"

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    with pytest.raises(CdpCredentialError) as exc_info:
        load_cdp_config(
            credentials_path="/mock/path",
            profile="missing_profile",
        )

    assert "CDP profile 'missing_profile' not found" in str(exc_info.value)


def test_load_cdp_config_missing_access_key_option(mocker):
    """Test exception when access key option is missing from profile."""

    config_content = "[default]\ncdp_private_key = private123\n"

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    with pytest.raises(CdpCredentialError) as exc_info:
        load_cdp_config(
            credentials_path="/mock/path",
            profile="default",
        )

    assert "CDP profile 'default' is missing 'cdp_access_key_id'" in str(exc_info.value)


def test_load_cdp_config_missing_private_key_option(mocker):
    """Test exception when private key option is missing from profile."""

    config_content = "[default]\ncdp_access_key_id = access123\n"

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    with pytest.raises(CdpCredentialError) as exc_info:
        load_cdp_config(
            credentials_path="/mock/path",
            profile="default",
        )

    assert "CDP profile 'default' is missing 'cdp_private_key'" in str(exc_info.value)


def test_load_cdp_config_custom_profile(mocker):
    """Test loading credentials from custom profile section."""

    config_content = """[default]
cdp_access_key_id = default-access
cdp_private_key = default-private

[production]
cdp_access_key_id = prod-access-key
cdp_private_key = prod-private-key
cdp_region = prod-region
"""

    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    result_access, result_private, result_region = load_cdp_config(
        credentials_path="/mock/path",
        profile="production",
    )

    assert result_access == "prod-access-key"
    assert result_private == "prod-private-key"
    assert result_region == "prod-region"


def test_load_cdp_config_expands_user_path(mocker):
    """Test that user home path (~) is properly expanded."""

    config_content = """[default]
cdp_access_key_id = test-access-key
cdp_private_key = test-private-key
"""

    # Mock the path expansion and file operations
    mock_expanduser = mocker.patch(
        "os.path.expanduser",
        return_value="/home/user/.cdp/credentials",
    )
    mock_abspath = mocker.patch(
        "os.path.abspath",
        return_value="/home/user/.cdp/credentials",
    )
    mocker.patch("os.path.exists", return_value=True)
    mock_open_object = mocker.mock_open(read_data=config_content)
    mocker.patch("builtins.open", mock_open_object)

    result_access, result_private, result_region = load_cdp_config(
        credentials_path="~/.cdp/credentials",
        profile="default",
    )

    # Verify path expansion was called
    mock_expanduser.assert_called_once_with("~/.cdp/credentials")
    mock_abspath.assert_called_once_with("/home/user/.cdp/credentials")

    # Verify credentials were loaded
    assert result_access == "test-access-key"
    assert result_private == "test-private-key"
    assert result_region == "us-west-1"


def test_load_cdp_config_path_expansion_error_message(mocker):
    """Test that error messages show expanded path when file doesn't exist."""

    # Mock path expansion but file doesn't exist
    mock_expanduser = mocker.patch(
        "os.path.expanduser",
        return_value="/home/user/.cdp/credentials",
    )
    mock_abspath = mocker.patch(
        "os.path.abspath",
        return_value="/home/user/.cdp/credentials",
    )
    mocker.patch("os.path.exists", return_value=False)

    with pytest.raises(CdpCredentialError) as exc_info:
        load_cdp_config(
            credentials_path="~/.cdp/credentials",
            profile="default",
        )

    # Verify path expansion was called
    mock_expanduser.assert_called_once_with("~/.cdp/credentials")
    mock_abspath.assert_called_once_with("/home/user/.cdp/credentials")

    # Verify error message shows expanded path
    assert "Credentials file '/home/user/.cdp/credentials' does not exist" in str(
        exc_info.value,
    )
