.. _df_customflow_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: df_customflow_info -- Gather information about CDP DataFlow CustomFlow Definitions

df_customflow_info -- Gather information about CDP DataFlow CustomFlow Definitions
==================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP DataFlow CustomFlow Definitions



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +---------------------+----------------------+------------------------------------------------------------------------+
   | **Parameter**       | **Choices/Defaults** | **Comments**                                                           |
   +---------------------+----------------------+------------------------------------------------------------------------+
   | **name**            |                      | If a name is provided, that DataFlow Flow Definition will be described |
   |                     |                      |                                                                        |
   | |br|                |                      |                                                                        |
   |                     |                      |                                                                        |
   | ``str``             |                      |                                                                        |
   +---------------------+----------------------+------------------------------------------------------------------------+
   | **include_details** |                      | If set to false, only a summary of each flow is returned               |
   |                     |                      |                                                                        |
   | |br|                |                      |                                                                        |
   |                     |                      |                                                                        |
   | ``bool``            |                      |                                                                        |
   +---------------------+----------------------+------------------------------------------------------------------------+
   | **verify_tls**      |                      | Verify the TLS certificates for the CDP endpoint.                      |
   |                     |                      |                                                                        |
   | |br|                |                      |                                                                        |
   |                     |                      |                                                                        |
   | ``bool``            |                      |                                                                        |
   |                     |                      |                                                                        |
   |                     |                      | |br|                                                                   |
   |                     |                      |                                                                        |
   |                     |                      | *Aliases: tls*                                                         |
   +---------------------+----------------------+------------------------------------------------------------------------+
   | **debug**           |                      | Capture the CDP SDK debug log.                                         |
   |                     |                      |                                                                        |
   | |br|                |                      |                                                                        |
   |                     |                      |                                                                        |
   | ``bool``            |                      |                                                                        |
   |                     |                      |                                                                        |
   |                     |                      | |br|                                                                   |
   |                     |                      |                                                                        |
   |                     |                      | *Aliases: debug_endpoints*                                             |
   +---------------------+----------------------+------------------------------------------------------------------------+
   | **profile**         |                      | If provided, the CDP SDK will use this value as its profile.           |
   |                     |                      |                                                                        |
   | |br|                |                      |                                                                        |
   |                     |                      |                                                                        |
   | ``str``             |                      |                                                                        |
   +---------------------+----------------------+------------------------------------------------------------------------+


Notes
-----

.. note::
   - The feature this module is for is in Technical Preview




Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List summary information about all Custom DataFlow Flow Definitions
  - cloudera.cloud.df_customflow_info:

  # Gather summary information about a specific DataFlow Flow Definition using a name
  - cloudera.cloud.df_customflow_info:
      name: my-flow-name
      include_details: False




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | **Key**                  | **Returned**                  | **Description**                                                                  |
   +--------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | **flows**                | always                        | The listing of CustomFlow Definitions in the DataFlow Catalog in this CDP Tenant |
   |                          |                               |                                                                                  |
   | |br|                     |                               |                                                                                  |
   |                          |                               |                                                                                  |
   | ``list``                 |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **crn**                | always                        | The DataFlow Flow Definition's CRN.                                              |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **name**               | always                        | The DataFlow Flow Definition's name.                                             |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **modifiedTimestamp**  | always                        | The timestamp the entry was last modified.                                       |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``int``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **versionCount**       | always                        | The number of versions uploaded to the catalog.                                  |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **artifactType**       | when include_details is False | The type of artifact                                                             |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **createdTimestamp**   | when include_details is True  | The created timestamp.                                                           |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``int``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **author**             | when include_details is True  | Author of the most recent version.                                               |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **description**        | when include_details is True  | The artifact description.                                                        |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``str``                |                               |                                                                                  |
   +-+------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | **versions**           | when include_details is True  | The list of artifactDetail versions.                                             |
   | |                        |                               |                                                                                  |
   | | |br|                   |                               |                                                                                  |
   | |                        |                               |                                                                                  |
   | | ``array``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **crn**              | when include_details is True  | The flow version CRN.                                                            |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``str``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **bucketIdentifier** | when include_details is True  | The bucketIdentifier of the flow.                                                |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``str``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **author**           | when include_details is True  | The author of the flow.                                                          |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``str``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **version**          | when include_details is True  | The version of the flow.                                                         |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``int``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **timestamp**        | when include_details is True  | The timestamp of the flow.                                                       |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``int``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **deploymentCount**  | when include_details is True  | The number of deployments of the flow.                                           |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``int``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | | | **comments**         | when include_details is True  | Comments about the flow.                                                         |
   | | |                      |                               |                                                                                  |
   | | | |br|                 |                               |                                                                                  |
   | | |                      |                               |                                                                                  |
   | | | ``str``              |                               |                                                                                  |
   +-+-+----------------------+-------------------------------+----------------------------------------------------------------------------------+
   | **sdk_out**              | when supported                | Returns the captured CDP SDK log.                                                |
   |                          |                               |                                                                                  |
   | |br|                     |                               |                                                                                  |
   |                          |                               |                                                                                  |
   | ``str``                  |                               |                                                                                  |
   +--------------------------+-------------------------------+----------------------------------------------------------------------------------+
   | **sdk_out_lines**        | when supported                | Returns a list of each line of the captured CDP SDK log.                         |
   |                          |                               |                                                                                  |
   | |br|                     |                               |                                                                                  |
   |                          |                               |                                                                                  |
   | ``list``                 |                               |                                                                                  |
   +--------------------------+-------------------------------+----------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Dan Chaffelson (@chaffelson)

