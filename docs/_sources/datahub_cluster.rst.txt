.. _datahub_cluster_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datahub_cluster -- Manage CDP Datahubs

datahub_cluster -- Manage CDP Datahubs
======================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create and delete CDP Datahubs.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults**  | **Comments**                                                                                                                     |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **name**        |                       | The name of the datahub.                                                                                                         |
   |                 |                       | This name must be unique, must have between 5 and 100 characters, and must contain only lowercase letters, numbers, and hyphens. |
   | |br|            |                       | Names are case-sensitive.                                                                                                        |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | *Required*      |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: datahub*                                                                                                               |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **state**       | **Choices:**          | The declarative state of the datahub.                                                                                            |
   |                 |  - **present** |larr| | If creating a datahub, the associate Environment and Datalake must be started as well.                                           |
   | |br|            |  - absent             |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **environment** |                       | The CDP environment name or CRN to which the datahub will be attached.                                                           |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: env*                                                                                                                   |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **definition**  |                       | The name or CRN of the cluster definition to use for cluster creation.                                                           |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **template**    |                       | Name or CRN of the cluster template to use for cluster creation.                                                                 |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **subnet**      |                       | The subnet ID in AWS, or the Subnet Name on Azure or GCP                                                                         |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **image**       |                       | ID of the image used for cluster instances                                                                                       |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **catalog**     |                       | Name of the image catalog to use for cluster instances                                                                           |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **groups**      |                       | Instance group details.                                                                                                          |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``array``       |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **tags**        |                       | Tags associated with the datahub and its resources.                                                                              |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``dict``        |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: datahub_tags*                                                                                                          |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **force**       |                       | Flag indicating if the datahub should be force deleted.                                                                          |
   |                 |                       | This option can be used when cluster deletion fails.                                                                             |
   | |br|            |                       | This removes the entry from Cloudera Datahub service.                                                                            |
   |                 |                       | Any lingering resources have to be deleted from the cloud provider manually.                                                     |
   | ``bool``        |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **wait**        |                       | Flag to enable internal polling to wait for the datahub to achieve the declared state.                                           |
   |                 |                       | If set to FALSE, the module will return immediately.                                                                             |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``bool``        |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **delay**       |                       | The internal polling interval (in seconds) while the module waits for the datahub to achieve the declared state.                 |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``int``         |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: polling_delay*                                                                                                         |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **timeout**     |                       | The internal polling timeout (in seconds) while the module waits for the datahub to achieve the declared state.                  |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``int``         |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: polling_timeout*                                                                                                       |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**  |                       | Verify the TLS certificates for the CDP endpoint.                                                                                |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``bool``        |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: tls*                                                                                                                   |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **debug**       |                       | Capture the CDP SDK debug log.                                                                                                   |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``bool``        |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   |                 |                       | |br|                                                                                                                             |
   |                 |                       |                                                                                                                                  |
   |                 |                       | *Aliases: debug_endpoints*                                                                                                       |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+
   | **profile**     |                       | If provided, the CDP SDK will use this value as its profile.                                                                     |
   |                 |                       |                                                                                                                                  |
   | |br|            |                       |                                                                                                                                  |
   |                 |                       |                                                                                                                                  |
   | ``str``         |                       |                                                                                                                                  |
   +-----------------+-----------------------+----------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a datahub specifying instance group details (and do not wait for status change)
  - cloudera.cloud.datahub_cluster:
      name: datahub-name
      env: name-or-crn
      state: present
      subnet: subnet-id-for-cloud-provider
      image: image-uuid-from-catalog
      catalog: name-of-catalog-for-image
      template: template-name
      groups:
        - nodeCount: 1
          instanceGroupName: master
          instanceGroupType: GATEWAY
          instanceType: instance-type-for-cloud-provider
          rootVolumeSize: 100
          recoveryMode: MANUAL
          recipeNames: []
          attachedVolumeConfiguration:
            - volumeSize: 100
              volumeCount: 1
              volumeType: volume-type-for-cloud-provider
      tags:
        project: Arbitrary content
      wait: no

  # Create a datahub specifying only a definition name
  - cloudera.cloud.datahub_cluster:
      name: datahub-name
      env: name-or-crn
      definition: definition-name
      tags:
        project: Arbitrary content
      wait: no

  # Delete the datahub (and wait for status change)
    cloudera.cloud.datahub:
      name: example-datahub
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------+----------------+---------------------------------------------------------------------+
   | **Key**                  | **Returned**   | **Description**                                                     |
   +--------------------------+----------------+---------------------------------------------------------------------+
   | **datahub**              | on success     | The information about the Datahub                                   |
   |                          |                |                                                                     |
   | |br|                     |                |                                                                     |
   |                          |                |                                                                     |
   | ``dict``                 |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **clusterName**        |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **crn**                |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **creationDate**       |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **status**             |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **clusterStatus**      |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **nodeCount**          |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``int``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **instanceGroups**     |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``array``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **instanceGroup**    |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``dict``             |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **name**           |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **id**             |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **state**          |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **privateIp**      |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **publicIp**       |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **fqdn**           |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **status**         |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | **workdloadType**      |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **cloudPlatform**      |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **imageDetails**       |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``array``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **name**             |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **id**               |                | This is the unique ID generated by the cloud provider for the image |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **catalogUrl**       |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **catalogName**      |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | **environmentCrn**     |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **credentialCrn**      |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **datalakeCrn**        |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **clusterTemplateCrn** |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **statusReason**       |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``str``                |                |                                                                     |
   +-+------------------------+----------------+---------------------------------------------------------------------+
   | | **clouderaManager**    |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``dict``               |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **version**          |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **platformVersion**  |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``str``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | **endpoints**          |                | tktk                                                                |
   | |                        |                |                                                                     |
   | | |br|                   |                |                                                                     |
   | |                        |                |                                                                     |
   | | ``array``              |                |                                                                     |
   +-+-+----------------------+----------------+---------------------------------------------------------------------+
   | | | **endpoint**         |                | tktk                                                                |
   | | |                      |                |                                                                     |
   | | | |br|                 |                |                                                                     |
   | | |                      |                |                                                                     |
   | | | ``dict``             |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **serviceName**    |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **serviceUrl**     |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **displayName**    |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **knoxService**    |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **mode**           |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``str``            |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | | | | **open**           |                | tktk                                                                |
   | | | |                    |                |                                                                     |
   | | | | |br|               |                |                                                                     |
   | | | |                    |                |                                                                     |
   | | | | ``bool``           |                |                                                                     |
   +-+-+-+--------------------+----------------+---------------------------------------------------------------------+
   | **sdk_out**              | when supported | Returns the captured CDP SDK log.                                   |
   |                          |                |                                                                     |
   | |br|                     |                |                                                                     |
   |                          |                |                                                                     |
   | ``str``                  |                |                                                                     |
   +--------------------------+----------------+---------------------------------------------------------------------+
   | **sdk_out_lines**        | when supported | Returns a list of each line of the captured CDP SDK log.            |
   |                          |                |                                                                     |
   | |br|                     |                |                                                                     |
   |                          |                |                                                                     |
   | ``list``                 |                |                                                                     |
   +--------------------------+----------------+---------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Daniel Chaffelson (@chaffelson)
- Chris Perro (@cmperro)

