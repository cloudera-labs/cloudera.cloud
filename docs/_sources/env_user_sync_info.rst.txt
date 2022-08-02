.. _env_user_sync_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_user_sync_info -- Get the status of a CDP Users and Groups sync

env_user_sync_info -- Get the status of a CDP Users and Groups sync
===================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Get the status of a synchronization event for users and groups with one or more CDP environments.

- The module support check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                                                                                                      |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **name**       |                      | The ``operations id`` for a User and Group sync event or the ``operations CRN`` for the event if the ``WORKLOAD_IAM_SYNC`` entitlement is enabled |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | *Required*     |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                              |
   |                |                      |                                                                                                                                                   |
   |                |                      | *Aliases: operations_id, operations_crn*                                                                                                          |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                                                                                                 |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                              |
   |                |                      |                                                                                                                                                   |
   |                |                      | *Aliases: tls*                                                                                                                                    |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                                                                                                    |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                              |
   |                |                      |                                                                                                                                                   |
   |                |                      | *Aliases: debug_endpoints*                                                                                                                        |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.                                                                                      |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                   |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Get the status of a sync event (non-WORKLOAD_IAM_SYNC)
  - cloudera.cloud.env_user_sync_info:
      name: 0e9bc67a-b308-4275-935c-b8c764dc13be




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **Key**                | **Returned**   | **Description**                                                                                         |
   +------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **sync**               | success        | Returns an object describing of the status of the User and Group sync event.                            |
   |                        |                |                                                                                                         |
   | |br|                   |                |                                                                                                         |
   |                        |                |                                                                                                         |
   | ``complex``            |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **endTime**          | when supported | Sync operation end timestamp (epoch seconds).                                                           |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | |                      |                | |br|                                                                                                    |
   | |                      |                |                                                                                                         |
   | |                      |                | **Sample:**                                                                                             |
   | |                      |                |                                                                                                         |
   | |                      |                | 1602080301000                                                                                           |
   | |                      |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **error**            | when supported | Error message for general failure of sync operation.                                                    |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **failure**          | when supported | List of sync operation details for all failed environments.                                             |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``list``             |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **environmentCrn** | always         | The environment CRN.                                                                                    |
   | | |                    |                |                                                                                                         |
   | | | |br|               |                |                                                                                                         |
   | | |                    |                |                                                                                                         |
   | | | ``str``            |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **message**        | when supported | Details on the failure.                                                                                 |
   | | |                    |                |                                                                                                         |
   | | | |br|               |                |                                                                                                         |
   | | |                    |                |                                                                                                         |
   | | | ``str``            |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **operationId**      | always         | UUID (or CRN, if running with the ``WORKLOAD_IAM_SYNC`` entitlement) of the request for this operation. |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | |                      |                | |br|                                                                                                    |
   | |                      |                |                                                                                                         |
   | |                      |                | **Sample:**                                                                                             |
   | |                      |                |                                                                                                         |
   | |                      |                | 0e9bc67a-b308-4275-935c-b8c764dc13be                                                                    |
   | |                      |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **operationType**    | when supported | The operation type.                                                                                     |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | |                      |                | |br|                                                                                                    |
   | |                      |                |                                                                                                         |
   | |                      |                | **Sample:**                                                                                             |
   | |                      |                |                                                                                                         |
   | |                      |                | USER_SYNC                                                                                               |
   | |                      |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **startTime**        | when supported | Sync operation start timestamp (epoch seconds).                                                         |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | |                      |                | |br|                                                                                                    |
   | |                      |                |                                                                                                         |
   | |                      |                | **Sample:**                                                                                             |
   | |                      |                |                                                                                                         |
   | |                      |                | 1602080301000                                                                                           |
   | |                      |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **status**           | when supported | Status of this operation.                                                                               |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``str``              |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | |                      |                | |br|                                                                                                    |
   | |                      |                |                                                                                                         |
   | |                      |                | **Sample:**                                                                                             |
   | |                      |                |                                                                                                         |
   | |                      |                | NEVER_RUN                                                                                               |
   | |                      |                |                                                                                                         |
   | |                      |                | REQUESTED                                                                                               |
   | |                      |                |                                                                                                         |
   | |                      |                | REJECTED                                                                                                |
   | |                      |                |                                                                                                         |
   | |                      |                | RUNNING                                                                                                 |
   | |                      |                |                                                                                                         |
   | |                      |                | COMPLETED                                                                                               |
   | |                      |                |                                                                                                         |
   | |                      |                | FAILED                                                                                                  |
   | |                      |                |                                                                                                         |
   | |                      |                | TIMEDOUT                                                                                                |
   | |                      |                |                                                                                                         |
   +-+----------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **success**          | when supported | List of sync operation details for all succeeded environments.                                          |
   | |                      |                |                                                                                                         |
   | | |br|                 |                |                                                                                                         |
   | |                      |                |                                                                                                         |
   | | ``list``             |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **environmentCrn** | always         | The environment CRN.                                                                                    |
   | | |                    |                |                                                                                                         |
   | | | |br|               |                |                                                                                                         |
   | | |                    |                |                                                                                                         |
   | | | ``str``            |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **message**        | when supported | Details on the success.                                                                                 |
   | | |                    |                |                                                                                                         |
   | | | |br|               |                |                                                                                                         |
   | | |                    |                |                                                                                                         |
   | | | ``str``            |                |                                                                                                         |
   +-+-+--------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **sdk_out**            | when supported | Returns the captured CDP SDK log.                                                                       |
   |                        |                |                                                                                                         |
   | |br|                   |                |                                                                                                         |
   |                        |                |                                                                                                         |
   | ``str``                |                |                                                                                                         |
   +------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**      | when supported | Returns a list of each line of the captured CDP SDK log.                                                |
   |                        |                |                                                                                                         |
   | |br|                   |                |                                                                                                         |
   |                        |                |                                                                                                         |
   | ``list``               |                |                                                                                                         |
   +------------------------+----------------+---------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Daniel Chaffelson (@chaffelson)

