.. _iam_group_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: iam_group_info -- Gather information about CDP Public IAM groups

iam_group_info -- Gather information about CDP Public IAM groups
================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Public IAM group or groups




Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+---------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                        |
   +----------------+----------------------+---------------------------------------------------------------------+
   | **name**       |                      | A list of group names or CRNs or a single group name/CRN.           |
   |                |                      | If no group name or CRN is provided, all groups are returned.       |
   | |br|           |                      | If any parameter group names are not found, no groups are returned. |
   |                |                      |                                                                     |
   | ``list``       |                      |                                                                     |
   |                |                      |                                                                     |
   |                |                      | |br|                                                                |
   |                |                      |                                                                     |
   |                |                      | *Aliases: group_name*                                               |
   +----------------+----------------------+---------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                   |
   |                |                      |                                                                     |
   | |br|           |                      |                                                                     |
   |                |                      |                                                                     |
   | ``bool``       |                      |                                                                     |
   |                |                      |                                                                     |
   |                |                      | |br|                                                                |
   |                |                      |                                                                     |
   |                |                      | *Aliases: tls*                                                      |
   +----------------+----------------------+---------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                      |
   |                |                      |                                                                     |
   | |br|           |                      |                                                                     |
   |                |                      |                                                                     |
   | ``bool``       |                      |                                                                     |
   |                |                      |                                                                     |
   |                |                      | |br|                                                                |
   |                |                      |                                                                     |
   |                |                      | *Aliases: debug_endpoints*                                          |
   +----------------+----------------------+---------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.        |
   |                |                      |                                                                     |
   | |br|           |                      |                                                                     |
   |                |                      |                                                                     |
   | ``str``        |                      |                                                                     |
   +----------------+----------------------+---------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about all Groups
  - cloudera.cloud.iam_group_info:

  # Gather information about a named Group
  - cloudera.cloud.iam_group_info:
      name: example-01

  # Gather information about several named Groups
  - cloudera.cloud.iam_group_info:
      name:
        - example-01
        - example-02
        - example-03




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **Key**                         | **Returned**   | **Description**                                                                                                  |
   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **groups**                      | always         | The information about the named Group or Groups                                                                  |
   |                                 |                |                                                                                                                  |
   | |br|                            |                |                                                                                                                  |
   |                                 |                |                                                                                                                  |
   | ``list``                        |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **creationDate**              | on success     | The date when this group record was created.                                                                     |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``str``                       |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | |                               |                | |br|                                                                                                             |
   | |                               |                |                                                                                                                  |
   | |                               |                | **Sample:**                                                                                                      |
   | |                               |                |                                                                                                                  |
   | |                               |                | 2020-07-06 12:24:05.531000+00:00                                                                                 |
   | |                               |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **crn**                       | on success     | The CRN of the group.                                                                                            |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``str``                       |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **groupName**                 | on success     | The group name.                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``str``                       |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | |                               |                | |br|                                                                                                             |
   | |                               |                |                                                                                                                  |
   | |                               |                | **Sample:**                                                                                                      |
   | |                               |                |                                                                                                                  |
   | |                               |                | example-01                                                                                                       |
   | |                               |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **users**                     | on success     | List of User CRNs which are members of the group.                                                                |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``list``                      |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **roles**                     | on success     | List of Role CRNs assigned to the group.                                                                         |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``list``                      |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **resource_roles**            | on success     | List of Resource-to-Role assignments, by CRN, that are associated with the group.                                |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``list``                      |                |                                                                                                                  |
   +-+-+-----------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | | **resourceCrn**             | on success     | The CRN of the resource granted the rights of the role.                                                          |
   | | |                             |                |                                                                                                                  |
   | | | |br|                        |                |                                                                                                                  |
   | | |                             |                |                                                                                                                  |
   | | | ``str``                     |                |                                                                                                                  |
   +-+-+-----------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | | **resourceRoleCrn**         | on success     | The CRN of the CDP Role.                                                                                         |
   | | |                             |                |                                                                                                                  |
   | | | |br|                        |                |                                                                                                                  |
   | | |                             |                |                                                                                                                  |
   | | | ``str``                     |                |                                                                                                                  |
   +-+-+-----------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | | **syncMembershipOnUserLogin** | when supported | Flag indicating whether group membership is synced when a user logs in. The default is to sync group membership. |
   | |                               |                |                                                                                                                  |
   | | |br|                          |                |                                                                                                                  |
   | |                               |                |                                                                                                                  |
   | | ``bool``                      |                |                                                                                                                  |
   +-+-------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**                     | when supported | Returns the captured CDP SDK log.                                                                                |
   |                                 |                |                                                                                                                  |
   | |br|                            |                |                                                                                                                  |
   |                                 |                |                                                                                                                  |
   | ``str``                         |                |                                                                                                                  |
   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**               | when supported | Returns a list of each line of the captured CDP SDK log.                                                         |
   |                                 |                |                                                                                                                  |
   | |br|                            |                |                                                                                                                  |
   |                                 |                |                                                                                                                  |
   | ``list``                        |                |                                                                                                                  |
   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

