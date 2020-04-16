.. _datalake_runtime_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datalake_runtime_info -- Gather information about CDP Datalake Runtimes

datalake_runtime_info -- Gather information about CDP Datalake Runtimes
=======================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Datalake Runtimes



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
   | **default**    |                      | Flag to return only the ``default`` Runtime.                 |
   |                |                      | Otherwise, all available Runtimes will be listed.            |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``bool``       |                      |                                                              |
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

  # List basic information about available Datalake Runtimes
  - cloudera.cloud.datalake_runtime_info:

  # List basic information about the default Datalake Runtime
  - cloudera.cloud.datalake_runtime_info:
      default: yes





Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------------+----------------+----------------------------------------------------------+
   | **Key**                     | **Returned**   | **Description**                                          |
   +-----------------------------+----------------+----------------------------------------------------------+
   | **versions**                | on success     | Details on available CDP Datalake Runtimes               |
   |                             |                |                                                          |
   | |br|                        |                |                                                          |
   |                             |                |                                                          |
   | ``list``                    |                |                                                          |
   +-+---------------------------+----------------+----------------------------------------------------------+
   | | **runtimeVersion**        | always         | The version number of the Runtime.                       |
   | |                           |                |                                                          |
   | | |br|                      |                |                                                          |
   | |                           |                |                                                          |
   | | ``str``                   |                |                                                          |
   | |                           |                |                                                          |
   | |                           |                | |br|                                                     |
   | |                           |                |                                                          |
   | |                           |                | **Sample:**                                              |
   | |                           |                |                                                          |
   | |                           |                | 7.2.6                                                    |
   | |                           |                |                                                          |
   +-+---------------------------+----------------+----------------------------------------------------------+
   | | **defaultRuntimeVersion** | always         | Flag designating default status.                         |
   | |                           |                |                                                          |
   | | |br|                      |                |                                                          |
   | |                           |                |                                                          |
   | | ``bool``                  |                |                                                          |
   +-+---------------------------+----------------+----------------------------------------------------------+
   | **sdk_out**                 | when supported | Returns the captured CDP SDK log.                        |
   |                             |                |                                                          |
   | |br|                        |                |                                                          |
   |                             |                |                                                          |
   | ``str``                     |                |                                                          |
   +-----------------------------+----------------+----------------------------------------------------------+
   | **sdk_out_lines**           | when supported | Returns a list of each line of the captured CDP SDK log. |
   |                             |                |                                                          |
   | |br|                        |                |                                                          |
   |                             |                |                                                          |
   | ``list``                    |                |                                                          |
   +-----------------------------+----------------+----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)

