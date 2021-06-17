.. _df_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: df -- Enable or Disable CDP DataFlow Services

df -- Enable or Disable CDP DataFlow Services
=============================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Enable or Disable CDP DataFlow Services



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**           | **Choices/Defaults**  | **Comments**                                                                                                              |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **crn**                 |                       | The name or crn of the CDP Environment to host the Dataflow Service                                                       |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``str``                 |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | *Required*              |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: name, env_crn*                                                                                                  |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **state**               | **Choices:**          | The declarative state of the Dataflow Service                                                                             |
   |                         |  - **present** |larr| |                                                                                                                           |
   | |br|                    |  - enabled            |                                                                                                                           |
   |                         |  - absent             |                                                                                                                           |
   | ``str``                 |  - disabled           |                                                                                                                           |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **nodes_min**           |                       | The minimum number of kubernetes nodes needed for the environment. Note that the lowest minimum is 3 nodes.               |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``int``                 |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: min_k8s_node_count*                                                                                             |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **nodes_max**           |                       | The maximum number of  kubernetes  nodes that environment may scale up under high-demand situations.                      |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``int``                 |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: max_k8s_node_count*                                                                                             |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **public_loadbalancer** |                       | Indicates whether or not to use a public load balancer when deploying dependencies stack.                                 |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``bool``                |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: use_public_load_balancer*                                                                                       |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **ip_ranges**           |                       | The IP ranges authorized to connect to the Kubernetes API server                                                          |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``list``                |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: authorized_ip_ranges*                                                                                           |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **persist**             |                       | Whether or not to retain the database records of related entities during removal.                                         |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``bool``                |                       |                                                                                                                           |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **wait**                |                       | Flag to enable internal polling to wait for the Dataflow Service to achieve the declared state.                           |
   |                         |                       | If set to FALSE, the module will return immediately.                                                                      |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``bool``                |                       |                                                                                                                           |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **delay**               |                       | The internal polling interval (in seconds) while the module waits for the Dataflow Service to achieve the declared state. |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``int``                 |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: polling_delay*                                                                                                  |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **timeout**             |                       | The internal polling timeout (in seconds) while the module waits for the Dataflow Service to achieve the declared state.  |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``int``                 |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: polling_timeout*                                                                                                |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**          |                       | Verify the TLS certificates for the CDP endpoint.                                                                         |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``bool``                |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: tls*                                                                                                            |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **debug**               |                       | Capture the CDP SDK debug log.                                                                                            |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``bool``                |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   |                         |                       | |br|                                                                                                                      |
   |                         |                       |                                                                                                                           |
   |                         |                       | *Aliases: debug_endpoints*                                                                                                |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+
   | **profile**             |                       | If provided, the CDP SDK will use this value as its profile.                                                              |
   |                         |                       |                                                                                                                           |
   | |br|                    |                       |                                                                                                                           |
   |                         |                       |                                                                                                                           |
   | ``str``                 |                       |                                                                                                                           |
   +-------------------------+-----------------------+---------------------------------------------------------------------------------------------------------------------------+


Notes
-----

.. note::
   - This feature this module is for is in Technical Preview




Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a Dataflow Service
  - cloudera.cloud.df:
      name: my-service
      nodes_min: 3
      nodes_max: 10
      public_loadbalancer: True
      ip_ranges: ['192.168.0.1/24']
      state: present
      wait: yes

  # Remove a Dataflow Service with Async wait
  - cloudera.cloud.df:
      name: my-service
      persist: False
      state: absent
      wait: yes
    async: 3600
    poll: 0
    register: __my_teardown_request





Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | **Key**                       | **Returned**   | **Description**                                                                                    |
   +-------------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | **environments**              | always         | The information about the named DataFlow Service or DataFlow Services                              |
   |                               |                |                                                                                                    |
   | |br|                          |                |                                                                                                    |
   |                               |                |                                                                                                    |
   | ``list``                      |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **crn**                     | always         | The DataFlow Service's parent environment CRN.                                                     |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **name**                    | always         | The DataFlow Service's parent environment name.                                                    |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **cloudPlatform**           | always         | The cloud platform of the environment.                                                             |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **region**                  | always         | The region of the environment.                                                                     |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **deploymentCount**         | always         | The deployment count.                                                                              |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **minK8sNodeCount**         | always         | The  minimum number of Kubernetes nodes that need to be provisioned in the environment.            |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``int``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **maxK8sNodeCount**         | always         | The maximum number of kubernetes nodes that environment may scale up under high-demand situations. |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **status**                  | always         | The status of a DataFlow enabled environment.                                                      |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``dict``                    |                |                                                                                                    |
   +-+-+---------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | | **state**                 | always         | The state of the environment.                                                                      |
   | | |                           |                |                                                                                                    |
   | | | |br|                      |                |                                                                                                    |
   | | |                           |                |                                                                                                    |
   | | | ``str``                   |                |                                                                                                    |
   +-+-+---------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | | **message**               | always         | A status message for the environment.                                                              |
   | | |                           |                |                                                                                                    |
   | | | |br|                      |                |                                                                                                    |
   | | |                           |                |                                                                                                    |
   | | | ``str``                   |                |                                                                                                    |
   +-+-+---------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **k8sNodeCount**            | always         | The number of kubernetes nodes currently in use by DataFlow for this environment.                  |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``int``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **instanceType**            | always         | The instance type of the kubernetes nodes currently in use by DataFlow for this environment.       |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **dfLocalUrl**              | always         | The URL of the environment local DataFlow application.                                             |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **authorizedIpRanges**      | always         | The authorized IP Ranges.                                                                          |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``list``                    |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **activeWarningAlertCount** | always         | Current count of active alerts classified as a warning.                                            |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``int``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **activeErrorAlertCount**   | always         | Current count of active alerts classified as an error.                                             |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``int``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | | **clusterId**               | if enabled     | Cluster id of the environment.                                                                     |
   | |                             |                |                                                                                                    |
   | | |br|                        |                |                                                                                                    |
   | |                             |                |                                                                                                    |
   | | ``str``                     |                |                                                                                                    |
   +-+-----------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | **sdk_out**                   | when supported | Returns the captured CDP SDK log.                                                                  |
   |                               |                |                                                                                                    |
   | |br|                          |                |                                                                                                    |
   |                               |                |                                                                                                    |
   | ``str``                       |                |                                                                                                    |
   +-------------------------------+----------------+----------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**             | when supported | Returns a list of each line of the captured CDP SDK log.                                           |
   |                               |                |                                                                                                    |
   | |br|                          |                |                                                                                                    |
   |                               |                |                                                                                                    |
   | ``list``                      |                |                                                                                                    |
   +-------------------------------+----------------+----------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Dan Chaffelson (@chaffelson)

