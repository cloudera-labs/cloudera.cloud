.. _dw_cluster_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: dw_cluster -- Create or Delete CDP Data Warehouse Clusters

dw_cluster -- Create or Delete CDP Data Warehouse Clusters
==========================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create or Delete CDP Data Warehouse Clusters



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**           | **Choices/Defaults**  | **Comments**                                                                                                                    |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **id**                  |                       | If an ID is provided, that Data Warehouse Cluster will be deleted if ``state=absent``                                           |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``str``                 |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: name*                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **env**                 |                       | The name of the target environment                                                                                              |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``str``                 |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: environment, env_crn*                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **aws_public_subnets**  |                       | List of zero or more Public AWS Subnet IDs to deploy to                                                                         |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``list``                |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **aws_private_subnets** |                       | List of zero or more Private AWS Subnet IDs to deploy to                                                                        |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``list``                |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **az_subnet**           |                       | Azure Subnet Name, not URI                                                                                                      |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``str``                 |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **az_enable_az**        |                       | Whether to enable AZ mode or not                                                                                                |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``bool``                |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | *Required*              |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **state**               | **Choices:**          | The declarative state of the Data Warehouse Cluster                                                                             |
   |                         |  - **present** |larr| |                                                                                                                                 |
   | |br|                    |  - absent             |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **wait**                |                       | Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.                           |
   |                         |                       | If set to FALSE, the module will return immediately.                                                                            |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``bool``                |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **delay**               |                       | The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared state. |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``int``                 |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: polling_delay*                                                                                                        |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **timeout**             |                       | The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared state.  |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``int``                 |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: polling_timeout*                                                                                                      |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**          |                       | Verify the TLS certificates for the CDP endpoint.                                                                               |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``bool``                |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: tls*                                                                                                                  |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **debug**               |                       | Capture the CDP SDK debug log.                                                                                                  |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``bool``                |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   |                         |                       | |br|                                                                                                                            |
   |                         |                       |                                                                                                                                 |
   |                         |                       | *Aliases: debug_endpoints*                                                                                                      |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **profile**             |                       | If provided, the CDP SDK will use this value as its profile.                                                                    |
   |                         |                       |                                                                                                                                 |
   | |br|                    |                       |                                                                                                                                 |
   |                         |                       |                                                                                                                                 |
   | ``str``                 |                       |                                                                                                                                 |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Delete a Data Warehouse Cluster
  - cloudera.cloud.dw_cluster:
      state: absent
      id: my-id

  # Request Azure Cluster creation
  - cloudera.cloud.dw_cluster:
      env_crn: crn:cdp:environments...
      az_subnet: my-subnet-name
      az_enable_az: yes

  # Request AWS Cluster Creation
  - cloudera.cloud.dw_cluster:
      env_crn: crn:cdp:environments...
      aws_public_subnets: [subnet-id-1, subnet-id-2]
      aws_private_subnets: [subnet-id-3, subnet-id-4]




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
   | |                          |                |                                                                               |
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

- Dan Chaffelson (@chaffelson)

