.. _env_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env -- Manage CDP Environments

env -- Manage CDP Environments
==============================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create, update, and delete CDP Environments

- Note that changing states, in particular, creating a new environment, can take several minutes.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**          | **Choices/Defaults**  | **Comments**                                                                                                                                             |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **name**               |                       | The name of the target environment.                                                                                                                      |
   |                        |                       | Names must begin with a lowercase alphanumeric, contain only lowercase alphanumerics and hyphens, and be between 5 to 28 characters in length.           |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | *Required*             |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: environment*                                                                                                                                   |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **state**              | **Choices:**          | The declarative state of the environment                                                                                                                 |
   |                        |  - **present** |larr| | If *state=present*, one of *cloud* or *credential* must be present.                                                                                      |
   | |br|                   |  - started            |                                                                                                                                                          |
   |                        |  - stopped            |                                                                                                                                                          |
   | ``str``                |  - absent             |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **cloud**              | **Choices:**          | The cloud provider or platform for the environment.                                                                                                      |
   |                        |  - aws                | Requires *region*, *credential*, *log_location*, and *log_identity*.                                                                                     |
   | |br|                   |  - azure              | If *cloud=aws*, one of *public_key* or *public_key_id* must be present.                                                                                  |
   |                        |  - gcp                | If *cloud=aws*, one of *network_cidr* or *vpc_id* must be present.                                                                                       |
   | ``str``                |                       | If *cloud=aws*, one of *network_cidr* or *vpc_id* must be present.                                                                                       |
   |                        |                       | If *cloud=aws*, one of *inbound_cidr* or *default_sg* and *knox_sg* must be present.                                                                     |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **region**             |                       | The cloud platform specified region                                                                                                                      |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **credential**         |                       | The CDP credential associated with the environment                                                                                                       |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **project**            |                       | Name of Project when deploying environment on GCP                                                                                                        |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **inbound_cidr**       |                       | CIDR range which is allowed for inbound traffic. Either IPv4 or IPv6 is allowed.                                                                         |
   |                        |                       | Mutually exclusive with *default_sg* and *knox_sg*.                                                                                                      |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: security_cidr*                                                                                                                                 |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **default_sg**         |                       | Security group where all other hosts are placed.                                                                                                         |
   |                        |                       | Mutually exclusive with *inbound_cidr*.                                                                                                                  |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: default, default_security_group*                                                                                                               |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **knox_sg**            |                       | Security group where Knox-enabled hosts are placed.                                                                                                      |
   |                        |                       | Mutually exclusive with *inbound_cidr*.                                                                                                                  |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: knox, knox_security_group*                                                                                                                     |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **public_key_text**    |                       | The content of a public SSH key.                                                                                                                         |
   |                        |                       | Mutually exclusive with *public_key_id*.                                                                                                                 |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: ssh_key_text*                                                                                                                                  |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **public_key_id**      |                       | The public SSH key ID already registered in the cloud provider.                                                                                          |
   |                        |                       | Mutually exclusive with *public_key_text*.                                                                                                               |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: public_key, ssh_key, ssh_key_id*                                                                                                               |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **log_location**       |                       | (AWS) The base location to store logs in S3. This should be an s3a:// url.                                                                               |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: storage_location_base*                                                                                                                         |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **log_identity**       |                       | (AWS) The instance profile ARN assigned the necessary permissions to access the S3 storage location, i.e. *log_location*.                                |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: instance_profile*                                                                                                                              |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **network_cidr**       |                       | (AWS) The network CIDR. This will create a VPC along with subnets in multiple Availability Zones.                                                        |
   |                        |                       | Mutually exclusive with *vpc_id* and *subnet_ids*.                                                                                                       |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **vpc_id**             |                       | (AWS) The VPC ID.                                                                                                                                        |
   |                        |                       | Mutually exclusive with *network_cidr* and requires *subnet_ids*.                                                                                        |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: vpc*                                                                                                                                           |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **subnet_ids**         |                       | (AWS) One or more subnet identifiers within the VPC.                                                                                                     |
   |                        |                       | Mutually exclusive with *network_cidr* and requires *vpc_id*.                                                                                            |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``list``               |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: subnets*                                                                                                                                       |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **tags**               |                       | Tags associated with the environment and its resources.                                                                                                  |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``dict``               |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: environment_tags*                                                                                                                              |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **workload_analytics** |                       | Flag to enable diagnostic information about job and query execution to be sent to Workload Manager for Data Hub clusters created within the environment. |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``bool``               |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **description**        |                       | A description for the environment.                                                                                                                       |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: desc*                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **tunnel**             |                       | Flag to enable SSH tunnelling for the environment.                                                                                                       |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``bool``               |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: enable_tunnel, ssh_tunnel*                                                                                                                     |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **freeipa**            |                       | The FreeIPA service for the environment.                                                                                                                 |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``dict``               |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **proxy**              |                       | The name of the proxy config to use for the environment.                                                                                                 |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: proxy_config, proxy_config_name*                                                                                                               |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **wait**               |                       | Flag to enable internal polling to wait for the environment to achieve the declared state.                                                               |
   |                        |                       | If set to FALSE, the module will return immediately.                                                                                                     |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``bool``               |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **delay**              |                       | The internal polling interval (in seconds) while the module waits for the environment to achieve the declared state.                                     |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``int``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: polling_delay*                                                                                                                                 |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **timeout**            |                       | The internal polling timeout (in seconds) while the module waits for the environment to achieve the declared state.                                      |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``int``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: polling_timeout*                                                                                                                               |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **s3_guard_name**      |                       | (AWS) AWS Dynamo table name for S3 Guard.                                                                                                                |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: s3_guard, s3_guard_table_name*                                                                                                                 |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**         |                       | Verify the TLS certificates for the CDP endpoint.                                                                                                        |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``bool``               |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: tls*                                                                                                                                           |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**              |                       | Capture the CDP SDK debug log.                                                                                                                           |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``bool``               |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | |br|                                                                                                                                                     |
   |                        |                       |                                                                                                                                                          |
   |                        |                       | *Aliases: debug_endpoints*                                                                                                                               |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**            |                       | If provided, the CDP SDK will use this value as its profile.                                                                                             |
   |                        |                       |                                                                                                                                                          |
   | |br|                   |                       |                                                                                                                                                          |
   |                        |                       |                                                                                                                                                          |
   | ``str``                |                       |                                                                                                                                                          |
   +------------------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create an environment
  - cloudera.cloud.env:
      name: example-environment
      state: present
      credential: example-credential
      cloud: aws
      region: us-east-1
      log_location: s3a://example-bucket/datalake/logs
      log_identity: arn:aws:iam::981304421142:instance-profile/example-log-role
      public_key_id: example-sshkey
      network_cidr: 10.10.0.0/16
      inbound_cidr: 0.0.0.0/0
      tags:
        project: Arbitrary content

  # Create an environment, but don't wait for completion (see env_info)
  - cloudera.cloud.env:
      name: example-environment
      state: present
      wait: no
      credential: example-credential
      cloud: aws
      region: us-east-1
      log_location: s3a://example-bucket/datalake/logs
      log_identity: arn:aws:iam::981304421142:instance-profile/example-log-role
      public_key_id: example-sshkey
      network_cidr: 10.10.0.0/16
      inbound_cidr: 0.0.0.0/0
      tags:
        project: Arbitrary content

  # Update the environment's CDP credential
  - cloudera.cloud.env:
      name: example-module
      credential: another-credential

  # Stop the environment (and wait for status change)
  - cloudera.cloud.env:
      name: example-module
      state: stopped

  # Start the environment (and wait for status change)
  - cloudera.cloud.env:
      name: example-module
      state: started

  # Delete the environment (and wait for status change)
    cloudera.cloud.env:
      name: example-module
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Key**                        | **Returned**   | **Description**                                                                                                                                    |
   +--------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | **environment**                | on success     | The information about the Environment                                                                                                              |
   |                                |                |                                                                                                                                                    |
   | |br|                           |                |                                                                                                                                                    |
   |                                |                |                                                                                                                                                    |
   | ``dict``                       |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **authentication**           | always         | Additional SSH key authentication configuration for accessing cluster node instances of the Environment.                                           |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``dict``                     |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **loginUserName**          | always         | SSH user name created on the node instances for SSH access.                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | cloudbreak                                                                                                                                         |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **publicKey**              | when supported | SSH Public key string                                                                                                                              |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | ssh-rsa AAAAB3NzaC...BH example-public-key                                                                                                         |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **publicKeyId**            | when supported | Public SSH key ID registered in the cloud provider.                                                                                                |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | a_labeled_public_key                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **awsDetails**               | when supported | AWS-specific environment configuration information.                                                                                                |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``dict``                     |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **s3GuardTableName**       | always         | The name for the DynamoDB table backing S3Guard.                                                                                                   |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | table_name                                                                                                                                         |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **cloudPlatform**            | always         | Cloud provider of the Environment.                                                                                                                 |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | AWS                                                                                                                                                |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | AZURE                                                                                                                                              |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | GCP                                                                                                                                                |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **credentialName**           | always         | Name of the CDP Credential of the Environment.                                                                                                     |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | a-cdp-credential                                                                                                                                   |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **crn**                      | always         | CDP CRN value for the Environment.                                                                                                                 |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:61eb5b97-226a-4be7-b56d-795d18a043b5                                |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **description**              | always         | Description of the Environment.                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | An example Environment                                                                                                                             |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **environmentName**          | always         | Name of the Environment.                                                                                                                           |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | a-cdp-environment-name                                                                                                                             |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **freeipa**                  | always         | Details of a FreeIPA instance in the Environment.                                                                                                  |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``complex``                  |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **crn**                    | always         | CRN of the FreeIPA instance.                                                                                                                       |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | crn:cdp:freeipa:us-west-1:558bc1d2-8867-4357-8524-311d51259233:freeipa:cbab8ee3-00f2-4958-90c1-6f7cc06b4937                                        |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **domain**                 | always         | Domain name of the FreeIPA instance.                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | example.012345-abcd.cloudera.site                                                                                                                  |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **hostname**               | always         | Hostname of the FreeIPA instance.                                                                                                                  |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | ipaserver                                                                                                                                          |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **serverIP**               | always         | IP addresses of the FreeIPA instance.                                                                                                              |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``list``                   |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | ['10.10.2.40']                                                                                                                                     |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **logStorage**               | always         | Storage configuration for cluster and audit logs for the Environment.                                                                              |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``complex``                  |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **awsDetails**             | when supported | AWS-specific log storage configuration details.                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``dict``                   |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **instanceProfile**      | always         | AWS instance profile that contains the necessary permissions to access the S3 storage location.                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | arn:aws:iam::381358652250:instance-profile/EXAMPLE-LOG_ROLE                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **storageLocationBase**  | always         | Base location to store logs in S3.                                                                                                                 |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | s3a://example-bucket/datalake/logs                                                                                                                 |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **azureDetails**           | when supported | Azure-specific log storage configuration details.                                                                                                  |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``dict``                   |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **managedIdentity**      | always         | Azure managing identity associated with the logger.                                                                                                |
   | | | |                          |                | This identify should have the Storage Blob Data Contributor role on the given storage account.                                                     |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | /subscriptions/01234-56789-abcd/resourceGroups/example-environment-name/providers/ Microsoft.ManagedIdentity/userAssignedIdentities/loggerIdentity |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **storageLocationBase**  | always         | Base location to store logs in Azure Blob Storage.                                                                                                 |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | abfs://logs@example_location.dfs.core.windows.net                                                                                                  |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **enabled**                | always         | Flag for external log storage.                                                                                                                     |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``bool``                   |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **network**                  | always         | Network details for the Environment                                                                                                                |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``complex``                  |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **aws**                    | when supported | AWS networking specifics for the Environment.                                                                                                      |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``dict``                   |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **vpcId**                | always         | VPC identifier.                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | vpc-08785c81e888251df                                                                                                                              |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **azure**                  | when supported | Azure networking specifics for the Environment.                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``dict``                   |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **networkId**            | always         | VNet identifier.                                                                                                                                   |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | example-vnet                                                                                                                                       |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **resourceGroupName**    | always         | Resource Group name.                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``str``                  |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | |br|                                                                                                                                               |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | **Sample:**                                                                                                                                        |
   | | | |                          |                |                                                                                                                                                    |
   | | | |                          |                | example-rg                                                                                                                                         |
   | | | |                          |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **usePublicIp**          | always         | Flag for associating public IP addresses to the resources within the network.                                                                      |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``bool``                 |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **networkCidr**            | always         | Range of private IPv4 addresses that resources will use for the Environment.                                                                       |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | 10.10.0.0/16                                                                                                                                       |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **subnetIds**              | always         | Subnet identifiers for the Environment.                                                                                                            |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``list``                   |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | ['subnet-04a332603a269535f', 'subnet-07bbea553ca667b66', 'subnet-0aad7d6d9aa66d1e7']                                                               |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **subnetMetadata**         | always         | Additional subnet metadata for the Environment.                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``complex``                |                |                                                                                                                                                    |
   +-+-+-+--------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **__subnetId__**         | always         | Keyed subnet identifier.                                                                                                                           |
   | | | |                          |                |                                                                                                                                                    |
   | | | | |br|                     |                |                                                                                                                                                    |
   | | | |                          |                |                                                                                                                                                    |
   | | | | ``dict``                 |                |                                                                                                                                                    |
   +-+-+-+-+------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **availabilityZone**   | when supported | Availability zone (AWS only)                                                                                                                       |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | |br|                   |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | ``str``                |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | |br|                                                                                                                                               |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | **Sample:**                                                                                                                                        |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | us-west-2a                                                                                                                                         |
   | | | | |                        |                |                                                                                                                                                    |
   +-+-+-+-+------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **subnetId**           | always         | Identifier for the subnet                                                                                                                          |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | |br|                   |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | ``str``                |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | |br|                                                                                                                                               |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | **Sample:**                                                                                                                                        |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | subnet-04a332603a269535f                                                                                                                           |
   | | | | |                        |                |                                                                                                                                                    |
   +-+-+-+-+------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **subnetName**         | always         | Name of the subnet                                                                                                                                 |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | |br|                   |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | | ``str``                |                |                                                                                                                                                    |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | |br|                                                                                                                                               |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | **Sample:**                                                                                                                                        |
   | | | | |                        |                |                                                                                                                                                    |
   | | | | |                        |                | subnet-04a332603a269535f                                                                                                                           |
   | | | | |                        |                |                                                                                                                                                    |
   +-+-+-+-+------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **proxyConfig**              | when supported | Proxy configuration of the Environment.                                                                                                            |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``dict``                     |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **proxyConfigName**        | always         | Name of the proxy configuration.                                                                                                                   |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | the-proxy-config                                                                                                                                   |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **crn**                    | always         | CDP CRN for the proxy configuration.                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:38eeb2b9-6e57-4d10-ad91-f6d9bceecb54                                |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **description**            | always         | Description of the proxy.                                                                                                                          |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | The proxy configuration description                                                                                                                |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **host**                   | always         | Proxy host.                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | some.host.example.com                                                                                                                              |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **password**               | always         | Proxy user password.                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | secret_password                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **port**                   | always         | Proxy port.                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | 8443                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **protocol**               | always         | Proxy protocol.                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | https                                                                                                                                              |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **user**                   | always         | Proxy user name.                                                                                                                                   |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | the_username                                                                                                                                       |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **region**                   | always         | Cloud provider region of the Environment.                                                                                                          |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | us-east-1                                                                                                                                          |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **securityAccess**           | always         | Security control configuration for FreeIPA and Datalake deployment in the Environment.                                                             |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``dict``                     |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **cidr**                   | when supported | CIDR range which is allowed for inbound traffic. Either IPv4 or IPv6 is allowed.                                                                   |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | 0.0.0.0/0                                                                                                                                          |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **defaultSecurityGroupId** | when supported | Security group associated with Knox-enabled hosts.                                                                                                 |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | /subscriptions/01234-56789-abcd/resourceGroups/example-environment/providers/Microsoft.Network/ networkSecurityGroups/example-default-nsg          |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **securityGroupIdForKnox** | when supported | Security group associated with all other hosts (non-Knox).                                                                                         |
   | | |                            |                |                                                                                                                                                    |
   | | | |br|                       |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | | ``str``                    |                |                                                                                                                                                    |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | |br|                                                                                                                                               |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | **Sample:**                                                                                                                                        |
   | | |                            |                |                                                                                                                                                    |
   | | |                            |                | /subscriptions/01234-56789-abcd/resourceGroups/example-environment/providers/Microsoft.Network/ networkSecurityGroups/example-knox-nsg             |
   | | |                            |                |                                                                                                                                                    |
   +-+-+----------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **status**                   | always         | Status of the Environment.                                                                                                                         |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | |br|                                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | **Sample:**                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | AVAILABLE                                                                                                                                          |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | CREATE_FAILED                                                                                                                                      |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | CREATION_INITIATED                                                                                                                                 |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | ENV_STOPPED                                                                                                                                        |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | FREEIPA_CREATION_IN_PROGRESS                                                                                                                       |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | FREEIPA_DELETE_IN_PROGRESS                                                                                                                         |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | FREEIPA_DELETED_ON_PROVIDER_SIDE                                                                                                                   |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | START_FREEIPA_FAILED                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   | |                              |                | STOP_FREEIPA_STARTED                                                                                                                               |
   | |                              |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **statusReason**             | when supported | Description for the status code of the Environment.                                                                                                |
   | |                              |                |                                                                                                                                                    |
   | | |br|                         |                |                                                                                                                                                    |
   | |                              |                |                                                                                                                                                    |
   | | ``str``                      |                |                                                                                                                                                    |
   +-+------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**                    | when supported | Returns the captured CDP SDK log.                                                                                                                  |
   |                                |                |                                                                                                                                                    |
   | |br|                           |                |                                                                                                                                                    |
   |                                |                |                                                                                                                                                    |
   | ``str``                        |                |                                                                                                                                                    |
   +--------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**              | when supported | Returns a list of each line of the captured CDP SDK log.                                                                                           |
   |                                |                |                                                                                                                                                    |
   | |br|                           |                |                                                                                                                                                    |
   |                                |                |                                                                                                                                                    |
   | ``list``                       |                |                                                                                                                                                    |
   +--------------------------------+----------------+----------------------------------------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

