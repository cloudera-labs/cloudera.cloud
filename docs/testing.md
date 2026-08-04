> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Testing Patterns

**Use `hatch test`, never raw `pytest`, never `ansible-test`.** `hatch test` is the project's
`pytest` wrapper — do not run `tests/unit/` files with `pytest` directly.

## Unit and Integration Tests

Use pytest with fixtures from `tests/unit/conftest.py`:

**Unit tests:**

```python
def test_create_resource(module_args, mocker):
    # Setup
    mock_method = mocker.patch("module_utils.client.Client.create", return_value=...)
    module_args({"endpoint": "https://example.com", "name": "test"})

    # Execute
    with pytest.raises(AnsibleExitJson) as e:
        module.main()

    # Assert
    result = e.value.args[0]
    assert result["changed"] is True
    mock_method.assert_called_once()
```

**Integration tests:**

- Suffix: `_int.py`
- Use `env_context` fixture for environment variable checks and built-in skip conditions
- Test against live APIs with proper environment variables set (e.g., `SERVICE_ENDPOINT`) using the `env_context` fixture

Fixtures should be defined in `tests/unit/conftest.py` or before the test functions in the same file.

```python
# Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "ENV_CRN",
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

# Test configuration constants
TEST_MIN_NODES = 3
TEST_MAX_NODES = 10


@pytest.fixture
def example_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to pre-populate common Example module arguments."""

    def wrapped_args(args=None):
        if args is None:
            args = {}

        args.update(
            {
                "endpoint": env_context["CDP_API_ENDPOINT"],
                "access_key": env_context["CDP_ACCESS_KEY_ID"],
                "private_key": env_context["CDP_PRIVATE_KEY"],
                "env_crn": env_context["ENV_CRN"],
            },
        )
        return module_args(args)

    return wrapped_args


@pytest.fixture
def example_client(test_cdp_client) -> CdpExampleClient:
    """Fixture to provide an Example client for tests."""
    return CdpExampleClient(api_client=test_cdp_client)


def test_example_service_enable(example_module_args):
    """Test Example service."""

    example_module_args(
        {
            "state": "present",
            "nodes_min": TEST_MIN_NODES,
            "nodes_max": TEST_MAX_NODES,
            "wait": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as result:
        example_service.main()

    # Verify the result
    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
    assert "environmentCrn" in result.value.service

    # Idempotency check - running again should not change anything
    with pytest.raises(AnsibleExitJson) as result:
        example_service.main()

    assert result.value.changed is False
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
```

## Fixture Factories & Cleanup

Live integration tests exercise real APIs, so they **must clean up after themselves** — a test that creates a resource must delete it, even when it fails, so no orphans are left behind. Do this with pytest [yield fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html#teardown-cleanup-aka-fixture-finalization), not manual teardown in the test body.

**Yield fixtures (finalization).** Replace `return` with `yield`: everything before the `yield` is setup, the yielded value is handed to the test, and everything after the `yield` runs as teardown once the test finishes — pass or fail.

```python
@pytest.fixture
def deletable_project(example_client, request):
    """Provision a per-test project, named from the test, removed on teardown."""
    project = example_client.create_project(
        ExampleProject(name=request.node.name),
    )
    yield project                       # <-- handed to the test
    example_client.delete_project(project.id)  # <-- teardown, always runs
```

**Factory-as-fixture.** When a test needs to register resources it creates *during* the test (whose identity isn't known at setup time), yield a callable that records each created object, then clean them all up after the `yield`:

```python
@pytest.fixture
def purge_project(example_client):
    """Return a callable the test hands its created project(s) to for teardown."""
    created = []

    def _register(project):
        created.append(project)
        return project

    yield _register
    for project in created:
        example_client.delete_project(project.id)
```

```python
def test_create_project(example_module_args, purge_project):
    example_module_args({"name": "acme", "state": "present"})

    with pytest.raises(AnsibleExitJson) as result:
        example_project.main()

    # Register the created resource so the fixture deletes it on teardown
    purge_project(from_dict(ExampleProject, result.value.args[0]["project"]))
    assert result.value.args[0]["changed"] is True
```

**Conventions.** Define these in `tests/unit/conftest.py` and name them by role:

- `purge_<resource>` — factory the test calls with the object it created; deletes it on teardown. Use for **create** tests.
- `existing_<resource>` — module-scoped; provisions one shared resource and removes it at teardown. Use for **idempotent / by-id / read** tests that don't mutate it.
- `deletable_<resource>` — function-scoped; provisions a per-test resource named from `request.node.name`. Use for **update / delete** tests.

Setup that fails before `yield` skips that fixture's teardown, but pytest still tears down every fixture that did complete — so keep one resource per fixture.

## Test Organization

```
tests/unit/plugins/<plugin_type>/
  <plugin_family>/
    <plugin_name>/
      test_<plugin_name>_<plugin_type>.py
      test_<plugin_name>_<plugin_type>_int.py
```

## Test Verification

Use the Hatch `test` subcommand to manage `pytest` executions.

- `hatch test -q tests/unit/plugins/module_utils/<service client>`
- `hatch test -q tests/unit/plugins/modules/<module>`

Integration tests skip themselves via the `env_context` fixture when credentials are absent, so no marker or `-m` selection is required.
