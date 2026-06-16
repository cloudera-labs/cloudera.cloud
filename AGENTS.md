# cloudera.cloud Collection - Development Guidelines

This is an Ansible collection for Cloudera Data Platform (CDP) Public and Private Cloud control plane. See [README.md](README.md) for overview and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow.

## Quick Start Commands

**Setup environment:**
```bash
pip install hatch
hatch shell  # Activates default environment with all dependencies
pre-commit install
```

**Run tests:**
```bash
pytest tests/unit/  # Unit and integration tests (integration tests require env vars)
hatch test  # Runs tests on first compatible environment of the hatch matrix
hatch -a test  # Run tests on all environments in the hatch matrix (sequentially)
```

**Build:**
```bash
hatch run lint  # Lint and format
ansible-galaxy collection build
hatch run docs:build  # Generate API docs
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
        # Use client for operations
        
class ExampleClient:
    def create_resource(self, resource: ExampleResource) -> ExampleResource:
        # API calls here
```

## Naming Conventions

- **Modules**: `{service}_{entity}.py` (e.g., `example_project.py`)
- **Info modules**: `{service}_{entity}_info.py` (read-only queries)
- **Module utils**: `{service}.py` or `cdp_{service}.py`
- **Test files**: `test_{module_name}_{type}.py` (or `test_{module_name}_{type}_int.py` for integration)

## Module Structure Template

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
  diff_mode: # Only if applicable
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
        # Implement logic
        # Set self.changed and self.diff
```

## Testing Patterns

### Unit Tests

Use pytest with fixtures from `tests/unit/conftest.py`:

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
- Test against live APIs with proper environment variables set (e.g., `SERVICE_ENDPOINT`) using `env_context` fixture

Fixtures should be defined in `tests/unit/conftest.py` or before the test functions in the same file.

### Test Organization

```
tests/unit/plugins/<plugin_type>/
  <plugin_family>/
    <plugin_name>/
      test_<plugin_name>_<plugin_type>.py
      test_<plugin_name>_<plugin_type>_int.py
```

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
- Include task names that explain purpose
- Show state transitions (present/absent) where applicable

### RETURN Block

- Document all module return values
- Specify `returned:` condition (always, on success, when changed, etc.)
- Include nested structure for dicts with `contains:`

### Validation

After updating plugin docs:
```bash
ansible-doc -t <plugin type> cloudera.cloud.<plugin name>  # Validate parsing
hatch run docs:build  # Regenerate RST docs
```

## State Management

- Standard states: `present`, `absent`
- Some modules: `started`, `stopped`, `synced`, `published`
- Implement idempotency through existence checks
- Use `diff_dict()` to detect changes
- Validate immutable fields and fail if they change after creation
- Restrict to declarative state management rather than imperative actions

## Authentication Patterns

- Parameters: `url`/`endpoint`, `url_username`, `url_password`
- Optional: `client_cert`, `client_key`, `validate_certs`

## Common Gotchas

1. **`AutoExecuteMeta` metaclass**: Modules with `ServicesModule` base auto-execute `process()` after `__init__` — no explicit `main()` call needed
2. **NULLABLE vs None**: Use `NULLABLE` for unset optional fields, `None` for explicitly null values
3. **Immutable fields**: Validate immutable fields don't change; fail with clear message if they do
4. **RST docs are generated**: Never edit `docsbuild/rst/*.rst` files directly — they're auto-generated from module DOCUMENTATION strings
5. **Collection path**: For `ansible-doc` and doc building, collection must be in `ANSIBLE_COLLECTIONS_PATHS`
6. **Integration tests**: Need environment variables for service endpoints — tests will be skipped if not set via the `env_context` fixture
7. **Pre-commit hooks**: Run automatically on commit — use `hatch run lint` to run manually on all files

## Development Workflow

1. Create/modify plugin in `plugins/<plugin_type>/<plugin_family>/<plugin_name>/`
2. Update DOCUMENTATION/EXAMPLES/RETURN strings
3. Validate: `ansible-doc -t <plugin_type> cloudera.cloud.<plugin_name>`
4. Write unit tests in `tests/unit/plugins/<plugin_type>/<plugin_family>/<plugin_name>/`
5. Write integration tests in `tests/unit/plugins/<plugin_type>/<plugin_family>/<plugin_name>/` with `_int.py` suffix and use `env_context` for env var checks
5. Run tests: `pytest tests/unit/ <plugin name filter>`
6. Run linter: `hatch run lint`
7. Build collection: `ansible-galaxy collection build`
8. Regenerate docs: `hatch run docs:build`

## Resources

- **API docs**: Run `hatch run docs:build` then open `docsbuild/build/html/index.html`
- **Testing guide**: See `tests/unit/conftest.py` for test fixtures and utilities
- **Hatch commands**: Run `hatch env show` to see available environments and scripts
