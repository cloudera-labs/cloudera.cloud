.. _env_auth_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_auth -- Set authentication details for the current CDP user

env_auth -- Set authentication details for the current CDP user
===============================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Set authentication details for the current CDP user for one or more Environments.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                                                                                                                      |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **name**       |                      | The targeted environment(s).                                                                                                                                      |
   |                |                      | If no environment is specified, all environments are affected.                                                                                                    |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``list``       |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                                              |
   |                |                      |                                                                                                                                                                   |
   |                |                      | *Aliases: environment*                                                                                                                                            |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **password**   |                      | The workload password to set for the current CDP user.                                                                                                            |
   |                |                      | Passwords must be a minimum of 8 characters and no more than 64 characters and should be a combination of upper case, lower case, digits, and special characters. |
   | |br|           |                      | Set to 'no_log' within Ansible.                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | *Required*     |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                                              |
   |                |                      |                                                                                                                                                                   |
   |                |                      | *Aliases: workload_password*                                                                                                                                      |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **strict**     |                      | A flag to ignore *Conflict* errors on password updates.                                                                                                           |
   |                |                      |                                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                                   |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                                                                                                                 |
   |                |                      |                                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                                              |
   |                |                      |                                                                                                                                                                   |
   |                |                      | *Aliases: tls*                                                                                                                                                    |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                                                                                                                    |
   |                |                      |                                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                                              |
   |                |                      |                                                                                                                                                                   |
   |                |                      | *Aliases: debug_endpoints*                                                                                                                                        |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.                                                                                                      |
   |                |                      |                                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                                   |
   |                |                      |                                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                                   |
   +----------------+----------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Set the workload user password for the current CDP user on all environments
  - cloudera.cloud.env_auth:
      password: Cloudera@2020!

  # Set the workload user password for the current CDP user on selected environments
  - cloudera.cloud.env_auth:
      name:
        - one-environment
        - two-environment
      password: Cloudera@2020!




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------+----------------+----------------------------------------------------------+
   | **Key**           | **Returned**   | **Description**                                          |
   +-------------------+----------------+----------------------------------------------------------+
   | **sdk_out**       | when supported | Returns the captured CDP SDK log.                        |
   |                   |                |                                                          |
   | |br|              |                |                                                          |
   |                   |                |                                                          |
   | ``str``           |                |                                                          |
   +-------------------+----------------+----------------------------------------------------------+
   | **sdk_out_lines** | when supported | Returns a list of each line of the captured CDP SDK log. |
   |                   |                |                                                          |
   | |br|              |                |                                                          |
   |                   |                |                                                          |
   | ``list``          |                |                                                          |
   +-------------------+----------------+----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

