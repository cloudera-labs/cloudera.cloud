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
      - Mutually exclusive with O(endpoint_region).
    type: str
    required: False
    aliases:
      - endpoint_url
      - url
  endpoint_region:
    description:
      - Specify the Cloudera on cloud API endpoint region.
      - See L(Cloudera Control Plane regions,https://docs.cloudera.com/cdp-public-cloud/cloud/cp-regions/topics/cdp-control-plane-regions.html) for more information.
      - If not provided, the API will attempt to use the value from the environment variable E(CDP_REGION).
      - V(default) is an alias for the V(us-west-1) region.
      - Mutually exclusive with O(endpoint).
    type: str
    required: False
    default: "us-west-1"
    choices:
      - default
      - us-west-1
      - eu-1
      - ap-1
    aliases:
      - cdp_endpoint_region
      - cdp_region
      - region
  endpoint_tls:
    description:
      - Verify the TLS certificates for the Cloudera on cloud API endpoint.
    type: bool
    required: False
    default: True
    aliases:
      - verify_endpoint_tls
      - verify_tls
      - verify_api_tls
  debug:
    description:
      - If C(true), the module will capture the Cloudera on cloud HTTP log and return it in the RV(sdk_out) and RV(sdk_out_lines) fields.
    type: bool
    required: False
    default: False
    aliases:
      - debug_endpoints
  http_agent:
    description:
      - The HTTP user agent to use for Cloudera on cloud API requests.
    type: str
    required: False
    default: "cloudera.cloud"
    aliases:
      - agent_header
  strict:
    description:
      - Legacy CDPy SDK error handling.
    type: bool
    required: False
    default: False
    aliases:
      - strict_errors
"""
