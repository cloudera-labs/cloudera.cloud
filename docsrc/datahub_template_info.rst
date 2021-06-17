.. _datahub_template_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: datahub_template_info -- Gather information about CDP Datahub Cluster Templates

datahub_template_info -- Gather information about CDP Datahub Cluster Templates
===============================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Datahub Cluster Templates



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +--------------------+----------------------+--------------------------------------------------------------+
   | **Parameter**      | **Choices/Defaults** | **Comments**                                                 |
   +--------------------+----------------------+--------------------------------------------------------------+
   | **name**           |                      | If a name is provided, that Template will be described.      |
   |                    |                      | If no name provided, all Templates will be listed.           |
   | |br|               |                      |                                                              |
   |                    |                      |                                                              |
   | ``str``            |                      |                                                              |
   |                    |                      |                                                              |
   |                    |                      | |br|                                                         |
   |                    |                      |                                                              |
   |                    |                      | *Aliases: template*                                          |
   +--------------------+----------------------+--------------------------------------------------------------+
   | **return_content** |                      | Flag dictating if cluster template content is returned       |
   |                    |                      |                                                              |
   | |br|               |                      |                                                              |
   |                    |                      |                                                              |
   | ``bool``           |                      |                                                              |
   |                    |                      |                                                              |
   |                    |                      | |br|                                                         |
   |                    |                      |                                                              |
   |                    |                      | *Aliases: template_content, content*                         |
   +--------------------+----------------------+--------------------------------------------------------------+
   | **verify_tls**     |                      | Verify the TLS certificates for the CDP endpoint.            |
   |                    |                      |                                                              |
   | |br|               |                      |                                                              |
   |                    |                      |                                                              |
   | ``bool``           |                      |                                                              |
   |                    |                      |                                                              |
   |                    |                      | |br|                                                         |
   |                    |                      |                                                              |
   |                    |                      | *Aliases: tls*                                               |
   +--------------------+----------------------+--------------------------------------------------------------+
   | **debug**          |                      | Capture the CDP SDK debug log.                               |
   |                    |                      |                                                              |
   | |br|               |                      |                                                              |
   |                    |                      |                                                              |
   | ``bool``           |                      |                                                              |
   |                    |                      |                                                              |
   |                    |                      | |br|                                                         |
   |                    |                      |                                                              |
   |                    |                      | *Aliases: debug_endpoints*                                   |
   +--------------------+----------------------+--------------------------------------------------------------+
   | **profile**        |                      | If provided, the CDP SDK will use this value as its profile. |
   |                    |                      |                                                              |
   | |br|               |                      |                                                              |
   |                    |                      |                                                              |
   | ``str``            |                      |                                                              |
   +--------------------+----------------------+--------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all Datahubs
  - cloudera.cloud.datahub_template_info:

  # Gather detailed information about a named Datahub
  - cloudera.cloud.datahub_template_info:
      name: example-template
      
  # Gather detailed information about a named Datahub, including the template contents in JSON
  - cloudera.cloud.datahub_template_info:
      name: example-template
      return_content: yes




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +------------------------------+----------------+----------------------------------------------------------+
   | **Key**                      | **Returned**   | **Description**                                          |
   +------------------------------+----------------+----------------------------------------------------------+
   | **templates**                | on success     | The information about the named Template or Templates    |
   |                              |                |                                                          |
   | |br|                         |                |                                                          |
   |                              |                |                                                          |
   | ``list``                     |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **clusterTemplateName**    | always         | The name of the cluster template.                        |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **crn**                    | always         | The CRN of the cluster template.                         |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **description**            | always         | The description of the cluster template.                 |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **productVersion**         | always         | The product version.                                     |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **instanceGroupCount**     | always         | The instance group count of the cluster.                 |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **status**                 | always         | The status of the cluster template.                      |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   | |                            |                |                                                          |
   | |                            |                | |br|                                                     |
   | |                            |                |                                                          |
   | |                            |                | **Sample:**                                              |
   | |                            |                |                                                          |
   | |                            |                | DEFAULT                                                  |
   | |                            |                |                                                          |
   | |                            |                | USER_MANAGED                                             |
   | |                            |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **clusterTemplateContent** | when specified | The cluster template contents, in JSON.                  |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``str``                    |                |                                                          |
   +-+----------------------------+----------------+----------------------------------------------------------+
   | | **tags**                   | always         | Tags added to the cluster template                       |
   | |                            |                |                                                          |
   | | |br|                       |                |                                                          |
   | |                            |                |                                                          |
   | | ``dict``                   |                |                                                          |
   +-+-+--------------------------+----------------+----------------------------------------------------------+
   | | | **key**                  | always         | The key of the tag.                                      |
   | | |                          |                |                                                          |
   | | | |br|                     |                |                                                          |
   | | |                          |                |                                                          |
   | | | ``str``                  |                |                                                          |
   +-+-+--------------------------+----------------+----------------------------------------------------------+
   | | | **value**                | always         | The value of the tag.                                    |
   | | |                          |                |                                                          |
   | | | |br|                     |                |                                                          |
   | | |                          |                |                                                          |
   | | | ``str``                  |                |                                                          |
   +-+-+--------------------------+----------------+----------------------------------------------------------+
   | **sdk_out**                  | when supported | Returns the captured CDP SDK log.                        |
   |                              |                |                                                          |
   | |br|                         |                |                                                          |
   |                              |                |                                                          |
   | ``str``                      |                |                                                          |
   +------------------------------+----------------+----------------------------------------------------------+
   | **sdk_out_lines**            | when supported | Returns a list of each line of the captured CDP SDK log. |
   |                              |                |                                                          |
   | |br|                         |                |                                                          |
   |                              |                |                                                          |
   | ``list``                     |                |                                                          |
   +------------------------------+----------------+----------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

