#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2023 Cloudera, Inc. All Rights Reserved.
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
module: datahub_cluster
short_description: Manage CDP Datahubs
description:
    - Create and delete CDP Datahubs.
author:
  - "Webster Mudge (@wmudge)"
  - "Daniel Chaffelson (@chaffelson)"
  - "Chris Perro (@cmperro)"
version_added: "1.0.0"
requirements:
  - cdpy
options:
  name:
    description:
      - The name of the datahub.
      - This name must be unique, must have between 5 and 20 characters, and must contain only lowercase letters,
        numbers, and hyphens.
      - Names are case-sensitive.
    required: True
    aliases:
      - datahub
      - cluster_name
  state:
    description:
      - The declarative state of the datahub.
      - If creating a datahub, the associate Environment and Datalake must be started as well.
    type: str
    required: False
    default: present
    choices:
      - present
      - started
      - stopped
      - absent
  environment:
    description:
      - The CDP environment name or CRN to which the datahub will be attached.
    type: str
    required: False
    aliases:
      - env
  definition:
    description:
      - The name or CRN of the cluster definition to use for cluster creation.
  template:
    description:
      - Name or CRN of the cluster template to use for cluster creation.
  subnet:
    description:
      - The subnet ID in AWS, or the Subnet Name on Azure or GCP
      - Mutually exclusive with the subnet and subnets options
    type: str
    required: False
  subnets:
    description:
      - List of subnet IDs in case of multi availability zone setup.
      - Mutually exclusive with the subnet and subnets options
    type: list
    required: False
  subnets_filter:
    description:
      - L(JMESPath,https://jmespath.org/) expression to filter the subnets to be used for the load balancer
      - The expression will be applied to the full list of subnets for the specified environment
      - Each subnet in the list is an object with the following attributes - subnetId, subnetName, availabilityZone, cidr
      - The filter expression must only filter the list, but not apply any attribute projection
      - Mutually exclusive with the subnet and subnets options
    type: list
    required: False
  image:
    description: ID of the image used for cluster instances
    type: str
    required: False
  catalog:
    description: Name of the image catalog to use for cluster instances
    type: str
    required: False
  groups:
    description:
      - Instance group details.
    type: list
    elements: dict
    required: False
    suboptions:
      nodeCount:
        description:
          - Number of instances in the instance group
        type: int
        required: True
      instanceGroupName:
        description:
          - The instance group name.
        required: True
      instanceGroupType:
        description:
          - The instance group type.
        required: True
      instanceType:
        description:
          - The cloud provider specific instance type to be used.
        required: True
      rootVolumeSize:
        description:
          - The root volume size.
        type: int
      recoveryMode:
        description:
          - Recovery mode for the instance group.
        type: str
      volumeEncryption:
        description:
          - The volume encryption settings.
          - This setting does not apply to Azure, which always encrypts volumes.
        type: dict
        suboptions:
          enableEncryption:
            description:
              - Enable encyrption for all volumes in the instance group. Default is false.
            type: bool
          encryptionKey:
            description:
              - The ARN of the encryption key to use. If nothing is specified, the default key will be used.
      recipeNames:
        description:
          - The names or CRNs of the recipes that would be applied to the instance group.
        type: list
        elements: str
      attachedVolumeConfiguration:
        description:
          - The attached volume configuration. This does not include root volume.
        type: list
        elements: dict
        suboptions:
          volumeSize:
            description:
              - The attached volume size.
            type: int
            required: True
          volumeCount:
            description:
              - The attached volume count.
            type: int
            required: True
          volumeType:
            description:
              - The attached volume type.
            required: True
      subnetIds:
        description:
          - The list of subnet IDs in case of multi-availability zone setup.
          - Specifying this field overrides the datahub level subnet ID setup for the multi-availability zone configuration.
        type: list
        elements: str
  tags:
    description:
      - Tags associated with the datahub and its resources.
    type: dict
    required: False
    aliases:
      - datahub_tags
  extension:
    description:
      - Cluster extensions for Data Hub cluster.
  multi_az:
    description:
      - (AWS) Flag indicating whether to defer to the CDP Environment for availability zone/subnet placement.
      - Useful for when you are not sure which subnet is available to the datahub cluster.
    type: bool
    required: False
    default: True
  force:
    description:
      - Flag indicating if the datahub should be force deleted.
      - This option can be used when cluster deletion fails.
      - This removes the entry from Cloudera Datahub service.
      - Any lingering resources have to be deleted from the cloud provider manually.
    type: bool
    required: False
    default: False
  wait:
    description:
      - Flag to enable internal polling to wait for the datahub to achieve the declared state.
      - If set to FALSE, the module will return immediately.
    type: bool
    required: False
    default: True
  delay:
    description:
      - The internal polling interval (in seconds) while the module waits for the datahub to achieve the declared state.
    type: int
    required: False
    default: 15
    aliases:
      - polling_delay
  timeout:
    description:
      - The internal polling timeout (in seconds) while the module waits for the datahub to achieve the declared state.
    type: int
    required: False
    default: 3600
    aliases:
      - polling_timeout
extends_documentation_fragment:
  - cloudera.cloud.cdp_sdk_options
  - cloudera.cloud.cdp_auth_options
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details.

- name: Create a datahub specifying instance group details (and do not wait for status change)
  cloudera.cloud.datahub_cluster:
    name: datahub-name
    env: name-or-crn
    state: present
    subnet: subnet-id-for-cloud-provider
    image: image-uuid-from-catalog
    catalog: name-of-catalog-for-image
    template: template-name
    groups:
      - nodeCount: 1
        instanceGroupName: master
        instanceGroupType: GATEWAY
        instanceType: instance-type-for-cloud-provider
        rootVolumeSize: 100
        recoveryMode: MANUAL
        recipeNames: []
        attachedVolumeConfiguration:
          - volumeSize: 100
            volumeCount: 1
            volumeType: volume-type-for-cloud-provider
    tags:
      project: Arbitrary content
    wait: false

- name: Create a datahub specifying only a definition name
  cloudera.cloud.datahub_cluster:
    name: datahub-name
    env: name-or-crn
    definition: definition-name
    tags:
      project: Arbitrary content
    wait: false

- name: Stop the datahub (and wait for status change)
  cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: stopped

- name: Start the datahub (and wait for status change)
  cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: started

- name: Delete the datahub (and wait for status change)
  cloudera.cloud.datahub_cluster:
    name: example-datahub
    state: absent
"""

RETURN = r"""
datahub:
  description: The information about the Datahub
  type: dict
  returned: always
  contains:
    cloudPlatform:
      description:
        - The cloud platform.
      returned: when supported
    clouderaManager:
      description:
        - The Cloudera Manager details.
      type: dict
      contains:
        platformVersion:
          description:
            - CDP Platform version.
          returned: when supported
        version:
          description: Cloudera Manager version.
          returned: always
    clusterName:
      description:
        - The name of the cluster.
      returned: always
    clusterStatus:
      description:
        - The status of the cluster.
      returned: when supported
    clusterTemplateCrn:
      description:
        - The CRN of the cluster template used for the cluster creation.
      returned: when supported
    creationDate:
      description:
        - The date when the cluster was created.
        - Return value is a date timestamp.
      returned: when supported
    credentialCrn:
      description:
        - The CRN of the credential.
      returned: when supported
    crn:
      description:
        - The CRN of the cluster.
      returned: always
    datalakeCrn:
      description:
        - The CRN of the attached datalake.
      returned: when supported
    endpoints:
      description:
        - The exposed service API endpoints.
      type: list
      elements: dict
      returned: when supported
      contains:
        endpoint:
          description:
            - The endpoints.
          type: list
          elements: dict
          returned: always
          contains:
            displayName:
              description:
                - The more consumable name of the exposed service.
              returned: always
            knoxService:
              description:
                - The related knox entry.
              returned: always
            mode:
              description:
                - The SSO mode of the given service.
              returned: always
            open:
              description:
                - Flag of the access status of the given endpoint.
              type: bool
              returned: always
            serviceName:
              description:
                - The name of the exposed service.
              returned: always
            serviceUrl:
              description:
                - The server url for the given exposed service’s API.
              returned: always
    environmentCrn:
      description:
        - The CRN of the environment.
      returned: when supported
    environmentName:
      description:
        - The name of the environment.
      returned: when supported
    imageDetails:
      description:
        - The image details.
      type: dict
      returned: when supported
      contains:
        catalogName:
          description:
            - The image catalog name.
          returned: when supported
        catalogUrl:
          description:
            - The image catalog URL.
          returned: when supported
        id:
          description:
            - The ID of the image used for cluster instances.
            - This is internally generated by the cloud provider to uniquely identify the image.
          returned: when supported
        name:
          description:
            - The name of the image used for cluster instances.
          returned: when supported
    instanceGroups:
      description:
        - The instance details.
      type: list
      elements: dict
      returned: when supported
      contains:
        availabilityZones:
          description:
            - List of availability zones associated with the instance group.
          type: list
          elements: str
          returned: when supported
        instances:
          description:
            - List of instances in this instance group.
          type: list
          elements: dict
          returned: always
          contains:
            attachedVolumes:
              description:
                - List of volumes attached to this instance.
              type: list
              elements: dict
              returned: when supported
              contains:
                count:
                  description:
                    - The number of volumes.
                  type: int
                  returned: when supported
                size:
                  description:
                    - The size of each volume in GB.
                  type: int
                  returned: when supported
                volumeType:
                  description:
                    - The type of volumes.
                  returned: when supported
            availabilityZone:
              description:
                - The availability zone of the instance.
              returned: when supported
            clouderaManagerServer:
              description:
                - Flag indicating if Cloudera Manager has been deployed or not.
              type: bool
              returned: when supported
            fqdn:
              description:
                - The fully-qualified domain name (FQDN) of the instance.
              returned: when supported
            id:
              description:
                - The ID of the given instance.
              returned: always
            instanceGroup:
              description:
                - The name of the instance group associated with the instance.
              returned: when supported
            instanceType:
              description:
                - The type of the given instance.
                - Values are C(GATEWAY), C(GATEWAY_PRIMARY), or C(CORE).
              returned: always
            instanceVmType:
              description:
                - The VM type of the instance.
                - Supported values depend on the cloud platform.
              returned: when supported
            privateIp:
              description:
                - The private IP of the given instance.
              returned: when supported
            publicIp:
              description:
                - The public IP of the given instance.
              returned: when supported
            rackId:
              description:
                - The rack ID of the instance in Cloudera Manager.
              returned: when supported
            sshPort:
              description:
                - The SSH port for the instance.
              type: int
              returned: when supported
            state:
              description:
                - The health state of the instance.
                - C(UNHEALTHY) represents instances with unhealthy services, lost instances, or failed operations.
              returned: always
            status:
              description:
                - The status of the instance.
                - This includes information like whether the instance is being provisioned, stopped, decommissioning failures etc.
              returned: when supported
            statusReason:
              description:
                - The reason for the current status of this instance.
              returned: when supported
            subnetId:
              description:
                - The subnet ID of the instance.
              returned: when supported
        name:
          description:
            - The name of the instance group where the given instance is located.
          returned: always
        subnetIds:
          description:
            - The list of subnet IDs in case of multi-availability zone setup.
          type: list
          elements: str
          returned: when supported
    nodeCount:
      description:
        - The cluster node count.
      type: int
      returned: when supported
    status:
      description:
        - The status of the stack.
      returned: when supported
    statusReason:
      description:
        - The status reason.
      returned: when supported
    workloadType:
      description:
        - The workload type for the cluster.
      returned: when supported
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

import json

import jmespath
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.cloud.plugins.module_utils.cdp_common import CdpModule


class DatahubCluster(CdpModule):
    def __init__(self, module):
        super(DatahubCluster, self).__init__(module)

        # Set variables
        self.name = self._get_param("name")
        self.state = self._get_param("state").lower()
        self.cloud = self._get_param("cloud")

        self.environment = self._get_param("environment")
        self.definition = self._get_param("definition")
        self.subnet = self._get_param("subnet")
        self.subnets = self._get_param("subnets")
        self.subnets_filter = self._get_param("subnets_filter")
        self.image_id = self._get_param("image")
        self.image_catalog = self._get_param("catalog")
        self.template = self._get_param("template")
        self.groups = self._get_param("groups")
        self.tags = self._get_param("tags")
        self.extension = self._get_param("extension")
        self.multi_az = self._get_param("multi_az")

        self.wait = self._get_param("wait")
        self.delay = self._get_param("delay")
        self.timeout = self._get_param("timeout")
        self.force = self._get_param("force")

        self.host_env = None

        # Initialize the return values
        self.datahub = dict()

        # Execute logic process
        self.process()

    @CdpModule._Decorators.process_debug
    def process(self):
        existing = self.cdpy.datahub.describe_cluster(self.name)
        if self.state in ["present", "started"]:
            # If the datahub exists
            if existing is not None:
                self.datahub = existing
                if (
                    "status" in existing
                    and existing["status"] not in self.cdpy.sdk.CREATION_STATES
                ):
                    # Reconcile and error if specifying invalid cloud parameters
                    if self.environment is not None:
                        self.host_env = self.cdpy.environments.describe_environment(
                            self.environment,
                        )
                        if self.host_env["crn"] != existing["environmentCrn"]:
                            self.module.fail_json(
                                msg="Datahub exists in a different Environment: %s"
                                % existing["environmentCrn"],
                            )
                        # Check for changes
                        mismatch = self._reconcile_existing_state(existing)
                        if mismatch:
                            msg = ""
                            for m in mismatch:
                                msg += "Parameter '%s' found to be '%s'\n" % (
                                    m[0],
                                    m[1],
                                )
                            self.module.fail_json(
                                msg="Datahub exists and differs from expected:\n" + msg,
                                violations=mismatch,
                            )
                # Attempt to start the datahub
                if (
                    "status" in existing
                    and existing["status"] not in self.cdpy.sdk.STARTED_STATES
                ):
                    self.cdpy.datahub.start_cluster(self.name)

                if self.wait and not self.module.check_mode:
                    self.datahub = self.cdpy.sdk.wait_for_state(
                        describe_func=self.cdpy.datahub.describe_cluster,
                        params=dict(name=self.name),
                        state="AVAILABLE",
                        delay=self.delay,
                        timeout=self.timeout,
                    )
            # Else not exists already, therefore create the datahub
            else:
                self.host_env = self.cdpy.environments.describe_environment(
                    self.environment,
                )
                if self.host_env is not None:
                    if self.cdpy.datalake.is_datalake_running(self.environment) is True:
                        self.create_cluster()
                    else:
                        self.module.fail_json(
                            msg="Unable to find datalake or not Running, '%s'"
                            % self.environment,
                        )
                else:
                    self.module.fail_json(
                        msg="Unable to find environment, '%s'" % self.environment,
                    )
        elif self.state == "stopped":
            # If the datahub exists
            if existing is not None:
                # Warn if attempting to stop an already stopped/stopping datahub
                if existing["status"] in self.cdpy.sdk.STOPPED_STATES:
                    self.module.warn(
                        "Attempting to stop a datahub already stopped or in stopping cycle",
                    )
                    self.datahub = existing
                # Warn if attempting to stop an already terminated/terminating datahub
                elif existing["status"] in self.cdpy.sdk.TERMINATION_STATES:
                    self.module.warn(
                        "Attempting to stop an datahub during the termination cycle",
                    )
                    self.datahub = existing
                # Otherwise, stop the datahub
                else:
                    if not self.module.check_mode:
                        self.cdpy.datahub.stop_cluster(self.name)
                        self.changed = True
                        if self.wait:
                            self.datahub = self.cdpy.sdk.wait_for_state(
                                describe_func=self.cdpy.datahub.describe_cluster,
                                params=dict(name=self.name),
                                state="STOPPED",
                                delay=self.delay,
                                timeout=self.timeout,
                            )

            else:
                self.module.fail_json(msg="Datahub %s does not exist" % self.name)

        elif self.state == "absent":
            # If the datahub exists
            if existing is not None:
                # Warn if attempting to delete an already terminated/terminating datahub
                if not self.module.check_mode:
                    if existing["status"] in self.cdpy.sdk.TERMINATION_STATES:
                        self.module.warn(
                            "Attempting to delete an datahub during the termination cycle",
                        )
                        self.datahub = existing
                    # Otherwise, delete the datahub
                    else:
                        self.cdpy.datahub.delete_cluster(self.name)
                        self.changed = True
                    if self.wait:
                        self.datahub = self.cdpy.sdk.wait_for_state(
                            describe_func=self.cdpy.datahub.describe_cluster,
                            params=dict(name=self.name),
                            field=None,
                            delay=self.delay,
                            timeout=self.timeout,
                            ignore_failures=True,
                        )
        else:
            self.module.fail_json(msg="Invalid state: %s" % self.state)

    def create_cluster(self):
        self._validate_datahub_name()

        payload = self._configure_payload()

        if self.host_env["cloudPlatform"] == "AWS":
            self.datahub = self.cdpy.sdk.call(
                "datahub",
                "create_aws_cluster",
                **payload,
            )
        elif self.host_env["cloudPlatform"] == "AZURE":
            self.datahub = self.cdpy.sdk.call(
                "datahub",
                "create_azure_cluster",
                **payload,
            )
        elif self.host_env["cloudPlatform"] == "GCP":
            self.datahub = self.cdpy.sdk.call(
                "datahub",
                "create_gcp_cluster",
                **payload,
            )
        else:
            self.module.fail_json(
                msg="cloudPlatform %s datahub deployment not implemented"
                % self.host_env["cloudPlatform"],
            )

        self.changed = True

        if self.wait and not self.module.check_mode:
            self.datahub = self.cdpy.sdk.wait_for_state(
                describe_func=self.cdpy.datahub.describe_cluster,
                params=dict(name=self.name),
                state="AVAILABLE",
                delay=self.delay,
                timeout=self.timeout,
            )

    def _configure_payload(self):
        payload = dict(clusterName=self.name, environmentName=self.environment)

        if self.definition is not None:
            if self.host_env["cloudPlatform"] == "AWS":
                payload["clusterDefinition"] = self.definition
            else:
                payload["clusterDefinitionName"] = self.definition
        else:
            payload["image"] = {"id": self.image_id, "catalogName": self.image_catalog}
            if self.host_env["cloudPlatform"] == "AWS":
                payload["clusterTemplate"] = self.template
            else:
                payload["clusterTemplateName"] = self.template
            payload["instanceGroups"] = self.groups

        if self.subnets_filter:
            try:
                env_info = self.cdpy.environments.describe_environment(self.environment)
                subnet_metadata = list(env_info["network"]["subnetMetadata"].values())
            except Exception:
                subnet_metadata = []
            if not subnet_metadata:
                self.module.fail_json(
                    msg="Could not retrieve subnet metadata for CDP Environment %s"
                    % self.env_crn,
                )

            subnets = self._filter_subnets(self.subnets_filter, subnet_metadata)
            self.module.warn("Found subnets: %s" % ", ".join(subnets))
            if len(subnets) == 1:
                self.subnet = subnets[0]
            else:
                self.subnets = subnets

        if self.subnet:
            if self.host_env["cloudPlatform"] == "GCP":
                payload["subnetName"] = self.subnet
            else:
                payload["subnetId"] = self.subnet
        elif self.subnets:
            payload["subnetIds"] = self.subnets

        if self.extension is not None:
            payload["clusterExtension"] = self.extension

        if self.host_env["cloudPlatform"] == "AWS":
            payload["multiAz"] = self.multi_az

        if self.tags is not None:
            payload["tags"] = list()
            for k in self.tags:
                payload["tags"].append(dict(key=k, value=str(self.tags[k])))

        return payload

    def _filter_subnets(self, query, subnets):
        """Apply a JMESPath to an array of subnets and return the id of the selected subnets.
        The query must only filter the array, without applying any projection. The query result must also be an
        array of subnet objects.

        :param query: JMESpath query to filter the subnet array.
        :param subnets: An array of subnet objects. Each subnet in the array is an object with the following attributes:
        subnetId, subnetName, availabilityZone, cidr.
        :return: An array of subnet ids.
        """
        filtered_subnets = []
        try:
            filtered_subnets = jmespath.search(query, subnets)
        except Exception:
            self.module.fail_json(
                msg="The specified subnet filter is an invalid JMESPath expression: "
                % query,
            )
        try:
            return [s["subnetId"] for s in filtered_subnets]
        except Exception:
            self.module.fail_json(
                msg='The subnet filter "%s" should return an array of subnet objects '
                "but instead returned this: %s" % (query, json.dumps(filtered_subnets)),
            )

    def _reconcile_existing_state(self, existing):
        mismatched = list()

        if existing["cloudPlatform"] == "AWS":
            self.module.warn(
                "Datahub configuration reconciliation not implemented on AWS",
            )

        if existing["cloudPlatform"].upper() == "AZURE":
            self.module.warn(
                "Datahub configuration reconciliation not implemented on Azure",
            )

        if existing["cloudPlatform"].upper() == "GCP":
            self.module.warn(
                "Datahub configuration reconciliation not implemented on GCP",
            )

        if self.tags:
            self.module.warn(
                "Updating an existing Datahub's 'tags' "
                "directly are not supported at this time. If you "
                "need to change the tags, explicitly delete "
                "and recreate the Datahub.",
            )
        return mismatched

    def _validate_datahub_name(self):
        if len(self.name) < 5 or len(self.name) > 100:
            self.module.fail_json(
                msg="Invalid datahub name, '%s'. Names must be between 5-100 characters."
                % self.name,
            )
        elif (
            self.cdpy.sdk.regex_search(self.cdpy.sdk.DATAHUB_NAME_PATTERN, self.name)
            is not None
        ):
            self.module.fail_json(
                msg="Invalid datahub name, '%s'. Names must contain only lowercase "
                "letters, numbers and hyphens." % self.name,
            )


def main():
    module = AnsibleModule(
        argument_spec=CdpModule.argument_spec(
            name=dict(required=True, type="str", aliases=["datahub", "cluster_name"]),
            state=dict(
                required=False,
                type="str",
                choices=["present", "started", "stopped", "absent"],
                default="present",
            ),
            definition=dict(required=False, type="str"),
            subnet=dict(required=False, type="str", default=None),
            subnets=dict(required=False, type="list", elements="str", default=None),
            subnets_filter=dict(required=False, type="str", default=None),
            image=dict(required=False, type="str", default=None),
            catalog=dict(required=False, type="str", default=None),
            template=dict(required=False, type="str", default=None),
            groups=dict(required=False, type="list", default=None),
            environment=dict(required=False, type="str", aliases=["env"], default=None),
            tags=dict(required=False, type="dict", aliases=["datahub_tags"]),
            extension=dict(required=False, type="dict"),
            multi_az=dict(required=False, type="bool", default=True),
            force=dict(required=False, type="bool", default=False),
            wait=dict(required=False, type="bool", default=True),
            delay=dict(
                required=False,
                type="int",
                aliases=["polling_delay"],
                default=15,
            ),
            timeout=dict(
                required=False,
                type="int",
                aliases=["polling_timeout"],
                default=3600,
            ),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ("subnet", "subnets", "subnets_filter"),
        ],
        # TODO Implement argument spec logic
        # Punting on additional checks here. There are a variety of supporting datahub invocations that can make this more complex
        # required_together=[
        #    ['subnet', 'image', 'catalog', 'template', 'groups', 'environment'],
        # ]
    )

    result = DatahubCluster(module)
    output = dict(changed=result.changed, datahub=result.datahub)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()
