.. _account_auth_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: account_auth -- Gather and set authentication details for a CDP Account

account_auth -- Gather and set authentication details for a CDP Account
=======================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather and set information for a CDP account.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**         | **Choices/Defaults** | **Comments**                                                                                                                                |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **enable_sso**        |                      | Flag to enable or disable interactive login using the Cloudera SSO for the account.                                                         |
   |                       |                      | When disabled, only users who are designated account administrators will be able to use Cloudera SSO to login interactively to the account. |
   | |br|                  |                      | All other users will only be able to login interactively using other SAML providers defined for the account.                                |
   |                       |                      |                                                                                                                                             |
   | ``bool``              |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   |                       |                      | |br|                                                                                                                                        |
   |                       |                      |                                                                                                                                             |
   |                       |                      | *Aliases: sso, enable_cloudera_sso*                                                                                                         |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **password_lifetime** |                      | The maximum lifetime of workload passwords for the account, in days.                                                                        |
   |                       |                      | If set to ``0``, passwords never expire.                                                                                                    |
   | |br|                  |                      | Changes to the workload password lifetime only affect passwords that are set after the policy has been updated.                             |
   |                       |                      |                                                                                                                                             |
   | ``int``               |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   |                       |                      | |br|                                                                                                                                        |
   |                       |                      |                                                                                                                                             |
   |                       |                      | *Aliases: workload_password_lifetime*                                                                                                       |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**        |                      | Verify the TLS certificates for the CDP endpoint.                                                                                           |
   |                       |                      |                                                                                                                                             |
   | |br|                  |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   | ``bool``              |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   |                       |                      | |br|                                                                                                                                        |
   |                       |                      |                                                                                                                                             |
   |                       |                      | *Aliases: tls*                                                                                                                              |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**             |                      | Capture the CDP SDK debug log.                                                                                                              |
   |                       |                      |                                                                                                                                             |
   | |br|                  |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   | ``bool``              |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   |                       |                      | |br|                                                                                                                                        |
   |                       |                      |                                                                                                                                             |
   |                       |                      | *Aliases: debug_endpoints*                                                                                                                  |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**           |                      | If provided, the CDP SDK will use this value as its profile.                                                                                |
   |                       |                      |                                                                                                                                             |
   | |br|                  |                      |                                                                                                                                             |
   |                       |                      |                                                                                                                                             |
   | ``str``               |                      |                                                                                                                                             |
   +-----------------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Disable Cloudera SSO login for all non-admin users
  - cloudera.cloud.account_auth:
      disable_sso: yes

  # Set the password expiration to 7 days
  - cloudera.cloud.account_auth:
      password_lifetime: 7




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

