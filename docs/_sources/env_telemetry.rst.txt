.. _env_telemetry_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_telemetry -- Set CDP environment telemetry

env_telemetry -- Set CDP environment telemetry
==============================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Set a CDP environment deployment log collection and workload analytics.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **Parameter**          | **Choices/Defaults** | **Comments**                                                                       |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **name**               |                      | The targeted environment.                                                          |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``str``                |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | *Required*             |                      |                                                                                    |
   |                        |                      |                                                                                    |
   |                        |                      | |br|                                                                               |
   |                        |                      |                                                                                    |
   |                        |                      | *Aliases: environment*                                                             |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **workload_analytics** |                      | A flag to specify the availability of the environment's workload analytics.        |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``bool``               |                      |                                                                                    |
   |                        |                      |                                                                                    |
   |                        |                      | |br|                                                                               |
   |                        |                      |                                                                                    |
   |                        |                      | *Aliases: analytics*                                                               |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **logs_collection**    |                      | A flag to specify the availability of the environment's deployment log collection. |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``bool``               |                      |                                                                                    |
   |                        |                      |                                                                                    |
   |                        |                      | |br|                                                                               |
   |                        |                      |                                                                                    |
   |                        |                      | *Aliases: report_deployment_logs*                                                  |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **verify_tls**         |                      | Verify the TLS certificates for the CDP endpoint.                                  |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``bool``               |                      |                                                                                    |
   |                        |                      |                                                                                    |
   |                        |                      | |br|                                                                               |
   |                        |                      |                                                                                    |
   |                        |                      | *Aliases: tls*                                                                     |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **debug**              |                      | Capture the CDP SDK debug log.                                                     |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``bool``               |                      |                                                                                    |
   |                        |                      |                                                                                    |
   |                        |                      | |br|                                                                               |
   |                        |                      |                                                                                    |
   |                        |                      | *Aliases: debug_endpoints*                                                         |
   +------------------------+----------------------+------------------------------------------------------------------------------------+
   | **profile**            |                      | If provided, the CDP SDK will use this value as its profile.                       |
   |                        |                      |                                                                                    |
   | |br|                   |                      |                                                                                    |
   |                        |                      |                                                                                    |
   | ``str``                |                      |                                                                                    |
   +------------------------+----------------------+------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Turn off both workload analytics and log collection
  - cloudera.cloud.env_telemetry:
      name: the-environment
      workload_analytics: no
      logs_collection: no




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

