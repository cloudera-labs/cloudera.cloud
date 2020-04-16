.. _datalake_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datalake_info -- Gather information about CDP Datalakes

datalake_info -- Gather information about CDP Datalakes
=======================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Datalakes



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults** | **Comments**                                                                                                     |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **name**        |                      | If a name is given, that Datalake will be described.                                                             |
   |                 |                      | If no name is given, all Datalakes will be listed and (optionally) constrained by the ``environment`` parameter. |
   | |br|            |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   | ``str``         |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   |                 |                      | |br|                                                                                                             |
   |                 |                      |                                                                                                                  |
   |                 |                      | *Aliases: datalake*                                                                                              |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **environment** |                      | The name of the Environment in which to find and describe the Datalake.                                          |
   |                 |                      |                                                                                                                  |
   | |br|            |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   | ``str``         |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   |                 |                      | |br|                                                                                                             |
   |                 |                      |                                                                                                                  |
   |                 |                      | *Aliases: env*                                                                                                   |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**  |                      | Verify the TLS certificates for the CDP endpoint.                                                                |
   |                 |                      |                                                                                                                  |
   | |br|            |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   | ``bool``        |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   |                 |                      | |br|                                                                                                             |
   |                 |                      |                                                                                                                  |
   |                 |                      | *Aliases: tls*                                                                                                   |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **debug**       |                      | Capture the CDP SDK debug log.                                                                                   |
   |                 |                      |                                                                                                                  |
   | |br|            |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   | ``bool``        |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   |                 |                      | |br|                                                                                                             |
   |                 |                      |                                                                                                                  |
   |                 |                      | *Aliases: debug_endpoints*                                                                                       |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+
   | **profile**     |                      | If provided, the CDP SDK will use this value as its profile.                                                     |
   |                 |                      |                                                                                                                  |
   | |br|            |                      |                                                                                                                  |
   |                 |                      |                                                                                                                  |
   | ``str``         |                      |                                                                                                                  |
   +-----------------+----------------------+------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all Datalakes
  - cloudera.cloud.datalake_info:

  # Gather detailed information about a named Datalake
  - cloudera.cloud.datalake_info:
      name: example-datalake

  # Gather detailed information about the Datalake in an Environment
  - cloudera.cloud.datalake_info:
      environment: example-env




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------------------+----------------+----------------------------------------------------------------+
   | **Key**                              | **Returned**   | **Description**                                                |
   +--------------------------------------+----------------+----------------------------------------------------------------+
   | **datalakes**                        | on success     | The information about the named Datalake or Datalakes          |
   |                                      |                |                                                                |
   | |br|                                 |                |                                                                |
   |                                      |                |                                                                |
   | ``list``                             |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **awsConfiguration**               | when supported | AWS-specific configuration details.                            |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``dict``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **instanceProfile**              | always         | The instance profile used for the ID Broker instance.          |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | **azureConfiguration**             | when supported | Azure-specific environment configuration information.          |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``dict``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **managedIdentity**              | always         | The managed identity used for the ID Broker instance.          |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | **cloudPlatform**                  | when supported | Cloud provider of the Datalake.                                |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   | |                                    |                |                                                                |
   | |                                    |                | |br|                                                           |
   | |                                    |                |                                                                |
   | |                                    |                | **Sample:**                                                    |
   | |                                    |                |                                                                |
   | |                                    |                | AWS                                                            |
   | |                                    |                |                                                                |
   | |                                    |                | AZURE                                                          |
   | |                                    |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **clouderaManager**                | when supported | The Cloudera Manager details.                                  |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``dict``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **clouderaManagerRepositoryURL** | always         | Cloudera Manager repository URL.                               |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **clouderaManagerServerURL**     | when supported | Cloudera Manager server URL.                                   |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **version**                      | always         | Cloudera Manager version.                                      |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   | | |                                  |                |                                                                |
   | | |                                  |                | |br|                                                           |
   | | |                                  |                |                                                                |
   | | |                                  |                | **Sample:**                                                    |
   | | |                                  |                |                                                                |
   | | |                                  |                | 7.2.1                                                          |
   | | |                                  |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | **creationDate**                   | when supported | The timestamp when the Datalake was created.                   |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   | |                                    |                |                                                                |
   | |                                    |                | |br|                                                           |
   | |                                    |                |                                                                |
   | |                                    |                | **Sample:**                                                    |
   | |                                    |                |                                                                |
   | |                                    |                | 2020-09-23 11:33:50.847000+00:00                               |
   | |                                    |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **credentialCrn**                  | when supported | CRN of the CDP Credential.                                     |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **crn**                            | always         | CRN value for the Datalake.                                    |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **datalakeName**                   | always         | Name of the Datalake.                                          |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **endpoints**                      | when supported | Details for the exposed service API endpoints of the Datalake. |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``dict``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **endpoints**                    | always         | The exposed API endpoints.                                     |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``list``                         |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **displayName**                | always         | User-friendly name of the exposed service.                     |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | Atlas                                                          |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **knoxService**                | always         | The related Knox entry for the service.                        |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | ATLAS_API                                                      |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **mode**                       | always         | The Single Sign-On (SSO) mode for the service.                 |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | PAM                                                            |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **open**                       | always         | Flag for the access status of the service.                     |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``bool``                       |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **serviceName**                | always         | The name of the exposed service.                               |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | ATLAS_SERVER                                                   |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **serviceUrl**                 | always         | The server URL for the exposed service’s API.                  |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | https://some.domain/a-datalake/endpoint                        |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | **environmentCrn**                 | when supported | CRN of the associated Environment.                             |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **instanceGroups**                 | when supported | The instance details of the Datalake.                          |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``list``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **instances**                    | always         | Details about the instances.                                   |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``list``                         |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **id**                         | always         | The identifier of the instance.                                |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | i-00b58f27be4e7ab9f                                            |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | | **state**                      | always         | The state of the instance.                                     |
   | | | |                                |                |                                                                |
   | | | | |br|                           |                |                                                                |
   | | | |                                |                |                                                                |
   | | | | ``str``                        |                |                                                                |
   | | | |                                |                |                                                                |
   | | | |                                |                | |br|                                                           |
   | | | |                                |                |                                                                |
   | | | |                                |                | **Sample:**                                                    |
   | | | |                                |                |                                                                |
   | | | |                                |                | HEALTHY                                                        |
   | | | |                                |                |                                                                |
   +-+-+-+--------------------------------+----------------+----------------------------------------------------------------+
   | | | **name**                         | always         | Name of the instance group associated with the instances.      |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   | | |                                  |                |                                                                |
   | | |                                  |                | |br|                                                           |
   | | |                                  |                |                                                                |
   | | |                                  |                | **Sample:**                                                    |
   | | |                                  |                |                                                                |
   | | |                                  |                | idbroker                                                       |
   | | |                                  |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | **productVersions**                | when supported | The product versions.                                          |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``list``                           |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **name**                         | always         | The name of the product.                                       |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   | | |                                  |                |                                                                |
   | | |                                  |                | |br|                                                           |
   | | |                                  |                |                                                                |
   | | |                                  |                | **Sample:**                                                    |
   | | |                                  |                |                                                                |
   | | |                                  |                | FLINK                                                          |
   | | |                                  |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | | **version**                      | always         | The version of the product.                                    |
   | | |                                  |                |                                                                |
   | | | |br|                             |                |                                                                |
   | | |                                  |                |                                                                |
   | | | ``str``                          |                |                                                                |
   | | |                                  |                |                                                                |
   | | |                                  |                | |br|                                                           |
   | | |                                  |                |                                                                |
   | | |                                  |                | **Sample:**                                                    |
   | | |                                  |                |                                                                |
   | | |                                  |                | 1.10.0-csa1.2.1.0-cdh7.2.1.0-240-4844562                       |
   | | |                                  |                |                                                                |
   +-+-+----------------------------------+----------------+----------------------------------------------------------------+
   | | **region**                         | when supported | The region of the Datalake.                                    |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **status**                         | when supported | The status of the Datalake.                                    |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   | |                                    |                |                                                                |
   | |                                    |                | |br|                                                           |
   | |                                    |                |                                                                |
   | |                                    |                | **Sample:**                                                    |
   | |                                    |                |                                                                |
   | |                                    |                | EXTERNAL_DATABASE_START_IN_PROGRESS                            |
   | |                                    |                |                                                                |
   | |                                    |                | START_IN_PROGRESS                                              |
   | |                                    |                |                                                                |
   | |                                    |                | RUNNING                                                        |
   | |                                    |                |                                                                |
   | |                                    |                | EXTERNAL_DATABASE_START_IN_PROGRESS                            |
   | |                                    |                |                                                                |
   | |                                    |                | START_IN_PROGRESS                                              |
   | |                                    |                |                                                                |
   | |                                    |                | EXTERNAL_DATABASE_STOP_IN_PROGRESS                             |
   | |                                    |                |                                                                |
   | |                                    |                | STOP_IN_PROGRESS                                               |
   | |                                    |                |                                                                |
   | |                                    |                | STOPPED                                                        |
   | |                                    |                |                                                                |
   | |                                    |                | REQUESTED                                                      |
   | |                                    |                |                                                                |
   | |                                    |                | EXTERNAL_DATABASE_CREATION_IN_PROGRESS                         |
   | |                                    |                |                                                                |
   | |                                    |                | STACK_CREATION_IN_PROGRESS                                     |
   | |                                    |                |                                                                |
   | |                                    |                | EXTERNAL_DATABASE_DELETION_IN_PROGRESS                         |
   | |                                    |                |                                                                |
   | |                                    |                | STACK_DELETION_IN_PROGRESS                                     |
   | |                                    |                |                                                                |
   | |                                    |                | PROVISIONING_FAILED                                            |
   | |                                    |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | | **statusReason**                   | when supported | An explanation of the status.                                  |
   | |                                    |                |                                                                |
   | | |br|                               |                |                                                                |
   | |                                    |                |                                                                |
   | | ``str``                            |                |                                                                |
   | |                                    |                |                                                                |
   | |                                    |                | |br|                                                           |
   | |                                    |                |                                                                |
   | |                                    |                | **Sample:**                                                    |
   | |                                    |                |                                                                |
   | |                                    |                | Datalake is running                                            |
   | |                                    |                |                                                                |
   +-+------------------------------------+----------------+----------------------------------------------------------------+
   | **sdk_out**                          | when supported | Returns the captured CDP SDK log.                              |
   |                                      |                |                                                                |
   | |br|                                 |                |                                                                |
   |                                      |                |                                                                |
   | ``str``                              |                |                                                                |
   +--------------------------------------+----------------+----------------------------------------------------------------+
   | **sdk_out_lines**                    | when supported | Returns a list of each line of the captured CDP SDK log.       |
   |                                      |                |                                                                |
   | |br|                                 |                |                                                                |
   |                                      |                |                                                                |
   | ``list``                             |                |                                                                |
   +--------------------------------------+----------------+----------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

