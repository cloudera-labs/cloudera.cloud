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


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  access_key:
    description:
      - If provided, the Cloudera on cloud API will use this value as its access key.
      - If not provided, the API will attempt to use the value from the environment variable E(CDP_ACCESS_KEY_ID).
      - Required if O(private_key) is provided.
      - Mutually exclusive with O(credentials_path).
    type: str
    required: False
  private_key:
    description:
      - If provided, the Cloudera on cloud API will use this value as its private key.
      - If not provided, the API will attempt to use the value from the environment variable E(CDP_PRIVATE_KEY).
      - Required if O(access_key) is provided.
    type: str
    required: False
  credentials_path:
    description:
      - If provided, the Cloudera on cloud API will use this value as its credentials path.
      - If not provided, the API will attempt to use the value from the environment variable E(CDP_CREDENTIALS_PATH).
    type: str
    required: False
    default: "~/.cdp/credentials"
  profile:
    description:
      - If provided, the Cloudera on cloud API will use this value as its profile.
      - If not provided, the API will attempt to use the value from the environment variable E(CDP_PROFILE).
    type: str
    required: False
    default: "default"
  endpoint:
    description:
      - The Cloudera on cloud API endpoint to use.
    type: str
    required: True
    aliases:
      - url
  debug:
    description:
      - If C(true), the module will capture the Cloudera on cloud HTTP log and return it in the RV(sdk_out) and RV(sdk_out_lines) fields.
    type: bool
    required: False
    default: False
  http_agent:
    description:
      - The HTTP user agent to use for Cloudera on cloud API requests.
    type: str
    required: False
    default: "cloudera.cloud"
"""
