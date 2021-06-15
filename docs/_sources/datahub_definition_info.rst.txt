.. _datahub_definition_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datahub_definition_info -- Gather information about CDP Datahub Cluster Definitions

datahub_definition_info -- Gather information about CDP Datahub Cluster Definitions
===================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Datahub Cluster Definitions



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                                          |
   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **name**       |                      | If a name or CRN is provided, that Definition will be described.                      |
   |                |                      | If no name or CRN is provided, all Definitions will be listed.                        |
   | |br|           |                      |                                                                                       |
   |                |                      |                                                                                       |
   | ``str``        |                      |                                                                                       |
   |                |                      |                                                                                       |
   |                |                      | |br|                                                                                  |
   |                |                      |                                                                                       |
   |                |                      | *Aliases: definition, crn*                                                            |
   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **content**    |                      | Flag dictating if the workload template content of the cluster definition is returned |
   |                |                      |                                                                                       |
   | |br|           |                      |                                                                                       |
   |                |                      |                                                                                       |
   | ``bool``       |                      |                                                                                       |
   |                |                      |                                                                                       |
   |                |                      | |br|                                                                                  |
   |                |                      |                                                                                       |
   |                |                      | *Aliases: definition_content*                                                         |
   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                                     |
   |                |                      |                                                                                       |
   | |br|           |                      |                                                                                       |
   |                |                      |                                                                                       |
   | ``bool``       |                      |                                                                                       |
   |                |                      |                                                                                       |
   |                |                      | |br|                                                                                  |
   |                |                      |                                                                                       |
   |                |                      | *Aliases: tls*                                                                        |
   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                                        |
   |                |                      |                                                                                       |
   | |br|           |                      |                                                                                       |
   |                |                      |                                                                                       |
   | ``bool``       |                      |                                                                                       |
   |                |                      |                                                                                       |
   |                |                      | |br|                                                                                  |
   |                |                      |                                                                                       |
   |                |                      | *Aliases: debug_endpoints*                                                            |
   +----------------+----------------------+---------------------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.                          |
   |                |                      |                                                                                       |
   | |br|           |                      |                                                                                       |
   |                |                      |                                                                                       |
   | ``str``        |                      |                                                                                       |
   +----------------+----------------------+---------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all Datahubs
  - cloudera.cloud.datahub_definition_info:

  # Gather detailed information about a named Datahub
  - cloudera.cloud.datahub_definition_info:
      name: example-definition




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------------+----------------+-----------------------------------------------------------+
   | **Key**                     | **Returned**   | **Description**                                           |
   +-----------------------------+----------------+-----------------------------------------------------------+
   | **definitions**             | on success     | The information about the named Definition or Definitions |
   |                             |                |                                                           |
   | |br|                        |                |                                                           |
   |                             |                |                                                           |
   | ``list``                    |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **clusterDefinitionName** | always         | The name of the cluster definition.                       |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **crn**                   | always         | The CRN of the cluster definition.                        |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **type**                  | always         | The type of cluster definition.                           |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   | |                           |                |                                                           |
   | |                           |                | |br|                                                      |
   | |                           |                |                                                           |
   | |                           |                | **Sample:**                                               |
   | |                           |                |                                                           |
   | |                           |                | DATAENGINEERING                                           |
   | |                           |                |                                                           |
   | |                           |                | DATAMART                                                  |
   | |                           |                |                                                           |
   | |                           |                | DISCOVERY_DATA_AND_EXPLORATION                            |
   | |                           |                |                                                           |
   | |                           |                | FLOW_MANAGEMENT                                           |
   | |                           |                |                                                           |
   | |                           |                | OPERATIONALDATABASE                                       |
   | |                           |                |                                                           |
   | |                           |                | STREAMING                                                 |
   | |                           |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **nodeCount**             | always         | The node count of the cluster definition.                 |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **cloudPlatform**         | always         | The cloud provider of the cluster definition.             |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **productVersion**        | always         | The product version of the cluster definition.            |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **description**           | always         | The description of the cluster definition.                |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | | **workloadTemplate**      | when specified | The workload template of the cluster definition, in JSON. |
   | |                           |                |                                                           |
   | | |br|                      |                |                                                           |
   | |                           |                |                                                           |
   | | ``str``                   |                |                                                           |
   +-+---------------------------+----------------+-----------------------------------------------------------+
   | **sdk_out**                 | when supported | Returns the captured CDP SDK log.                         |
   |                             |                |                                                           |
   | |br|                        |                |                                                           |
   |                             |                |                                                           |
   | ``str``                     |                |                                                           |
   +-----------------------------+----------------+-----------------------------------------------------------+
   | **sdk_out_lines**           | when supported | Returns a list of each line of the captured CDP SDK log.  |
   |                             |                |                                                           |
   | |br|                        |                |                                                           |
   |                             |                |                                                           |
   | ``list``                    |                |                                                           |
   +-----------------------------+----------------+-----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Chris Perro (@cmperro)
- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

