#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Cloudera, Inc. All Rights Reserved.
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
A common Ansible Module for shared functions in the Cloudera CDP Collection
"""

from functools import wraps

from cdpy.cdpy import Cdpy
from cdpy.common import CdpError, CdpWarning


__credits__ = ["cleroy@cloudera.com"]
__maintainer__ = [
    "dchaffelson@cloudera.com",
    "wmudge@cloudera.com"
]


class CdpModule(object):
    """A base CDP module class for common parameters, fields, and methods."""
    class _Decorators(object):
        @classmethod
        def process_debug(cls, f):
            @wraps(f)
            def _impl(self, *args, **kwargs):
                result = f(self, *args, **kwargs)
                if self.debug:
                    self.log_out = self.cdpy.sdk.get_log()
                    self.log_lines.append(self.log_out.splitlines())
                return result

            return _impl

    def __init__(self, module):
        # Set common parameters
        self.module = module
        self.tls = self._get_param('verify_tls', False)
        self.debug = self._get_param('debug', False)
        self.strict = self._get_param('strict', False)

        # Initialize common return values
        self.log_out = None
        self.log_lines = []
        self.changed = False

        # Client Wrapper
        self.cdpy = Cdpy(debug=self.debug, tls_verify=self.tls, strict_errors=self.strict,
                         error_handler=self._cdp_module_throw_error, warning_handler=self._cdp_module_throw_warning)

    # Private functions

    def _get_param(self, param, default=None):
        """Fetches an Ansible Input Parameter if it exists, else returns optional default or None"""
        if self.module is not None:
            return self.module.params[param] if param in self.module.params else default
        return default

    def _cdp_module_throw_error(self, error: 'CdpError'):
        """Error handler for CDPy SDK"""
        self.module.fail_json(msg=str(error.message), error=str(error.__dict__), violations=error.violations)

    def _cdp_module_throw_warning(self, warning: 'CdpWarning'):
        """Warning handler for CDPy SDK"""
        if self.module._debug or self.module._verbosity >= 2:
            self.module.warn(warning.message)

    @staticmethod
    def argument_spec(**spec):
        """Default Ansible Module spec values for convenience"""
        return dict(
            **spec,
            verify_tls=dict(required=False, type='bool', default=True, aliases=['tls']),
            debug=dict(required=False, type='bool', default=False, aliases=['debug_endpoints']),
            strict=dict(required=False, type='bool', default=False, aliases=['strict_errors']),
        )
