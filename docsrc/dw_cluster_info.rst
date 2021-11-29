.. _dw_cluster_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: dw_cluster_info -- Gather information about CDP Data Warehouse Clusters

dw_cluster_info -- Gather information about CDP Data Warehouse Clusters
=======================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Data Warehouse Clusters



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults** | **Comments**                                                                              |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **cluster_id**  |                      | The identifier of the Data Warehouse Cluster.                                             |
   |                 |                      | Mutually exclusive with *environment*.                                                    |
   | |br|            |                      |                                                                                           |
   |                 |                      |                                                                                           |
   | ``str``         |                      |                                                                                           |
   |                 |                      |                                                                                           |
   |                 |                      | |br|                                                                                      |
   |                 |                      |                                                                                           |
   |                 |                      | *Aliases: id*                                                                             |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **environment** |                      | The name or CRN of the Environment in which to find and describe Data Warehouse Clusters. |
   |                 |                      | Mutually exclusive with *cluster_id*.                                                     |
   | |br|            |                      |                                                                                           |
   |                 |                      |                                                                                           |
   | ``str``         |                      |                                                                                           |
   |                 |                      |                                                                                           |
   |                 |                      | |br|                                                                                      |
   |                 |                      |                                                                                           |
   |                 |                      | *Aliases: env*                                                                            |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **verify_tls**  |                      | Verify the TLS certificates for the CDP endpoint.                                         |
   |                 |                      |                                                                                           |
   | |br|            |                      |                                                                                           |
   |                 |                      |                                                                                           |
   | ``bool``        |                      |                                                                                           |
   |                 |                      |                                                                                           |
   |                 |                      | |br|                                                                                      |
   |                 |                      |                                                                                           |
   |                 |                      | *Aliases: tls*                                                                            |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **debug**       |                      | Capture the CDP SDK debug log.                                                            |
   |                 |                      |                                                                                           |
   | |br|            |                      |                                                                                           |
   |                 |                      |                                                                                           |
   | ``bool``        |                      |                                                                                           |
   |                 |                      |                                                                                           |
   |                 |                      | |br|                                                                                      |
   |                 |                      |                                                                                           |
   |                 |                      | *Aliases: debug_endpoints*                                                                |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+
   | **profile**     |                      | If provided, the CDP SDK will use this value as its profile.                              |
   |                 |                      |                                                                                           |
   | |br|            |                      |                                                                                           |
   |                 |                      |                                                                                           |
   | ``str``         |                      |                                                                                           |
   +-----------------+----------------------+-------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List information about all Data Warehouse Clusters
  - cloudera.cloud.dw_cluster_info:

  # Gather information about all Data Warehouse Clusters within an Environment
  - cloudera.cloud.dw_cluster_info:
      env: example-environment
      
  # Gather information about an identified Cluster
  - cloudera.cloud.dw_cluster_info:
      cluster_id: env-xyzabc




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **Key**                  | **Returned**   | **Description**                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **clusters**             | always         | The information about the named Cluster or Clusters                         |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``list``                 |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **id**                 | always         | The cluster identifier.                                                     |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **environmentCrn**     | always         | The CRN of the cluster's Environment                                        |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **crn**                | always         | The cluster's CRN.                                                          |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **creationDate**       | always         | The creation timestamp of the cluster in UTC.                               |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **status**             | always         | The status of the cluster                                                   |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **creator**            | always         | The cluster creator details.                                                |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``dict``               |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **crn**              | always         | The Actor CRN.                                                              |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **email**            | when supported | Email address (users).                                                      |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **workloadUsername** | when supported | Username (users).                                                           |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **machineUsername**  | when supported | Username (machine users).                                                   |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | **cloudPlatform**      | always         | The cloud platform of the environment that was used to create this cluster. |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out**              | when supported | Returns the captured CDP SDK log.                                           |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``str``                  |                |                                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out_lines**        | when supported | Returns a list of each line of the captured CDP SDK log.                    |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``list``                 |                |                                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

