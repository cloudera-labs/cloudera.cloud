.. _iam_group_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: iam_group -- Create, update, or destroy CDP IAM Groups

iam_group -- Create, update, or destroy CDP IAM Groups
======================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create, update, and destroy CDP IAM Groups.

- A group is a named collection of users and machine users.

- Roles and resource roles can be assigned to a group impacting all members of the group.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**      | **Choices/Defaults**  | **Comments**                                                                                                                |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **name**           |                       | The name of the group.                                                                                                      |
   |                    |                       | The name must be unique, must have a maximum of 32 characters, and must contain only alphanumeric characters, "-", and "_". |
   | |br|               |                       | The first character of the name must be alphabetic or an underscore.                                                        |
   |                    |                       | Names are are not case-sensitive.                                                                                           |
   | ``str``            |                       | The group named "administrators" is reserved.                                                                               |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | *Required*         |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   |                    |                       | |br|                                                                                                                        |
   |                    |                       |                                                                                                                             |
   |                    |                       | *Aliases: group_name*                                                                                                       |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **purge**          |                       | Flag to replace ``roles``, ``users``, and ``resource_roles`` with their specified values.                                   |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``bool``           |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   |                    |                       | |br|                                                                                                                        |
   |                    |                       |                                                                                                                             |
   |                    |                       | *Aliases: replace*                                                                                                          |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **resource_roles** |                       | A list of resource role assignments.                                                                                        |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``list``           |                       |                                                                                                                             |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **roles**          |                       | A single role or list of roles assigned to the group.                                                                       |
   |                    |                       | The role must be identified by its full CRN.                                                                                |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``list``           |                       |                                                                                                                             |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **state**          | **Choices:**          | The state of the group.                                                                                                     |
   |                    |  - **present** |larr| |                                                                                                                             |
   | |br|               |  - absent             |                                                                                                                             |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **sync**           |                       | Whether group membership is synced when a user logs in.                                                                     |
   |                    |                       | The default is to sync group membership.                                                                                    |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``bool``           |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   |                    |                       | |br|                                                                                                                        |
   |                    |                       |                                                                                                                             |
   |                    |                       | *Aliases: sync_membership, sync_on_login*                                                                                   |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **users**          |                       | A single user or list of users assigned to the group.                                                                       |
   |                    |                       | The user can be either the name or CRN.                                                                                     |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``list``           |                       |                                                                                                                             |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls**     |                       | Verify the TLS certificates for the CDP endpoint.                                                                           |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``bool``           |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   |                    |                       | |br|                                                                                                                        |
   |                    |                       |                                                                                                                             |
   |                    |                       | *Aliases: tls*                                                                                                              |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **debug**          |                       | Capture the CDP SDK debug log.                                                                                              |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``bool``           |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   |                    |                       | |br|                                                                                                                        |
   |                    |                       |                                                                                                                             |
   |                    |                       | *Aliases: debug_endpoints*                                                                                                  |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+
   | **profile**        |                       | If provided, the CDP SDK will use this value as its profile.                                                                |
   |                    |                       |                                                                                                                             |
   | |br|               |                       |                                                                                                                             |
   |                    |                       |                                                                                                                             |
   | ``str``            |                       |                                                                                                                             |
   +--------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a group
  - cloudera.cloud.iam_group:
      name: group-example

  # Create a group with membership sync disabled
  - cloudera.cloud.iam_group:
      state: present
      name: group-example
      sync: no

  # Delete a group
  - cloudera.cloud.iam_group:
      state: absent
      name: group-example

  # Assign users to a group
  - cloudera.cloud.iam_group:
      name: group-example
      users:
        - user-a
        - user-b

  # Assign roles to a group
  - cloudera.cloud.iam_group:
      name: group-example
      roles:
        - role-a
        - role-b

  # Replace resource roles a group
  - cloudera.cloud.iam_group:
      name: group-example
      resource_roles:
        - role-c
        - role-d
      purge: yes




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **Key**                         | **Returned**   | **Description**                                                                                                  |
   +---------------------------------+----------------+------------------------------------------------------------------------------------------------------------------+
   | **group**                       | always         | The information about the Group                                                                                  |
   |                                 |                |                                                                                                                  |
   | |br|                            |                |                                                                                                                  |
   |                                 |                |                                                                                                                  |
   | ``dict``                        |                |                                                                                                                  |
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

