.. _de_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: de_info -- Gather information about CDP DE Workspaces

de_info -- Gather information about CDP DE Workspaces
=====================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP DE Workspaces



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults** | **Comments**                                                                   |
   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **name**        |                      | If a name is provided, that DE service will be described (if it exists)        |
   |                 |                      | Note that there should be only 1 or 0 (non-deleted) services with a given name |
   | |br|            |                      |                                                                                |
   |                 |                      |                                                                                |
   | ``str``         |                      |                                                                                |
   |                 |                      |                                                                                |
   |                 |                      | |br|                                                                           |
   |                 |                      |                                                                                |
   |                 |                      | *Aliases: name*                                                                |
   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **environment** |                      | The name of the Environment in which to find and describe the DE service(s).   |
   |                 |                      |                                                                                |
   | |br|            |                      |                                                                                |
   |                 |                      |                                                                                |
   | ``str``         |                      |                                                                                |
   |                 |                      |                                                                                |
   |                 |                      | |br|                                                                           |
   |                 |                      |                                                                                |
   |                 |                      | *Aliases: env*                                                                 |
   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **verify_tls**  |                      | Verify the TLS certificates for the CDP endpoint.                              |
   |                 |                      |                                                                                |
   | |br|            |                      |                                                                                |
   |                 |                      |                                                                                |
   | ``bool``        |                      |                                                                                |
   |                 |                      |                                                                                |
   |                 |                      | |br|                                                                           |
   |                 |                      |                                                                                |
   |                 |                      | *Aliases: tls*                                                                 |
   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **debug**       |                      | Capture the CDP SDK debug log.                                                 |
   |                 |                      |                                                                                |
   | |br|            |                      |                                                                                |
   |                 |                      |                                                                                |
   | ``bool``        |                      |                                                                                |
   |                 |                      |                                                                                |
   |                 |                      | |br|                                                                           |
   |                 |                      |                                                                                |
   |                 |                      | *Aliases: debug_endpoints*                                                     |
   +-----------------+----------------------+--------------------------------------------------------------------------------+
   | **profile**     |                      | If provided, the CDP SDK will use this value as its profile.                   |
   |                 |                      |                                                                                |
   | |br|            |                      |                                                                                |
   |                 |                      |                                                                                |
   | ``str``         |                      |                                                                                |
   +-----------------+----------------------+--------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all DE Services
  - cloudera.cloud.de_info:

  # List basic information about all DE Services within a given environment
  - cloudera.cloud.de_info:
      environment: example-environment

  # Gather detailed information about a named DE Service
  - cloudera.cloud.de_info:
      name: example-service

  # Gather detailed information about a named DE Service within a particular environment
  - cloudera.cloud.de_info:
      name: example-service
      environment: example-environment




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | **Key**                             | **Returned**                | **Description**                                                               |
   +-------------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | **services**                        | always                      | List of DE service descriptions                                               |
   |                                     |                             |                                                                               |
   | |br|                                |                             |                                                                               |
   |                                     |                             |                                                                               |
   | ``list``                            |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **clusterId**                     | always                      | Cluster Id of the CDE Service.                                                |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **creatorEmail**                  | always                      | Email Address of the CDE creator.                                             |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **enablingTime**                  | always                      | Timestamp of service enabling.                                                |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **environmentName**               | always                      | CDP Environment Name.                                                         |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **name**                          | always                      | Name of the CDE Service.                                                      |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **status**                        | always                      | Status of the CDE Service.                                                    |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **chartValueOverrides**           | if full service description | Status of the CDE Service.                                                    |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``array``                         |                             |                                                                               |
   +-+-+---------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | **ChartValueOverridesResponse** | always                      |                                                                               |
   | | |                                 |                             |                                                                               |
   | | | |br|                            |                             |                                                                               |
   | | |                                 |                             |                                                                               |
   | | | ``list``                        |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **chartName**                 | always                      | Name of the chart that has to be overridden.                                  |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **overrides**                 | always                      | Space separated key value-pairs for overriding chart values (colon separated) |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **cloudPlatform**                 | if full service description | The cloud platform where the CDE service is enabled.                          |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **clusterFqdn**                   | if full service description | FQDN of the CDE service.                                                      |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **creatorCrn**                    | if full service description | CRN of the creator.                                                           |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **dataLakeAtlasUIEndpoint**       | if full service description | Endpoint of Data Lake Atlas.E                                                 |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **dataLakeFileSystems**           | if full service description | The Data lake file system.                                                    |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **environmentCrn**                | if full service description | CRN of the environment.                                                       |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **logLocation**                   | if full service description | Location for the log files of jobs.                                           |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **resources**                     | if full service description | Resources details of CDE Service.                                             |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``complex``                       |                             |                                                                               |
   +-+-+---------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | **ServiceResources**            | always                      | Object to store resources for a CDE service.                                  |
   | | |                                 |                             |                                                                               |
   | | | |br|                            |                             |                                                                               |
   | | |                                 |                             |                                                                               |
   | | | ``complex``                     |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **initial_instances**         | always                      | Initial instances for the CDE service.                                        |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **initial_spot_instances**    | always                      | Initial Spot Instances for the CDE Service.                                   |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **instance_type**             | always                      | Instance type of the CDE service.                                             |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **max_instances**             | always                      | Maximum instances for the CDE service.                                        |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **max_spot_instances**        | always                      | Maximum Number of Spot instances.                                             |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **min_instances**             | always                      | Minimum Instances for the CDE service.                                        |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **min_spot_instances**        | always                      | Minimum number of spot instances for the CDE service.                         |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | | | **root_vol_size**             | always                      | Root Volume Size.                                                             |
   | | | |                               |                             |                                                                               |
   | | | | |br|                          |                             |                                                                               |
   | | | |                               |                             |                                                                               |
   | | | | ``str``                       |                             |                                                                               |
   +-+-+-+-------------------------------+-----------------------------+-------------------------------------------------------------------------------+
   | | **tenantId**                      | if full service description | CDP tenant ID.                                                                |
   | |                                   |                             |                                                                               |
   | | |br|                              |                             |                                                                               |
   | |                                   |                             |                                                                               |
   | | ``str``                           |                             |                                                                               |
   +-+-----------------------------------+-----------------------------+-------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Curtis Howard (@curtishoward)
- Alan Silva (@acsjumpi)

