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

   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults** | **Comments**                                                                           |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **id**          |                      | If a name is provided, that Data Warehouse Cluster will be described.                  |
   |                 |                      | environment must be provided if using name to retrieve a Cluster                       |
   | |br|            |                      |                                                                                        |
   |                 |                      |                                                                                        |
   | ``str``         |                      |                                                                                        |
   |                 |                      |                                                                                        |
   |                 |                      | |br|                                                                                   |
   |                 |                      |                                                                                        |
   |                 |                      | *Aliases: name*                                                                        |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **environment** |                      | The name of the Environment in which to find and describe the Data Warehouse Clusters. |
   |                 |                      | Required with name to retrieve a Cluster                                               |
   | |br|            |                      |                                                                                        |
   |                 |                      |                                                                                        |
   | ``str``         |                      |                                                                                        |
   |                 |                      |                                                                                        |
   |                 |                      | |br|                                                                                   |
   |                 |                      |                                                                                        |
   |                 |                      | *Aliases: env*                                                                         |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **verify_tls**  |                      | Verify the TLS certificates for the CDP endpoint.                                      |
   |                 |                      |                                                                                        |
   | |br|            |                      |                                                                                        |
   |                 |                      |                                                                                        |
   | ``bool``        |                      |                                                                                        |
   |                 |                      |                                                                                        |
   |                 |                      | |br|                                                                                   |
   |                 |                      |                                                                                        |
   |                 |                      | *Aliases: tls*                                                                         |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **debug**       |                      | Capture the CDP SDK debug log.                                                         |
   |                 |                      |                                                                                        |
   | |br|            |                      |                                                                                        |
   |                 |                      |                                                                                        |
   | ``bool``        |                      |                                                                                        |
   |                 |                      |                                                                                        |
   |                 |                      | |br|                                                                                   |
   |                 |                      |                                                                                        |
   |                 |                      | *Aliases: debug_endpoints*                                                             |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+
   | **profile**     |                      | If provided, the CDP SDK will use this value as its profile.                           |
   |                 |                      |                                                                                        |
   | |br|            |                      |                                                                                        |
   |                 |                      |                                                                                        |
   | ``str``         |                      |                                                                                        |
   +-----------------+----------------------+----------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all Data Warehouse Clusters
  - cloudera.cloud.dw_cluster_info:

  # Gather detailed information about a named Cluster
  - cloudera.cloud.dw_cluster_info:
      name: example-cluster
      env: example-environment




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +----------------------------+----------------+-------------------------------------------------------------------------------+
   | **Key**                    | **Returned**   | **Description**                                                               |
   +----------------------------+----------------+-------------------------------------------------------------------------------+
   | **clusters**               | always         | The information about the named Cluster or Clusters                           |
   |                            |                |                                                                               |
   | |br|                       |                |                                                                               |
   |                            |                |                                                                               |
   | ``list``                   |                |                                                                               |
   +-+--------------------------+----------------+-------------------------------------------------------------------------------+
   | | **cluster**              |                |                                                                               |
   | |                          |                |                                                                               |
   | | |br|                     |                |                                                                               |
   | |                          |                |                                                                               |
   | | ``dict``                 |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **name**               | always         | The name of the cluster.                                                      |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **environmentCrn**     | always         | The crn of the cluster's environment.                                         |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **crn**                | always         | The cluster's crn.                                                            |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **creationDate**       | always         | The creation time of the cluster in UTC.                                      |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **status**             | always         | The status of the Cluster                                                     |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | | | **creator**            | always         | The CRN of the cluster creator.                                               |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``dict``               |                |                                                                               |
   +-+-+-+----------------------+----------------+-------------------------------------------------------------------------------+
   | | | | **crn**              |                | Actor CRN                                                                     |
   | | | |                      |                |                                                                               |
   | | | | |br|                 |                |                                                                               |
   | | | |                      |                |                                                                               |
   | | | | ``str``              |                |                                                                               |
   +-+-+-+----------------------+----------------+-------------------------------------------------------------------------------+
   | | | | **email**            |                | Email address for users                                                       |
   | | | |                      |                |                                                                               |
   | | | | |br|                 |                |                                                                               |
   | | | |                      |                |                                                                               |
   | | | | ``str``              |                |                                                                               |
   +-+-+-+----------------------+----------------+-------------------------------------------------------------------------------+
   | | | | **workloadUsername** |                | Username for users                                                            |
   | | | |                      |                |                                                                               |
   | | | | |br|                 |                |                                                                               |
   | | | |                      |                |                                                                               |
   | | | | ``str``              |                |                                                                               |
   +-+-+-+----------------------+----------------+-------------------------------------------------------------------------------+
   | | | | **machineUsername**  |                | Username for machine users                                                    |
   | | | |                      |                |                                                                               |
   | | | | |br|                 |                |                                                                               |
   | | | |                      |                |                                                                               |
   | | | | ``str``              |                |                                                                               |
   +-+-+-+----------------------+----------------+-------------------------------------------------------------------------------+
   | | | **cloudPlatform**      | always         | The  cloud  platform  of the environment that was used to create this cluster |
   | | |                        |                |                                                                               |
   | | | |br|                   |                |                                                                               |
   | | |                        |                |                                                                               |
   | | | ``str``                |                |                                                                               |
   +-+-+------------------------+----------------+-------------------------------------------------------------------------------+
   | **sdk_out**                | when supported | Returns the captured CDP SDK log.                                             |
   |                            |                |                                                                               |
   | |br|                       |                |                                                                               |
   |                            |                |                                                                               |
   | ``str``                    |                |                                                                               |
   +----------------------------+----------------+-------------------------------------------------------------------------------+
   | **sdk_out_lines**          | when supported | Returns a list of each line of the captured CDP SDK log.                      |
   |                            |                |                                                                               |
   | |br|                       |                |                                                                               |
   |                            |                |                                                                               |
   | ``list``                   |                |                                                                               |
   +----------------------------+----------------+-------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

