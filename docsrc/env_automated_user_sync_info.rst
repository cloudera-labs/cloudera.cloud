.. _env_automated_user_sync_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_automated_user_sync_info -- Get the status of the automated CDP Users and Groups synchronization service

env_automated_user_sync_info -- Get the status of the automated CDP Users and Groups synchronization service
============================================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Get the status of the automated synchronization for users and groups for a given Environment.

- Requires the ``WORKLOAD_IAM_SYNC`` entitlement.

- The module support check_mode.



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
   | **name**       |                      | The CDP Environment name or CRN to check.                    |
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

  # Get the status of a sync event (non-WORKLOAD_IAM_SYNC)
  - cloudera.cloud.env_automated_user_sync_info:
      name: example-env




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +------------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | **Key**                | **Returned**   | **Description**                                                                                     |
   +------------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | **sync**               | success        | Returns an object describing of the status of the automated User and Group synchronization service. |
   |                        |                |                                                                                                     |
   | |br|                   |                |                                                                                                     |
   |                        |                |                                                                                                     |
   | ``complex``            |                |                                                                                                     |
   +-+----------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | **environmentCrn**   | always         | The environment CRN.                                                                                |
   | |                      |                |                                                                                                     |
   | | |br|                 |                |                                                                                                     |
   | |                      |                |                                                                                                     |
   | | ``str``              |                |                                                                                                     |
   +-+----------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | **lastSyncStatus**   | always         | Status of the last automated sync operation for the environment.                                    |
   | |                      |                |                                                                                                     |
   | | |br|                 |                |                                                                                                     |
   | |                      |                |                                                                                                     |
   | | ``dict``             |                |                                                                                                     |
   +-+-+--------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | | **status**         | always         | The status of the sync.                                                                             |
   | | |                    |                |                                                                                                     |
   | | | |br|               |                |                                                                                                     |
   | | |                    |                |                                                                                                     |
   | | | ``str``            |                |                                                                                                     |
   | | |                    |                |                                                                                                     |
   | | |                    |                | |br|                                                                                                |
   | | |                    |                |                                                                                                     |
   | | |                    |                | **Sample:**                                                                                         |
   | | |                    |                |                                                                                                     |
   | | |                    |                | UNKNOWN                                                                                             |
   | | |                    |                |                                                                                                     |
   | | |                    |                | SUCCESS                                                                                             |
   | | |                    |                |                                                                                                     |
   | | |                    |                | FAILED                                                                                              |
   | | |                    |                |                                                                                                     |
   +-+-+--------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | | **statusMessages** | when supported | Additional detail related to the status.                                                            |
   | | |                    |                |                                                                                                     |
   | | | |br|               |                |                                                                                                     |
   | | |                    |                |                                                                                                     |
   | | | ``list``           |                |                                                                                                     |
   +-+-+--------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | | **timestamp**      | always         | A datetime stamp of when the sync was processed.                                                    |
   | | |                    |                |                                                                                                     |
   | | | |br|               |                |                                                                                                     |
   | | |                    |                |                                                                                                     |
   | | | ``str``            |                |                                                                                                     |
   +-+-+--------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | | **syncPendingState** | always         | The state indicating whether the environment is synced or has a sync pending.                       |
   | |                      |                |                                                                                                     |
   | | |br|                 |                |                                                                                                     |
   | |                      |                |                                                                                                     |
   | | ``str``              |                |                                                                                                     |
   | |                      |                |                                                                                                     |
   | |                      |                | |br|                                                                                                |
   | |                      |                |                                                                                                     |
   | |                      |                | **Sample:**                                                                                         |
   | |                      |                |                                                                                                     |
   | |                      |                | UNKNOWN                                                                                             |
   | |                      |                |                                                                                                     |
   | |                      |                | SYNC_PENDING                                                                                        |
   | |                      |                |                                                                                                     |
   | |                      |                | SYNCED                                                                                              |
   | |                      |                |                                                                                                     |
   | |                      |                | SYNC_HALTED                                                                                         |
   | |                      |                |                                                                                                     |
   +-+----------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | **sdk_out**            | when supported | Returns the captured CDP SDK log.                                                                   |
   |                        |                |                                                                                                     |
   | |br|                   |                |                                                                                                     |
   |                        |                |                                                                                                     |
   | ``str``                |                |                                                                                                     |
   +------------------------+----------------+-----------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**      | when supported | Returns a list of each line of the captured CDP SDK log.                                            |
   |                        |                |                                                                                                     |
   | |br|                   |                |                                                                                                     |
   |                        |                |                                                                                                     |
   | ``list``               |                |                                                                                                     |
   +------------------------+----------------+-----------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)

