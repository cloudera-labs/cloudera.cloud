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

from dataclasses import asdict, is_dataclass
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.parameters import env_fallback

from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_client import (
    load_cdp_config,
    AnsibleCdpClient,
    CdpCredentialError,
)


LOG_FORMAT = "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"


T = TypeVar("T")


NULLABLE = object  # Sentinel value to allow explicit None values in to_dict()


def from_dict(cls: Type[T], data: Any) -> T:
    """
    Recursively loads a dict into a dataclass
    """

    def _from_dict_recursive(current_cls: Type[Any], current_data: Any) -> Any:
        if current_data is None:
            return None

        origin = get_origin(current_cls)

        if origin is Union:
            # If a Union, check each type in the Union
            for union_arg in get_args(current_cls):
                # Ignore NoneType
                if union_arg is type(None):
                    continue

                # Process only dataclasses (not instances) and Lists
                if isinstance(union_arg, type) and (
                    is_dataclass(union_arg) or get_origin(union_arg) in (list, List)
                ):
                    # If Union contains a dataclass or List, parse accordingly
                    return _from_dict_recursive(union_arg, current_data)
            # If a Union of primitives, return data as-is
            return current_data

        if origin is list or origin is List:
            # If a list, get the item type and parse each item
            item_type = get_args(current_cls)[0]
            if isinstance(current_data, list):
                return [_from_dict_recursive(item_type, item) for item in current_data]
            return []  # or raise error if data isn't a list

        if is_dataclass(current_cls) and isinstance(current_data, dict):
            # Get type hints for all fields in this specific dataclass
            type_hints = get_type_hints(current_cls)

            return current_cls(
                **{
                    field: _from_dict_recursive(
                        type_hints[field],
                        current_data.get(field),
                    )
                    for field in current_data
                    if field in type_hints
                },
            )

        if isinstance(current_data, dict):
            # If a dict, parse each value, assuming keys are strings
            value_cls = get_args(current_cls)[1]
            return {
                k: _from_dict_recursive(value_cls, v) for k, v in current_data.items()
            }

        # Return primitives (int, str, bool)
        return current_data

    return _from_dict_recursive(cls, data)


def to_dict(instance: Any) -> Dict[str, Any]:
    """
    Recursively convert a dataclass instance to a dictionary, skipping default NULLABLE values.
    NoneType values are included in the dictionary.

    Args:
        instance: The dataclass instance to convert.
    """

    def _skip_none_factory(data):
        return {k: v for k, v in data if v is not NULLABLE}

    if is_dataclass(instance) and not isinstance(instance, type):
        return asdict(instance, dict_factory=_skip_none_factory)

    raise TypeError(f"Expected dataclass type, got {type(instance)}")


def diff_dict(
    prev: Any,
    next: Any,
    filter_nullable: bool = True,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Compare two dataclass instances and return their differences.

    Recursively compares two dataclass instances field by field and returns
    a tuple of dictionaries containing the old and new values for fields that differ.
    Supports nested dataclasses, lists, and primitive types.

    Args:
        prev: The previous dataclass instance to compare from.
        next: The next dataclass instance to compare to.
        filter_nullable: If True, exclude fields with NULLABLE sentinel values from comparison.
            Defaults to True.

    Returns:
        A tuple of two dictionaries (old_values, new_values) containing only the fields
        that differ between the instances. Nested differences are represented as nested
        dictionaries. Empty dictionaries are returned if instances are identical.

    Raises:
        TypeError: If instances are not dataclasses or are of different types.

    Example:
        >>> @dataclass
        ... class Person:
        ...     name: str
        ...     age: int
        >>> old = Person(name="Alice", age=30)
        >>> new = Person(name="Alice", age=31)
        >>> old_diff, new_diff = diff_dict(old, new)
        >>> print(old_diff)
        {'age': 30}
        >>> print(new_diff)
        {'age': 31}
    """

    def _diff_recursive(prev_val: Any, new_val: Any) -> Tuple[Any, Any, bool]:
        """
        Recursively compare values and return (prev_val, new_val, has_diff).

        Returns:
            Tuple of (prev_value, new_value, has_difference)
        """
        # Handle NULLABLE filtering
        if filter_nullable:
            if prev_val is NULLABLE and new_val is NULLABLE:
                return None, None, False
            if prev_val is NULLABLE:
                prev_val = None
            if new_val is NULLABLE:
                new_val = None

        # If both are None, no difference
        if prev_val is None and new_val is None:
            return None, None, False

        # If one is None and the other isn't, there's a difference
        if prev_val is None or new_val is None:
            # Convert dataclass instances to dicts for consistency
            prev_result = (
                to_dict(prev_val)
                if is_dataclass(prev_val) and not isinstance(prev_val, type)
                else prev_val
            )
            new_result = (
                to_dict(new_val)
                if is_dataclass(new_val) and not isinstance(new_val, type)
                else new_val
            )
            return prev_result, new_result, True

        # If both are dataclasses, recursively compare fields
        if is_dataclass(prev_val) and is_dataclass(new_val):
            if type(prev_val) != type(new_val):
                # Different types, convert both to dicts
                prev_result = (
                    to_dict(prev_val) if not isinstance(prev_val, type) else prev_val
                )
                new_result = (
                    to_dict(new_val) if not isinstance(new_val, type) else new_val
                )
                return prev_result, new_result, True

            old_dict = {}
            new_dict = {}
            has_diff = False

            type_hints = get_type_hints(type(prev_val))
            for field_name in type_hints:
                old_field = getattr(prev_val, field_name, NULLABLE)
                new_field = getattr(new_val, field_name, NULLABLE)

                old_result, new_result, field_diff = _diff_recursive(
                    old_field,
                    new_field,
                )

                if field_diff:
                    old_dict[field_name] = old_result
                    new_dict[field_name] = new_result
                    has_diff = True

            if has_diff:
                return old_dict, new_dict, True
            return {}, {}, False

        # If both are lists, compare element by element
        if isinstance(prev_val, list) and isinstance(new_val, list):
            if len(prev_val) != len(new_val):
                # Convert any dataclass instances in the lists to dicts
                prev_result = [
                    (
                        to_dict(item)
                        if is_dataclass(item) and not isinstance(item, type)
                        else item
                    )
                    for item in prev_val
                ]
                new_result = [
                    (
                        to_dict(item)
                        if is_dataclass(item) and not isinstance(item, type)
                        else item
                    )
                    for item in new_val
                ]
                return prev_result, new_result, True

            old_list = []
            new_list = []
            has_diff = False

            for old_item, new_item in zip(prev_val, new_val):
                old_result, new_result, item_diff = _diff_recursive(
                    old_item,
                    new_item,
                )
                if item_diff:
                    old_list.append(old_result)
                    new_list.append(new_result)
                    has_diff = True
                else:
                    # Include unchanged items to maintain list structure
                    # Convert dataclass instances to dicts for consistency
                    old_item_result = (
                        to_dict(old_item)
                        if is_dataclass(old_item) and not isinstance(old_item, type)
                        else old_item
                    )
                    new_item_result = (
                        to_dict(new_item)
                        if is_dataclass(new_item) and not isinstance(new_item, type)
                        else new_item
                    )
                    old_list.append(old_item_result)
                    new_list.append(new_item_result)

            if has_diff:
                return old_list, new_list, True
            return [], [], False

        # If both are dicts, compare key by key
        if isinstance(prev_val, dict) and isinstance(new_val, dict):
            old_dict = {}
            new_dict = {}
            has_diff = False

            all_keys = set(prev_val.keys()) | set(new_val.keys())
            for key in all_keys:
                old_item = prev_val.get(key, None)
                new_item = new_val.get(key, None)

                old_result, new_result, item_diff = _diff_recursive(
                    old_item,
                    new_item,
                )

                if item_diff:
                    old_dict[key] = old_result
                    new_dict[key] = new_result
                    has_diff = True

            if has_diff:
                return old_dict, new_dict, True
            return {}, {}, False

        # For primitives and other types, direct comparison
        if prev_val != new_val:
            return prev_val, new_val, True

        return prev_val, new_val, False

    # Validate inputs
    if not is_dataclass(prev) or isinstance(prev, type):
        raise TypeError(
            f"Expected dataclass instance for prev, got {type(prev)}",
        )

    if not is_dataclass(next) or isinstance(next, type):
        raise TypeError(
            f"Expected dataclass instance for next, got {type(next)}",
        )

    if type(prev) != type(next):
        raise TypeError(
            f"Cannot compare different dataclass types: {type(prev)} vs {type(next)}",
        )

    prev_diff, next_diff, _ = _diff_recursive(prev, next)

    return prev_diff if isinstance(prev_diff, dict) else {}, (
        next_diff
        if isinstance(
            next_diff,
            dict,
        )
        else {}
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
        client_class=None,
    ):
        """
        Initializes the base Cloudera on cloud service module.

        Args:
            client_class: Optional API client class to use (defaults to AnsibleCdpClient).
                          Must be a subclass of CdpClient. Used by service-specific modules
                          that need specialized client behavior (e.g., DataFlow with 308 redirects).
        """
        super().__init__()

        # Store client class for later instantiation (defaults to AnsibleCdpClient)
        self._client_class = (
            client_class if client_class is not None else AnsibleCdpClient
        )

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
                    fallback=(env_fallback, ["CDP_ENDPOINT_URL"]),
                ),
                endpoint_region=dict(
                    required=False,
                    type="str",
                    fallback=(env_fallback, ["CDP_REGION"]),
                    default="us-west-1",
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

        # Create the CDP client using the configured client class
        self.api_client = self._client_class(
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
