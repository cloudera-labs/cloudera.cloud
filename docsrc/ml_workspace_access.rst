.. _ml_workspace_access_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: ml_workspace_access -- Grant and revoke user access to CDP Machine Learning Workspaces

ml_workspace_access -- Grant and revoke user access to CDP Machine Learning Workspaces
======================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Grant and revoke user access to CDP Machine Learning Workspaces



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +-----------------+-----------------------+--------------------------------------------------------------+
   | **Parameter**   | **Choices/Defaults**  | **Comments**                                                 |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **name**        |                       | The name of the ML Workspace                                 |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``str``         |                       |                                                              |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | *Required*      |                       |                                                              |
   |                 |                       |                                                              |
   |                 |                       | |br|                                                         |
   |                 |                       |                                                              |
   |                 |                       | *Aliases: workspace*                                         |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **environment** |                       | The name of the Environment for the ML Workspace             |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``str``         |                       |                                                              |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | *Required*      |                       |                                                              |
   |                 |                       |                                                              |
   |                 |                       | |br|                                                         |
   |                 |                       |                                                              |
   |                 |                       | *Aliases: env*                                               |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **user**        |                       | The cloud provider identifier for the user.                  |
   |                 |                       | For ``AWS``, this is the User ARN.                           |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``str``         |                       |                                                              |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | *Required*      |                       |                                                              |
   |                 |                       |                                                              |
   |                 |                       | |br|                                                         |
   |                 |                       |                                                              |
   |                 |                       | *Aliases: identifier*                                        |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **state**       | **Choices:**          | The declarative state of the access to the ML Workspace      |
   |                 |  - **present** |larr| |                                                              |
   | |br|            |  - absent             |                                                              |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **verify_tls**  |                       | Verify the TLS certificates for the CDP endpoint.            |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``bool``        |                       |                                                              |
   |                 |                       |                                                              |
   |                 |                       | |br|                                                         |
   |                 |                       |                                                              |
   |                 |                       | *Aliases: tls*                                               |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **debug**       |                       | Capture the CDP SDK debug log.                               |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``bool``        |                       |                                                              |
   |                 |                       |                                                              |
   |                 |                       | |br|                                                         |
   |                 |                       |                                                              |
   |                 |                       | *Aliases: debug_endpoints*                                   |
   +-----------------+-----------------------+--------------------------------------------------------------+
   | **profile**     |                       | If provided, the CDP SDK will use this value as its profile. |
   |                 |                       |                                                              |
   | |br|            |                       |                                                              |
   |                 |                       |                                                              |
   | ``str``         |                       |                                                              |
   +-----------------+-----------------------+--------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Grant access for user (and register the output to capture the kubeconfig)
  - cloudera.cloud.ml_workspace_access:
      name: ml-example
      env: cdp-env
      user: some-cloud-provider-specific-id
    register: access_output

  # Revoke access for user
  - cloudera.cloud.ml_workspace_acces:
      name: ml-k8s-example
      env: cdp-env
      user: some-cloud-provider-specific-id
      state: absent




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-------------------+----------------+-------------------------------------------------------------+
   | **Key**           | **Returned**   | **Description**                                             |
   +-------------------+----------------+-------------------------------------------------------------+
   | **workspace**     | on success     | The information about the user's access to the ML Workspace |
   |                   |                |                                                             |
   | |br|              |                |                                                             |
   |                   |                |                                                             |
   | ``dict``          |                |                                                             |
   +-+-----------------+----------------+-------------------------------------------------------------+
   | | **kubeconfig**  | always         | The kubeconfig file as a string                             |
   | |                 |                |                                                             |
   | | |br|            |                |                                                             |
   | |                 |                |                                                             |
   | | ``str``         |                |                                                             |
   +-+-----------------+----------------+-------------------------------------------------------------+
   | **sdk_out**       | when supported | Returns the captured CDP SDK log.                           |
   |                   |                |                                                             |
   | |br|              |                |                                                             |
   |                   |                |                                                             |
   | ``str``           |                |                                                             |
   +-------------------+----------------+-------------------------------------------------------------+
   | **sdk_out_lines** | when supported | Returns a list of each line of the captured CDP SDK log.    |
   |                   |                |                                                             |
   | |br|              |                |                                                             |
   |                   |                |                                                             |
   | ``list``          |                |                                                             |
   +-------------------+----------------+-------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)

