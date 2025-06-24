============================
Cloudera.Cloud Release Notes
============================

.. contents:: Topics

v2.5.1
======

Minor Changes
-------------

- Increment actions to remove deprecation notices and use main branch for docs construction workflow

v2.5.0
======

Minor Changes
-------------

- Add extra top-level parameters for CDW create cluster module (https://github.com/cloudera-labs/cloudera.cloud/pull/155)
- Add pre-commit hooks and workflow (https://github.com/cloudera-labs/cloudera.cloud/pull/157)

Bugfixes
--------

- Update default value of use_ssd argument in CDE module (https://github.com/cloudera-labs/cloudera.cloud/pull/156)
- Update module example typo (https://github.com/cloudera-labs/cloudera.cloud/pull/154)

v2.4.0
======

Minor Changes
-------------

- Add Ansible Galaxy imports (https://github.com/cloudera-labs/cloudera.cloud/pull/147)
- Add analytics to API documents (https://github.com/cloudera-labs/cloudera.cloud/pull/143)
- Add autoscaling and impala_ha parameters to cdw vw module (https://github.com/cloudera-labs/cloudera.cloud/pull/145)
- Add extra Azure parameters to cloudera.cloud.dw_cluster (https://github.com/cloudera-labs/cloudera.cloud/pull/140)
- Add module defaults groups (https://github.com/cloudera-labs/cloudera.cloud/pull/144)
- Add template and image parameters to dw data viz module (https://github.com/cloudera-labs/cloudera.cloud/pull/146)
- Update to version 2.4.0 (https://github.com/cloudera-labs/cloudera.cloud/pull/148)

v2.3.1
======

Bugfixes
--------

- Add enterprise to datalake scale parameter (https://github.com/cloudera-labs/cloudera.cloud/pull/141)

v2.3.0
======

Minor Changes
-------------

- Add cdp_region parameters fo CDP Endpoint region (https://github.com/cloudera-labs/cloudera.cloud/pull/136)

v2.2.0
======

Minor Changes
-------------

- Add private_cluster parameters (https://github.com/cloudera-labs/cloudera.cloud/pull/133)

Bugfixes
--------

- Update AWS subnet parameter names for CDW cluster creation (https://github.com/cloudera-labs/cloudera.cloud/pull/132)

v2.1.1
======

Bugfixes
--------

- Fix malformed return value in API docs (https://github.com/cloudera-labs/cloudera.cloud/pull/130)

v2.1.0
======

Minor Changes
-------------

- Add CDP recipe and Data Hub repair modules (https://github.com/cloudera-labs/cloudera.cloud/pull/127)
- Update collection version to 2.1.0 (https://github.com/cloudera-labs/cloudera.cloud/pull/128)

Bugfixes
--------

- Update env_idbroker return value to 'idbroker' from 'mappings' (https://github.com/cloudera-labs/cloudera.cloud/pull/92)

New Modules
-----------

- cloudera.cloud.datahub_cluster_recipe - Manage CDP Datahub recipes on an instance group.
- cloudera.cloud.datahub_cluster_repair - Repair CDP Datahub instances or instance groups.
- cloudera.cloud.recipe - Manage a CDP recipe.
- cloudera.cloud.recipe_info - Gather information about CDP recipes.

v2.0.1
======

Minor Changes
-------------

- Report warning when discovering subnets from filter (https://github.com/cloudera-labs/cloudera.cloud/pull/114)

Bugfixes
--------

- Ignore errors when deleting Data Hub (https://github.com/cloudera-labs/cloudera.cloud/pull/115)
- Update import for cdp_service in datalake_service lookup plugin (https://github.com/cloudera-labs/cloudera.cloud/pull/122)
- Update pip requirements to update to latest 2.12.* (https://github.com/cloudera-labs/cloudera.cloud/pull/124)

v2.0.0
======

Minor Changes
-------------

- Add Datalake service lookup (https://github.com/cloudera-labs/cloudera.cloud/pull/97)
- Add FreeIPA lookup plugins (https://github.com/cloudera-labs/cloudera.cloud/pull/100)
- Add GCP region zones parameter (https://github.com/cloudera-labs/cloudera.cloud/pull/101)
- Add backup storage options to env module (https://github.com/cloudera-labs/cloudera.cloud/pull/95)
- Add datahub_service lookup plugin (https://github.com/cloudera-labs/cloudera.cloud/pull/96)
- Add integration targets for CDP Environment and general teardown (https://github.com/cloudera-labs/cloudera.cloud/pull/91)
- Add integration test for cross-account credentials (https://github.com/cloudera-labs/cloudera.cloud/pull/90)
- Add loadbalancer_ips parameter to 'de' module (https://github.com/cloudera-labs/cloudera.cloud/pull/108)
- Add lookup plugins for DL and DH (https://github.com/cloudera-labs/cloudera.cloud/pull/98)
- Add multi-az support for AWS environment and datalake (https://github.com/cloudera-labs/cloudera.cloud/pull/89)
- Add noProxyHosts parameter to cloudera.cloud.env_proxy (https://github.com/cloudera-labs/cloudera.cloud/pull/105)
- Add recipes parameter to cloudera.cloud.datalake (https://github.com/cloudera-labs/cloudera.cloud/pull/107)
- Added modules for custom flows and a fix fixes for deployments. (https://github.com/cloudera-labs/cloudera.cloud/pull/62)
- Configure documentation toolchain with antsibull-docs (https://github.com/cloudera-labs/cloudera.cloud/pull/109)
- Remove PVC Base feature branch (https://github.com/cloudera-labs/cloudera.cloud/pull/110)
- Subnet filters for the DF service (https://github.com/cloudera-labs/cloudera.cloud/pull/64)
- Update payload to use clusterDefinition and clusterTemplate parameters (https://github.com/cloudera-labs/cloudera.cloud/pull/94)
- Update release/v2.0.0 (#117) (https://github.com/cloudera-labs/cloudera.cloud/pull/119)
- Update release/v2.0.0 (https://github.com/cloudera-labs/cloudera.cloud/pull/117)

Bugfixes
--------

- Add Documentation for Data Visualization (https://github.com/cloudera-labs/cloudera.cloud/pull/106)
- Fix documentation on datahub name length (https://github.com/cloudera-labs/cloudera.cloud/pull/79)
- Update creation parameters to reflect cloud provider specifics (https://github.com/cloudera-labs/cloudera.cloud/pull/102)
- Update multiAz parameter docs (https://github.com/cloudera-labs/cloudera.cloud/pull/93)

New Plugins
-----------

Lookup
~~~~~~

- cloudera.cloud.datahub_definition - Get a Datahub definition for a CDP Public Cloud Environment.
- cloudera.cloud.datahub_instance - Get the instances for a CDP Public Cloud Datahub.
- cloudera.cloud.datahub_service - Get the URL for a CDP Public Cloud Datahub service.
- cloudera.cloud.datahub_template - Get a Datahub template for a CDP Public Cloud Environment.
- cloudera.cloud.datalake_instance - Get the instances for a CDP Public Cloud Datalake.
- cloudera.cloud.datalake_runtime - Get the Datalake Runtime for CDP Public Cloud Environments.
- cloudera.cloud.datalake_service - Get the URL for a CDP Public Cloud Datalake service.
- cloudera.cloud.env_freeipa_domain - Get information about the FreeIPA domain and DNS server IP address(es) for the selected CDP Public Cloud Environment.
- cloudera.cloud.env_freeipa_hosts - Get information about FreeIPA hosts for selected Environment.

New Modules
-----------

- cloudera.cloud.df_customflow - Import or Delete CustomFlows into the DataFlow Catalog.
- cloudera.cloud.df_customflow_version - Import CustomFlow versions into the DataFlow Catalog.
- cloudera.cloud.dw_data_visualization - Create or Delete CDP Data Visualization Instance.
- cloudera.cloud.dw_data_visualization_info - Gather information about CDP Data Visualization Instances.

v1.7.4
======

Bugfixes
--------

- Update bindep installation and execution (https://github.com/cloudera-labs/cloudera.cloud/pull/88)

v1.7.3
======

Minor Changes
-------------

- Update to support ansible-builder (https://github.com/cloudera-labs/cloudera.cloud/pull/87)

v1.7.2
======

Minor Changes
-------------

- Add workflows for PR validation tasks and labeling (https://github.com/cloudera-labs/cloudera.cloud/pull/84)
- Start an environment without starting the datahubs within it (https://github.com/cloudera-labs/cloudera.cloud/pull/76)
- Update collection version to 2.0.0-alpha1 (https://github.com/cloudera-labs/cloudera.cloud/pull/70)
- Update to support ansible-builder (https://github.com/cloudera-labs/cloudera.cloud/pull/85)

Bugfixes
--------

- Fix for CDW Virtual Warehouse race condition (https://github.com/cloudera-labs/cloudera.cloud/pull/75)
- Increment collection to 1.7.2 (https://github.com/cloudera-labs/cloudera.cloud/pull/86)

v1.7.1
======

Bugfixes
--------

- Remove 'enableRangerRaz' from DL payload for GCP (https://github.com/cloudera-labs/cloudera.cloud/pull/69)

v1.7.0
======

Minor Changes
-------------

- Add initial testing components (https://github.com/cloudera-labs/cloudera.cloud/pull/65)
- Add support for stopped and started states to datahub cluster (https://github.com/cloudera-labs/cloudera.cloud/pull/57)
- Multi-AZ Datahub support (https://github.com/cloudera-labs/cloudera.cloud/pull/68)
- RAZ Support - PR 49 Redo (https://github.com/cloudera-labs/cloudera.cloud/pull/55)
- Update to handle automated user synchronization (https://github.com/cloudera-labs/cloudera.cloud/pull/53)

Bugfixes
--------

- Fix freeipa parameter for env module (https://github.com/cloudera-labs/cloudera.cloud/pull/61)
- Update DBC restart process (https://github.com/cloudera-labs/cloudera.cloud/pull/66)

New Modules
-----------

- cloudera.cloud.env_automated_user_sync_info - Get the status of the automated CDP Users and Groups synchronization service.

v1.6.0
======

Minor Changes
-------------

- Enable cascade and force parameters for environment deletion (https://github.com/cloudera-labs/cloudera.cloud/pull/52)
- Support for DataFlow Deployments (https://github.com/cloudera-labs/cloudera.cloud/pull/45)

New Modules
-----------

- cloudera.cloud.df_customflow_info - Gather information about CDP DataFlow CustomFlow Definitions.
- cloudera.cloud.df_deployment - Enable or Disable CDP DataFlow Deployments.
- cloudera.cloud.df_deployment_info - Gather information about CDP DataFlow Deployments.
- cloudera.cloud.df_readyflow - Import or Delete ReadyFlows from your CDP Tenant.
- cloudera.cloud.df_readyflow_info - Gather information about CDP DataFlow ReadyFlow Definitions.

v1.5.1
======

Bugfixes
--------

- Hotfix env_cred_info (https://github.com/cloudera-labs/cloudera.cloud/pull/47)

v1.5.0
======

Minor Changes
-------------

- Add 'id' as an alias to 'catalog_id' (https://github.com/cloudera-labs/cloudera.cloud/pull/33)
- Add and update CDW modules (https://github.com/cloudera-labs/cloudera.cloud/pull/29)
- Add configurable user agent for CDPCLI interface (https://github.com/cloudera-labs/cloudera.cloud/pull/38)
- Add support for CDE (https://github.com/cloudera-labs/cloudera.cloud/pull/39)
- Add support for CDE (part 2 - virtual clusters) (https://github.com/cloudera-labs/cloudera.cloud/pull/40)
- Azure AuthZ/Single Resource Group Work - CLOUD (https://github.com/cloudera-labs/cloudera.cloud/pull/43)
- Move DFX Beta implementation to GA process (https://github.com/cloudera-labs/cloudera.cloud/pull/31)

Bugfixes
--------

- Fix agent_header parameter (https://github.com/cloudera-labs/cloudera.cloud/pull/42)
- Fix module name in API docs (https://github.com/cloudera-labs/cloudera.cloud/pull/44)

New Modules
-----------

- cloudera.cloud.de - Enable and Disable CDP Data Engineering Services.
- cloudera.cloud.de_info - Gather information about CDP DE Workspaces.
- cloudera.cloud.de_virtual_cluster - Create or delete CDP Data Engineering Virtual Clusters.
- cloudera.cloud.de_virtual_cluster_info - Gather information about CDP DE virtual clusters.
- cloudera.cloud.dw_database_catalog - Create, manage, and destroy CDP Data Warehouse Database Catalogs.
- cloudera.cloud.dw_database_catalog_info - Gather information about CDP Data Warehouse Database Catalogs.
- cloudera.cloud.dw_virtual_warehouse - Create, manage, and destroy CDP Data Warehouse Virtual Warehouses.
- cloudera.cloud.dw_virtual_warehouse_info - Gather information about CDP Data Warehouse Virtual Warehouses.

v1.4.0
======

Minor Changes
-------------

- Add support for endpointaccessgateway for AWS (https://github.com/cloudera-labs/cloudera.cloud/pull/15)
- Changes for DF-beta inclusion (https://github.com/cloudera-labs/cloudera.cloud/pull/17)
- Improve Azure deployment stability (https://github.com/cloudera-labs/cloudera.cloud/pull/24)
- Improve DF Integration (https://github.com/cloudera-labs/cloudera.cloud/pull/20)
- Improve teardown functionality and support purge mode (https://github.com/cloudera-labs/cloudera.cloud/pull/18)
- Update env module to support FreeIPA Instance Count (https://github.com/cloudera-labs/cloudera.cloud/pull/30)

Removed Features (previously deprecated)
----------------------------------------

- Ciao dynamo (https://github.com/cloudera-labs/cloudera.cloud/pull/23)
- Remove DF dependency until GA (https://github.com/cloudera-labs/cloudera.cloud/pull/25)

Bugfixes
--------

- Df module incorrectly refers to deprecated value self.env (https://github.com/cloudera-labs/cloudera.cloud/pull/16)

v1.3.0
======

Minor Changes
-------------

- Add 'content' flag for including template content. (https://github.com/cloudera-labs/cloudera.cloud/pull/13)
- Add new definition info module for datahubs and update datahub_cluste… (https://github.com/cloudera-labs/cloudera.cloud/pull/12)

New Modules
-----------

- cloudera.cloud.datahub_definition_info - Gather information about CDP Datahub Cluster Definitions.

v1.2.0
======

Minor Changes
-------------

- Add support for DFX Tech Preview (https://github.com/cloudera-labs/cloudera.cloud/pull/11)

Bugfixes
--------

- Fix missing DF docs references (https://github.com/cloudera-labs/cloudera.cloud/pull/14)

New Modules
-----------

- cloudera.cloud.df_service - Enable or Disable CDP DataFlow Services.
- cloudera.cloud.df_service_info - Gather information about CDP DataFlow Services.

v1.1.0
======

New Modules
-----------

- cloudera.cloud.freeipa_info - Gather information about FreeIPA.
- cloudera.cloud.ml_workspace_access - Grant and revoke user access to CDP Machine Learning Workspaces.

v1.0.0
======

New Modules
-----------

- cloudera.cloud.account_auth - Gather and set authentication details for a CDP Account.
- cloudera.cloud.account_auth_info - Gather information about CDP Account authentication settings.
- cloudera.cloud.account_cred_info - Gather information about Account prerequisites for CDP Credentials.
- cloudera.cloud.datahub_cluster - Manage CDP Datahubs.
- cloudera.cloud.datahub_cluster_info - Gather information about CDP Datahubs.
- cloudera.cloud.datahub_template_info - Gather information about CDP Datahub Cluster Templates.
- cloudera.cloud.datalake - Manage CDP Datalakes.
- cloudera.cloud.datalake_info - Gather information about CDP Datalakes.
- cloudera.cloud.datalake_runtime_info - Gather information about CDP Datalake Runtimes.
- cloudera.cloud.dw_cluster - Create or Delete CDP Data Warehouse Clusters.
- cloudera.cloud.dw_cluster_info - Gather information about CDP Data Warehouse Clusters.
- cloudera.cloud.env - Manage CDP Environments.
- cloudera.cloud.env_auth - Set authentication details for the current CDP user.
- cloudera.cloud.env_auth_info - Gather information about CDP environment authentication details.
- cloudera.cloud.env_cred - Create, update, and destroy CDP credentials.
- cloudera.cloud.env_cred_info - Gather information about CDP Credentials.
- cloudera.cloud.env_idbroker - Update ID Broker for CDP Environments.
- cloudera.cloud.env_idbroker_info - Gather information about CDP ID Broker.
- cloudera.cloud.env_info - Gather information about CDP Environments.
- cloudera.cloud.env_proxy - Create, update, or destroy CDP Environment Proxies.
- cloudera.cloud.env_proxy_info - Gather information about CDP Environment Proxies.
- cloudera.cloud.env_telemetry - Set CDP environment telemetry.
- cloudera.cloud.env_user_sync - Sync CDP Users and Groups to Environments.
- cloudera.cloud.env_user_sync_info - Get the status of a CDP Users and Groups sync.
- cloudera.cloud.iam_group - Create, update, or destroy CDP IAM Groups.
- cloudera.cloud.iam_group_info - Gather information about CDP Public IAM groups.
- cloudera.cloud.iam_resource_role_info - Gather information about CDP Public IAM resource roles.
- cloudera.cloud.iam_user_info - Gather information about CDP Public IAM users.
- cloudera.cloud.ml - Create or Destroy CDP Machine Learning Workspaces.
- cloudera.cloud.ml_info - Gather information about CDP ML Workspaces.
- cloudera.cloud.opdb - Create or destroy CDP OpDB Databases.
- cloudera.cloud.opdb_info - Gather information about CDP OpDB Databases.
