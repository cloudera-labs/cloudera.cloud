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
            ParametersMixin() # pyright: ignore[reportAbstractUsage]

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
                    "test_param": dict(required=False, type="str", default="test_value")
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
        # Dynamically add the method since MessageParameter doesn't have get_param
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
            ServicesModule() # pyright: ignore[reportAbstractUsage]

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
        # Mock the load_cdp_config to avoid file system dependencies
        self._process_called = False
        self._execute_called = False
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


class TestConcreteServicesModule:
    """Test cases for concrete ServicesModule implementations."""

    @pytest.fixture
    def mock_load_cdp_config(self, mocker):
        """Mock the load_cdp_config function."""
        return mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.common.load_cdp_config",
            return_value=("test-access-key", "test-private-key")
        )

    @pytest.fixture
    def mock_ansible_module(self, mocker):
        """Mock AnsibleModule for testing."""
        mock_module = mocker.patch(
            "ansible_collections.cloudera.cloud.plugins.module_utils.common.AnsibleModule"
        )
        
        # Configure the mock instance
        instance = mock_module.return_value
        instance.params = {
            "endpoint": "https://api.cloudera.com",
            "debug": False,
            "agent_header": "cloudera.cloud",
            "access_key": None,
            "private_key": None,
            "credentials_path": "~/.cdp/credentials",
            "profile": "default",
        }
        
        return mock_module

    def test_services_module_initialization(self, mock_ansible_module, mock_load_cdp_config, mocker):
        """Test basic ServicesModule initialization."""
        
        # Prevent actual execute from running during init
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        module._execute_called = False
        
        # Call init manually to test without auto-execute
        ServicesModule.__init__(module)
        
        # Verify AnsibleModule was created with correct arguments
        mock_ansible_module.assert_called_once()
        call_kwargs = mock_ansible_module.call_args[1]
        
        assert "argument_spec" in call_kwargs
        assert "endpoint" in call_kwargs["argument_spec"]
        assert "access_key" in call_kwargs["argument_spec"]
        assert "private_key" in call_kwargs["argument_spec"]
        
        # Verify CDP config was loaded
        mock_load_cdp_config.assert_called_once()
        
        # Verify attributes are set
        assert module.endpoint == "https://api.cloudera.com"
        assert module.debug_log is False
        assert module.agent_header == "cloudera.cloud"
        assert module.access_key == "test-access-key"
        assert module.private_key == "test-private-key"

    def test_services_module_with_debug_logging(self, mock_ansible_module, mocker):
        """Test ServicesModule initialization with debug logging enabled."""
        
        # Configure debug=True
        mock_ansible_module.return_value.params["debug"] = True
        
        # Mock logging components
        mock_logger = mocker.patch("logging.getLogger")
        mock_string_io = mocker.patch("io.StringIO")
        mock_handler = mocker.patch("logging.StreamHandler")
        mock_formatter = mocker.patch("logging.Formatter")
        
        # Prevent actual execute from running
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Verify debug logging setup
        assert module.debug_log is True
        assert module.log_capture is not None
        mock_string_io.assert_called_once()
        mock_handler.assert_called_once()
        mock_formatter.assert_called_once()

    def test_services_module_get_param(self, mock_ansible_module, mocker):
        """Test the get_param method."""
        
        mock_ansible_module.return_value.params["endpoint"] = "https://api.cloudera.com"

        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Test getting existing parameter
        assert module.get_param("endpoint") == "https://api.cloudera.com"
        
        # Test getting non-existent parameter with default
        assert module.get_param("nonexistent", "default_val") == "default_val"
        
        # Test getting non-existent parameter without default
        assert module.get_param("nonexistent") is None

    @pytest.mark.skip(reason="Module params dictionary is never None")
    def test_services_module_get_param_none_params(self, mock_ansible_module, mocker):
        """Test get_param when module.params is None."""

        mock_ansible_module.return_value.params = {}
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Should return default when params is None
        assert module.get_param("any_param", "default") == "default"
        assert module.get_param("any_param") is None

    def test_services_module_with_mixin(self, mock_ansible_module, mocker):
        """Test ServicesModule with a parameter mixin."""
        
        # Add message parameter to mock params
        mock_ansible_module.return_value.params["message"] = "test message"
        
        mocker.patch.object(ConcreteServicesModuleWithMixin, "execute")
        
        module = ConcreteServicesModuleWithMixin.__new__(ConcreteServicesModuleWithMixin)
        module._process_called = False
        ServicesModule.__init__(module)
        MessageParameter.init_parameters(module)
        
        # Verify mixin argument spec was merged
        call_kwargs = mock_ansible_module.call_args[1]
        assert "message" in call_kwargs["argument_spec"]
        
        # Verify mixin parameters were initialized
        assert hasattr(module, "message")
        assert module.message == "test message"

    def test_services_module_execute_method(self, mock_ansible_module):
        """Test the execute method."""
        
        # Don't patch execute, we want to test it
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Manually call execute
        module.execute()
        
        # Verify process was called
        assert module._process_called is True

    def test_services_module_execute_with_debug_logging(self, mock_ansible_module, mocker):
        """Test execute method captures logging output when debug is enabled."""
        
        # Enable debug logging
        mock_ansible_module.return_value.params["debug"] = True
        
        # Mock StringIO to simulate log output
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = "Test log output\nSecond line"
        mock_string_io = mocker.patch("io.StringIO", return_value=mock_string_io_instance)
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Execute the module
        module.execute()
        
        # Verify logging output was captured
        assert module.log_out == "Test log output\nSecond line"
        assert module.log_lines == ["Test log output", "Second line"]
        mock_string_io_instance.getvalue.assert_called_once()

    def test_services_module_execute_with_empty_log_capture(self, mock_ansible_module, mocker):
        """Test execute method handles empty log capture correctly."""
        
        # Enable debug logging
        mock_ansible_module.return_value.params["debug"] = True
        
        # Mock StringIO to return empty string
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = ""
        mocker.patch("io.StringIO", return_value=mock_string_io_instance)
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Execute the module
        module.execute()
        
        # Verify empty logging output is handled
        assert module.log_out == ""
        assert module.log_lines == []

    def test_services_module_argument_spec_merging(self, mock_ansible_module, mocker):
        """Test that argument specs are properly merged."""
        
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        custom_spec = {"custom_param": dict(required=True, type="str")}
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module, argument_spec=custom_spec)
        
        # Verify both custom and default arguments are present
        call_kwargs = mock_ansible_module.call_args[1]
        arg_spec = call_kwargs["argument_spec"]
        
        # Custom argument
        assert "custom_param" in arg_spec
        assert arg_spec["custom_param"]["required"] is True
        
        # Default arguments
        assert "endpoint" in arg_spec
        assert "access_key" in arg_spec
        assert "debug" in arg_spec

    def test_services_module_auto_execute_integration(self, mock_ansible_module):
        """Test that AutoExecuteMeta calls execute automatically during instantiation."""
        
        # This will create the instance with auto-execute
        module = ConcreteServicesModule()
        
        # Verify that process was called via auto-execute
        assert module._process_called is True

    def test_services_module_ansible_module_options(self, mock_ansible_module, mocker):
        """Test that AnsibleModule is created with correct options."""
        
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        
        # Test with various options
        ServicesModule.__init__(
            module,
            bypass_checks=True,
            no_log=True,
            mutually_exclusive=[["param1", "param2"]],
            required_together=[["param3", "param4"]],
            required_one_of=[["param5", "param6"]],
            supports_check_mode=True,
        )
        
        # Verify options were passed to AnsibleModule
        call_kwargs = mock_ansible_module.call_args[1]
        assert call_kwargs["bypass_checks"] is True
        assert call_kwargs["no_log"] is True
        assert sorted(call_kwargs["mutually_exclusive"]) == sorted([["access_key", "credentials_path"], ["param1", "param2"]])
        assert sorted(call_kwargs["required_together"]) == sorted([["access_key", "private_key"], ["param3", "param4"]])
        assert sorted(call_kwargs["required_one_of"]) == sorted([["access_key", "credentials_path"], ["param5", "param6"]])
        assert call_kwargs["supports_check_mode"] is True

    def test_services_module_no_cdp_config_loading(self, mock_ansible_module, mock_load_cdp_config, mocker):
        """Test CDP configuration loading."""
        
        # Configure specific parameter values
        mock_ansible_module.return_value.params.update({
            "access_key": "param_access_key",
            "private_key": "param_private_key",
            "credentials_path": "/custom/path",
            "profile": "production",
        })
        
        mocker.patch.object(ConcreteServicesModule, "execute")
        
        module = ConcreteServicesModule.__new__(ConcreteServicesModule)
        module._process_called = False
        ServicesModule.__init__(module)
        
        # Verify load_cdp_config was called with correct parameters
        mock_load_cdp_config.assert_not_called()
        
        # Verify credentials were set
        assert module.access_key == "param_access_key"
        assert module.private_key == "param_private_key"
