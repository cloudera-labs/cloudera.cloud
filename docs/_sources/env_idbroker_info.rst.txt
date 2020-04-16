.. _env_idbroker_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_idbroker_info -- Gather information about CDP ID Broker

env_idbroker_info -- Gather information about CDP ID Broker
===========================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about the ID Broker mappings for a CDP Environment.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+--------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                 |
   +----------------+----------------------+--------------------------------------------------------------+
   | **name**       |                      | The name of the Environment.                                 |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``str``        |                      |                                                              |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | *Required*     |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: environment*                                       |
   +----------------+----------------------+--------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.            |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``bool``       |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: tls*                                               |
   +----------------+----------------------+--------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                               |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``bool``       |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: debug_endpoints*                                   |
   +----------------+----------------------+--------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile. |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``str``        |                      |                                                              |
   +----------------+----------------------+--------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about the ID Broker mappings
  - cloudera.cloud.env_idbroker_info:
      name: example-environment




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Key**                               | **Returned**   | **Description**                                                                                                                                       |
   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **idbroker**                          | when supported | Returns the mappings and sync status for the ID Broker for the Environment.                                                                           |
   |                                       |                |                                                                                                                                                       |
   | |br|                                  |                |                                                                                                                                                       |
   |                                       |                |                                                                                                                                                       |
   | ``dict``                              |                |                                                                                                                                                       |
   +-+-------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **mappingsVersion**                 | always         | The version of the mappings.                                                                                                                          |
   | |                                     |                |                                                                                                                                                       |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``str``                             |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | |                                     |                | |br|                                                                                                                                                  |
   | |                                     |                |                                                                                                                                                       |
   | |                                     |                | **Sample:**                                                                                                                                           |
   | |                                     |                |                                                                                                                                                       |
   | |                                     |                | AWS                                                                                                                                                   |
   | |                                     |                |                                                                                                                                                       |
   +-+-------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **dataAccessRole**                  | always         | The cloud provider role to which data access services will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).                                    |
   | |                                     |                |                                                                                                                                                       |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``str``                             |                |                                                                                                                                                       |
   +-+-------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **rangerAuditRole**                 | always         | The cloud provider role to which services that write to Ranger audit logs will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).                |
   | |                                     |                | Note that some data access services also write to Ranger audit logs; such services will be mapped to the 'dataAccessRole', not the 'rangerAuditRole'. |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``str``                             |                |                                                                                                                                                       |
   +-+-------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **rangerCloudAccessAuthorizerRole** | when supported | The cloud provider role to which the Ranger RAZ service will be mapped (e.g. an ARN in AWS, a Resource ID in Azure).                                  |
   | |                                     |                |                                                                                                                                                       |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``str``                             |                |                                                                                                                                                       |
   +-+-------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **mappings**                        | when supported | ID Broker mappings for individual actors and groups. Does not include mappings for data access services.                                              |
   | |                                     |                |                                                                                                                                                       |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``list``                            |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **accessorCrn**                   | on success     | The CRN of the actor (group or user) mapped to the cloud provider role.                                                                               |
   | | |                                   |                |                                                                                                                                                       |
   | | | |br|                              |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | | ``str``                           |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **role**                          | on success     | The cloud provider identitier for the role.                                                                                                           |
   | | |                                   |                |                                                                                                                                                       |
   | | | |br|                              |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | | ``str``                           |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | **syncStatus**                      | when supported | The status of the most recent ID Broker mappings sync operation, if any. Not present if there is no Datalake associated with the Environment.         |
   | |                                     |                |                                                                                                                                                       |
   | | |br|                                |                |                                                                                                                                                       |
   | |                                     |                |                                                                                                                                                       |
   | | ``dict``                            |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **globalStatus**                  | always         | The overall mappings sync status for all Datalake clusters in the Environment.                                                                        |
   | | |                                   |                |                                                                                                                                                       |
   | | | |br|                              |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | | ``str``                           |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | |br|                                                                                                                                                  |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | **Sample:**                                                                                                                                           |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | NEVER_RUN                                                                                                                                             |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | REQUESTED                                                                                                                                             |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | REJECTED                                                                                                                                              |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | RUNNING                                                                                                                                               |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | COMPLETED                                                                                                                                             |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | FAILED                                                                                                                                                |
   | | |                                   |                |                                                                                                                                                       |
   | | |                                   |                | TIMEDOUT                                                                                                                                              |
   | | |                                   |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **syncNeeded**                    | always         | Flag indicating whether a sync is needed to bring in-cluster mappings up-to-date.                                                                     |
   | | |                                   |                |                                                                                                                                                       |
   | | | |br|                              |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | | ``bool``                          |                |                                                                                                                                                       |
   +-+-+-----------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | **statuses**                      | always         | Map of Datalake cluster CRN-to-mappings sync status for each Datalake cluster in the environment.                                                     |
   | | |                                   |                |                                                                                                                                                       |
   | | | |br|                              |                |                                                                                                                                                       |
   | | |                                   |                |                                                                                                                                                       |
   | | | ``dict``                          |                |                                                                                                                                                       |
   +-+-+-+---------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | **__datalake CRN__**            | always         | The Datalake cluster CRN                                                                                                                              |
   | | | |                                 |                |                                                                                                                                                       |
   | | | | |br|                            |                |                                                                                                                                                       |
   | | | |                                 |                |                                                                                                                                                       |
   | | | | ``dict``                        |                |                                                                                                                                                       |
   +-+-+-+-+-------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **endDate**                   | when supported | The date when the mappings sync completed or was terminated. Omitted if status is NEVER_RUN or RUNNING.                                               |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | |br|                          |                |                                                                                                                                                       |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | ``str``                       |                |                                                                                                                                                       |
   +-+-+-+-+-------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **errorDetail**               | when supported | The detail of the error. Omitted if status is not FAILED.                                                                                             |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | |br|                          |                |                                                                                                                                                       |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | ``str``                       |                |                                                                                                                                                       |
   +-+-+-+-+-------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **startDate**                 | when supported | The date when the mappings sync started executing. Omitted if status is NEVER_RUN.                                                                    |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | |br|                          |                |                                                                                                                                                       |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | ``str``                       |                |                                                                                                                                                       |
   +-+-+-+-+-------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | | | | | **status**                    | always         | The mappings sync summary status.                                                                                                                     |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | |br|                          |                |                                                                                                                                                       |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | | ``str``                       |                |                                                                                                                                                       |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | |br|                                                                                                                                                  |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | **Sample:**                                                                                                                                           |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | NEVER_RUN                                                                                                                                             |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | REQUESTED                                                                                                                                             |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | REJECTED                                                                                                                                              |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | RUNNING                                                                                                                                               |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | COMPLETED                                                                                                                                             |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | FAILED                                                                                                                                                |
   | | | | |                               |                |                                                                                                                                                       |
   | | | | |                               |                | TIMEDOUT                                                                                                                                              |
   | | | | |                               |                |                                                                                                                                                       |
   +-+-+-+-+-------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**                           | when supported | Returns the captured CDP SDK log.                                                                                                                     |
   |                                       |                |                                                                                                                                                       |
   | |br|                                  |                |                                                                                                                                                       |
   |                                       |                |                                                                                                                                                       |
   | ``str``                               |                |                                                                                                                                                       |
   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**                     | when supported | Returns a list of each line of the captured CDP SDK log.                                                                                              |
   |                                       |                |                                                                                                                                                       |
   | |br|                                  |                |                                                                                                                                                       |
   |                                       |                |                                                                                                                                                       |
   | ``list``                              |                |                                                                                                                                                       |
   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

