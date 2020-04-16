.. _env_cred_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_cred_info -- Gather information about CDP Credentials

env_cred_info -- Gather information about CDP Credentials
=========================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Credentials using the CDP SDK.

- The module supports check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                                                                                                      |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **name**       |                      | If a name is provided, the module will describe the found Credential. If the Credential is not found, the module will return an empty dictionary. |
   |                |                      | If no name is provided, the module will list all found Credentials. If no Credentials are found, the module will return an empty list.            |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                   |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                                                                                                 |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                              |
   |                |                      |                                                                                                                                                   |
   |                |                      | *Aliases: tls*                                                                                                                                    |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                                                                                                    |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``bool``       |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   |                |                      | |br|                                                                                                                                              |
   |                |                      |                                                                                                                                                   |
   |                |                      | *Aliases: debug_endpoints*                                                                                                                        |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.                                                                                      |
   |                |                      |                                                                                                                                                   |
   | |br|           |                      |                                                                                                                                                   |
   |                |                      |                                                                                                                                                   |
   | ``str``        |                      |                                                                                                                                                   |
   +----------------+----------------------+---------------------------------------------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Gather information about all Credentials
  - cloudera.cloud.env_cred_info:

  # Gather information about a named Credential
  - cloudera.cloud.env_cred_info:
      name: example-credential




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **Key**              | **Returned**   | **Description**                                                                                                     |
   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **credentials**      | always         | Returns an array of objects for the named Credential or all Credentials.                                            |
   |                      |                |                                                                                                                     |
   | |br|                 |                |                                                                                                                     |
   |                      |                |                                                                                                                     |
   | ``complex``          |                |                                                                                                                     |
   +-+--------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **cloudPlatform**  | always         | The name of the cloud provider for the Credential.                                                                  |
   | |                    |                |                                                                                                                     |
   | | |br|               |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | | ``str``            |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | |                    |                | |br|                                                                                                                |
   | |                    |                |                                                                                                                     |
   | |                    |                | **Sample:**                                                                                                         |
   | |                    |                |                                                                                                                     |
   | |                    |                | AWS                                                                                                                 |
   | |                    |                |                                                                                                                     |
   +-+--------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **credentialName** | always         | The name of the Credential.                                                                                         |
   | |                    |                |                                                                                                                     |
   | | |br|               |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | | ``str``            |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | |                    |                | |br|                                                                                                                |
   | |                    |                |                                                                                                                     |
   | |                    |                | **Sample:**                                                                                                         |
   | |                    |                |                                                                                                                     |
   | |                    |                | example-credential                                                                                                  |
   | |                    |                |                                                                                                                     |
   +-+--------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **crn**            | always         | The CDP CRN value derived from the cross-account Role ARN used during creation.                                     |
   | |                    |                |                                                                                                                     |
   | | |br|               |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | | ``str``            |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | |                    |                | |br|                                                                                                                |
   | |                    |                |                                                                                                                     |
   | |                    |                | **Sample:**                                                                                                         |
   | |                    |                |                                                                                                                     |
   | |                    |                | crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:61eb5b97-226a-4be7-b56d-795d18a043b5 |
   | |                    |                |                                                                                                                     |
   +-+--------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **description**    | when supported | The description of the Credential.                                                                                  |
   | |                    |                |                                                                                                                     |
   | | |br|               |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | | ``str``            |                |                                                                                                                     |
   | |                    |                |                                                                                                                     |
   | |                    |                | |br|                                                                                                                |
   | |                    |                |                                                                                                                     |
   | |                    |                | **Sample:**                                                                                                         |
   | |                    |                |                                                                                                                     |
   | |                    |                | An example Credential                                                                                               |
   | |                    |                |                                                                                                                     |
   +-+--------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**          | when supported | Returns the captured CDP SDK log.                                                                                   |
   |                      |                |                                                                                                                     |
   | |br|                 |                |                                                                                                                     |
   |                      |                |                                                                                                                     |
   | ``str``              |                |                                                                                                                     |
   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**    | when supported | Returns a list of each line of the captured CDP SDK log.                                                            |
   |                      |                |                                                                                                                     |
   | |br|                 |                |                                                                                                                     |
   |                      |                |                                                                                                                     |
   | ``list``             |                |                                                                                                                     |
   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

