.. _datalake_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datalake -- Manage CDP Datalakes

datalake -- Manage CDP Datalakes
================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create and delete CDP Datalakes.

- To start and stop a datalake, use the :ref:`env <env_module>` module to change the associated CDP Environment's state.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**        | **Choices/Defaults**     | **Comments**                                                                                                                     |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **name**             |                          | The name of the datalake.                                                                                                        |
   |                      |                          | This name must be unique, must have between 5 and 100 characters, and must contain only lowercase letters, numbers, and hyphens. |
   | |br|                 |                          | Names are case-sensitive.                                                                                                        |
   |                      |                          |                                                                                                                                  |
   | ``str``              |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | *Required*           |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: datalake*                                                                                                              |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **state**            | **Choices:**             | The declarative state of the datalake.                                                                                           |
   |                      |  - **present** |larr|    | If creating a datalake, the associate environment must be started as well.                                                       |
   | |br|                 |  - absent                |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **environment**      | **Choices:**             | The CDP environment name or CRN to which the datalake will be attached.                                                          |
   |                      |  - env                   | If the environment is AWS-based, *instance_profile* and *storage* must be present.                                               |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **instance_profile** |                          | (AWS) The IAM instance profile of the ID Broker role, which can assume the Datalake Admin S3 role.                               |
   |                      |                          | (Azure) The URI of the Identity of the ID Broker Role, which can assume the Datalake Admin ADLS role.                            |
   | |br|                 |                          | (GCP) The Service Account email of the ID Broker Role, which can assume the Datalake Admin GCS role.                             |
   |                      |                          |                                                                                                                                  |
   | ``str``              |                          |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **storage**          |                          | (AWS) The S3 bucket (and optional path) for the Storage Location Base for the datalake, starting with ``s3a://``                 |
   |                      |                          | (Azure) The ADLS bucket URI (and optional path) for the Datalake storage                                                         |
   | |br|                 |                          | (GCP) The bucket name and optional path for the GCS Storage Location Base for the Datalake, starting with ``gs://``              |
   |                      |                          |                                                                                                                                  |
   | ``str``              |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: storage_location, storage_location_base*                                                                               |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **runtime**          |                          | The Cloudera Runtime version for the datalake, when supported                                                                    |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``str``              |                          |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **scale**            | **Choices:**             | The scale of the datalake.                                                                                                       |
   |                      |  - **LIGHT_DUTY** |larr| |                                                                                                                                  |
   | |br|                 |  - MEDIUM_DUTY_HA        |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **tags**             |                          | Tags associated with the datalake and its resources.                                                                             |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``dict``             |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: datalake_tags*                                                                                                         |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **force**            |                          | Flag indicating if the datalake should be force deleted.                                                                         |
   |                      |                          | This option can be used when cluster deletion fails.                                                                             |
   | |br|                 |                          | This removes the entry from Cloudera Datalake service.                                                                           |
   |                      |                          | Any lingering resources have to be deleted from the cloud provider manually.                                                     |
   | ``bool``             |                          |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **wait**             |                          | Flag to enable internal polling to wait for the datalake to achieve the declared state.                                          |
   |                      |                          | If set to FALSE, the module will return immediately.                                                                             |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``bool``             |                          |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **delay**            |                          | The internal polling interval (in seconds) while the module waits for the datalake to reach the declared state.                  |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``int``              |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: polling_delay*                                                                                                         |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **timeout**          |                          | The internal polling timeout (in seconds) while the module waits for the datalake to achieve the declared state.                 |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``int``              |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: polling_timeout*                                                                                                       |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**       |                          | Verify the TLS certificates for the CDP endpoint.                                                                                |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``bool``             |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: tls*                                                                                                                   |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **debug**            |                          | Capture the CDP SDK debug log.                                                                                                   |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``bool``             |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   |                      |                          | |br|                                                                                                                             |
   |                      |                          |                                                                                                                                  |
   |                      |                          | *Aliases: debug_endpoints*                                                                                                       |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **profile**          |                          | If provided, the CDP SDK will use this value as its profile.                                                                     |
   |                      |                          |                                                                                                                                  |
   | |br|                 |                          |                                                                                                                                  |
   |                      |                          |                                                                                                                                  |
   | ``str``              |                          |                                                                                                                                  |
   +----------------------+--------------------------+----------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a datalake in AWS
  - cloudera.cloud.datalake:
      name: example-datalake
      state: present
      environment: an-aws-environment-name-or-crn
      instance_profile: arn:aws:iam::1111104421142:instance-profile/example-role
      storage: s3a://example-bucket/datalake/data
      tags:
        project: Arbitrary content

  # Create a datalake in AWS, but don't wait for completion (see datalake_info for datalake status)
  - cloudera.cloud.datalake:
      name: example-datalake
      state: present
      wait: no
      environment: an-aws-environment-name-or-crn
      instance_profile: arn:aws:iam::1111104421142:instance-profile/example-role
      storage: s3a://example-bucket/datalake/data
      tags:
        project: Arbitrary content

  # Delete the datalake (and wait for status change)
    cloudera.cloud.datalake:
      name: example-datalake
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------------------+----------------+-------------------------------------------------------------------------+
   | **Key**                              | **Returned**   | **Description**                                                         |
   +--------------------------------------+----------------+-------------------------------------------------------------------------+
   | **datalake**                         | on success     | The information about the Datalake                                      |
   |                                      |                |                                                                         |
   | |br|                                 |                |                                                                         |
   |                                      |                |                                                                         |
   | ``dict``                             |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **awsConfiguration**               | when supported | AWS-specific configuration details.                                     |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``dict``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **instanceProfile**              | always         | The instance profile used for the ID Broker instance.                   |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **azureConfiguration**             | when supported | Azure-specific environment configuration information.                   |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``dict``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **managedIdentity**              | always         | The managed identity used for the ID Broker instance.                   |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **gcpConfiguration**               | when supported | GCP-specific environment configuration information.                     |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``dict``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **serviceAccountEmail**          | always         | The email id of the service account used for  the  ID  Broker instance. |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **cloudPlatform**                  | when supported | Cloud provider of the Datalake.                                         |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   | |                                    |                |                                                                         |
   | |                                    |                | |br|                                                                    |
   | |                                    |                |                                                                         |
   | |                                    |                | **Sample:**                                                             |
   | |                                    |                |                                                                         |
   | |                                    |                | AWS                                                                     |
   | |                                    |                |                                                                         |
   | |                                    |                | AZURE                                                                   |
   | |                                    |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **clouderaManager**                | when supported | The Cloudera Manager details.                                           |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``dict``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **clouderaManagerRepositoryURL** | always         | Cloudera Manager repository URL.                                        |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **clouderaManagerServerURL**     | when supported | Cloudera Manager server URL.                                            |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **version**                      | always         | Cloudera Manager version.                                               |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | |                                  |                | |br|                                                                    |
   | | |                                  |                |                                                                         |
   | | |                                  |                | **Sample:**                                                             |
   | | |                                  |                |                                                                         |
   | | |                                  |                | 7.2.1                                                                   |
   | | |                                  |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **creationDate**                   | when supported | The timestamp when the Datalake was created.                            |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   | |                                    |                |                                                                         |
   | |                                    |                | |br|                                                                    |
   | |                                    |                |                                                                         |
   | |                                    |                | **Sample:**                                                             |
   | |                                    |                |                                                                         |
   | |                                    |                | 2020-09-23 11:33:50.847000+00:00                                        |
   | |                                    |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **credentialCrn**                  | when supported | CRN of the CDP Credential.                                              |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **crn**                            | always         | CRN value for the Datalake.                                             |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **datalakeName**                   | always         | Name of the Datalake.                                                   |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **endpoints**                      | when supported | Details for the exposed service API endpoints of the Datalake.          |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``dict``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **endpoints**                    | always         | The exposed API endpoints.                                              |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``list``                         |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **displayName**                | always         | User-friendly name of the exposed service.                              |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | Atlas                                                                   |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **knoxService**                | always         | The related Knox entry for the service.                                 |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | ATLAS_API                                                               |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **mode**                       | always         | The Single Sign-On (SSO) mode for the service.                          |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | PAM                                                                     |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **open**                       | always         | Flag for the access status of the service.                              |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``bool``                       |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **serviceName**                | always         | The name of the exposed service.                                        |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | ATLAS_SERVER                                                            |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **serviceUrl**                 | always         | The server URL for the exposed service’s API.                           |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | https://some.domain/a-datalake/endpoint                                 |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | **environmentCrn**                 | when supported | CRN of the associated Environment.                                      |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **instanceGroups**                 | when supported | The instance details of the Datalake.                                   |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``list``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **instances**                    | always         | Details about the instances.                                            |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``list``                         |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **id**                         | always         | The identifier of the instance.                                         |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | i-00b58f27be4e7ab9f                                                     |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | | **state**                      | always         | The state of the instance.                                              |
   | | | |                                |                |                                                                         |
   | | | | |br|                           |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | | ``str``                        |                |                                                                         |
   | | | |                                |                |                                                                         |
   | | | |                                |                | |br|                                                                    |
   | | | |                                |                |                                                                         |
   | | | |                                |                | **Sample:**                                                             |
   | | | |                                |                |                                                                         |
   | | | |                                |                | HEALTHY                                                                 |
   | | | |                                |                |                                                                         |
   +-+-+-+--------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **name**                         | always         | Name of the instance group associated with the instances.               |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | |                                  |                | |br|                                                                    |
   | | |                                  |                |                                                                         |
   | | |                                  |                | **Sample:**                                                             |
   | | |                                  |                |                                                                         |
   | | |                                  |                | idbroker                                                                |
   | | |                                  |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **productVersions**                | when supported | The product versions.                                                   |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``list``                           |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **name**                         | always         | The name of the product.                                                |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | |                                  |                | |br|                                                                    |
   | | |                                  |                |                                                                         |
   | | |                                  |                | **Sample:**                                                             |
   | | |                                  |                |                                                                         |
   | | |                                  |                | FLINK                                                                   |
   | | |                                  |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | | **version**                      | always         | The version of the product.                                             |
   | | |                                  |                |                                                                         |
   | | | |br|                             |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | | ``str``                          |                |                                                                         |
   | | |                                  |                |                                                                         |
   | | |                                  |                | |br|                                                                    |
   | | |                                  |                |                                                                         |
   | | |                                  |                | **Sample:**                                                             |
   | | |                                  |                |                                                                         |
   | | |                                  |                | 1.10.0-csa1.2.1.0-cdh7.2.1.0-240-4844562                                |
   | | |                                  |                |                                                                         |
   +-+-+----------------------------------+----------------+-------------------------------------------------------------------------+
   | | **region**                         | when supported | The region of the Datalake.                                             |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **status**                         | when supported | The status of the Datalake.                                             |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   | |                                    |                |                                                                         |
   | |                                    |                | |br|                                                                    |
   | |                                    |                |                                                                         |
   | |                                    |                | **Sample:**                                                             |
   | |                                    |                |                                                                         |
   | |                                    |                | EXTERNAL_DATABASE_START_IN_PROGRESS                                     |
   | |                                    |                |                                                                         |
   | |                                    |                | START_IN_PROGRESS                                                       |
   | |                                    |                |                                                                         |
   | |                                    |                | RUNNING                                                                 |
   | |                                    |                |                                                                         |
   | |                                    |                | EXTERNAL_DATABASE_START_IN_PROGRESS                                     |
   | |                                    |                |                                                                         |
   | |                                    |                | START_IN_PROGRESS                                                       |
   | |                                    |                |                                                                         |
   | |                                    |                | EXTERNAL_DATABASE_STOP_IN_PROGRESS                                      |
   | |                                    |                |                                                                         |
   | |                                    |                | STOP_IN_PROGRESS                                                        |
   | |                                    |                |                                                                         |
   | |                                    |                | STOPPED                                                                 |
   | |                                    |                |                                                                         |
   | |                                    |                | REQUESTED                                                               |
   | |                                    |                |                                                                         |
   | |                                    |                | EXTERNAL_DATABASE_CREATION_IN_PROGRESS                                  |
   | |                                    |                |                                                                         |
   | |                                    |                | STACK_CREATION_IN_PROGRESS                                              |
   | |                                    |                |                                                                         |
   | |                                    |                | EXTERNAL_DATABASE_DELETION_IN_PROGRESS                                  |
   | |                                    |                |                                                                         |
   | |                                    |                | STACK_DELETION_IN_PROGRESS                                              |
   | |                                    |                |                                                                         |
   | |                                    |                | PROVISIONING_FAILED                                                     |
   | |                                    |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | | **statusReason**                   | when supported | An explanation of the status.                                           |
   | |                                    |                |                                                                         |
   | | |br|                               |                |                                                                         |
   | |                                    |                |                                                                         |
   | | ``str``                            |                |                                                                         |
   | |                                    |                |                                                                         |
   | |                                    |                | |br|                                                                    |
   | |                                    |                |                                                                         |
   | |                                    |                | **Sample:**                                                             |
   | |                                    |                |                                                                         |
   | |                                    |                | Datalake is running                                                     |
   | |                                    |                |                                                                         |
   +-+------------------------------------+----------------+-------------------------------------------------------------------------+
   | **sdk_out**                          | when supported | Returns the captured CDP SDK log.                                       |
   |                                      |                |                                                                         |
   | |br|                                 |                |                                                                         |
   |                                      |                |                                                                         |
   | ``str``                              |                |                                                                         |
   +--------------------------------------+----------------+-------------------------------------------------------------------------+
   | **sdk_out_lines**                    | when supported | Returns a list of each line of the captured CDP SDK log.                |
   |                                      |                |                                                                         |
   | |br|                                 |                |                                                                         |
   |                                      |                |                                                                         |
   | ``list``                             |                |                                                                         |
   +--------------------------------------+----------------+-------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

