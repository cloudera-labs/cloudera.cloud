.. _freeipa_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: freeipa_info -- Gather information about FreeIPA

freeipa_info -- Gather information about FreeIPA
================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about FreeIPA



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
   | **name**       |                      | The FreeIPA environment specified will be described          |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``str``        |                      |                                                              |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | *Required*     |                      |                                                              |
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

  # List FreeIPA information about a named Environment
  - cloudera.cloud.freeipa_info:
      name: example-environment




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------+--------------+-------------------------------------------------------------+
   | **Key**               | **Returned** | **Description**                                             |
   +-----------------------+--------------+-------------------------------------------------------------+
   | **environments**      | on success   | The information about the named Environment or Environments |
   |                       |              |                                                             |
   | |br|                  |              |                                                             |
   |                       |              |                                                             |
   | ``dict``              |              |                                                             |
   +-+---------------------+--------------+-------------------------------------------------------------+
   | | **environmentCrn**  | always       | CDP CRN value for the Environment.                          |
   | |                     |              |                                                             |
   | | |br|                |              |                                                             |
   | |                     |              |                                                             |
   | | ``str``             |              |                                                             |
   +-+---------------------+--------------+-------------------------------------------------------------+
   | | **environmentName** | always       | Name of the Environment.                                    |
   | |                     |              |                                                             |
   | | |br|                |              |                                                             |
   | |                     |              |                                                             |
   | | ``str``             |              |                                                             |
   | |                     |              |                                                             |
   | |                     |              | |br|                                                        |
   | |                     |              |                                                             |
   | |                     |              | **Sample:**                                                 |
   | |                     |              |                                                             |
   | |                     |              | a-cdp-environment-name                                      |
   | |                     |              |                                                             |
   +-+---------------------+--------------+-------------------------------------------------------------+
   | | **instances**       | always       | Details about the instances.                                |
   | |                     |              |                                                             |
   | | |br|                |              |                                                             |
   | |                     |              |                                                             |
   | | ``list``            |              |                                                             |
   +-+-+-------------------+--------------+-------------------------------------------------------------+
   | | | **id**            | always       | The identifier of the instance.                             |
   | | |                   |              |                                                             |
   | | | |br|              |              |                                                             |
   | | |                   |              |                                                             |
   | | | ``str``           |              |                                                             |
   | | |                   |              |                                                             |
   | | |                   |              | |br|                                                        |
   | | |                   |              |                                                             |
   | | |                   |              | **Sample:**                                                 |
   | | |                   |              |                                                             |
   | | |                   |              | i-00b58f27be                                                |
   | | |                   |              |                                                             |
   +-+-+-------------------+--------------+-------------------------------------------------------------+
   | | | **state**         | always       | The state of the instance.                                  |
   | | |                   |              |                                                             |
   | | | |br|              |              |                                                             |
   | | |                   |              |                                                             |
   | | | ``str``           |              |                                                             |
   | | |                   |              |                                                             |
   | | |                   |              | |br|                                                        |
   | | |                   |              |                                                             |
   | | |                   |              | **Sample:**                                                 |
   | | |                   |              |                                                             |
   | | |                   |              | CREATED                                                     |
   | | |                   |              |                                                             |
   +-+-+-------------------+--------------+-------------------------------------------------------------+
   | | | **hostname**      | always       | The hostname of the instance.                               |
   | | |                   |              |                                                             |
   | | | |br|              |              |                                                             |
   | | |                   |              |                                                             |
   | | | ``str``           |              |                                                             |
   | | |                   |              |                                                             |
   | | |                   |              | |br|                                                        |
   | | |                   |              |                                                             |
   | | |                   |              | **Sample:**                                                 |
   | | |                   |              |                                                             |
   | | |                   |              | ipaserver0.a-cdp-environment-name.example.site              |
   | | |                   |              |                                                             |
   +-+-+-------------------+--------------+-------------------------------------------------------------+
   | | | **issues**        | always       | Details of any issues encountered with server.              |
   | | |                   |              |                                                             |
   | | | |br|              |              |                                                             |
   | | |                   |              |                                                             |
   | | | ``list``          |              |                                                             |
   +-+-+-------------------+--------------+-------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Jim Enright (@jenright)

