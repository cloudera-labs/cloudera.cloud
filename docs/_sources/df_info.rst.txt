.. _df_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: df_info -- Gather information about CDP DataFlow Services

df_info -- Gather information about CDP DataFlow Services
=========================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP DataFlow Services



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+-----------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                    |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **name**       |                      | If a name is provided, that DataFlow Service will be described. |
   |                |                      | Must be CDP Environment CRN or string name of DataFlow Service  |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``str``        |                      |                                                                 |
   |                |                      |                                                                 |
   |                |                      | |br|                                                            |
   |                |                      |                                                                 |
   |                |                      | *Aliases: crn*                                                  |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.               |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``bool``       |                      |                                                                 |
   |                |                      |                                                                 |
   |                |                      | |br|                                                            |
   |                |                      |                                                                 |
   |                |                      | *Aliases: tls*                                                  |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                  |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``bool``       |                      |                                                                 |
   |                |                      |                                                                 |
   |                |                      | |br|                                                            |
   |                |                      |                                                                 |
   |                |                      | *Aliases: debug_endpoints*                                      |
   +----------------+----------------------+-----------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.    |
   |                |                      |                                                                 |
   | |br|           |                      |                                                                 |
   |                |                      |                                                                 |
   | ``str``        |                      |                                                                 |
   +----------------+----------------------+-----------------------------------------------------------------+


Notes
-----

.. note::
   - This feature this module is for is in Technical Preview




Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all DataFlow Services
  - cloudera.cloud.df_info:

  # Gather detailed information about a named DataFlow Service using a name
  - cloudera.cloud.df_info:
      name: example-service

  # Gather detailed information about a named DataFlow Service using a CRN
  - cloudera.cloud.df_info:
      crn: example-service-crn




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **Key**                       | **Returned**   | **Description**                                                                                         |
   +-------------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **environments**              | always         | The information about the named DataFlow Service or DataFlow Services                                   |
   |                               |                |                                                                                                         |
   | |br|                          |                |                                                                                                         |
   |                               |                |                                                                                                         |
   | ``list``                      |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **crn**                     | always         | The DataFlow Service's parent environment CRN.                                                          |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **name**                    | always         | The DataFlow Service's parent environment name.                                                         |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **cloudPlatform**           | always         | The cloud platform of the environment.                                                                  |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **region**                  | always         | The region of the environment.                                                                          |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **deploymentCount**         | always         | The deployment count.                                                                                   |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **minK8sNodeCount**         | always         | The  minimum  number  of Kubernetes nodes that need to be provisioned in the environment.               |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``int``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **maxK8sNodeCount**         | always         | The maximum number of  kubernetes  nodes  that  environment  may scale up under high-demand situations. |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **status**                  | always         | The status of a DataFlow enabled environment.                                                           |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``dict``                    |                |                                                                                                         |
   +-+-+---------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **state**                 | always         | The state of the environment.                                                                           |
   | | |                           |                |                                                                                                         |
   | | | |br|                      |                |                                                                                                         |
   | | |                           |                |                                                                                                         |
   | | | ``str``                   |                |                                                                                                         |
   +-+-+---------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | | **message**               | always         | A status message for the environment.                                                                   |
   | | |                           |                |                                                                                                         |
   | | | |br|                      |                |                                                                                                         |
   | | |                           |                |                                                                                                         |
   | | | ``str``                   |                |                                                                                                         |
   +-+-+---------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **k8sNodeCount**            | always         | The  number of kubernetes nodes currently in use by DataFlow for this environment.                      |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``int``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **instanceType**            | always         | The instance type of the kubernetes nodes currently  in  use  by DataFlow for this environment.         |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **dfLocalUrl**              | always         | The URL of the environment local DataFlow application.                                                  |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **authorizedIpRanges**      | always         | The authorized IP Ranges.                                                                               |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``list``                    |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **activeWarningAlertCount** | always         | Current count of active alerts classified as a warning.                                                 |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``int``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **activeErrorAlertCount**   | always         | Current count of active alerts classified as an error.                                                  |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``int``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | | **clusterId**               | if enabled     | Cluster id of the environment.                                                                          |
   | |                             |                |                                                                                                         |
   | | |br|                        |                |                                                                                                         |
   | |                             |                |                                                                                                         |
   | | ``str``                     |                |                                                                                                         |
   +-+-----------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **sdk_out**                   | when supported | Returns the captured CDP SDK log.                                                                       |
   |                               |                |                                                                                                         |
   | |br|                          |                |                                                                                                         |
   |                               |                |                                                                                                         |
   | ``str``                       |                |                                                                                                         |
   +-------------------------------+----------------+---------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**             | when supported | Returns a list of each line of the captured CDP SDK log.                                                |
   |                               |                |                                                                                                         |
   | |br|                          |                |                                                                                                         |
   |                               |                |                                                                                                         |
   | ``list``                      |                |                                                                                                         |
   +-------------------------------+----------------+---------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

