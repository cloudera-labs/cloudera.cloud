.. _dw_database_catalog_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: dw_database_catalog_info -- Gather information about CDP Data Warehouse Database Catalogs

dw_database_catalog_info -- Gather information about CDP Data Warehouse Database Catalogs
=========================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Data Warehouse Database Catalogs



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+---------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                              |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **catalog_id** |                      | The identifier of the Database Catalog.                                   |
   |                |                      | If undefined, will return a list of all Database Catalogs in the Cluster. |
   | |br|           |                      | Exclusive with *name*.                                                    |
   |                |                      |                                                                           |
   | ``str``        |                      |                                                                           |
   |                |                      |                                                                           |
   |                |                      | |br|                                                                      |
   |                |                      |                                                                           |
   |                |                      | *Aliases: id*                                                             |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **cluster_id** |                      | The identifier of the parent Cluster of the Database Catalog or Catalogs. |
   |                |                      |                                                                           |
   | |br|           |                      |                                                                           |
   |                |                      |                                                                           |
   | ``str``        |                      |                                                                           |
   |                |                      |                                                                           |
   | |br|           |                      |                                                                           |
   |                |                      |                                                                           |
   | *Required*     |                      |                                                                           |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **name**       |                      | The name of the Database Catalog.                                         |
   |                |                      | If undefined, will return a list of all Database Catalogs in the Cluster. |
   | |br|           |                      | Exclusive with *id*.                                                      |
   |                |                      |                                                                           |
   | ``str``        |                      |                                                                           |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                         |
   |                |                      |                                                                           |
   | |br|           |                      |                                                                           |
   |                |                      |                                                                           |
   | ``bool``       |                      |                                                                           |
   |                |                      |                                                                           |
   |                |                      | |br|                                                                      |
   |                |                      |                                                                           |
   |                |                      | *Aliases: tls*                                                            |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                            |
   |                |                      |                                                                           |
   | |br|           |                      |                                                                           |
   |                |                      |                                                                           |
   | ``bool``       |                      |                                                                           |
   |                |                      |                                                                           |
   |                |                      | |br|                                                                      |
   |                |                      |                                                                           |
   |                |                      | *Aliases: debug_endpoints*                                                |
   +----------------+----------------------+---------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.              |
   |                |                      |                                                                           |
   | |br|           |                      |                                                                           |
   |                |                      |                                                                           |
   | ``str``        |                      |                                                                           |
   +----------------+----------------------+---------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Get a single Database Catalog
  - cloudera.cloud.dw_database_catalog_info:
      name: example-database-catalog-name
      cluster_id: example-cluster-id
      
  # Get all Database Catalogs within a Cluster
  - cloudera.cloud.dw_database_catalog_info:
      cluster_id: example-cluster-id




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------+----------------+----------------------------------------------------------+
   | **Key**               | **Returned**   | **Description**                                          |
   +-----------------------+----------------+----------------------------------------------------------+
   | **database_catalogs** | always         | Details about the Database Catalogs.                     |
   |                       |                |                                                          |
   | |br|                  |                |                                                          |
   |                       |                |                                                          |
   | ``list``              |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **id**              | always         | The identifier of the Database Catalog.                  |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **name**            | always         | The name of the Database Catalog.                        |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **status**          | always         | The status of the Database Catalog.                      |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | **sdk_out**           | when supported | Returns the captured CDP SDK log.                        |
   |                       |                |                                                          |
   | |br|                  |                |                                                          |
   |                       |                |                                                          |
   | ``str``               |                |                                                          |
   +-----------------------+----------------+----------------------------------------------------------+
   | **sdk_out_lines**     | when supported | Returns a list of each line of the captured CDP SDK log. |
   |                       |                |                                                          |
   | |br|                  |                |                                                          |
   |                       |                |                                                          |
   | ``list``              |                |                                                          |
   +-----------------------+----------------+----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)
- Saravanan Raju (@raju-saravanan)

