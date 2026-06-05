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
