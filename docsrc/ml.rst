.. _ml_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: ml -- Create or Destroy CDP Machine Learning Workspaces

ml -- Create or Destroy CDP Machine Learning Workspaces
=======================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create or Destroy CDP Machine Learning Workspaces



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **Parameter**           | **Choices/Defaults**  | **Comments**                                                                                                          |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **name**                |                       | The name of the ML Workspace                                                                                          |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``str``                 |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | *Required*              |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: workspace*                                                                                                  |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **environment**         |                       | The name of the Environment for the ML Workspace                                                                      |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``str``                 |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | *Required*              |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: env*                                                                                                        |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **state**               | **Choices:**          | The declarative state of the ML Workspace                                                                             |
   |                         |  - **present** |larr| |                                                                                                                       |
   | |br|                    |  - absent             |                                                                                                                       |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **tls**                 |                       | The flag to manage TLS for the ML Workspace.                                                                          |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: enable_tls*                                                                                                 |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **monitoring**          |                       | The flag to manage monitoring for the ML Workspace.                                                                   |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: enable_monitoring*                                                                                          |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **governance**          |                       | The flag to enable governance by integrating with Cloudera Atlas for the ML Workspace.                                |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: enable_governance*                                                                                          |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **metrics**             |                       | The flag to enable the exporting of model metrics to a metrics store for the ML Workspace.                            |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: enable_metrics*                                                                                             |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **database**            |                       | Configuration for exporting model metrics to an existing Postgres database.                                           |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``dict``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: existing_database, database_config*                                                                         |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **nfs**                 |                       | An existing NFS mount (hostname and desired path).                                                                    |
   |                         |                       | Applicable to *Azure* and *Private Cloud* deployments only.                                                           |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``str``                 |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: existing_nfs*                                                                                               |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **nfs_version**         |                       | The NFS Protocol version of the NFS server as declared in ``nfs``.                                                    |
   |                         |                       | Applicable to *Azure* and *Private Cloud* deployments only.                                                           |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``str``                 |                       |                                                                                                                       |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **k8s_request**         |                       | Configuration for the Kubernetes provisioning of the ML Workspace.                                                    |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``dict``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: provision_k8s*                                                                                              |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **ip_addresses**        |                       | List of allowed CIDR blocks for the load balancer.                                                                    |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``list``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: loadbalancer_access_ips*                                                                                    |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **public_loadbalancer** |                       | Flag to manage the usage of a public load balancer.                                                                   |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: enable_public_loadbalancer*                                                                                 |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **force**               |                       | Flag to force delete a workspace even if errors occur during deletion.                                                |
   |                         |                       | Force delete removes the guarantee that the cloud provider resources are destroyed.                                   |
   | |br|                    |                       | Applicable to ``state=absent`` only.                                                                                  |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: force_delete*                                                                                               |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **storage**             |                       | Flag to delete the ML Workspace backing storage during delete operations.                                             |
   |                         |                       | Applicable to ``state=absent`` only.                                                                                  |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: remove_storage*                                                                                             |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **wait**                |                       | Flag to enable internal polling to wait for the ML Workspace to achieve the declared state.                           |
   |                         |                       | If set to FALSE, the module will return immediately.                                                                  |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **delay**               |                       | The internal polling interval (in seconds) while the module waits for the ML Workspace to achieve the declared state. |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``int``                 |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: polling_delay*                                                                                              |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **timeout**             |                       | The internal polling timeout (in seconds) while the module waits for the ML Workspace to achieve the declared state.  |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``int``                 |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: polling_timeout*                                                                                            |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**          |                       | Verify the TLS certificates for the CDP endpoint.                                                                     |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: tls*                                                                                                        |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **debug**               |                       | Capture the CDP SDK debug log.                                                                                        |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``bool``                |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   |                         |                       | |br|                                                                                                                  |
   |                         |                       |                                                                                                                       |
   |                         |                       | *Aliases: debug_endpoints*                                                                                            |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
   | **profile**             |                       | If provided, the CDP SDK will use this value as its profile.                                                          |
   |                         |                       |                                                                                                                       |
   | |br|                    |                       |                                                                                                                       |
   |                         |                       |                                                                                                                       |
   | ``str``                 |                       |                                                                                                                       |
   +-------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a ML Workspace with TLS turned off and wait for setup completion
  - cloudera.cloud.ml:
      name: ml-example
      env: cdp-env
      tls: no
      wait: yes

  # Create a ML Workspace (in AWS) with a custom Kubernetes request configuration
  - cloudera.cloud.ml:
      name: ml-k8s-example
      env: cdp-env
      k8s_request:
        environmentName: cdp-env
        instanceGroups:
          - name: default_settings
            autoscaling:
              maxInstances: 10
              minInstances: 1
            instanceType: m5.2xlarge
          - name: cpu_settings
            autoscaling:
              maxInstances: 10
              minInstances: 1
            instanceCount: 0
            instanceTier: "ON_DEMAND"
            instanceType: m5.2xlarge
            rootVolume:
              size: 60
          - name: gpu_settings
            autoscaling:
              maxInstances: 1
              minInstances: 0
            instanceCount: 0
            instanceTier: "ON_DEMAND"
            instanceType: "p2.8xlarge"
            rootVolume:
              size: 40
        wait: yes

  # Remove a ML Workspace, but return immediately
  - cloudera.cloud.ml:
      name: ml-example
      env: cdp-env
      state: absent
      wait: no




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | **Key**                        | **Returned**   | **Description**                                                                                                           |
   +--------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | **workspace**                  | when supported | The information about the ML Workspace                                                                                    |
   |                                |                |                                                                                                                           |
   | |br|                           |                |                                                                                                                           |
   |                                |                |                                                                                                                           |
   | ``dict``                       |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **cloudPlatform**            | always         | The cloud platform of the environment that was used to create this workspace.                                             |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **clusterBaseDomain**        | when supported | The basedomain of the cluster.                                                                                            |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **creationDate**             | always         | Creation date of workspace (date-time).                                                                                   |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | |                              |                | |br|                                                                                                                      |
   | |                              |                |                                                                                                                           |
   | |                              |                | **Sample:**                                                                                                               |
   | |                              |                |                                                                                                                           |
   | |                              |                | 2021-05-19T15:35:17.997000+00:00                                                                                          |
   | |                              |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **creatorCrn**               | always         | The CRN of the creator of the workspace.                                                                                  |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **crn**                      | always         | The CRN of the workspace.                                                                                                 |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **endpointPublicAccess**     | always         | Flag indicating if the cluster is publicly accessible.                                                                    |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``bool``                     |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **environmentCrn**           | always         | CRN of the environment.                                                                                                   |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **environmentName**          | always         | The name of the workspace's environment.                                                                                  |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **failureMessage**           | during failure | Failure message from the most recent failure that has occurred during workspace provisioning.                             |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **filesystemID**             | always         | A filesystem ID referencing the filesystem that was created on the cloud provider environment that this workspace uses.   |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **governanceEnabled**        | when supported | Flag indicating if Cloudera Atlas governance is enabled for the cluster.                                                  |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``bool``                     |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **healthInfoLists**          |                | The health info information of the workspace.                                                                             |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``list``                     |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **HealthInfo**             | always         | Healthinfo  object  contains  the health information of a resource.                                                       |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``array``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **details**              | always         | The detail of the health info.                                                                                            |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``array``                |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **isHealthy**            | always         | The boolean that indicates the health status.                                                                             |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``bool``                 |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **message**              | always         | The message to show for the health info.                                                                                  |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **resourceName**         | always         | The resource name being checked.                                                                                          |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **updatedAt**            | always         | The unix timestamp for the heartbeat.                                                                                     |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **httpsEnabled**             | always         | Indicates if HTTPS communication was enabled on this workspace when provisioned.                                          |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``bool``                     |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **instanceGroups**           | always         | The instance groups details for the cluster.                                                                              |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``array``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **instanceCount**          | always         | The initial number of instance nodes.                                                                                     |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``int``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **instanceGroupName**      | always         | The unique name of the instance group.                                                                                    |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``str``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **instanceType**           | always         | The cloud provider instance type for the node instances.                                                                  |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``str``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **instances**              | always         | Instances in the instance group.                                                                                          |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``list``                   |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **availabilityZone**     | always         | Availability zone of the instance.                                                                                        |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **instanceId**           | always         | Unique instance Id generated by the cloud provider.                                                                       |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **maxInstances**           | always         | The maximum number of instances that can be deployed to this instance group.                                              |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``int``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **minInstances**           | always         | The minimum number of instances that can be deployed to this instance group. If the value is 0, the group might be empty. |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``int``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **tags**                   | always         | Key/value pairs applied to all applicable resources deployed in cloud provider.                                           |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``list``                   |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **key**                  | always         | Tag name                                                                                                                  |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | | **value**                | always         | Tag value                                                                                                                 |
   | | | |                          |                |                                                                                                                           |
   | | | | |br|                     |                |                                                                                                                           |
   | | | |                          |                |                                                                                                                           |
   | | | | ``str``                  |                |                                                                                                                           |
   +-+-+-+--------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **instanceName**             | always         | The name of the workspace.                                                                                                |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **instanceStatus**           | always         | The workspace's current status.                                                                                           |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **instanceUrl**              | always         | URL of the workspace's user interface.                                                                                    |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **k8sClusterName**           | always         | The Kubernetes cluster name.                                                                                              |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **loadBalancerIPWhitelists** | always         | The whitelist of ips for loadBalancer.                                                                                    |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``array``                    |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **modelMetricsEnabled**      | when supported | Flag indicating if model metrics export is enabled for the cluster.                                                       |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``bool``                     |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **monitoringEnabled**        | always         | If usage monitoring is enabled or not on this workspace.                                                                  |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``bool``                     |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **tags**                     | always         | Tags provided by the user at the time of workspace creation.                                                              |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``list``                     |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **key**                    | always         | Tag name                                                                                                                  |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``str``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | | **value**                  | always         | Tag value                                                                                                                 |
   | | |                            |                |                                                                                                                           |
   | | | |br|                       |                |                                                                                                                           |
   | | |                            |                |                                                                                                                           |
   | | | ``str``                    |                |                                                                                                                           |
   +-+-+----------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | | **version**                  | always         | The version of Cloudera Machine Learning that was installed on the workspace.                                             |
   | |                              |                |                                                                                                                           |
   | | |br|                         |                |                                                                                                                           |
   | |                              |                |                                                                                                                           |
   | | ``str``                      |                |                                                                                                                           |
   +-+------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**                    | when supported | Returns the captured CDP SDK log.                                                                                         |
   |                                |                |                                                                                                                           |
   | |br|                           |                |                                                                                                                           |
   |                                |                |                                                                                                                           |
   | ``str``                        |                |                                                                                                                           |
   +--------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**              | when supported | Returns a list of each line of the captured CDP SDK log.                                                                  |
   |                                |                |                                                                                                                           |
   | |br|                           |                |                                                                                                                           |
   |                                |                |                                                                                                                           |
   | ``list``                       |                |                                                                                                                           |
   +--------------------------------+----------------+---------------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

