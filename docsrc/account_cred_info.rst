.. _account_cred_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: account_cred_info -- Gather information about Account prerequisites for CDP Credentials

account_cred_info -- Gather information about Account prerequisites for CDP Credentials
=======================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather prerequisites information from the Account for creating CDP Credentials using the CDP SDK.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+-----------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                    |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **cloud**      | **Choices:**         | Designates the cloud provider for the credential prerequisites. |
   |                |  - aws               |                                                                 |
   | |br|           |  - azure             |                                                                 |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.               |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``bool``       |                      |                                                                 |
   |                |                      |                                                                 |
   |                |                      | |br|                                                            |
   |                |                      |                                                                 |
   |                |                      | *Aliases: tls*                                                  |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                  |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``bool``       |                      |                                                                 |
   |                |                      |                                                                 |
   |                |                      | |br|                                                            |
   |                |                      |                                                                 |
   |                |                      | *Aliases: debug_endpoints*                                      |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.    |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``str``        |                      |                                                                 |
   +----------------+----------------------+-----------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about the AWS account credential prerequisites
  - cloudera.cloud.account_cred_info:
      cloud: aws




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------+----------------+-----------------------------------------------------------------------------------+
   | **Key**           | **Returned**   | **Description**                                                                   |
   +-------------------+----------------+-----------------------------------------------------------------------------------+
   | **prerequisites** | always         | Returns a dictionary of the specific cloud provider prerequisites for Credentials |
   |                   |                |                                                                                   |
   | |br|              |                |                                                                                   |
   |                   |                |                                                                                   |
   | ``dict``          |                |                                                                                   |
   +-+-----------------+----------------+-----------------------------------------------------------------------------------+
   | | **account_id**  | always         | The account identifier for the CDP installation.                                  |
   | |                 |                |                                                                                   |
   | | |br|            |                |                                                                                   |
   | |                 |                |                                                                                   |
   | | ``str``         |                |                                                                                   |
   | |                 |                |                                                                                   |
   | |                 |                | |br|                                                                              |
   | |                 |                |                                                                                   |
   | |                 |                | **Sample:**                                                                       |
   | |                 |                |                                                                                   |
   | |                 |                | 3875500000000                                                                     |
   | |                 |                |                                                                                   |
   +-+-----------------+----------------+-----------------------------------------------------------------------------------+
   | | **external_id** | when supported | The AWS cross-account identifier for the CDP installation.                        |
   | |                 |                |                                                                                   |
   | | |br|            |                |                                                                                   |
   | |                 |                |                                                                                   |
   | | ``str``         |                |                                                                                   |
   | |                 |                |                                                                                   |
   | |                 |                | |br|                                                                              |
   | |                 |                |                                                                                   |
   | |                 |                | **Sample:**                                                                       |
   | |                 |                |                                                                                   |
   | |                 |                | 32b18f82-f868-414f-aedc-b3ee137560e3                                              |
   | |                 |                |                                                                                   |
   +-+-----------------+----------------+-----------------------------------------------------------------------------------+
   | | **policy**      | always         | The policy definition, returned as a base64 string.                               |
   | |                 |                |                                                                                   |
   | | |br|            |                |                                                                                   |
   | |                 |                |                                                                                   |
   | | ``str``         |                |                                                                                   |
   +-+-----------------+----------------+-----------------------------------------------------------------------------------+
   | **sdk_out**       | when supported | Returns the captured CDP SDK log.                                                 |
   |                   |                |                                                                                   |
   | |br|              |                |                                                                                   |
   |                   |                |                                                                                   |
   | ``str``           |                |                                                                                   |
   +-------------------+----------------+-----------------------------------------------------------------------------------+
   | **sdk_out_lines** | when supported | Returns a list of each line of the captured CDP SDK log.                          |
   |                   |                |                                                                                   |
   | |br|              |                |                                                                                   |
   |                   |                |                                                                                   |
   | ``list``          |                |                                                                                   |
   +-------------------+----------------+-----------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

