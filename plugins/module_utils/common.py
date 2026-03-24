# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
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

from typing import Any, Dict, List, Optional, Tuple, Union

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.parameters import env_fallback

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    load_cdp_config,
    AnsibleCdpClient,
    CdpCredentialError,
)


LOG_FORMAT = "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"


def diff_dict(
    prev: Optional[Dict[str, Any]],
    next: Optional[Dict[str, Any]],
    exclude_keys: Optional[List[str]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Compare two dictionaries and return their differences.

    Recursively compares two dictionaries field by field and returns
    a tuple of dictionaries containing the old and new values for fields that differ.
    Supports nested dictionaries, lists, and primitive types.

    Args:
        prev: The previous dictionary to compare from (can be None).
        next: The next dictionary to compare to (can be None).
        exclude_keys: Optional list of keys to exclude from comparison (e.g., read-only fields).

    Returns:
        A tuple of two dictionaries (old_values, new_values) containing only the fields
        that differ between the dictionaries. Nested differences are represented as nested
        dictionaries. Empty dictionaries are returned if dictionaries are identical.

    Example:
        >>> old = {"name": "Alice", "age": 30, "city": "NYC"}
        >>> new = {"name": "Alice", "age": 31, "city": "NYC"}
        >>> old_diff, new_diff = diff_dict(old, new)
        >>> print(old_diff)
        {'age': 30}
        >>> print(new_diff)
        {'age': 31}
    """
    exclude_keys = exclude_keys or []

    def _diff_recursive(prev_val: Any, new_val: Any) -> Tuple[Any, Any, bool]:
        """
        Recursively compare values and return (prev_val, new_val, has_diff).

        Returns:
            Tuple of (prev_value, new_value, has_difference)
        """
        # If both are None, no difference
        if prev_val is None and new_val is None:
            return None, None, False

        # If one is None and the other isn't, there's a difference
        if prev_val is None or new_val is None:
            return prev_val, new_val, True

        # If both are dictionaries, compare key by key
        if isinstance(prev_val, dict) and isinstance(new_val, dict):
            prev_diff = {}
            new_diff = {}
            has_diff = False

            # Get all unique keys from both dictionaries
            all_keys = set(prev_val.keys()) | set(new_val.keys())

            for key in all_keys:
                # Skip excluded keys
                if key in exclude_keys:
                    continue

                prev_item = prev_val.get(key)
                new_item = new_val.get(key)

                prev_item_diff, new_item_diff, item_has_diff = _diff_recursive(
                    prev_item,
                    new_item,
                )

                if item_has_diff:
                    prev_diff[key] = prev_item_diff
                    new_diff[key] = new_item_diff
                    has_diff = True

            return prev_diff, new_diff, has_diff

        # If both are lists, compare element by element
        if isinstance(prev_val, list) and isinstance(new_val, list):
            # For lists, we'll do a simple equality check
            # More sophisticated list comparison can be added if needed
            if len(prev_val) != len(new_val):
                return prev_val, new_val, True

            # Check if lists have different elements (order-independent for simplicity)
            prev_set = set(str(x) for x in prev_val)
            new_set = set(str(x) for x in new_val)

            if prev_set != new_set:
                return prev_val, new_val, True

            return None, None, False

        # For primitives and other types, direct comparison
        if prev_val != new_val:
            return prev_val, new_val, True

        return None, None, False

    # Handle None inputs
    if prev is None and next is None:
        return {}, {}

    if prev is None:
        return {}, next

    if next is None:
        return prev, {}

    prev_diff, next_diff, _ = _diff_recursive(prev, next)

    return (
        prev_diff if isinstance(prev_diff, dict) else {},
        next_diff if isinstance(next_diff, dict) else {},
    )


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
            "message": dict(required=False, type="str", default=None),
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
        argument_spec: Dict[str, Dict[str, Any]] = {},
        bypass_checks: bool = False,
        no_log: bool = False,
        mutually_exclusive: Union[List[str], List[List[str]]] = [],
        required_together: List[List[str]] = [],
        required_one_of: List[List[str]] = [],
        add_file_common_args: bool = False,
        supports_check_mode: bool = False,
        required_if: List[List[Any]] = [],
        required_by: Dict[str, List[str]] = {},
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
        # TODO Add CDP_ACCESS_TOKEN
        self.module = AnsibleModule(
            argument_spec=dict(
                **merged_argument_spec,
                access_key=dict(
                    required=False,
                    type="str",
                    fallback=(env_fallback, ["CDP_ACCESS_KEY_ID"]),
                ),
                private_key=dict(
                    required=False,
                    type="str",
                    no_log=True,
                    fallback=(env_fallback, ["CDP_PRIVATE_KEY"]),
                ),
                credentials_path=dict(
                    required=False,
                    type="str",
                    fallback=(env_fallback, ["CDP_CREDENTIALS_PATH"]),
                    default="~/.cdp/credentials",
                ),
                profile=dict(
                    required=False,
                    type="str",
                    fallback=(env_fallback, ["CDP_PROFILE"]),
                    default="default",
                ),
                endpoint=dict(
                    required=False,
                    type="str",
                    aliases=["endpoint_url", "url"],
                ),
                endpoint_region=dict(
                    required=False,
                    type="str",
                    fallback=(env_fallback, ["CDP_REGION"]),
                    # default="us-west-1", # NOTE: Handled by load_cdp_region()
                    aliases=["cdp_endpoint_region", "cdp_region", "region"],
                    choices=["default", "us-west-1", "eu-1", "ap-1"],
                ),
                endpoint_tls=dict(
                    required=False,
                    type="bool",
                    default=True,
                    aliases=["verify_endpoint_tls", "verify_tls", "verify_api_tls"],
                ),
                debug=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["debug_endpoints"],
                ),
                http_agent=dict(
                    required=False,
                    type="str",
                    default="cloudera.cloud",
                    aliases=["agent_header"],
                ),
            ),
            required_together=required_together + [["access_key", "private_key"]],
            bypass_checks=bypass_checks,
            no_log=no_log,
            mutually_exclusive=mutually_exclusive
            + [
                ["access_key", "credentials_path"],
                ["endpoint", "endpoint_region"],
            ],
            required_one_of=required_one_of,
            add_file_common_args=add_file_common_args,
            supports_check_mode=supports_check_mode,
            required_if=required_if,
            required_by=required_by,
        )

        # Initialize common parameters
        self.endpoint: str = self.get_param("endpoint")
        self.debug_log: bool = self.get_param("debug")

        # Load CDP credentials - check if provided via parameters first
        access_key = self.get_param("access_key")
        private_key = self.get_param("private_key")
        region = self.get_param("endpoint_region")

        # If any credential is missing, load from credentials file
        if access_key is None or private_key is None or region is None:
            try:
                credentials_path = self.get_param("credentials_path")
                profile = self.get_param("profile")

                self.module.debug(
                    f"Loading CDP credentials from file: {credentials_path}, profile: {profile}",
                )

                file_access_key, file_private_key, file_region = load_cdp_config(
                    credentials_path=self.get_param("credentials_path"),
                    profile=self.get_param("profile"),
                )
            except CdpCredentialError as e:
                self.module.fail_json(
                    msg=f"access key, private_key, or region not provided and failed to load credentials from file: {str(e)}",
                )
            # Use file credentials for any missing parameters
            if access_key is None:
                access_key = file_access_key
            if private_key is None:
                private_key = file_private_key
            if region is None:
                region = file_region

        self.access_key: str = access_key
        self.private_key: str = private_key

        # Handle legacy parameter value
        if region == "default":
            self.endpoint_region = "us-west-1"
        else:
            self.endpoint_region: str = region

        # NOTE: If endpoint is not provided, construct the endpoint parameter from the region
        if self.endpoint is None:
            self.endpoint = f"https://api.{self.endpoint_region}.cdp.cloudera.com"

        # Initialize mixins parameters
        for base in self.__class__.__mro__:
            if (
                isinstance(base, type)
                and issubclass(base, ParametersMixin)
                and base != ParametersMixin
            ):
                base.init_parameters(self)  # type: ignore[misc]

        # Configure the urllib3 logger
        self.logger = logging.getLogger("cloudera.cloud")

        # Initialize logging properties
        self.log_out: str = ""
        self.log_lines: List[str] = []
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

        self.logger.debug("cloudera.cloud API agent: %s", self.get_param("http_agent"))

        # Create the CDP client
        self.api_client = AnsibleCdpClient(
            module=self.module,
            base_url=self.endpoint,
            access_key=self.access_key,
            private_key=self.private_key,
        )

    def get_param(self, param, default=None) -> Any:
        if self.module.params is not None and isinstance(self.module.params, dict):
            return self.module.params.get(param, default)
        return default

    @abc.abstractmethod
    def process(self) -> None:
        """Abstract method that Service modules must implement to perform their logic."""
        pass

    def execute(self) -> None:
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
