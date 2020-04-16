.. _env_idbroker_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_idbroker -- Update ID Broker for CDP Environments

env_idbroker -- Update ID Broker for CDP Environments
=====================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Update ID Broker mappings for CDP Environments for data access.

- The module supports ``check_mode``.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**           | **Choices/Defaults** | **Comments**                                                                                                                                                  |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **name**                |                      | The name of the Environment.                                                                                                                                  |
   |                         |                      |                                                                                                                                                               |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``str``                 |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | *Required*              |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: environment*                                                                                                                                        |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **data_access**         |                      | The cloud provider IAM role for data access.                                                                                                                  |
   |                         |                      | Must be the cloud provider resource identifier                                                                                                                |
   | |br|                    |                      | For AWS, it should be the ARN                                                                                                                                 |
   |                         |                      | For Azure, it should be the Resource ID                                                                                                                       |
   | ``str``                 |                      | for GCP, it should be the Service Account fully qualified name                                                                                                |
   |                         |                      | for GCP, it should be the Service Account fully qualified name                                                                                                |
   |                         |                      | When creating a new set of data access mappings, this parameter is required.                                                                                  |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: data_access_arn, data*                                                                                                                              |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **ranger_audit**        |                      | The cloud provider role to which services that write to Ranger audit logs will be mapped                                                                      |
   |                         |                      | For AWS, it should be the ARN                                                                                                                                 |
   | |br|                    |                      | For Azure, it should be the Resource ID                                                                                                                       |
   |                         |                      | for GCP, it should be the Service Account fully qualified name                                                                                                |
   | ``str``                 |                      | Note that some data access services also write to Ranger audit logs; such services will be mapped to the ``data_access`` role, not the ``ranger_audit`` role. |
   |                         |                      | Note that some data access services also write to Ranger audit logs; such services will be mapped to the ``data_access`` role, not the ``ranger_audit`` role. |
   |                         |                      | When creating a new set of data access mappings, this parameter is required.                                                                                  |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: ranger_audit_arn, audit*                                                                                                                            |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **ranger_cloud_access** |                      | The cloud provider role to which the Ranger RAZ service will be mapped                                                                                        |
   |                         |                      | For AWS, it should be the ARN                                                                                                                                 |
   | |br|                    |                      | For Azure, it should be the Resource ID                                                                                                                       |
   |                         |                      | for GCP, it should be the Service Account fully qualified name                                                                                                |
   | ``str``                 |                      | This is required in RAZ-enabled environments.                                                                                                                 |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: ranger_cloud_access_arn, cloud*                                                                                                                     |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **mappings**            |                      | ID Broker mappings for individual users and groups.                                                                                                           |
   |                         |                      | Does not include mappings for data access services.                                                                                                           |
   | |br|                    |                      | Mutually exclusive with ``clear_mappings``.                                                                                                                   |
   |                         |                      |                                                                                                                                                               |
   | ``list``                |                      |                                                                                                                                                               |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **clear_mappings**      |                      | Flag to install an empty set of individual mappings, deleting any existing mappings.                                                                          |
   |                         |                      | Mutually exclusive with ``mappings``.                                                                                                                         |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``bool``                |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: set_empty_mappings*                                                                                                                                 |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **sync**                |                      | Flag to sync mappings to the Environment's Datalake(s).                                                                                                       |
   |                         |                      | If the mappings do not need to be synced or there is no Datalake associated with the Environment, the flag will be ignored.                                   |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``bool``                |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: sync_mappings*                                                                                                                                      |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**          |                      | Verify the TLS certificates for the CDP endpoint.                                                                                                             |
   |                         |                      |                                                                                                                                                               |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``bool``                |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: tls*                                                                                                                                                |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**               |                      | Capture the CDP SDK debug log.                                                                                                                                |
   |                         |                      |                                                                                                                                                               |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``bool``                |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | |br|                                                                                                                                                          |
   |                         |                      |                                                                                                                                                               |
   |                         |                      | *Aliases: debug_endpoints*                                                                                                                                    |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**             |                      | If provided, the CDP SDK will use this value as its profile.                                                                                                  |
   |                         |                      |                                                                                                                                                               |
   | |br|                    |                      |                                                                                                                                                               |
   |                         |                      |                                                                                                                                                               |
   | ``str``                 |                      |                                                                                                                                                               |
   +-------------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a fresh set of data access mappings for ID Broker
  - cloudera.cloud.env_idbroker:
      name: example-environment
      data_access: arn:aws:iam::654468598544:role/some-data-access-role
      ranger_audit: arn:aws:iam::654468598544:role/some-ranger-audit-role

  # Set the data access role for ID Broker on an existing environment
  - cloudera.cloud.env_idbroker:
      name: example-environment
      data_access: arn:aws:iam::654468598544:role/some-data-access-role

  # Set the Ranger audit role for ID Broker on an existing environment
  - cloudera.cloud.env_idbroker:
      name: example-environment
      ranger_audit: arn:aws:iam::654468598544:role/some-ranger-audit-role

  # Set some actor-to-role mappings for ID Broker on an existing environment
  - cloudera.cloud.env_idbroker:
      name: example-environment
      mappings:
        - accessor: crn:altus:iam:us-west-1:1234:group:some-group/abcd-1234-efghi
          role: arn:aws:iam::654468598544:role/another-data-access-role

  # Clear the actor-to-role mappings for ID Broker on an existing environment
  - cloudera.cloud.env_idbroker:
      name: example-environment
      clear_mappings: yes

  # Don't sync the mappings for ID Broker to the environment's datalakes
  - cloudera.cloud.env_idbroker:
      name: example-environment
      mappings:
        - accessor: crn:altus:iam:us-west-1:1234:group:some-group/abcd-1234-efghi
          role: arn:aws:iam::654468598544:role/another-data-access-role
      sync: no

  # Now sync the mappings for the ID Broker once the environment has a datalake
  - cloudera.cloud.env_idbroker:
      name: example-environment
      sync: yes




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Key**                               | **Returned**   | **Description**                                                                                                                                       |
   +---------------------------------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **idbroker**                          | always         | Returns the mappings and sync status for the ID Broker for the Environment.                                                                           |
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

