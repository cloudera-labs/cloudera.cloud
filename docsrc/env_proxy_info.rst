.. _env_proxy_info_module:
.. include:: <isoamsa.txt>
.. |br| raw:: html

   <br />

.. Macros for table-building
.. Start the module documentation


.. title:: env_proxy_info -- Gather information about CDP Environment Proxies

env_proxy_info -- Gather information about CDP Environment Proxies
==================================================================

.. contents::
   :local:
   :depth: 1

Synopsis
--------

- Gather information about CDP Environment Proxy Configurations



Requirements
------------
The below requirements are needed on the host that executes this module.

- cdpy


Parameters
----------




.. table::
   :widths: 30 20 50

   +----------------+----------------------+-------------------------------------------------------------------+
   | **Parameter**  | **Choices/Defaults** | **Comments**                                                      |
   +----------------+----------------------+-------------------------------------------------------------------+
   | **name**       |                      | If a name is provided, that proxy configuration will be described |
   |                |                      | If no name is provided, all proxy configurations will be listed   |
   | |br|           |                      |                                                                   |
   |                |                      |                                                                   |
   | ``str``        |                      |                                                                   |
   +----------------+----------------------+-------------------------------------------------------------------+
   | **verify_tls** |                      | Verify the TLS certificates for the CDP endpoint.                 |
   |                |                      |                                                                   |
   | |br|           |                      |                                                                   |
   |                |                      |                                                                   |
   | ``bool``       |                      |                                                                   |
   |                |                      |                                                                   |
   |                |                      | |br|                                                              |
   |                |                      |                                                                   |
   |                |                      | *Aliases: tls*                                                    |
   +----------------+----------------------+-------------------------------------------------------------------+
   | **debug**      |                      | Capture the CDP SDK debug log.                                    |
   |                |                      |                                                                   |
   | |br|           |                      |                                                                   |
   |                |                      |                                                                   |
   | ``bool``       |                      |                                                                   |
   |                |                      |                                                                   |
   |                |                      | |br|                                                              |
   |                |                      |                                                                   |
   |                |                      | *Aliases: debug_endpoints*                                        |
   +----------------+----------------------+-------------------------------------------------------------------+
   | **profile**    |                      | If provided, the CDP SDK will use this value as its profile.      |
   |                |                      |                                                                   |
   | |br|           |                      |                                                                   |
   |                |                      |                                                                   |
   | ``str``        |                      |                                                                   |
   +----------------+----------------------+-------------------------------------------------------------------+






Examples
--------

.. code-block:: yaml+jinja

  
  # Note: These examples do not set authentication details.

  # List basic information about all Proxy Configurations
  - cloudera.cloud.env_proxy_info:

  # Gather detailed information about a named Proxy Configuration
  - cloudera.cloud.env_proxy_info:
      name: example-proxy




Return Values
-------------

Common return values are documented here, the following are fields unique to this module.


.. table::
   :widths: 30 20 50

   +-----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **Key**               | **Returned**   | **Description**                                                                                                     |
   +-----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **proxies**           | on success     | Details on the proxies.                                                                                             |
   |                       |                |                                                                                                                     |
   | |br|                  |                |                                                                                                                     |
   |                       |                |                                                                                                                     |
   | ``list``              |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **crn**             | always         | The CRN of the proxy config.                                                                                        |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | crn:cdp:environments:us-west-1:558bc1d2-8867-4357-8524-311d51259233:credential:eb6c5fc8-38fe-4c3c-8194-1a0f05edc010 |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **description**     | when supported | A description for the proxy config.                                                                                 |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | Example proxy configuration                                                                                         |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **host**            | always         | The proxy host.                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | example.cloudera.com                                                                                                |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **port**            | always         | The proxy port.                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``int``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | 8443                                                                                                                |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **protocol**        | always         | The proxy protocol.                                                                                                 |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | https                                                                                                               |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **proxyConfigName** | always         | The name of the proxy config.                                                                                       |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | example-proxy-config                                                                                                |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | | **user**            | when supported | The proxy user.                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | |br|                |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | | ``str``             |                |                                                                                                                     |
   | |                     |                |                                                                                                                     |
   | |                     |                | |br|                                                                                                                |
   | |                     |                |                                                                                                                     |
   | |                     |                | **Sample:**                                                                                                         |
   | |                     |                |                                                                                                                     |
   | |                     |                | proxy_username                                                                                                      |
   | |                     |                |                                                                                                                     |
   +-+---------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **sdk_out**           | when supported | Returns the captured CDP SDK log.                                                                                   |
   |                       |                |                                                                                                                     |
   | |br|                  |                |                                                                                                                     |
   |                       |                |                                                                                                                     |
   | ``str``               |                |                                                                                                                     |
   +-----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+
   | **sdk_out_lines**     | when supported | Returns a list of each line of the captured CDP SDK log.                                                            |
   |                       |                |                                                                                                                     |
   | |br|                  |                |                                                                                                                     |
   |                       |                |                                                                                                                     |
   | ``list``              |                |                                                                                                                     |
   +-----------------------+----------------+---------------------------------------------------------------------------------------------------------------------+


Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Webster Mudge (@wmudge)
- Dan Chaffelson (@chaffelson)

