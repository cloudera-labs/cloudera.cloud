# Collections Plugins Directory

The `cloudera.cloud` collection contains modules that interact with the various endpoints of the CDP control plane. The
modules employ the underlying SDK contained within the `cdpy` Python package.

# Modules

| Module | Description |
| --- | --- |
| [account_auth](./modules/account_auth.py) | Manage about Account authentication services and policies |
| [account_auth_info](./modules/account_auth_info.py) | Gather information about Account authentication services and policies |
| [account_cred_info](./modules/account_cred_info.py) | Gather information about Account prerequisites for CDP Credentials |
| [datahub_cluster](./modules/datahub_cluster.py) | Create, manage, and destroy CDP Data Hubs |
| [datahub_cluster_info](./modules/datahub_cluster_info.py) | Gather information about CDP Data Hubs |
| [datahub_definition_info](./modules/datahub_definition_info.py) | Gather information about CDP Data Hub Cluster Definitions |
| [datahub_template_info](./modules/datahub_template_info.py) | Gather information about CDP Data Hub templates |
| [datalake](./modules/datalake.py) | Create, manage, and destroy CDP Datalakes |
| [datalake_info](./modules/datalake_info.py) | Gather information about CDP Datalakes |
| [datalake_runtime_info](./modules/datalake_runtime_info.py) | Gather information about CDP Datalake Runtimes |
| [de](./modules/de.py) | Enable and Disable CDP Data Engineering services |
| [de_info](./modules/de_info.py) | Gather information about CDP Data Engineering Workspaces |
| [de_virtual_cluster](./modules/de_virtual_cluster.py) | Create or delete CDP Data Engineering Virtual Clusters |
| [de_virtual_cluster_info](./modules/de_virtual_cluster_info.py) | Gather information about CDP Data Engineering Virtual Clusters |
| [df_service](./modules/df_service.py) | Enable or disable CDP DataFlow services |
| [df_service_info](./modules/df_service_info.py) | Gather information about CDP DataFlow services |
| [df_customflow_info](./modules/df_customflow_info.py) | Gather information about CDP DataFlow CustomFlow definitions |
| [df_deployment](./modules/df_deployment.py) | Enable or Disable CDP DataFlow Deployments |
| [df_deployment_info](./modules/df_deployment_info.py) | Gather information about CDP DataFlow Deployments |
| [df_readyflow](./modules/df_readyflow.py) | Import or Delete ReadyFlows from a CDP Tenant |
| [df_readyflow_info](./modules/df_readyflow_info.py) | Gather information about CDP DataFlow ReadyFlow Definitions |
| [dw_cluster](./modules/dw_cluster.py) | Create, manage, and destroy CDP Data Warehouse experiences |
| [dw_cluster_info](./modules/dw_cluster_info.py) | Gather information about CDP Data Warehouse experiences |
| [dw_database_catalog](./modules/dw_database_catalog.py) | Create, manage, and destroy CDP Data Warehouse Data Catalogs |
| [dw_database_catalog_info](./modules/dw_database_catalog_info.py) | Gather information about CDP Data Warehouse Data Catalogs |
| [dw_virtual_warehouse](./modules/dw_virtual_warehouse.py) | Create, manage, and destroy CDP Data Warehouse Virtual Warehouses |
| [dw_virtual_warehouse_info](./modules/dw_virtual_warehouse_info.py) | Gather information about CDP Data Warehouse Virtual Warehouses |
| [env](./modules/env.py) | Create, manage, and destroy CDP Environments |
| [env_auth](./modules/env_auth.py) | Set authentication details for CDP Environments |
| [env_auth_info](./modules/env_auth_info.py) | Gather information about CDP Environment authentication details |
| [env_automated_user_sync_info](./modules/env_automated_user_sync_info.py) | Get the status of the automated CDP Users and Groups synchronization service |
| [env_cred](./modules/env_cred.py) | Create, update, and destroy CDP Credentials |
| [env_cred_info](./modules/env_cred_info.py) | Gather information about CDP Credentials |
| [env_idbroker](./modules/env_idbroker.py) | Manage CDP Environment ID Broker data access mappings |
| [env_idbroker_info](./modules/env_idbroker_info.py) | Gather information on CDP Environment ID Broker data access mappings |
| [env_info](./modules/env_info.py) | Gather information about CDP Environments |
| [env_proxy](./modules/env_proxy.py) | Create, update, or destroy CDP Environment Proxies |
| [env_proxy_info](./modules/env_proxy_info.py) | Gather information about CDP Environment Proxies |
| [env_telemetry](./modules/env_telemetry.py) | Set CDP Environment telemetry |
| [env_user_sync](./modules/env_user_sync.py) | Manage CDP User and Group synchronization events |
| [env_user_sync_info](./modules/env_user_sync_info.py) | Gather information about CDP User and Group synchronization events |
| [freeipa_info](./modules/freipa_info.py) | Gather information about FreeIPA |
| [iam_group](./modules/iam_group.py) | Create, manage, and destroy CDP IAM groups |
| [iam_group_info](./modules/iam_group_info.py) | Gather information about CDP IAM Groups |
| [iam_resource_role_info](./modules/iam_resource_role_info.py) | Gather information about CDP IAM resource roles |
| [iam_user_info](./modules/iam_user_info.py) | Gather information about CDP IAM users |
| [ml](./modules/ml.py) | Create, manage, and destroy CDP Machine Learning experiences |
| [ml_info](./modules/ml_info.py) | Gather information about CDP Machine Learning experiences |
| [ml_workspace_access](./modules/ml_workspace_access.py) | Grant and revoke user access to and from CDP Machine Learning experiences |
| [opdb](./modules/opdb.py) | Create, manage, and destroy CDP Operational Database experiences |
| [opdb_info](./modules/opdb_info.py) | Gather information about CDP Operational Database experiences |
