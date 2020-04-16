.. _account_auth_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: account_auth_info -- Gather information about CDP Account authentication settings

account_auth_info -- Gather information about CDP Account authentication settings
=================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about the authentication settings for a CDP Account.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+-------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                            |
   +----------------+----------------------+-------------------------------------------------------------------------+
   | **debug**      |                      | Flag to capture and return the debugging log of the underlying CDP SDK. |
   |                |                      | If set, the log level will be set from ERROR to DEBUG.                  |
   | |br|           |                      |                                                                         |
   |                |                      |                                                                         |
   | ``bool``       |                      |                                                                         |
   |                |                      |                                                                         |
   |                |                      | |br|                                                                    |
   |                |                      |                                                                         |
   |                |                      | *Aliases: debug_cdpsdk*                                                 |
   +----------------+----------------------+-------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                       |
   |                |                      |                                                                         |
   | |br|           |                      |                                                                         |
   |                |                      |                                                                         |
   | ``bool``       |                      |                                                                         |
   |                |                      |                                                                         |
   |                |                      | |br|                                                                    |
   |                |                      |                                                                         |
   |                |                      | *Aliases: tls*                                                          |
   +----------------+----------------------+-------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.            |
   |                |                      |                                                                         |
   | |br|           |                      |                                                                         |
   |                |                      |                                                                         |
   | ``str``        |                      |                                                                         |
   +----------------+----------------------+-------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about the Account authentication settings
  - cloudera.cloud.account_auth_info:




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +---------------------------------+----------------+-----------------------------------------------------------------------------+
   | **Key**                         | **Returned**   | **Description**                                                             |
   +---------------------------------+----------------+-----------------------------------------------------------------------------+
   | **account**                     | always         | Returns the authentication settings for the CDP Account                     |
   |                                 |                |                                                                             |
   | |br|                            |                |                                                                             |
   |                                 |                |                                                                             |
   | ``dict``                        |                |                                                                             |
   +-+-------------------------------+----------------+-----------------------------------------------------------------------------+
   | | **clouderaSSOLoginEnabled**   | always         | Flag indicating whether interactive login using Cloudera SSO is enabled.    |
   | |                               |                |                                                                             |
   | | |br|                          |                |                                                                             |
   | |                               |                |                                                                             |
   | | ``bool``                      |                |                                                                             |
   +-+-------------------------------+----------------+-----------------------------------------------------------------------------+
   | | **workloadPasswordPolicy**    | always         | Information about the workload password policy for an account.              |
   | |                               |                |                                                                             |
   | | |br|                          |                |                                                                             |
   | |                               |                |                                                                             |
   | | ``dict``                      |                |                                                                             |
   +-+-+-----------------------------+----------------+-----------------------------------------------------------------------------+
   | | | **maxPasswordLifetimeDays** | always         | The max lifetime, in days, of the password. If '0', passwords never expire. |
   | | |                             |                |                                                                             |
   | | | |br|                        |                |                                                                             |
   | | |                             |                |                                                                             |
   | | | ``int``                     |                |                                                                             |
   +-+-+-----------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out**                     | when supported | Returns the captured CDP SDK log.                                           |
   |                                 |                |                                                                             |
   | |br|                            |                |                                                                             |
   |                                 |                |                                                                             |
   | ``str``                         |                |                                                                             |
   +---------------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out_lines**               | when supported | Returns a list of each line of the captured CDP SDK log.                    |
   |                                 |                |                                                                             |
   | |br|                            |                |                                                                             |
   |                                 |                |                                                                             |
   | ``list``                        |                |                                                                             |
   +---------------------------------+----------------+-----------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

