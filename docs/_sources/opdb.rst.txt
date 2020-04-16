.. _opdb_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: opdb -- Create or destroy CDP OpDB Databases

opdb -- Create or destroy CDP OpDB Databases
============================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create or destroy CDP OpDB Databases



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults**  | **Comments**                                                                                                           |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **name**        |                       | If a name is provided, that OpDB Database will be created or dropped.                                                  |
   |                 |                       | environment must be provided                                                                                           |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``str``         |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | *Required*      |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: database*                                                                                                    |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **environment** |                       | The name of the Environment in which to find or place the OpDB Databases.                                              |
   |                 |                       | Required with name                                                                                                     |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``str``         |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | *Required*      |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: env*                                                                                                         |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **state**       | **Choices:**          | The declarative state of the OpDB Database                                                                             |
   |                 |  - **present** |larr| |                                                                                                                        |
   | |br|            |  - absent             |                                                                                                                        |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **wait**        |                       | Flag to enable internal polling to wait for the Opdb Database to achieve the declared state.                           |
   |                 |                       | If set to FALSE, the module will return immediately.                                                                   |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``bool``        |                       |                                                                                                                        |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **delay**       |                       | The internal polling interval (in seconds) while the module waits for the OpDB Database to achieve the declared state. |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``int``         |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: polling_delay*                                                                                               |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **timeout**     |                       | The internal polling timeout (in seconds) while the module waits for the OpDB Database to achieve the declared state.  |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``int``         |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: polling_timeout*                                                                                             |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**  |                       | Verify the TLS certificates for the CDP endpoint.                                                                      |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``bool``        |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: tls*                                                                                                         |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **debug**       |                       | Capture the CDP SDK debug log.                                                                                         |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``bool``        |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   |                 |                       | |br|                                                                                                                   |
   |                 |                       |                                                                                                                        |
   |                 |                       | *Aliases: debug_endpoints*                                                                                             |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+
   | **profile**     |                       | If provided, the CDP SDK will use this value as its profile.                                                           |
   |                 |                       |                                                                                                                        |
   | |br|            |                       |                                                                                                                        |
   |                 |                       |                                                                                                                        |
   | ``str``         |                       |                                                                                                                        |
   +-----------------+-----------------------+------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create an OpDB Database
  - cloudera.cloud.opdb:
      name: example-database
      env: example-environment

  # Remove an OpDB Database
  - cloudera.cloud.opdb:
      name: example-database
      env: example-environment
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------+----------------+----------------------------------------------------------+
   | **Key**               | **Returned**   | **Description**                                          |
   +-----------------------+----------------+----------------------------------------------------------+
   | **database**          | always         | The information about the Created Database               |
   |                       |                |                                                          |
   | |br|                  |                |                                                          |
   |                       |                |                                                          |
   | ``dict``              |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **databaseName**    | present        | The name of the database.                                |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **environmentCrn**  | present        | The crn of the database's environment.                   |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **crn**             | present        | The database's crn.                                      |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **creationDate**    | present        | The creation time of the database in UTC.                |
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
   | | **creatorCrn**      | present        | The CRN of the database creator.                         |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **dbVersion**       | present        | The version of the Database.                             |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **hueEndpoint**     | present        | The Hue endpoint for the Database.                       |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **environmentName** | present        | The name of the Database's environment                   |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``bool``            |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **storageLocation** | present        | HBase cloud storage location                             |
   | |                     |                |                                                          |
   | | |br|                |                |                                                          |
   | |                     |                |                                                          |
   | | ``str``             |                |                                                          |
   +-+---------------------+----------------+----------------------------------------------------------+
   | | **internalName**    | present        | Internal cluster name for this database                  |
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

- Dan Chaffelson (@chaffelson)

