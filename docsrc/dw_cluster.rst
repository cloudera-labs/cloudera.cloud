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

   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**             | **Choices/Defaults**  | **Comments**                                                                                                                    |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **cluster_id**            |                       | The identifier of the Data Warehouse Cluster.                                                                                   |
   |                           |                       | Required if *state=absent* and *env* is not specified.                                                                          |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``str``                   |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: id, name*                                                                                                             |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **env**                   |                       | The name of the target environment.                                                                                             |
   |                           |                       | Required if *state=present*.                                                                                                    |
   | |br|                      |                       | Required if *state=absent* and *cluster_id* is not specified.                                                                   |
   |                           |                       |                                                                                                                                 |
   | ``str``                   |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: environment, env_crn*                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **overlay**               |                       | Flag to use private IP addresses for Pods within the cluster.                                                                   |
   |                           |                       | Otherwise, use IP addresses within the VPC.                                                                                     |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **private_load_balancer** |                       | Flag to set up a load balancer for private subnets.                                                                             |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **aws_public_subnets**    |                       | List of zero or more Public AWS Subnet IDs used for deployment.                                                                 |
   |                           |                       | Required if *state=present* and the *env* is deployed to AWS.                                                                   |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``list``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **aws_private_subnets**   |                       | List of zero or more Private AWS Subnet IDs used for deployment.                                                                |
   |                           |                       | Required if *state=present* and the *env* is deployed to AWS.                                                                   |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``list``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **az_subnet**             |                       | The Azure Subnet Name.                                                                                                          |
   |                           |                       | Required if *state=present* and the *env* is deployed to Azure.                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``str``                   |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **az_enable_az**          |                       | Flag to enable Availability Zone mode.                                                                                          |
   |                           |                       | Required if *state=present* and the *env* is deployed to Azure.                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **state**                 | **Choices:**          | The state of the Data Warehouse Cluster                                                                                         |
   |                           |  - **present** |larr| |                                                                                                                                 |
   | |br|                      |  - absent             |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **wait**                  |                       | Flag to enable internal polling to wait for the Data Warehouse Cluster to achieve the declared state.                           |
   |                           |                       | If set to FALSE, the module will return immediately.                                                                            |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **force**                 |                       | Flag to enable force deletion of the Data Warehouse Cluster.                                                                    |
   |                           |                       | This will not destroy the underlying cloud provider assets.                                                                     |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **delay**                 |                       | The internal polling interval (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared state. |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``int``                   |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: polling_delay*                                                                                                        |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **timeout**               |                       | The internal polling timeout (in seconds) while the module waits for the Data Warehouse Cluster to achieve the declared state.  |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``int``                   |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: polling_timeout*                                                                                                      |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**            |                       | Verify the TLS certificates for the CDP endpoint.                                                                               |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: tls*                                                                                                                  |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **debug**                 |                       | Capture the CDP SDK debug log.                                                                                                  |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``bool``                  |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   |                           |                       | |br|                                                                                                                            |
   |                           |                       |                                                                                                                                 |
   |                           |                       | *Aliases: debug_endpoints*                                                                                                      |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+
   | **profile**               |                       | If provided, the CDP SDK will use this value as its profile.                                                                    |
   |                           |                       |                                                                                                                                 |
   | |br|                      |                       |                                                                                                                                 |
   |                           |                       |                                                                                                                                 |
   | ``str``                   |                       |                                                                                                                                 |
   +---------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

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

  # Delete a Data Warehouse Cluster
  - cloudera.cloud.dw_cluster:
      state: absent
      cluster_id: my-id
      
  # Delete the Data Warehouse Cluster within the Environment
  - cloudera.cloud.dw_cluster:
      state: absent
      env: crn:cdp:environments...




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **Key**                  | **Returned**   | **Description**                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **cluster**              |                | Details for the Data Warehouse cluster                                      |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``dict``                 |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **id**                 | always         | The cluster identifier.                                                     |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **environmentCrn**     | always         | The CRN of the cluster's Environment                                        |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **crn**                | always         | The cluster's CRN.                                                          |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **creationDate**       | always         | The creation timestamp of the cluster in UTC.                               |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **status**             | always         | The status of the cluster                                                   |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | | **creator**            | always         | The cluster creator details.                                                |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``dict``               |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **crn**              | always         | The Actor CRN.                                                              |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **email**            | when supported | Email address (users).                                                      |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **workloadUsername** | when supported | Username (users).                                                           |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | | **machineUsername**  | when supported | Username (machine users).                                                   |
   | | |                      |                |                                                                             |
   | | | |br|                 |                |                                                                             |
   | | |                      |                |                                                                             |
   | | | ``str``              |                |                                                                             |
   +-+-+----------------------+----------------+-----------------------------------------------------------------------------+
   | | **cloudPlatform**      | always         | The cloud platform of the environment that was used to create this cluster. |
   | |                        |                |                                                                             |
   | | |br|                   |                |                                                                             |
   | |                        |                |                                                                             |
   | | ``str``                |                |                                                                             |
   +-+------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out**              | when supported | Returns the captured CDP SDK log.                                           |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``str``                  |                |                                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+
   | **sdk_out_lines**        | when supported | Returns a list of each line of the captured CDP SDK log.                    |
   |                          |                |                                                                             |
   | |br|                     |                |                                                                             |
   |                          |                |                                                                             |
   | ``list``                 |                |                                                                             |
   +--------------------------+----------------+-----------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Dan Chaffelson (@chaffelson)
- Saravanan Raju (@raju-saravanan)
- Webster Mudge (@wmudge)

