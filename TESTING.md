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

**Run all tests in the first (default) test environment.**

```bash
hatch test
```

**Run selected tests in the default test environment.**

```bash
hatch test -k iam_machine_user
```

**Run all tests in all test environments, i.e. matrix of testing environments.**

```bash
hatch test --all
```
