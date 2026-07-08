#!/usr/bin/python
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

DOCUMENTATION = r"""
module: de
short_description: Enable, disable or update CDP Data Engineering Services
description:
  - Enable, disable or update CDP Data Engineering Services.
author:
  - "Curtis Howard (@curtishoward)"
  - "Alan Silva (@acsjumpi)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.5.0"
options:
  name:
    description:
      - The name of the CDE Service.
    type: str
    required: True
  environment:
    description:
      - The CDP environment name where the CDE service should be enabled.
    type: str
    required: True
    aliases:
      - env
  instance_type:
    description:
      - Instance type of the cluster for the CDE Service.
      - For example, C(m5.2xlarge) for AWS or C(Standard_D8s_v3) for Azure.
      - Required when O(state=present) and the service does not yet exist.
    type: str
    required: False
  minimum_instances:
    description:
      - Minimum number of instances for the CDE Service.
    type: int
    required: False
    default: 1
  maximum_instances:
    description:
      - Maximum number of instances for the CDE Service.
    type: int
    required: False
    default: 4
  minimum_spot_instances:
    description:
      - Minimum number of spot instances for the CDE Service.
    type: int
    required: False
    default: 0
  maximum_spot_instances:
    description:
      - Maximum number of spot instances for the CDE Service.
    type: int
    required: False
    default: 0
  all_purpose_minimum_instances:
    description:
      - Minimum number of instances for the All Purpose Instance Group.
      - Applicable to services with the All Purpose (ALLP) virtual cluster tier.
    type: int
    required: False
  all_purpose_maximum_instances:
    description:
      - Maximum number of instances for the All Purpose Instance Group.
      - Applicable to services with the All Purpose (ALLP) virtual cluster tier.
    type: int
    required: False
  all_purpose_minimum_spot_instances:
    description:
      - Minimum number of spot instances for the All Purpose Instance Group.
      - Applicable to services with the All Purpose (ALLP) virtual cluster tier.
    type: int
    required: False
  all_purpose_maximum_spot_instances:
    description:
      - Maximum number of spot instances for the All Purpose Instance Group.
      - Applicable to services with the All Purpose (ALLP) virtual cluster tier.
    type: int
    required: False
  chart_value_overrides:
    description:
      - Chart overrides for enabling a service.
    type: list
    elements: dict
    required: False
    suboptions:
      chart_name:
        description:
          - The key-value pair for the chart override.
        type: str
        required: False
  enable_public_endpoint:
    description:
      - Creates a CDE endpoint (Load Balancer) in a publicly accessible subnet.
    type: bool
    required: False
    default: True
  enable_private_network:
    description:
      - Create a fully private CDE instance.
    type: bool
    required: False
    default: False
  loadbalancer_ips:
    description:
      - List of CIDRs allowed to access the load balancer.
    type: list
    elements: str
    required: False
  enable_workload_analytics:
    description:
      - If set to False, diagnostic information about job and query execution
        is not sent to Cloudera Workload Manager.
    type: bool
    required: False
    default: True
  initial_instances:
    description:
      - Initial number of instances when the service is enabled.
    type: int
    required: False
    default: 1
  initial_spot_instances:
    description:
      - Initial number of spot instances when the service is enabled.
    type: int
    required: False
    default: 0
  root_volume_size:
    description:
      - EBS volume size in GB.
    type: int
    required: False
    default: 100
  resource_pool:
    description:
      - Resource Pool for the CDE service.
      - Applicable to I(Private Cloud) deployments only.
    type: str
    required: False
  cpu_requests:
    description:
      - Service wide CPU resource request quota.
      - Applicable to I(Private Cloud) deployments only.
    type: str
    required: False
  memory_requests:
    description:
      - Service wide memory resource request quota.
      - Applicable to I(Private Cloud) deployments only.
    type: str
    required: False
  gpu_requests:
    description:
      - Service wide GPU resource request quota.
      - Applicable to I(Private Cloud) deployments only.
    type: str
    required: False
  skip_validation:
    description:
      - Skip validation check.
    type: bool
    required: False
    default: False
  tags:
    description:
      - User defined labels that tag all provisioned cloud resources.
      - Specified as a dictionary of key-value string pairs.
    type: dict
    required: False
  use_ssd:
    description:
      - Instance local storage (SSD) would be used for the workload filesystem.
      - Currently supported only for AWS services.
    type: bool
    required: False
  whitelist_ips:
    description:
      - List of CIDRs that would be allowed to access the Kubernetes master API server.
    type: list
    elements: str
    required: False
  force:
    description:
      - Flag to force delete a service even if errors occur during deletion.
    type: bool
    required: False
    default: False
    aliases:
      - force_delete
  state:
    description:
      - The declarative state of the CDE service.
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  wait:
    description:
      - Flag to enable internal polling to wait for the DE Service to achieve the declared state.
      - If set to False, the module will return immediately after initiating the operation.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the
        DE Service to achieve the declared state.
    type: int
    required: False
    default: 60
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the
        DE Service to achieve the declared state.
    type: int
    required: False
    default: 7200
    aliases:
      - polling_timeout
notes:
  - "When updating an existing service, only the following parameters can be changed:
    minimum_instances, maximum_instances, minimum_spot_instances, maximum_spot_instances,
    all_purpose_minimum_instances, all_purpose_maximum_instances,
    all_purpose_minimum_spot_instances, all_purpose_maximum_spot_instances,
    whitelist_ips, loadbalancer_ips."
  - Immutable parameters (instance_type, network settings, etc.) cannot be changed after creation.
    To change them, disable and recreate the service.
extends_documentation_fragment:
  - cloudera.cloud.cdp_client
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

# Enable a CDE service and wait for it to become active
- cloudera.cloud.de:
    name: my-cde-service
    environment: my-cdp-environment
    instance_type: m5.2xlarge
    minimum_instances: 1
    maximum_instances: 4
    state: present
    wait: true

# Enable a CDE service with additional options
- cloudera.cloud.de:
    name: my-cde-service
    environment: my-cdp-environment
    instance_type: m5.2xlarge
    minimum_instances: 2
    maximum_instances: 8
    enable_public_endpoint: true
    enable_workload_analytics: false
    tags:
      team: data-engineering
      cost-center: "12345"
    state: present
    wait: true

# Disable a CDE service without waiting
- cloudera.cloud.de:
    name: my-cde-service
    environment: my-cdp-environment
    state: absent
    wait: false

# Force disable a CDE service
- cloudera.cloud.de:
    name: my-cde-service
    environment: my-cdp-environment
    force: true
    state: absent
    wait: true
"""

RETURN = r"""
service:
  description: Description of the CDE Service.
  type: dict
  returned: always
  contains:
    clusterId:
      description: Cluster ID of the CDE Service.
      returned: always
      type: str
    name:
      description: Name of the CDE Service.
      returned: always
      type: str
    status:
      description: Status of the CDE Service.
      returned: always
      type: str
    environmentName:
      description: CDP Environment Name.
      returned: always
      type: str
    environmentCrn:
      description: CRN of the environment.
      returned: always
      type: str
    cloudPlatform:
      description: The cloud platform where the CDE service is enabled.
      returned: always
      type: str
    clusterFqdn:
      description: FQDN of the CDE service.
      returned: always
      type: str
    creatorEmail:
      description: Email address of the CDE creator.
      returned: always
      type: str
    creatorCrn:
      description: CRN of the creator.
      returned: always
      type: str
    enablingTime:
      description: Timestamp of service enabling.
      returned: always
      type: str
    resources:
      description: Resource details of the CDE Service.
      returned: always
      type: dict
      contains:
        instance_type:
          description: Instance type of the CDE service.
          type: str
        min_instances:
          description: Minimum instances for the CDE service.
          type: str
        max_instances:
          description: Maximum instances for the CDE service.
          type: str
        min_spot_instances:
          description: Minimum number of spot instances.
          type: str
        max_spot_instances:
          description: Maximum number of spot instances.
          type: str
        initial_instances:
          description: Initial instances for the CDE service.
          type: str
        initial_spot_instances:
          description: Initial spot instances for the CDE service.
          type: str
        root_vol_size:
          description: Root volume size in GB.
          type: str
    tenantId:
      description: CDP tenant ID.
      returned: always
      type: str
    logLocation:
      description: Location for the log files of jobs.
      returned: always
      type: str
sdk_out:
  description: Returns the captured CDP SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CDP SDK log.
  returned: when supported
  type: list
  elements: str
"""

from typing import Optional

from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_de import (
    CdpDeClient,
    check_service_updates,
)


class DEService(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(required=True, type="str"),
                environment=dict(required=True, type="str", aliases=["env"]),
                instance_type=dict(required=False, type="str"),
                minimum_instances=dict(required=False, type="int", default=1),
                maximum_instances=dict(required=False, type="int", default=4),
                minimum_spot_instances=dict(required=False, type="int", default=0),
                maximum_spot_instances=dict(required=False, type="int", default=0),
                all_purpose_minimum_instances=dict(
                    required=False,
                    type="int",
                    default=None,
                ),
                all_purpose_maximum_instances=dict(
                    required=False,
                    type="int",
                    default=None,
                ),
                all_purpose_minimum_spot_instances=dict(
                    required=False,
                    type="int",
                    default=None,
                ),
                all_purpose_maximum_spot_instances=dict(
                    required=False,
                    type="int",
                    default=None,
                ),
                chart_value_overrides=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    default=None,
                    options=dict(
                        chart_name=dict(required=False, type="str"),
                    ),
                ),
                enable_public_endpoint=dict(
                    required=False,
                    type="bool",
                    default=True,
                ),
                enable_private_network=dict(
                    required=False,
                    type="bool",
                    default=False,
                ),
                loadbalancer_ips=dict(
                    required=False,
                    type="list",
                    elements="str",
                    default=None,
                ),
                enable_workload_analytics=dict(
                    required=False,
                    type="bool",
                    default=True,
                ),
                initial_instances=dict(required=False, type="int", default=1),
                initial_spot_instances=dict(required=False, type="int", default=0),
                root_volume_size=dict(required=False, type="int", default=100),
                resource_pool=dict(required=False, type="str"),
                cpu_requests=dict(required=False, type="str"),
                memory_requests=dict(required=False, type="str"),
                gpu_requests=dict(required=False, type="str"),
                skip_validation=dict(required=False, type="bool", default=False),
                tags=dict(required=False, type="dict", default=None),
                use_ssd=dict(required=False, type="bool", default=None),
                whitelist_ips=dict(
                    required=False,
                    type="list",
                    elements="str",
                    default=None,
                ),
                force=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["force_delete"],
                ),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                wait=dict(required=False, type="bool", default=True),
                delay=dict(
                    required=False,
                    type="int",
                    aliases=["polling_delay"],
                    default=60,
                ),
                timeout=dict(
                    required=False,
                    type="int",
                    aliases=["polling_timeout"],
                    default=7200,
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name: str = self.get_param("name")
        self.environment: str = self.get_param("environment")
        self.instance_type: Optional[str] = self.get_param("instance_type")
        self.minimum_instances: int = self.get_param("minimum_instances")
        self.maximum_instances: int = self.get_param("maximum_instances")
        self.minimum_spot_instances: int = self.get_param("minimum_spot_instances")
        self.maximum_spot_instances: int = self.get_param("maximum_spot_instances")
        self.all_purpose_minimum_instances: Optional[int] = self.get_param(
            "all_purpose_minimum_instances",
        )
        self.all_purpose_maximum_instances: Optional[int] = self.get_param(
            "all_purpose_maximum_instances",
        )
        self.all_purpose_minimum_spot_instances: Optional[int] = self.get_param(
            "all_purpose_minimum_spot_instances",
        )
        self.all_purpose_maximum_spot_instances: Optional[int] = self.get_param(
            "all_purpose_maximum_spot_instances",
        )
        self.chart_value_overrides: Optional[list] = self.get_param(
            "chart_value_overrides",
        )
        self.enable_public_endpoint: bool = self.get_param("enable_public_endpoint")
        self.enable_private_network: bool = self.get_param("enable_private_network")
        self.loadbalancer_ips: Optional[list] = self.get_param("loadbalancer_ips")
        self.enable_workload_analytics: bool = self.get_param(
            "enable_workload_analytics",
        )
        self.initial_instances: int = self.get_param("initial_instances")
        self.initial_spot_instances: int = self.get_param("initial_spot_instances")
        self.root_volume_size: int = self.get_param("root_volume_size")
        self.resource_pool: Optional[str] = self.get_param("resource_pool")
        self.cpu_requests: Optional[str] = self.get_param("cpu_requests")
        self.memory_requests: Optional[str] = self.get_param("memory_requests")
        self.gpu_requests: Optional[str] = self.get_param("gpu_requests")
        self.skip_validation: bool = self.get_param("skip_validation")
        self.tags: Optional[dict] = self.get_param("tags")
        self.use_ssd: Optional[bool] = self.get_param("use_ssd")
        self.whitelist_ips: Optional[list] = self.get_param("whitelist_ips")
        self.force: bool = self.get_param("force")
        self.state: str = self.get_param("state")
        self.wait: bool = self.get_param("wait")
        self.delay: int = self.get_param("delay")
        self.timeout: int = self.get_param("timeout")

        # Initialize DE client
        self.de_client = CdpDeClient(self.api_client)

        # Initialize return values
        self.service = {}
        self.changed = False

    def process(self):
        existing_result = self.de_client.get_service_by_name(
            self.name,
            env_name=self.environment,
        )

        if existing_result:
            existing_service = existing_result.get("service", existing_result)
            cluster_id = existing_service.get("clusterId")

            if self.state == "absent":
                self.changed = True
                self.service = existing_service

                if not self.module.check_mode:
                    if self.wait:
                        result = self.de_client.wait_for_service_state(
                            cluster_id=cluster_id,
                            target_statuses=CdpDeClient.STOPPED_STATUSES,
                            timeout=self.timeout,
                            delay=self.delay,
                            force=self.force,
                        )
                        self.service = result if result else {}
                    else:
                        self.de_client.disable_service(cluster_id, force=self.force)

            elif self.state == "present":
                update_params = check_service_updates(
                    cluster_id=cluster_id,
                    service_details=existing_service,
                    minimum_instances=self.minimum_instances,
                    maximum_instances=self.maximum_instances,
                    minimum_spot_instances=self.minimum_spot_instances,
                    maximum_spot_instances=self.maximum_spot_instances,
                    whitelist_ips=self.whitelist_ips,
                    loadbalancer_allowlist=self.loadbalancer_ips,
                    all_purpose_minimum_instances=self.all_purpose_minimum_instances,
                    all_purpose_maximum_instances=self.all_purpose_maximum_instances,
                    all_purpose_minimum_spot_instances=self.all_purpose_minimum_spot_instances,
                    all_purpose_maximum_spot_instances=self.all_purpose_maximum_spot_instances,
                )

                if update_params:
                    self.changed = True
                    self.service = existing_service

                    if not self.module.check_mode:
                        self.de_client.update_service(**update_params)

                        if self.wait:
                            result = self.de_client.wait_for_service_state(
                                cluster_id=cluster_id,
                                target_statuses=CdpDeClient.REMOVABLE_STATUSES,
                                timeout=self.timeout,
                                delay=self.delay,
                            )
                            if result:
                                self.service = result
                else:
                    self.service = existing_service

        else:

            if self.state == "present":
                self.changed = True

                if not self.module.check_mode:
                    result = self.de_client.enable_service(
                        name=self.name,
                        env=self.environment,
                        instance_type=self.instance_type,
                        minimum_instances=self.minimum_instances,
                        maximum_instances=self.maximum_instances,
                        minimum_spot_instances=self.minimum_spot_instances,
                        maximum_spot_instances=self.maximum_spot_instances,
                        enable_public_endpoint=self.enable_public_endpoint,
                        enable_private_network=self.enable_private_network,
                        enable_workload_analytics=self.enable_workload_analytics,
                        initial_instances=self.initial_instances,
                        initial_spot_instances=self.initial_spot_instances,
                        root_volume_size=self.root_volume_size,
                        chart_value_overrides=self.chart_value_overrides,
                        loadbalancer_allowlist=self.loadbalancer_ips,
                        whitelist_ips=self.whitelist_ips,
                        skip_validation=self.skip_validation,
                        use_ssd=self.use_ssd,
                        tags=self.tags,
                        resource_pool=self.resource_pool,
                        cpu_requests=self.cpu_requests,
                        memory_requests=self.memory_requests,
                        gpu_requests=self.gpu_requests,
                    )

                    service = result.get("service") if result else None
                    if service:
                        self.service = service
                        cluster_id = service.get("clusterId")

                        if self.wait and cluster_id:
                            wait_result = self.de_client.wait_for_service_state(
                                cluster_id=cluster_id,
                                target_statuses=CdpDeClient.REMOVABLE_STATUSES,
                                timeout=self.timeout,
                                delay=self.delay,
                            )
                            if wait_result:
                                self.service = wait_result


def main():
    result = DEService()
    output = dict(changed=result.changed, service=result.service)

    if result.debug_log:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()
