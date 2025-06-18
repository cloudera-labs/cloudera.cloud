# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc.
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

import re

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_text, to_native
from ansible.utils.display import Display

from cdpy.cdpy import Cdpy

display = Display()
SEMVER = re.compile("(\d+\.[.\d]*\d+)")


def parse_services(
    terms: list, name: str, entity: dict, service: str, knox: bool, default: any
):
    lookup = "knoxService" if knox else "serviceName"
    results = []
    try:
        for term in LookupBase._flatten(terms):
            display.vvv(
                "%s_service lookup connecting to '%s[%s]'" % (service, name, term)
            )
            services = [
                s
                for s in entity["endpoints"]["endpoints"]
                if s[lookup] == term and "serviceUrl" in s
            ]
            if services:
                results.append([to_text(s["serviceUrl"]) for s in services])
            else:
                results.append(default)
        return results
    except KeyError as e:
        raise AnsibleError("Error parsing result for '%s':'" % name, to_native(e))


def parse_environment(environment: str):
    env = Cdpy().datalake.describe_all_datalakes(environment)

    if not env:
        raise AnsibleError("No Datalake found for Environment '%s'" % environment)
    elif len(env) > 1:
        raise AnsibleError("Multiple Datalakes found for Enviroment '%s'" % environment)

    raw_version = env[0]["productVersions"][0]["version"]

    match = SEMVER.match(raw_version)
    if not match:
        raise AnsibleError(
            "Unable to parse runtime version for Environment '%s': %s"
            % (environment, raw_version)
        )

    return env[0]["cloudPlatform"], raw_version, match.group(0)
