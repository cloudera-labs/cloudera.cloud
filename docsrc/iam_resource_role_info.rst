.. _iam_resource_role_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: iam_resource_role_info -- Gather information about CDP Public IAM resource roles

iam_resource_role_info -- Gather information about CDP Public IAM resource roles
================================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Public IAM resource role or roles




Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+--------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                 |
   +----------------+----------------------+--------------------------------------------------------------+
   | **name**       |                      | A list of Resource Role CRNs or a single role's CRN.         |
   |                |                      | If no CRNs are provided, all Resource Roles are returned.    |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``list``       |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: crn*                                               |
   +----------------+----------------------+--------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.            |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``bool``       |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: tls*                                               |
   +----------------+----------------------+--------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                               |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``bool``       |                      |                                                              |
   |                |                      |                                                              |
   |                |                      | |br|                                                         |
   |                |                      |                                                              |
   |                |                      | *Aliases: debug_endpoints*                                   |
   +----------------+----------------------+--------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile. |
   |                |                      |                                                              |
   | |br|           |                      |                                                              |
   |                |                      |                                                              |
   | ``str``        |                      |                                                              |
   +----------------+----------------------+--------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about all Resource Roles
  - cloudera.cloud.iam_resource_role_info:

  # Gather information about a named Resource Role
  - cloudera.cloud.iam_resource_role_info:
      name: crn:altus:iam:us-west-1:altus:resourceRole:ODUser

  # Gather information about several named Resource Roles
  - cloudera.cloud.iam_resource_role_info:
      name:
        - crn:altus:iam:us-west-1:altus:resourceRole:DWAdmin
        - crn:altus:iam:us-west-1:altus:resourceRole:DWUser




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +--------------------+----------------+----------------------------------------------------------+
   | **Key**            | **Returned**   | **Description**                                          |
   +--------------------+----------------+----------------------------------------------------------+
   | **resource_roles** | always         | The information about the named Resource Role or Roles   |
   |                    |                |                                                          |
   | |br|               |                |                                                          |
   |                    |                |                                                          |
   | ``list``           |                |                                                          |
   +-+------------------+----------------+----------------------------------------------------------+
   | | **crn**          | on success     | The CRN of the resource role.                            |
   | |                  |                |                                                          |
   | | |br|             |                |                                                          |
   | |                  |                |                                                          |
   | | ``str``          |                |                                                          |
   +-+------------------+----------------+----------------------------------------------------------+
   | | **rights**       | on success     | List of rights assigned to the group.                    |
   | |                  |                |                                                          |
   | | |br|             |                |                                                          |
   | |                  |                |                                                          |
   | | ``list``         |                |                                                          |
   +-+------------------+----------------+----------------------------------------------------------+
   | **sdk_out**        | when supported | Returns the captured CDP SDK log.                        |
   |                    |                |                                                          |
   | |br|               |                |                                                          |
   |                    |                |                                                          |
   | ``str``            |                |                                                          |
   +--------------------+----------------+----------------------------------------------------------+
   | **sdk_out_lines**  | when supported | Returns a list of each line of the captured CDP SDK log. |
   |                    |                |                                                          |
   | |br|               |                |                                                          |
   |                    |                |                                                          |
   | ``list``           |                |                                                          |
   +--------------------+----------------+----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

