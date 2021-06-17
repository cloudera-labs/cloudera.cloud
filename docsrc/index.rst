cloudera.cloud Ansible Collection
=================================

.. toctree::
   :hidden:
   :caption: Module APIs

   account_auth <account_auth>
   account_auth_info <account_auth_info>
   account_cred_info <account_cred_info>
   datalake <datalake>
   datalake_info <datalake_info>
   datalake_runtime_info <datalake_runtime_info>
   datahub_cluster <datahub_cluster>
   datahub_cluster_info <datahub_cluster_info>
   datahub_definition_info <datahub_definition_info>
   datahub_template_info <datahub_template_info>
   df <df>
   df_info <df_info>
   dw_cluster <dw_cluster>
   dw_cluster_info <dw_cluster_info>
   env <env>
   env_auth <env_auth>
   env_auth_info <env_auth_info>
   env_cred <env_cred>
   env_cred_info <env_cred_info>
   env_idbroker <env_idbroker>
   env_idbroker_info <env_idbroker_info>
   env_info <env_info>
   env_proxy <env_proxy>
   env_proxy_info <env_proxy_info>
   env_telemetry <env_telemetry>
   env_user_sync <env_user_sync>
   env_user_sync_info <env_user_sync_info>
   freeipa_info <freeipa_info>
   iam_group <iam_group>
   iam_group_info <iam_group_info>
   iam_resource_role_info <iam_resource_role_info>
   iam_user_info <iam_user_info>
   ml <ml>
   ml_info <ml_info>
   ml_workspace_access <ml_workspace_access>
   opdb <opdb>
   opdb_info <opdb_info>

This repository hosts the ``cloudera.cloud`` Ansible collection. The collection includes modules and other Ansible
assets to help automate the provisioning and use of Cloudera Data Platform (CDP) experiences, datalakes, and 
environments as well as the management of CDP users, groups, and credentials.

For details on the Cloudera Data Platform management console, please see the online documentation for the `Cloudera
Management Console <CdpMgmtDocs_>`_.

Installation and Usage
======================

Requirements for running the collection
---------------------------------------

The CDP collection requires the `cdpy <CdpyRepo_>`_ Python library, which is a simple Pythonic wrapper to the 
`CDP CLI/SDK <CdpCliPip_>`_ Python library. You also need to have an `API access key <CdpApiAccessKey_>`_ for your CDP
account. The collection also assumes that you have provisioned the necessary cloud provider resources used by the 
various CDP functions (see `AWS Requirements <CdpAwsRequirements_>`_ and `Azure Requirements <CdpAzureRequirements_>`_);
this collection will not provision these cloud resources.

Installing the collection from GitHub
-------------------------------------

Before using the CDP collection, you must install it with the `Ansible Galaxy CLI <AnsibleGalaxyCLI_>`_:

.. code-block:: bash

   ansible-galaxy collection install git+https://github.com/cloudera-labs/cloudera.cloud.git,main

You can also include it in a ``requirements.yml`` file and install it via ``ansible-galaxy collection install -r
requirements.yml``, using the format:

.. code-block:: yaml

   collections:
     - name: https://github.com/cloudera-labs/cloudera.cloud.git
       type: git
       version: main

Installing the cdpy Python library
----------------------------------

This collection requires the `cdpy <CdpyRepo_>`_ to interact with the CDP endpoint APIs. You can install it
using:

.. code-block:: bash

   pip install cdpy

The ``requirements.txt`` file declares this library. You can install it via ``pip``:

.. code-block:: bash

   pip install -r requirements.txt

Using the collection in your playbooks
--------------------------------------

The best practice for using the content in the collection is to reference the Fully Qualified Collection Namespace
(FQCN), for example ``cloudera.cloud.env_info``:

.. code-block:: yaml

   - hosts: localhost
     connection: local
     gather_facts: no

     tasks:
       - name: List all CDP environments
         cloudera.cloud.env_info:
         register: output

       - name: Debug the results
         debug:
           var: output

       - name: Ensure the example environment exists on AWS
         cloudera.cloud.env:
           name: example-environment
           state: present
           credential: example-credential
           cloud: aws
           region: us-east-1
           log_location: s3a://example-bucket/datalake/logs
           log_identity: arn:aws:iam::981304421142:instance-profile/example-log-role
           public_key_id: example-sshkey
           network_cidr: 10.10.0.0/16
           inbound_cidr: 0.0.0.0/0
           tags:
             project: Example environment

Testing and Development
=======================

To work on this collection, the best practice and easiest way is to clone the repository into one of your configured
``COLLECTION_PATHS`` and manage development from there.

More Information
================

.. _CdpMgmtDocs: https://docs.cloudera.com/management-console/cloud/index.html
.. _AnsibleGalaxyCLI: https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html
.. _CdpyRepo: https://github.com/cloudera-labs/cdpy
.. _CdpCliPip: https://pypi.org/project/cdpcli/
.. _CdpApiAccessKey: https://docs.cloudera.com/management-console/cloud/user-management/topics/mc-generating-an-api-access-key.html
.. _CdpAwsRequirements: https://docs.cloudera.com/management-console/cloud/requirements-aws/topics/mc-requirements-aws.html
.. _CdpAzureRequirements: https://docs.cloudera.com/management-console/cloud/requirements-azure/topics/mc-azure-requirements.html