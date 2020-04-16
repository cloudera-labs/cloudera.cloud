.. _env_auth_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_auth_info -- Gather information about CDP environment authentication details

env_auth_info -- Gather information about CDP environment authentication details
================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP environment authentication details, notably the FreeIPA root certificate and user keytabs.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **Parameter**        | **Choices/Defaults** | **Comments**                                                                                                 |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **name**             |                      | A target list of environments or a single environment string.                                                |
   |                      |                      | If no environments are specified, all environments are targeted.                                             |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``list``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: environment*                                                                                       |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **root_certificate** |                      | A flag indicating whether to retrieve the given environment's FreeIPA root certificate.                      |
   |                      |                      |                                                                                                              |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``bool``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: root_ca, cert*                                                                                     |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **keytab**           |                      | A flag to retrieve the keytabs for the given environment or environments, governed by the value of ``user``. |
   |                      |                      | If no environments are declared, all environments will be queried.                                           |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``bool``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: keytabs, user_keytabs*                                                                             |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **user**             |                      | A list of user IDs or a single user ID for retrieving the keytabs from the specified environment(s).         |
   |                      |                      | If no user ID is declared, the current CDP user will be used.                                                |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``list``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: users*                                                                                             |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **verify_tls**       |                      | Verify the TLS certificates for the CDP endpoint.                                                            |
   |                      |                      |                                                                                                              |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``bool``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: tls*                                                                                               |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **debug**            |                      | Capture the CDP SDK debug log.                                                                               |
   |                      |                      |                                                                                                              |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``bool``             |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   |                      |                      | |br|                                                                                                         |
   |                      |                      |                                                                                                              |
   |                      |                      | *Aliases: debug_endpoints*                                                                                   |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+
   | **profile**          |                      | If provided, the CDP SDK will use this value as its profile.                                                 |
   |                      |                      |                                                                                                              |
   | |br|                 |                      |                                                                                                              |
   |                      |                      |                                                                                                              |
   | ``str``              |                      |                                                                                                              |
   +----------------------+----------------------+--------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Retrieve only the root certificate for a single environment
  - cloudera.cloud.env_auth_info:
      name: the-environment
      root_certificate: yes
      keytab: no

  # Retrieve the root certificate for multiple environments
  - cloudera.cloud.env_auth_info:
      name:
        - one-environment
        - two-environment
      root_certificate: yes
      keytab: no

  # Retrieve the keytab details for the current CDP user for selected environments
  - cloudera.cloud.env_auth_info:
      name:
        - one-environment
        - two-environment
      keytab: yes
      root_certificate: no

  # Retrieve the keytab details for the specified users for selected environments
  - cloudera.cloud.env_auth_info:
      name:
        - one-environment
        - two-environment
      user:
        - UserA
        - UserB
      keytab: yes
      root_certificate: no




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +------------------------------+----------------+---------------------------------------------------------------------+
   | **Key**                      | **Returned**   | **Description**                                                     |
   +------------------------------+----------------+---------------------------------------------------------------------+
   | **authentication**           | always         | Returns a dictionary of the environment authentication details.     |
   |                              |                |                                                                     |
   | |br|                         |                |                                                                     |
   |                              |                |                                                                     |
   | ``dict``                     |                |                                                                     |
   +-+----------------------------+----------------+---------------------------------------------------------------------+
   | | **certificates**           | when supported | A dictionary of environment-to-FreeIPA root certificate             |
   | |                            |                |                                                                     |
   | | |br|                       |                |                                                                     |
   | |                            |                |                                                                     |
   | | ``dict``                   |                |                                                                     |
   +-+-+--------------------------+----------------+---------------------------------------------------------------------+
   | | | **_environment name_**   | always         | The FreeIPA root certificate for the environment                    |
   | | |                          |                |                                                                     |
   | | | |br|                     |                |                                                                     |
   | | |                          |                |                                                                     |
   | | | ``str``                  |                |                                                                     |
   +-+-+--------------------------+----------------+---------------------------------------------------------------------+
   | | **keytabs**                | when supported | A dictionary of the keytabs for each specified environment by user. |
   | |                            |                |                                                                     |
   | | |br|                       |                |                                                                     |
   | |                            |                |                                                                     |
   | | ``dict``                   |                |                                                                     |
   +-+-+--------------------------+----------------+---------------------------------------------------------------------+
   | | | **_workload username_**  | always         | The user's workload username.                                       |
   | | |                          |                |                                                                     |
   | | | |br|                     |                |                                                                     |
   | | |                          |                |                                                                     |
   | | | ``dict``                 |                |                                                                     |
   +-+-+-+------------------------+----------------+---------------------------------------------------------------------+
   | | | | **_environment name_** | always         | The keytab for the environment. The keytab is encoded in base64.    |
   | | | |                        |                |                                                                     |
   | | | | |br|                   |                |                                                                     |
   | | | |                        |                |                                                                     |
   | | | | ``str``                |                |                                                                     |
   +-+-+-+------------------------+----------------+---------------------------------------------------------------------+
   | **sdk_out**                  | when supported | Returns the captured CDP SDK log.                                   |
   |                              |                |                                                                     |
   | |br|                         |                |                                                                     |
   |                              |                |                                                                     |
   | ``str``                      |                |                                                                     |
   +------------------------------+----------------+---------------------------------------------------------------------+
   | **sdk_out_lines**            | when supported | Returns a list of each line of the captured CDP SDK log.            |
   |                              |                |                                                                     |
   | |br|                         |                |                                                                     |
   |                              |                |                                                                     |
   | ``list``                     |                |                                                                     |
   +------------------------------+----------------+---------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

