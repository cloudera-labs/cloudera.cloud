.. _dw_virtual_warehouse_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: dw_virtual_warehouse_info -- Gather information about CDP Data Warehouse Virtual Warehouses

dw_virtual_warehouse_info -- Gather information about CDP Data Warehouse Virtual Warehouses
===========================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Virtual Warehouses



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**    | **Choices/Defaults** | **Comments**                                                                                                               |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **warehouse_id** |                      | The identifier of the Virtual Warehouse.                                                                                   |
   |                  |                      | Requires *cluster_id*.                                                                                                     |
   | |br|             |                      | Mutually exclusive with *name* and *catalog_id*.                                                                           |
   |                  |                      |                                                                                                                            |
   | ``str``          |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: vw_id, id*                                                                                                       |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **cluster_id**   |                      | The identifier of the parent Data Warehouse Cluster of the Virtual Warehouse(s).                                           |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``str``          |                      |                                                                                                                            |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **catalog_id**   |                      | The identifier of the parent Database Catalog attached to the Virtual Warehouse(s).                                        |
   |                  |                      | Requires *cluster_id*.                                                                                                     |
   | |br|             |                      | Mutally exclusive with *warehouse_id* and *name*.                                                                          |
   |                  |                      |                                                                                                                            |
   | ``str``          |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: dbc_id*                                                                                                          |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **name**         |                      | The name of the Virtual Warehouse.                                                                                         |
   |                  |                      | Requires *cluster_id*.                                                                                                     |
   | |br|             |                      | Mutually exclusive with *warehouse_id* and *catalog_id*.                                                                   |
   |                  |                      |                                                                                                                            |
   | ``str``          |                      |                                                                                                                            |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **delay**        |                      | The internal polling interval (in seconds) while the module waits for the Virtual Warehouse to achieve the declared state. |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``int``          |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: polling_delay*                                                                                                   |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **timeout**      |                      | The internal polling timeout (in seconds) while the module waits for the Virtual Warehouse to achieve the declared state.  |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``int``          |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: polling_timeout*                                                                                                 |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**   |                      | Verify the TLS certificates for the CDP endpoint.                                                                          |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``bool``         |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: tls*                                                                                                             |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **debug**        |                      | Capture the CDP SDK debug log.                                                                                             |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``bool``         |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   |                  |                      | |br|                                                                                                                       |
   |                  |                      |                                                                                                                            |
   |                  |                      | *Aliases: debug_endpoints*                                                                                                 |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+
   | **profile**      |                      | If provided, the CDP SDK will use this value as its profile.                                                               |
   |                  |                      |                                                                                                                            |
   | |br|             |                      |                                                                                                                            |
   |                  |                      |                                                                                                                            |
   | ``str``          |                      |                                                                                                                            |
   +------------------+----------------------+----------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List all Virtual Warehouses in a Cluster
  - cloudera.cloud.dw_virtual_warehouse_info:
      cluster_id: example-cluster-id

  # List all Virtual Warehouses associated with a Data Catalog
  - cloudera.cloud.dw_virtual_warehouse_info:
      cluster_id: example-cluster-id
      catalog_id: example-data-catalog-id

  # Describe a Virtual Warehouse by ID
  - cloudera.cloud.dw_virtual_warehouse_info:
      cluster_id: example-cluster-id
      warehouse_id: example-virtual-warehouse-id

  # Describe a Virtual Warehouse by name
  - cloudera.cloud.dw_virtual_warehouse_info:
      cluster_id: example-cluster-id
      name: example-virtual-warehouse




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +------------------------+----------------+----------------------------------------------------------------+
   | **Key**                | **Returned**   | **Description**                                                |
   +------------------------+----------------+----------------------------------------------------------------+
   | **virtual_warehouses** |                | The details about the CDP Data Warehouse Virtual Warehouse(s). |
   |                        |                |                                                                |
   | |br|                   |                |                                                                |
   |                        |                |                                                                |
   | ``list``               |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **id**               | always         | The identifier of the Virtual Warehouse.                       |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **name**             | always         | The name of the Virtual Warehouse.                             |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **vwType**           | always         | The Virtual Warehouse type.                                    |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **dbcId**            | always         | The Database Catalog ID associated with the Virtual Warehouse. |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **creationDate**     | always         | The creation time of the Virtual Warehouse in UTC.             |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **status**           | always         | The status of the Virtual Warehouse.                           |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``str``              |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **creator**          | always         | Details about the Virtual Warehouse creator.                   |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``dict``             |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | | **tags**             | always         | Custom tags applied to the Virtual Warehouse.                  |
   | |                      |                |                                                                |
   | | |br|                 |                |                                                                |
   | |                      |                |                                                                |
   | | ``dict``             |                |                                                                |
   +-+----------------------+----------------+----------------------------------------------------------------+
   | **sdk_out**            | when supported | Returns the captured CDP SDK log.                              |
   |                        |                |                                                                |
   | |br|                   |                |                                                                |
   |                        |                |                                                                |
   | ``str``                |                |                                                                |
   +------------------------+----------------+----------------------------------------------------------------+
   | **sdk_out_lines**      | when supported | Returns a list of each line of the captured CDP SDK log.       |
   |                        |                |                                                                |
   | |br|                   |                |                                                                |
   |                        |                |                                                                |
   | ``list``               |                |                                                                |
   +------------------------+----------------+----------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)
- Saravanan Raju (@raju-saravanan)

