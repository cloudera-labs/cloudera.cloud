.. _env_cred_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_cred -- Create, update, and destroy CDP credentials

env_cred -- Create, update, and destroy CDP credentials
=======================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Create, update, and destroy CDP credentials.

- The module support check_mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **Parameter**    | **Choices/Defaults**  | **Comments**                                                                                               |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **name**         |                       | The name of the Credential.                                                                                |
   |                  |                       | The name must conform to the CDP Credential format, which is lowercase letters, numbers, and hyphens only. |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | *Required*       |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   |                  |                       | |br|                                                                                                       |
   |                  |                       |                                                                                                            |
   |                  |                       | *Aliases: credential*                                                                                      |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **state**        | **Choices:**          | Establish the state of the Credential in CDP.                                                              |
   |                  |  - **present** |larr| |                                                                                                            |
   | |br|             |  - absent             |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **cloud**        | **Choices:**          | The target cloud provider for the Credential.                                                              |
   |                  |  - aws                | Required if *state=present*.                                                                               |
   | |br|             |  - azure              |                                                                                                            |
   |                  |  - gcp                |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **role**         |                       | The CDP cross-account role for AWS                                                                         |
   |                  |                       | For *cloud=aws*, this is the Role ARN for the cross-account role.                                          |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   |                  |                       | |br|                                                                                                       |
   |                  |                       |                                                                                                            |
   |                  |                       | *Aliases: arn, role_arn*                                                                                   |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **subscription** |                       | The Subscription ID or URI of the Azure Subscription being used                                            |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **tenant**       |                       | The URI of the Azure Tenant                                                                                |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **application**  |                       | The ApplicationId of the Azure Application used for access                                                 |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **secret**       |                       | The Secret for the Application access on Azure                                                             |
   |                  |                       | The path to the Key File for the Service Account being used on Google                                      |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **description**  |                       | Descriptive text for the Credential.                                                                       |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   |                  |                       | |br|                                                                                                       |
   |                  |                       |                                                                                                            |
   |                  |                       | *Aliases: desc*                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **retries**      |                       | Number of times to retry the create operation if a possible eventual consistency error is returned         |
   |                  |                       | Set to 0 to fail immediately on such errors                                                                |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``int``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **delay**        |                       | Delay period in seconds between retries                                                                    |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``int``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **verify_tls**   |                       | Verify the TLS certificates for the CDP endpoint.                                                          |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``bool``         |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   |                  |                       | |br|                                                                                                       |
   |                  |                       |                                                                                                            |
   |                  |                       | *Aliases: tls*                                                                                             |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **debug**        |                       | Capture the CDP SDK debug log.                                                                             |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``bool``         |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   |                  |                       | |br|                                                                                                       |
   |                  |                       |                                                                                                            |
   |                  |                       | *Aliases: debug_endpoints*                                                                                 |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+
   | **profile**      |                       | If provided, the CDP SDK will use this value as its profile.                                               |
   |                  |                       |                                                                                                            |
   | |br|             |                       |                                                                                                            |
   |                  |                       |                                                                                                            |
   | ``str``          |                       |                                                                                                            |
   +------------------+-----------------------+------------------------------------------------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # Create a CDP Credential for AWS
  - cloudera.cloud.env_cred:
      state: present
      cloud: aws
      name: example-credential
      description: This is an example Credential
      role: arn:aws:iam::981304421142:role/some-cross-account-role

  # Delete a CDP Credential
  - cloudera.cloud.env_cred:
      state: absent
      name: example-credential

  # Create a CDP Credential for AWS and log the output of the CDP SDK in the return values
  - cloudera.cloud.env_cred:
      name: example-credential
      debug: yes




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **Key**              | **Returned**   | **Description**                                                                                                     |
   +----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **credential**       | success        | Returns an object for the Credential.                                                                               |
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
- Daniel Chaffelson (@chaffelson)

