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

from typing import Any, Dict

from ansible_collections.cloudera.cloud.tests.unit import AnsibleFailJson

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    RestClient,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ParametersMixin,
    MessageParameter,
    AutoExecuteMeta,
    ServicesModule,
)


class TestParametersMixin:
    """Test cases for the ParametersMixin abstract base class."""

    def test_parameters_mixin_is_abstract(self):
        """Test that ParametersMixin cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ParametersMixin()  # pyright: ignore[reportAbstractUsage]

    def test_parameters_mixin_abstract_methods(self):
        """Test that ParametersMixin has the expected abstract methods."""
        assert hasattr(ParametersMixin, "get_argument_spec")
        assert hasattr(ParametersMixin, "init_parameters")

        # Check that methods are abstract
        assert getattr(ParametersMixin.get_argument_spec, "__isabstractmethod__", False)
        assert getattr(ParametersMixin.init_parameters, "__isabstractmethod__", False)

    def test_concrete_mixin_implementation(self):
        """Test that a concrete implementation of ParametersMixin works correctly."""

        class TestMixin(ParametersMixin):
            @staticmethod
            def get_argument_spec() -> Dict[str, Dict[str, Any]]:
                return {
                    "test_param": dict(
                        required=False,
                        type="str",
                        default="test_value",
                    ),
                }

            def init_parameters(self) -> None:
                self.test_param = "initialized"

        # Should be able to instantiate concrete implementation
        mixin = TestMixin()
        assert mixin is not None

        # Test the methods
        spec = mixin.get_argument_spec()
        assert "test_param" in spec
        assert spec["test_param"]["default"] == "test_value"

        mixin.init_parameters()
        assert mixin.test_param == "initialized"


class TestMessageParameter:
    """Test cases for the MessageParameter mixin class."""

    def test_message_parameter_inherits_parameters_mixin(self):
        """Test that MessageParameter inherits from ParametersMixin."""
        assert issubclass(MessageParameter, ParametersMixin)

    def test_message_parameter_get_argument_spec(self):
        """Test the get_argument_spec method of MessageParameter."""
        spec = MessageParameter.get_argument_spec()

        assert "message" in spec
        assert spec["message"]["required"] is False
        assert spec["message"]["type"] == "str"
        assert spec["message"]["default"] is None

    def test_message_parameter_init_parameters(self, mocker):
        """Test the init_parameters method of MessageParameter."""
        # Create a mock object with get_param method
        mock_get_param = mocker.Mock(return_value="test message")

        # Create MessageParameter instance and add get_param method
        message_param = MessageParameter()

        # Dynamically add the method since MessageParameter itself (the doesn't have get_param()
        setattr(message_param, "get_param", mock_get_param)

        # Call init_parameters
        message_param.init_parameters()

        # Verify the message attribute is set
        assert hasattr(message_param, "message")
        assert message_param.message == "test message"
        mock_get_param.assert_called_once_with("message")

    def test_message_parameter_init_parameters_none_value(self, mocker):
        """Test init_parameters when get_param returns None."""
        mock_get_param = mocker.Mock(return_value=None)

        message_param = MessageParameter()
        setattr(message_param, "get_param", mock_get_param)
        message_param.init_parameters()

        assert message_param.message is None


class TestAutoExecuteMeta:
    """Test cases for the AutoExecuteMeta metaclass."""

    def test_auto_execute_meta_calls_execute(self, mocker):
        """Test that AutoExecuteMeta automatically calls execute() method."""

        class TestClass(metaclass=AutoExecuteMeta):
            def __init__(self):
                self.initialized = True
                self.execute_called = False

            def execute(self):
                self.execute_called = True

        # Create instance - execute should be called automatically
        instance = TestClass()

        assert instance.initialized is True
        assert instance.execute_called is True

    def test_auto_execute_meta_no_execute_method(self):
        """Test that AutoExecuteMeta doesn't fail when no execute method exists."""

        class TestClass(metaclass=AutoExecuteMeta):
            def __init__(self):
                self.initialized = True

        # Should not raise an exception
        instance = TestClass()
        assert instance.initialized is True

    def test_auto_execute_meta_execute_not_callable(self):
        """Test that AutoExecuteMeta handles non-callable execute attribute."""

        class TestClass(metaclass=AutoExecuteMeta):
            def __init__(self):
                self.initialized = True
                self.execute = "not callable"

        # Should not raise an exception
        instance = TestClass()
        assert instance.initialized is True
        assert instance.execute == "not callable"


class TestServicesModule:
    """Test cases for the ServicesModule base class."""

    def test_services_module_is_abstract(self):
        """Test that ServicesModule cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ServicesModule()  # pyright: ignore[reportAbstractUsage]

    def test_services_module_abstract_methods(self):
        """Test that ServicesModule has the expected abstract methods."""
        assert hasattr(ServicesModule, "process")
        assert getattr(ServicesModule.process, "__isabstractmethod__", False)

    def test_services_module_uses_auto_execute_meta(self):
        """Test that ServicesModule uses AutoExecuteMeta metaclass."""
        assert ServicesModule.__class__ == AutoExecuteMeta


class ConcreteServicesModule(ServicesModule):
    """Concrete implementation of ServicesModule for testing."""

    def __init__(self, **kwargs):
        self._process_called = False
        super().__init__(**kwargs)

    def process(self):
        """Concrete implementation of abstract process method."""
        self._process_called = True
        self.logger.info("Process method called")


class ConcreteServicesModuleWithMixin(ServicesModule, MessageParameter):
    """Concrete implementation with mixin for testing."""

    def __init__(self, **kwargs):
        self._process_called = False
        super().__init__(**kwargs)

    def process(self):
        """Concrete implementation of abstract process method."""
        self._process_called = True
        self.logger.info("Process method called")


@pytest.mark.usefixtures("mock_load_cdp_config", "unset_cdp_env_vars")
class TestConcreteServicesModule:
    """Test cases for concrete ServicesModule implementations."""

    def test_services_module_initialization_basic(
        self,
        module_args,
    ):
        """Test basic ServicesModule initialization."""

        module_args(
            {},
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.test-region.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_explicit(
        self,
        module_args,
    ):
        """Test ServicesModule explicit endpoint."""

        module_args(
            {
                "endpoint": "example-endpoint",
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "example-endpoint"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_region_default(
        self,
        module_args,
    ):
        """Test ServicesModule default endpoint."""

        module_args(
            {
                "endpoint_region": "default",
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.us-west-1.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_region_us_west_1(
        self,
        module_args,
    ):
        """Test ServicesModule US-WEST-1 endpoint."""

        module_args(
            {
                "endpoint_region": "us-west-1",
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.us-west-1.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_region_eu_1(
        self,
        module_args,
    ):
        """Test ServicesModule EU-1 endpoint."""

        module_args(
            {
                "endpoint_region": "eu-1",
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.eu-1.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_region_ap_1(
        self,
        module_args,
    ):
        """Test ServicesModule AP-1 endpoint."""

        module_args(
            {
                 "endpoint_region": "ap-1",
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.ap-1.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_endpoint_region_env(
        self,
        module_args,
        monkeypatch,
    ):
        """Test ServicesModule environment variable endpoint."""

        module_args(
            {},
        )

        monkeypatch.setenv("CDP_REGION", "eu-1")

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.eu-1.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_credentials(
        self,
        module_args,
    ):
        """Test ServicesModule explicit credentials."""

        module_args(
            {
                "access_key": "explicit-access-key",
                "private_key": "explicit-private-key"
            },
        )

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.test-region.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "explicit-access-key"
        assert module.private_key == "explicit-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_credentials_env(
        self,
        module_args,
        monkeypatch,
    ):
        """Test ServicesModule environment variable credentials."""

        module_args(
            {},
        )

        monkeypatch.setenv("CDP_ACCESS_KEY_ID", "env-access-key")
        monkeypatch.setenv("CDP_PRIVATE_KEY", "env-private-key")

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        assert module.endpoint == "https://api.test-region.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "env-access-key"
        assert module.private_key == "env-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_profile_env(
        self,
        module_args,
        monkeypatch,
        mock_load_cdp_config
    ):
        """Test ServicesModule environment variable credentials."""

        module_args(
            {},
        )

        monkeypatch.setenv("CDP_PROFILE", "env-profile")

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        mock_load_cdp_config.assert_called_once_with(
            credentials_path="~/.cdp/credentials",
            profile="env-profile",
        )

        assert module.endpoint == "https://api.test-region.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_cred_path_env(
        self,
        module_args,
        monkeypatch,
        mock_load_cdp_config
    ):
        """Test ServicesModule environment variable credentials."""

        module_args(
            {},
        )

        monkeypatch.setenv("CDP_CREDENTIALS_PATH", "env-cred-path")

        module = ConcreteServicesModule()

        # Verify default (or mock) attributes are set
        mock_load_cdp_config.assert_called_once_with(
            credentials_path="env-cred-path",
            profile="default",
        )

        assert module.endpoint == "https://api.test-region.cdp.cloudera.com"
        assert module.debug_log is False
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"
        assert module.api_client is not None
        assert isinstance(module.api_client, RestClient)

    def test_services_module_initialization_invalid_endpoint_region(
        self,
        module_args,
    ):
        """Test invalid endpoint region in ServicesModule initialization."""

        module_args(
            {
                "endpoint_region": "invalid-region"
            },
        )

        with pytest.raises(
            AnsibleFailJson,
            match="value of endpoint_region must be one of: default, us-west-1, eu-1, ap-1, got: invalid-region",
        ):
            ConcreteServicesModule()

    def test_services_module_initialization_invalid_endpoint_parameters(
        self,
        module_args,
    ):
        """Test invalid parameters in ServicesModule endpoint initialization."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "endpoint_region": "example-region",
            },
        )

        with pytest.raises(
            AnsibleFailJson,
            match="parameters are mutually exclusive: endpoint|endpoint_region",
        ):
            ConcreteServicesModule()

    def test_services_module_initialization_missing_private_key(
        self,
        module_args,
    ):
        """Test missing private_key in ServicesModule initialization."""

        module_args(
            {
                "access_key": "example-access-key",
            },
        )

        with pytest.raises(
            AnsibleFailJson,
            match="parameters are required together: access_key, private_key",
        ):
            ConcreteServicesModule()

    def test_services_module_initialization_missing_access_key(
        self,
        module_args,
    ):
        """Test missing access_key in ServicesModule initialization."""

        module_args(
            {
                "private_key": "test-private-key",
            },
        )

        with pytest.raises(
            AnsibleFailJson,
            match="parameters are required together: access_key, private_key",
        ):
            ConcreteServicesModule()

    def test_services_module_initialization_invalid_credential_parameters(
        self,
        module_args,
    ):
        """Test invalid parameters in ServicesModule initialization."""

        module_args(
            {
                "access_key": "example-access-key",
                "credentials_path": "test-credentials-path",
            },
        )

        with pytest.raises(
            AnsibleFailJson,
            match="parameters are mutually exclusive: access_key|credentials_path",
        ):
            ConcreteServicesModule()

    def test_services_module_with_debug_logging(self, module_args, mocker):
        """Test ServicesModule initialization with debug logging enabled."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "debug": True,
            },
        )

        # Mock logging components
        mock_logger = mocker.patch("logging.getLogger")
        mock_string_io = mocker.patch("io.StringIO")
        mock_handler = mocker.patch("logging.StreamHandler")
        mock_formatter = mocker.patch("logging.Formatter")

        module = ConcreteServicesModule()

        # Verify debug logging setup
        assert module.debug_log is True
        assert module.log_capture is not None
        assert mock_logger.call_count == 2
        mock_logger.assert_has_calls([mocker.call("cloudera.cloud"), mocker.call()])
        mock_string_io.assert_called_once()
        mock_handler.assert_called_once()
        mock_formatter.assert_called_once()

    def test_services_module_get_param(self, module_args):
        """Test the get_param method."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "debug": True,
            },
        )

        module = ConcreteServicesModule()

        # Test getting existing parameter
        assert module.get_param("endpoint") == "example-endpoint"

        # Test getting non-existent parameter with default
        assert module.get_param("nonexistent", "default_val") == "default_val"

        # Test getting non-existent parameter without default
        assert module.get_param("nonexistent") is None

    def test_services_module_with_mixin(self, module_args, mocker):
        """Test ServicesModule with a parameter mixin."""

        # Add message parameter to mock params
        module_args(
            {
                "endpoint": "example-endpoint",
                "message": "test message",
            },
        )

        module = ConcreteServicesModuleWithMixin()

        # Verify mixin parameters were initialized
        assert module.message == "test message"

    def test_services_module_execute_method(self, module_args):
        """Test the execute method."""

        module_args(
            {
                "endpoint": "example-endpoint",
            },
        )

        module = ConcreteServicesModule()

        # Verify process was called
        assert module._process_called is True

    def test_services_module_execute_with_debug_logging(
        self,
        module_args,
        mocker,
    ):
        """Test execute method captures logging output when debug is enabled."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "debug": True,
            },
        )

        # Mock StringIO to simulate log output
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = "Test log output\nSecond line"
        mocker.patch(
            "io.StringIO",
            return_value=mock_string_io_instance,
        )

        module = ConcreteServicesModule()

        # Verify logging output was captured
        assert module.log_out == "Test log output\nSecond line"
        assert module.log_lines == ["Test log output", "Second line"]
        mock_string_io_instance.getvalue.assert_called_once()

    def test_services_module_execute_with_empty_log_capture(
        self,
        module_args,
        mocker,
    ):
        """Test execute method handles empty log capture correctly."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "debug": True,
            },
        )

        # Mock StringIO to return empty string
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = ""
        mocker.patch("io.StringIO", return_value=mock_string_io_instance)

        module = ConcreteServicesModule()

        # Verify empty logging output is handled
        assert module.log_out == ""
        assert module.log_lines == []

    def test_services_module_argument_spec_merging(self, module_args, mocker):
        """Test that argument specs are properly merged."""

        module_args(
            {
                "endpoint": "example-endpoint",
                "custom_param": "custom_value",
            },
        )

        custom_spec = dict(custom_param=dict(required=True, type="str"))

        module = ConcreteServicesModule(argument_spec=custom_spec)

        # Verify that custom parameter is set
        assert module.get_param("custom_param") == "custom_value"

    def test_services_module_auto_execute_integration(self, module_args):
        """Test that AutoExecuteMeta calls execute automatically during instantiation."""

        module_args(
            {
                "endpoint": "example-endpoint",
            },
        )

        # This will create the instance with auto-execute
        module = ConcreteServicesModule()

        # Verify that process was called via auto-execute
        assert module._process_called is True
