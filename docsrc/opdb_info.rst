.. _opdb_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: opdb_info -- Gather information about CDP OpDB Databases

opdb_info -- Gather information about CDP OpDB Databases
========================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP OpDB Databases



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults** | **Comments**                                                                  |
   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **name**        |                      | If a ``name`` is provided, that OpDB Database will be described.              |
   |                 |                      | ``environment`` must be provided if using ``name`` to retrieve a Database     |
   | |br|            |                      |                                                                               |
   |                 |                      |                                                                               |
   | ``str``         |                      |                                                                               |
   |                 |                      |                                                                               |
   |                 |                      | |br|                                                                          |
   |                 |                      |                                                                               |
   |                 |                      | *Aliases: database*                                                           |
   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **environment** |                      | The name of the Environment in which to find and describe the OpDB Databases. |
   |                 |                      | Required with name to retrieve a Database                                     |
   | |br|            |                      |                                                                               |
   |                 |                      |                                                                               |
   | ``str``         |                      |                                                                               |
   |                 |                      |                                                                               |
   |                 |                      | |br|                                                                          |
   |                 |                      |                                                                               |
   |                 |                      | *Aliases: env*                                                                |
   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **verify_tls**  |                      | Verify the TLS certificates for the CDP endpoint.                             |
   |                 |                      |                                                                               |
   | |br|            |                      |                                                                               |
   |                 |                      |                                                                               |
   | ``bool``        |                      |                                                                               |
   |                 |                      |                                                                               |
   |                 |                      | |br|                                                                          |
   |                 |                      |                                                                               |
   |                 |                      | *Aliases: tls*                                                                |
   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **debug**       |                      | Capture the CDP SDK debug log.                                                |
   |                 |                      |                                                                               |
   | |br|            |                      |                                                                               |
   |                 |                      |                                                                               |
   | ``bool``        |                      |                                                                               |
   |                 |                      |                                                                               |
   |                 |                      | |br|                                                                          |
   |                 |                      |                                                                               |
   |                 |                      | *Aliases: debug_endpoints*                                                    |
   +-----------------+----------------------+-------------------------------------------------------------------------------+
   | **profile**     |                      | If provided, the CDP SDK will use this value as its profile.                  |
   |                 |                      |                                                                               |
   | |br|            |                      |                                                                               |
   |                 |                      |                                                                               |
   | ``str``         |                      |                                                                               |
   +-----------------+----------------------+-------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all OpDB Databases
  - cloudera.cloud.opdb_info:

  # Gather detailed information about a named Database
  - cloudera.cloud.opdb_info:
      name: example-database
      env: example-environment




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------+----------------+----------------------------------------------------------+
   | **Key**               | **Returned**   | **Description**                                          |
   +-----------------------+----------------+----------------------------------------------------------+
   | **databases**         | always         | The information about the named Database or Databases    |
   |                       |                |                                                          |
   | |br|                  |                |                                                          |
   |                       |                |                                                          |
   | ``list``              |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **databaseName**    | always         | The name of the database.                                |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **environmentCrn**  | always         | The crn of the database's environment.                   |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **crn**             | always         | The database's crn.                                      |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **creationDate**    | always         | The creation time of the database in UTC.                |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **status**          | always         | The status of the Database                               |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **creatorCrn**      | always         | The CRN of the database creator.                         |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **k8sClusterName**  | always         | The Kubernetes cluster name.                             |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **dbVersion**       | always         | The version of the Database.                             |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **hueEndpoint**     | always         | The Hue endpoint for the Database.                       |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **environmentName** | always         | The name of the Database's environment                   |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``bool``            |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **storageLocation** | always         | HBase cloud storage location                             |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **internalName**    | always         | Internal cluster name for this database                  |
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

