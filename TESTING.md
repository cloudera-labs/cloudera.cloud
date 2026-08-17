# Testing cloudera.cloud

The project has rallied around using `pytest` for most everything within the collection, including _integration_ tests.

To run integration tests, set the following environment variables.

_For access key credentials_

- `CDP_ACCESS_KEY_ID`
- `CDP_PRIVATE_KEY`

_For token access_

- `CDP_TOKEN`

Integration tests are decorated with `integration_api` and `integration_token` and will run dynamically based on the presence of the above variables.

> [!IMPORTANT]
> Make sure `PYTHONPATH` is set properly in order to find the nested Ansible imports, i.e. `ansible_collections.namespace.collection.plugins.modules`.

`hatch` is configured to run tests via a matrix of Python vs. Ansible versions.

**Run all regular tests in the first (default) test environment.**

```bash
hatch test
```

**Run selected, regular tests in the default test environment.**

```bash
hatch test -k iam_machine_user
```

**Run selected, _marked_ tests in the default test environment.**

```bash
hatch test -k iam_machine_user -m slow
```

**Run _all_ selected tests in the default test environment.**

```bash
hatch test -k iam_machine_user -m all
```

**Run all tests in all test environments, i.e. matrix of testing environments.**

```bash
hatch test --all -m all
```

> [!WARNING] Testing Python 3.9
> Hatch currently has a dependency (`coverage[toml]`) that conflicts with Python 3.9. To test Python 3.9, run `pytest` in a standalone virtual environment. For example:

```bash
python3.9 -m venv cloudera-cloud-python3.9
```

Activate this virtual environment, and install the minimal requirements for testing.

```bash
pip install pytest pytest-mock ansible-core==2.15 "cdpy @ git+https://github.com/cloudera-labs/cdpy@main#egg=cdpy"
```

Then run `pytest` directly instead of `hatch test`.

All other requirements, like `PYTHONPATH`, are still valid.

## Data Warehouse (CDW) integration tests

The Data Warehouse (`dw_*`) integration tests do **not** use the `integration_api`/`integration_token` markers. Instead each test (or its fixture) skips itself when a required environment variable is absent — via the `env_context` fixture, the `required_or_skip` helper, or a direct `os.getenv` check. Set the variables below to enable the corresponding tests; leave them unset to skip.

**Always required** (all DW tests skip without these):

| Variable | Description |
| --- | --- |
| `CDP_API_ENDPOINT` | CDP control-plane API endpoint, e.g. `https://console.us-west-1.cdp.cloudera.com` |
| `CDP_ACCESS_KEY_ID` | CDP API access key ID |
| `CDP_PRIVATE_KEY` | CDP API private key |
| `CDW_CLUSTER_ID` | ID of an existing CDW cluster (environment), e.g. `env-abc123` |

**Virtual Warehouse tests** (`dw_virtual_warehouse`, `dw_virtual_warehouse_info`,
and the client VW suites):

| Variable | Required? | Description |
| --- | --- | --- |
| `CDW_DBC_ID` | Required | ID of an existing Database Catalog to attach new Virtual Warehouses to, e.g. `warehouse-abc123`. Without it, all VW tests skip. |
| `CDW_CONNECTOR_ID` | Optional | ID of an existing connector, e.g. `connector-...`. Enables the Trino connector-association tests; if unset, those tests skip. |
| `CDW_VW_TIMEOUT` | Optional | Seconds to wait for a Virtual Warehouse to reach a stable state (default `3600`). Creation is slow — raise on constrained clusters. |

> [!WARNING]
> VW integration tests create and delete **real** Virtual Warehouses in `CDW_CLUSTER_ID`, which is not immediate (minutes) and incurs cloud cost. Shared, read-only warehouses are created once per test class; delete tests provision their own throwaway warehouse.

**Secret tests** (`dw_secret`, `dw_secret_info`):

| Variable | Required? | Description |
| --- | --- | --- |
| `CDW_SECRET_VALUE` | Optional | Value for a Kubernetes-stored secret. Enables secret **creation** tests; if unset, they skip. |
| `CDW_SECRET_PROVIDER_KEY` | Optional | Provider key for a cloud-vault secret. Enables secret **registration** tests; if unset, they skip. |
| `CDW_SECRET_AZURE_VAULT_NAME` | Optional | Azure Key Vault name, paired with `CDW_SECRET_PROVIDER_KEY` for Azure registration. |

**Example — run the DW Virtual Warehouse suites**

```bash
export CDP_API_ENDPOINT="https://console.us-west-1.cdp.cloudera.com"
export CDP_ACCESS_KEY_ID="..."
export CDP_PRIVATE_KEY="..."
export CDW_CLUSTER_ID="env-abc123"
export CDW_DBC_ID="warehouse-abc123"
export CDW_CONNECTOR_ID="connector-..."   # optional, for Trino association

hatch test -k dw_virtual_warehouse
```

## Custom Pytest Markers

| Marker | Enabled | Description |
| --- | --- | --- |
| `integration_api` | `True` | Marks tests as integration tests using CDP API credentials |
| `integration_token`  | `True` | Marks tests as integration tests using CDP token credentials |
| `slow` | `False` | Marks tests as slow tests |
| `data_service` | `False` | Marks tests that require a CDP Data Service environment |
| `all` | `False` | Marks all tests to run (slow, data_service, and regular) |

By default, only tests _not_ marked with `slow` or `data_service` are executed.

**Run only the slow tests**

```bash
hatch test -m slow
```

**Run only the tests requiring a Data Service fixture**

```bash
hatch test -m data_service
```

**Run only slow and Data Service fixture tests**

```bash
hatch test -m "slow or data_service"
```

**Run all tests**

```bash
hatch test -m all
```
