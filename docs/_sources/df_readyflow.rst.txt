.. _df_readyflow_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: df_readyflow -- Import or Delete ReadyFlows from your CDP Tenant

df_readyflow -- Import or Delete ReadyFlows from your CDP Tenant
================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Import or Delete ReadyFlows from your CDP Tenant



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+-----------------------+--------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults**  | **Comments**                                                 |
   +----------------+-----------------------+--------------------------------------------------------------+
   | **name**       |                       | The name of the ReadyFlow to be acted upon.                  |
   |                |                       |                                                              |
   | |br|           |                       |                                                              |
   |                |                       |                                                              |
   | ``str``        |                       |                                                              |
   |                |                       |                                                              |
   | |br|           |                       |                                                              |
   |                |                       |                                                              |
   | *Required*     |                       |                                                              |
   +----------------+-----------------------+--------------------------------------------------------------+
   | **state**      | **Choices:**          | The declarative state of the ReadyFlow                       |
   |                |  - **present** |larr| |                                                              |
   | |br|           |  - absent             |                                                              |
   +----------------+-----------------------+--------------------------------------------------------------+
   | **verify_tls** |                       | Verify the TLS certificates for the CDP endpoint.            |
   |                |                       |                                                              |
   | |br|           |                       |                                                              |
   |                |                       |                                                              |
   | ``bool``       |                       |                                                              |
   |                |                       |                                                              |
   |                |                       | |br|                                                         |
   |                |                       |                                                              |
   |                |                       | *Aliases: tls*                                               |
   +----------------+-----------------------+--------------------------------------------------------------+
   | **debug**      |                       | Capture the CDP SDK debug log.                               |
   |                |                       |                                                              |
   | |br|           |                       |                                                              |
   |                |                       |                                                              |
   | ``bool``       |                       |                                                              |
   |                |                       |                                                              |
   |                |                       | |br|                                                         |
   |                |                       |                                                              |
   |                |                       | *Aliases: debug_endpoints*                                   |
   +----------------+-----------------------+--------------------------------------------------------------+
   | **profile**    |                       | If provided, the CDP SDK will use this value as its profile. |
   |                |                       |                                                              |
   | |br|           |                       |                                                              |
   |                |                       |                                                              |
   | ``str``        |                       |                                                              |
   +----------------+-----------------------+--------------------------------------------------------------+


Notes
-----

.. note::
   - This feature this module is for is in Technical Preview




Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Import a ReadyFlow into your CDP Tenant
  - cloudera.cloud.df_readyflow:
      name: my-readyflow-name

  # Delete an added ReadyFlow from your CDP Tenant
  - cloudera.cloud.df_readyflow:
      name: my-readyflow-name
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------------------+-----------------------+--------------------------------------------------------------------+
   | **Key**                       | **Returned**          | **Description**                                                    |
   +-------------------------------+-----------------------+--------------------------------------------------------------------+
   | **readyflow**                 | always                | The ReadyFlow Definition                                           |
   |                               |                       |                                                                    |
   | |br|                          |                       |                                                                    |
   |                               |                       |                                                                    |
   | ``dict``                      |                       |                                                                    |
   +-+-----------------------------+-----------------------+--------------------------------------------------------------------+
   | | **readyflowCrn**            | always                | The DataFlow readyflow Definition's CRN.                           |
   | |                             |                       | Use this readyflowCrn to address this object                       |
   | | |br|                        |                       |                                                                    |
   | |                             |                       |                                                                    |
   | | ``str``                     |                       |                                                                    |
   +-+-----------------------------+-----------------------+--------------------------------------------------------------------+
   | | **readyflow**               | varies                | The details of the ReadyFlow object                                |
   | |                             |                       |                                                                    |
   | | |br|                        |                       |                                                                    |
   | |                             |                       |                                                                    |
   | | ``dict``                    |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **readyflowCrn**          | always                | The general base CRN of this ReadyFlow                             |
   | | |                           |                       | Different to the unique readyflowCrn containing a UUID4            |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **name**                  | always                | The DataFlow Flow Definition's name.                               |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **author**                | always                | Author of the most recent version.                                 |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **summary**               | always                | The ready flow summary (short).                                    |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **description**           | always                | The ready flow description (long).                                 |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **documentationLink**     | always                | A link to the ready flow documentation.                            |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **notes**                 | always                | Optional notes about the ready flow.                               |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **source**                | always                | The ready flow data source.                                        |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **sourceDataFormat**      | always                | The ready flow data source format.                                 |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **destination**           | always                | The ready flow data destination.                                   |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **destinationDataFormat** | always                | The ready flow data destination format.                            |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **imported**              | always                | Whether the ready flow has been imported into the current account. |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``bool``                  |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **modifiedTimestamp**     | always                | The timestamp the entry was last modified.                         |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``int``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | **versions**                | When imported is True | The list of artifactDetail versions.                               |
   | |                             |                       |                                                                    |
   | | |br|                        |                       |                                                                    |
   | |                             |                       |                                                                    |
   | | ``list``                    |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **crn**                   | always                | The artifact version CRN.                                          |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **bucketIdentifier**      | always                | The bucketIdentifier of the flow.                                  |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **author**                | always                | The author of the artifact.                                        |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **version**               | always                | The version of the artifact.                                       |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``int``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **timestamp**             | always                | The timestamp of the artifact.                                     |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``int``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **deploymentCount**       | always                | The number of deployments of the artifact.                         |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``int``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | | | **comments**              | always                | Comments about the version.                                        |
   | | |                           |                       |                                                                    |
   | | | |br|                      |                       |                                                                    |
   | | |                           |                       |                                                                    |
   | | | ``str``                   |                       |                                                                    |
   +-+-+---------------------------+-----------------------+--------------------------------------------------------------------+
   | **sdk_out**                   | when supported        | Returns the captured CDP SDK log.                                  |
   |                               |                       |                                                                    |
   | |br|                          |                       |                                                                    |
   |                               |                       |                                                                    |
   | ``str``                       |                       |                                                                    |
   +-------------------------------+-----------------------+--------------------------------------------------------------------+
   | **sdk_out_lines**             | when supported        | Returns a list of each line of the captured CDP SDK log.           |
   |                               |                       |                                                                    |
   | |br|                          |                       |                                                                    |
   |                               |                       |                                                                    |
   | ``list``                      |                       |                                                                    |
   +-------------------------------+-----------------------+--------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Dan Chaffelson (@chaffelson)

