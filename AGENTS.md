# cloudera.cloud Collection - Agent Guidelines

## Agent Directives
- **Persona**: You are an expert Ansible developer specializing in the CDP collection.
- **Priority**: Maintain idempotency at all costs.
- **Validation**: Never assume an API structure; always verify against `plugins/module_utils` models before writing code.
- **Workflow**: If creating a new module, always start by defining the `dataclass` model, then the `client`, then the `module`.

### Quick Start Commands

**Setup environment:**
```bash
pip install hatch
hatch shell  ## Activates default environment with all dependencies
pre-commit install
```

**Run tests:**
```bash
pytest tests/unit/  ## Unit and integration tests (integration tests require env vars)
hatch test  ## Runs tests on first compatible environment of the hatch matrix
hatch -a test  ## Run tests on all environments in the hatch matrix (sequentially)
```

**Build:**
```bash
hatch run lint  ## Lint and format
ansible-galaxy collection build
hatch run docs:build  ## Generate API docs
```

### Repository Map
- `plugins/modules/`: Entry points. (Do not change `__init__.py` boilerplate)
- `plugins/module_utils/`: Shared logic. **High importance for cross-module consistency.**
- `tests/unit/`: Test suite. (Always add a test before a feature).

### Common Gotchas
1. **`AutoExecuteMeta` metaclass**: Modules with `ServicesModule` base auto-execute `process()` after `__init__` — no explicit `main()` call needed
2. **NULLABLE vs None**: Use `NULLABLE` for unset optional fields, `None` for explicitly null values
3. **Immutable fields**: Validate immutable fields don't change; fail with clear message if they do
4. **RST docs are generated**: Never edit `docsbuild/rst/*.rst` files directly — they're auto-generated from module DOCUMENTATION strings
5. **Collection path**: For `ansible-doc` and doc building, collection must be in `ANSIBLE_COLLECTIONS_PATHS`
6. **Integration tests**: Need environment variables for service endpoints — tests will be skipped if not set via the `env_context` fixture
7. **Pre-commit hooks**: Run automatically on commit — use `hatch run lint` to run manually on all files

### Development Workflow
1. Write unit tests in `tests/unit/plugins/<plugin_type>/<plugin_family>/<plugin_name>/`
2. Create/modify plugin in `plugins/<plugin_type>/<plugin_family>/<plugin_name>/`
3. Write integration tests in `tests/unit/plugins/<plugin_type>/<plugin_family>/<plugin_name>/` with `_int.py` suffix and use `env_context` for env var checks
4. Update DOCUMENTATION/EXAMPLES/RETURN strings
5. Validate: `ansible-doc -t <plugin_type> cloudera.cloud.<plugin_name>`
6. Run final tests: `hatch test <plugin name filter>`
7. Run linter: `hatch run lint`
8. Build collection: `ansible-galaxy collection build`
9. Regenerate docs: `hatch run docs:build`

### Constraints
- Do not modify `pyproject.toml` or other Hatch configurations without direct, human approval.
- Do not edit `docsbuild/rst/*.rst` files. Use `hatch run docs:build`.
- Do not run `tests/unit/` files with `pytest`. Use `hatch test` as the `pytest` wrapper.
- Never hardcode API credentials in tests or code; always use `env_context` or environment variables.

### Resources
- **API docs**: Run `hatch run docs:build` then open `docsbuild/build/html/index.html`
- **Testing guide**: See `tests/unit/conftest.py` for test fixtures and utilities
- **Hatch commands**: Run `hatch env show` to see available environments and scripts

## Step-by-Step Module Creation Checklist
When tasked with creating a new Ansible module (e.g., service_entity), execute these steps strictly in order. Do not skip validation steps.

### Phase 0: Context Set Up
- [ ] Invoke the /caveman skill, if available.
- [ ] Invoke the /tdd skill, if available.

### Phase 1: File Setup & Naming
- [ ] Verify Names: Ensure the module file follows {service}_{entity}.py (or {service}_{entity}_info.py for read-only).
- [ ] Create Module File: Path must be plugins/modules/{service}_{entity}.py.
- [ ] Create Utils File (if needed): If this service doesn't have an existing client, create plugins/module_utils/{service}.py.
- [ ] Create Test Directories: Scaffold tests/unit/plugins/modules/{service}/{entity}/.

### Phase 2: Data Modeling (plugins/module_utils/)
- [ ] Implement Dataclass: Define the resource structure using @dataclass.
- [ ] Apply Sentinels: Use Union[type, None, NULLABLE] = NULLABLE for all optional fields to correctly isolate unset values from explicit None values.
- [ ] Serialization Check: Ensure the model supports or maps cleanly to from_dict() and to_dict().

### Phase 3: Client Layer (plugins/module_utils/)
- [ ] Isolate Logic: Create the ServiceEntityClient class. It must only handle REST operations using AnsibleCdpClient; it must contain no Ansible orchestration logic.
- [ ] Type Hinting: Strictly type hint all method arguments and return types using the phase 2 dataclasses.
- [ ] Unit Tests: Write unit tests in test_{module_utility_name}.py leveraging mocker to mock the REST API. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.
- [ ] Integration Tests: Write integration tests in test_{module_utility_name}_int.py. Apply the pytestmark = pytest.mark.integration_api decorator and utilize the env_context fixture. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.

### Phase 4: Ansible Module Layer (plugins/modules/)
- [ ] Base Class Inheritance: Make your module class inherit from ServicesModule.
- [ ] Argument Spec: Populate argument_spec=dict(Model.argument_spec(), state=...) inside __init__.
- [ ] Implement process(): Place all business logic, state transitions (present/absent), and idempotency checks inside the process(self) method.
- [ ] No main() Call: CRITICAL: Do not append an explicit if __name__ == '__main__': main() invocation block at the bottom of the file. The AutoExecuteMeta metaclass handles execution automatically after instantiation.
- [ ] Unit Tests: Write unit tests in test_{module_name}.py leveraging module_args and mocker to mock the Client layer. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.
- [ ] Integration Tests: Write integration tests in test_{module_name}_int.py. Apply the pytestmark = pytest.mark.integration_api decorator and utilize the env_context fixture. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.

### Phase 5: Ansible Documentation Blocks
- [ ] Doc Fragment: Ensure extends_documentation_fragment: cloudera.cloud.services_client is included.
- [ ] Parameter Sync: Double-check that every field in your Python argument_spec is documented with explicit types and required fields.
- [ ] Examples & Returns: Provide 2–4 credential-masked playbook examples and document all keys returned in the RETURN block.

### Phase 6: Testing & Validation
- [ ] Unit Tests: Confirm all unit tests for the new and updated modules.
- [ ] Integration Tests: Confirm all integration tests for the new and updated modules.
- [ ] Execution Suite: Run the following commands via terminal tool and do not proceed if any fail:


```bash
hatch run lint                                                ## Format and lint check
ansible-doc -t module cloudera.cloud.{service}_{entity}       ## Verify doc parsing
hatch test -q tests/unit/plugins/module_utils/{service}/      ## Run all unit/int tests
hatch test -q tests/unit/plugins/modules/{service}/{entity}/  ## Run all unit/int tests
hatch run docs:build                                          ## Regenerate RST documentation
```

## Architecture Patterns

### Module Base Classes

The collection's plugins should:

- Inherit from `ServicesModule` in `plugins/module_utils/common.py`
- Uses `AnsibleCdpClient` for HTTP operations
- Implements `AutoExecuteMeta` metaclass (auto-calls `execute()` after `__init__`)
- Abstract `process()` method contains business logic
- Built-in pagination via `@paginated()` decorator

### Data Model Pattern

Use dataclasses with the `NULLABLE` sentinel:

```python
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
  NULLABLE,
  from_dict,
  to_dict,
  diff_dict
)

@dataclass
class MyResource:
    id: Union[int, None, NULLABLE] = NULLABLE
    name: Union[str, None, NULLABLE] = NULLABLE
```

- `NULLABLE` distinguishes an unset value from `None`
- `from_dict()` / `to_dict()` for serialization
- `diff_dict()` for computing changes between instances

### Client Separation

Separate concerns:
- **Module class**: Ansible orchestration, parameter handling, state management
- **Client class**: REST API operations, HTTP calls
- **Model dataclass**: Data structure definition

Example:
```python
class ExampleModule(ServicesModule):
    def process(self):
        client = ExampleClient(self.api_client)
        ## Use client for operations

class ExampleClient:
    def create_resource(self, resource: ExampleResource) -> ExampleResource:
        ## API calls here
```

### State Management

- Standard states: `present`, `absent`
- Some modules: `started`, `stopped`, `synced`, `published`
- Implement idempotency through existence checks
- Use `diff_dict()` to detect changes
- Validate immutable fields and fail if they change after creation
- Restrict to declarative state management rather than imperative actions

### Authentication Patterns

- Parameters: `url`/`endpoint`, `url_username`, `url_password`
- Optional: `client_cert`, `client_key`, `validate_certs`

### Naming Conventions

- **Modules**: `{service}_{entity}.py` (e.g., `example_project.py`)
- **Info modules**: `{service}_{entity}_info.py` (read-only queries)
- **Module utils**: `{service}.py` or `cdp_{service}.py`
- **Test files**: `test_{module_name}_{type}.py` (or `test_{module_name}_{type}_int.py` for integration)

### Module Structure Template

```python
DOCUMENTATION = r"""
module: service_entity
short_description: Brief description (< 50 chars)
description:
  - Detailed description
  - The module supports check_mode
extends_documentation_fragment: cloudera.cloud.services_client
options:
  parameter_name:
    description: What it does
    type: str
    required: true
attributes:
  check_mode:
    support: full
  diff_mode: ## Only if applicable
    support: full
  platform:
    platforms: all
"""

EXAMPLES = r"""
- name: Example task
  cloudera.cloud.service_entity:
    endpoint: "{{ service_endpoint }}"
    username: "{{ service_username }}"
    password: "{{ service_password }}"
    name: resource_name
    state: present
"""

RETURN = r"""
resource:
    description: Resource details
    returned: on success
    type: dict
"""

class ServiceEntityModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(**Model.argument_spec(), state=...),
            supports_check_mode=True,
        )

    def process(self):
        ## Implement logic
        ## Set self.changed and self.diff
```

## Testing Patterns

### Unit and Integration Tests

Use pytest with fixtures from `tests/unit/conftest.py`:

**Unit tests:**
```python
def test_create_resource(module_args, mocker):
    ## Setup
    mock_method = mocker.patch("module_utils.client.Client.create", return_value=...)
    module_args({"endpoint": "https://example.com", "name": "test"})

    ## Execute
    with pytest.raises(AnsibleExitJson) as e:
        module.main()

    ## Assert
    result = e.value.args[0]
    assert result["changed"] is True
    mock_method.assert_called_once()
```

**Integration tests:**
- Suffix: `_int.py`
- Use `env_context` fixture for environment variable checks and built-in skip conditions
- Test against live APIs with proper environment variables set (e.g., `SERVICE_ENDPOINT`) using `env_context` fixture

Fixtures should be defined in `tests/unit/conftest.py` or before the test functions in the same file.

```python
## Required environment variables for integration tests
REQUIRED_ENV_VARS = [
    "ENV_CRN",
    "CDP_API_ENDPOINT",
    "CDP_ACCESS_KEY_ID",
    "CDP_PRIVATE_KEY",
]

## Test configuration constants
TEST_MIN_NODES = 3
TEST_MAX_NODES = 10

## Mark all tests in this module as integration tests requiring API credentials
pytestmark = pytest.mark.integration_api


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

    ## Verify the result
    assert result.value.changed is True
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
    assert "environmentCrn" in result.value.service

    ## Idempotency check - running again should not change anything
    with pytest.raises(AnsibleExitJson) as result:
        example_service.main()

    assert result.value.changed is False
    assert result.value.service is not None
    assert result.value.service.get("crn") == service_crn
```

### Test Organization

```
tests/unit/plugins/<plugin_type>/
  <plugin_family>/
    <plugin_name>/
      test_<plugin_name>_<plugin_type>.py
      test_<plugin_name>_<plugin_type>_int.py
```

### Test Verification

Use Hatch `test` subcommand to manage `pytest` executions.

. `hatch test -q tests/unit/plugins/module_utils/<service client>`
. `hatch test -q tests/unit/plugins/modules/<module>`
. `hatch test -q -m integration_api tests/unit/plugins/module_utils/<service client>`
. `hatch test -q -m integration_api tests/unit/plugins/modules/<module>`

## Documentation Standards

### Doc Fragments

Use `extends_documentation_fragment: cloudera.cloud.services_client` for:
- Standard HTTP client parameters (url/endpoint, username, password, certs)
- Avoids duplicating common parameter docs

Create new fragments in `plugins/doc_fragments/` for shared parameter groups for a module as needed.

### DOCUMENTATION Block

- Include all parameters from `argument_spec`
- Specify accurate types: `str`, `int`, `bool`, `list`, `dict`, `path`
- Add `required: true/false` and `default:` values
- Use `choices:` for enums
- Mark deprecated params appropriately

### EXAMPLES Block

- Use variables for credentials: `{{ endpoint }}`, `{{ username }}`
- Show 2-4 common use cases (not exhaustive)
- Include task `name:` to explain each example's purpose
- Show state transitions (present/absent) where applicable

### RETURN Block

- Document all module return values
- Specify `returned:` condition (always, on success, when changed, etc.)
- Include nested structure for dicts with `contains:`

### Validation

After updating plugin docs:
```bash
ansible-doc -t <plugin type> cloudera.cloud.<plugin name>  ## Validate parsing
hatch run docs:build  ## Regenerate RST docs
```
