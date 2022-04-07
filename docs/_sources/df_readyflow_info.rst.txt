.. _df_readyflow_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: df_readyflow_info -- Gather information about CDP DataFlow ReadyFlow Definitions

df_readyflow_info -- Gather information about CDP DataFlow ReadyFlow Definitions
================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP DataFlow ReadyFlow Definitions



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **Parameter**       | **Choices/Defaults** | **Comments**                                                                |
   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **name**            |                      | If a name is provided, that DataFlow ReadyFlow Definition will be described |
   |                     |                      |                                                                             |
   | |br|                |                      |                                                                             |
   |                     |                      |                                                                             |
   | ``str``             |                      |                                                                             |
   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **include_details** |                      | If set to false, only a summary of each ReadyFlow Definition is returned    |
   |                     |                      |                                                                             |
   | |br|                |                      |                                                                             |
   |                     |                      |                                                                             |
   | ``bool``            |                      |                                                                             |
   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **verify_tls**      |                      | Verify the TLS certificates for the CDP endpoint.                           |
   |                     |                      |                                                                             |
   | |br|                |                      |                                                                             |
   |                     |                      |                                                                             |
   | ``bool``            |                      |                                                                             |
   |                     |                      |                                                                             |
   |                     |                      | |br|                                                                        |
   |                     |                      |                                                                             |
   |                     |                      | *Aliases: tls*                                                              |
   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **debug**           |                      | Capture the CDP SDK debug log.                                              |
   |                     |                      |                                                                             |
   | |br|                |                      |                                                                             |
   |                     |                      |                                                                             |
   | ``bool``            |                      |                                                                             |
   |                     |                      |                                                                             |
   |                     |                      | |br|                                                                        |
   |                     |                      |                                                                             |
   |                     |                      | *Aliases: debug_endpoints*                                                  |
   +---------------------+----------------------+-----------------------------------------------------------------------------+
   | **profile**         |                      | If provided, the CDP SDK will use this value as its profile.                |
   |                     |                      |                                                                             |
   | |br|                |                      |                                                                             |
   |                     |                      |                                                                             |
   | ``str``             |                      |                                                                             |
   +---------------------+----------------------+-----------------------------------------------------------------------------+


Notes
-----

.. note::
   - This feature this module is for is in Technical Preview




Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List summary information about all Custom DataFlow ReadyFlow Definitions
  - cloudera.cloud.df_readyflow_info:

  # Gather summary information about a specific DataFlow Flow Definition using a name
  - cloudera.cloud.df_readyflow_info:
      name: my-flow-name




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | **Key**                       | **Returned**                    | **Description**                                                                    |
   +-------------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | **flows**                     | always                          | The listing of ReadyFlow Definitions in the DataFlow Catalog in this CDP Tenant    |
   |                               |                                 |                                                                                    |
   | |br|                          |                                 |                                                                                    |
   |                               |                                 |                                                                                    |
   | ``list``                      |                                 |                                                                                    |
   +-+-----------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | **addedReadyflowCrn**       | when readyflow imported is True | The CRN of this readyflow when it is imported to the CDP Tenant                    |
   | |                             |                                 | Use this readyflowCrn to address this object when doing deployments                |
   | | |br|                        |                                 |                                                                                    |
   | |                             |                                 |                                                                                    |
   | | ``str``                     |                                 |                                                                                    |
   +-+-----------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | **readyflow**               | always                          | The details of the ReadyFlow object                                                |
   | |                             |                                 |                                                                                    |
   | | |br|                        |                                 |                                                                                    |
   | |                             |                                 |                                                                                    |
   | | ``dict``                    |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **readyflowCrn**          | always                          | The CRN of this readyflow in the Control Plane                                     |
   | | |                           |                                 | Different to the addedReadyflowCrn of the imported readyflow within the CDP Tenant |
   | | | |br|                      |                                 | Use this readyflowCrn when importing the object to your CDP Tenant                 |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **name**                  | always                          | The DataFlow Flow Definition's name.                                               |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **author**                | always                          | Author of the most recent version.                                                 |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **summary**               | always                          | The ready flow summary (short).                                                    |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **description**           | always                          | The ready flow description (long).                                                 |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **documentationLink**     | always                          | A link to the ready flow documentation.                                            |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **notes**                 | always                          | Optional notes about the ready flow.                                               |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **source**                | always                          | The ready flow data source.                                                        |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **sourceDataFormat**      | always                          | The ready flow data source format.                                                 |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **destination**           | always                          | The ready flow data destination.                                                   |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **destinationDataFormat** | always                          | The ready flow data destination format.                                            |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **imported**              | always                          | Whether the ready flow has been imported into the current account.                 |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``bool``                  |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **modifiedTimestamp**     | always                          | The timestamp the entry was last modified.                                         |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``int``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | **versions**                | When imported is True           | The list of artifactDetail versions.                                               |
   | |                             |                                 |                                                                                    |
   | | |br|                        |                                 |                                                                                    |
   | |                             |                                 |                                                                                    |
   | | ``array``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **crn**                   | always                          | The artifact version CRN.                                                          |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **bucketIdentifier**      | always                          | The bucketIdentifier of the flow.                                                  |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **author**                | always                          | The author of the artifact.                                                        |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **version**               | always                          | The version of the artifact.                                                       |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``int``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **timestamp**             | always                          | The timestamp of the artifact.                                                     |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``int``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **deploymentCount**       | always                          | The number of deployments of the artifact.                                         |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``int``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | | | **comments**              | always                          | Comments about the version.                                                        |
   | | |                           |                                 |                                                                                    |
   | | | |br|                      |                                 |                                                                                    |
   | | |                           |                                 |                                                                                    |
   | | | ``str``                   |                                 |                                                                                    |
   +-+-+---------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | **sdk_out**                   | when supported                  | Returns the captured CDP SDK log.                                                  |
   |                               |                                 |                                                                                    |
   | |br|                          |                                 |                                                                                    |
   |                               |                                 |                                                                                    |
   | ``str``                       |                                 |                                                                                    |
   +-------------------------------+---------------------------------+------------------------------------------------------------------------------------+
   | **sdk_out_lines**             | when supported                  | Returns a list of each line of the captured CDP SDK log.                           |
   |                               |                                 |                                                                                    |
   | |br|                          |                                 |                                                                                    |
   |                               |                                 |                                                                                    |
   | ``list``                      |                                 |                                                                                    |
   +-------------------------------+---------------------------------+------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Dan Chaffelson (@chaffelson)

