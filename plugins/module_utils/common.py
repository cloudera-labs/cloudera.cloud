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

"""
Shared functions for Cloudera on cloud Ansible modules
"""

import abc
import io
import logging

from typing import Any, Dict, Optional

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.parameters import env_fallback

LOG_FORMAT = "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"


class ParametersMixin(abc.ABC):
    """Abstract base class for parameter mixins."""

    @staticmethod
    @abc.abstractmethod
    def get_argument_spec() -> Dict[str, Dict[str, Any]]:
        """Returns the argument spec for the parameter(s)."""
        pass

    @abc.abstractmethod
    def init_parameters(self) -> None:
        """Initialize the parameter value(s)."""
        pass


class MessageParameter(ParametersMixin):
    """Mixin class to add a 'message' parameter to the argument_spec."""

    @staticmethod
    def get_argument_spec() -> Dict[str, Dict[str, Any]]:
        """Returns the argument spec for the message parameter."""
        return {
            "message": dict(required=False, type="str", default=None)
        }

    def init_parameters(self) -> None:
        """Initialize the message parameter value."""
        self.message: Optional[str] = self.get_param("message")  # type: ignore[attr-defined]


class AutoExecuteMeta(abc.ABCMeta):
    """Metaclass that automatically calls execute() after all __init__ methods complete."""

    def __call__(cls, *args, **kwargs):
        # Create the instance normally
        instance = super().__call__(*args, **kwargs)

        # After all __init__ methods have completed, call execute()
        if hasattr(instance, "execute") and callable(instance.execute):
            instance.execute()

        return instance


class ServicesModule(abc.ABC, metaclass=AutoExecuteMeta):
    """Base class for Cloudera on cloud Ansible modules"""

    def __init__(
        self,
        argument_spec={},
        bypass_checks=False,
        no_log=False,
        mutually_exclusive=[],
        required_together=[],
        required_one_of=[],
        add_file_common_args=False,
        supports_check_mode=False,
        required_if=None,
        required_by=None,
    ):
        """Initializes the base Cloudera on cloud service module"""
        super().__init__()

        # Merge in mixin argument specs
        merged_argument_spec = dict(argument_spec)
        for base in self.__class__.__mro__:
            if hasattr(base, "get_argument_spec") and base != ServicesModule:
                mixin_spec = base.get_argument_spec()
                if mixin_spec:
                    merged_argument_spec.update(mixin_spec)

        # Initialize the Ansible module
        self.module = AnsibleModule(
            argument_spec=dict(
                **merged_argument_spec,
                endpoint=dict(required=True, type="str", aliases=["url"]),
                debug=dict(required=False, type="bool", default=False),
                agent_header=dict(
                    required=False,
                    type="str",
                    default="cloudera.cloud",
                ),
            ),
            required_together=required_together,
            bypass_checks=bypass_checks,
            no_log=no_log,
            mutually_exclusive=mutually_exclusive,
            required_one_of=required_one_of,
            add_file_common_args=add_file_common_args,
            supports_check_mode=supports_check_mode,
            required_if=required_if,
            required_by=required_by,
        )

        # Initialize common parameters
        self.endpoint: str = self.get_param("endpoint")
        self.debug_log = self.get_param("debug")
        self.agent_header = self.get_param("agent_header")

        # Initialize mixins parameters
        for base in self.__class__.__mro__:
            if isinstance(base, type) and issubclass(base, ParametersMixin) and base != ParametersMixin:
                base.init_parameters(self)  # type: ignore[misc]

        # Configure the urllib3 logger
        self.logger = logging.getLogger("cloudera.cloud")

        # Initialize logging properties
        self.log_out: str = ""
        self.log_lines: list[str] = []
        self.log_capture = None

        # If debug is enabled, set up logging capture to return in the module output
        if self.debug_log:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.propagate = True

            self.log_capture = io.StringIO()
            handler = logging.StreamHandler(self.log_capture)

            formatter = logging.Formatter(LOG_FORMAT)
            handler.setFormatter(formatter)

            root_logger.addHandler(handler)

        self.logger.debug("cloudera.cloud API agent: %s", self.agent_header)

    def get_param(self, param, default=None) -> Any:
        if self.module.params is not None and isinstance(self.module.params, dict):
            return self.module.params.get(param, default)
        return default

    @abc.abstractmethod
    def process(self):
        """Abstract method that Service modules must implement to perform their logic."""
        pass

    def execute(self):
        """Execute the process method and capture logging output."""
        try:
            # Call the abstract process method
            self.process()
        finally:
            # Capture logging output if debug is enabled and the capture is not empty
            if self.debug_log and self.log_capture:
                captured = self.log_capture.getvalue()
                self.log_out = captured if captured else ""
                self.log_lines = self.log_out.splitlines() if self.log_out else []
