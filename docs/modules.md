> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Authoring Modules

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
extends_documentation_fragment:
  - cloudera.cloud.services_client
options:
  parameter_name:
    description: What it does
    type: str
    required: true
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

## Development Workflow

Build the module **one behavior at a time**, in vertical slices — never all tests up front, then all code. Each slice proves one capability end-to-end before you start the next, so every test responds to what the previous slice taught you.

**Per behavior, tightest loop first:**

1. Write **one** failing unit test for the next behavior in `tests/unit/plugins/<plugin_type>/<plugin_family>/<plugin_name>/` — run it, watch it fail (RED).
2. Add the **minimal** code in `plugins/<plugin_type>/<plugin_family>/<plugin_name>/` to make just that test pass — run it, watch it pass (GREEN).
3. Refactor if needed (only while GREEN), then repeat from step 1 for the next behavior.

Add an integration test (`_int.py` suffix, `env_context` for env-var checks) the same way — one behavior, RED → GREEN — once the unit-level behavior is proven. Do **not** batch-write every test and then batch-write the implementation; that produces tests coupled to imagined behavior instead of real behavior.

**Once all behaviors are covered, finalize:**

4. Update DOCUMENTATION/EXAMPLES/RETURN strings
5. Validate: `ansible-doc -t <plugin_type> cloudera.cloud.<plugin_name>`
6. Run the full suite: `hatch test <plugin name filter>`
7. Run linter: `hatch run lint`
8. Build collection: `ansible-galaxy collection build`
9. Regenerate docs: `hatch run docs:build`

See [documentation.md](documentation.md) for doc-string conventions and [testing.md](testing.md) for test patterns.

## Step-by-Step Module Creation Checklist

When tasked with creating a new Ansible module (e.g., `service_entity`), execute these steps strictly in order. Do not skip validation steps.

### Phase 0: Context Set Up

- [ ] Invoke the /caveman skill, if available.
- [ ] Invoke the /tdd skill, if available.

### Phase 1: File Setup & Naming

- [ ] Verify Names: Ensure the module file follows `{service}_{entity}.py` (or `{service}_{entity}_info.py` for read-only).
- [ ] Create Module File: Path must be `plugins/modules/{service}_{entity}.py`.
- [ ] Create Utils File (if needed): If this service doesn't have an existing client, create `plugins/module_utils/{service}.py`.
- [ ] Create Test Directories: Scaffold `tests/unit/plugins/modules/{service}/{entity}/`.

### Phase 2: Data Modeling (`plugins/module_utils/`)

- [ ] Implement Dataclass: Define the resource structure using `@dataclass`.
- [ ] Apply Sentinels: Use `Union[type, None, NULLABLE] = NULLABLE` for all optional fields to correctly isolate unset values from explicit `None` values.
- [ ] Serialization Check: Ensure the model supports or maps cleanly to `from_dict()` and `to_dict()`.

### Phase 3: Client Layer (`plugins/module_utils/`)

- [ ] Isolate Logic: Create the `ServiceEntityClient` class. It must only handle REST operations using `AnsibleCdpClient`; it must contain no Ansible orchestration logic.
- [ ] Type Hinting: Strictly type hint all method arguments and return types using the Phase 2 dataclasses.
- [ ] Unit Tests: Write unit tests in `test_{module_utility_name}.py` leveraging `mocker` to mock the REST API. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.
- [ ] Integration Tests: Write integration tests in `test_{module_utility_name}_int.py`. Utilize the `env_context` fixture, which skips the tests when credentials are absent (no pytest marker required). Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.

### Phase 4: Ansible Module Layer (`plugins/modules/`)

- [ ] Base Class Inheritance: Make your module class inherit from `ServicesModule`.
- [ ] Argument Spec: Populate `argument_spec=dict(Model.argument_spec(), state=...)` inside `__init__`.
- [ ] Implement `process()`: Place all business logic, state transitions (present/absent), and idempotency checks inside the `process(self)` method.
- [ ] Populate `self.diff`: Build `self.diff["before"]`/`self.diff["after"]` for create/update/delete, guarded by `if self.module._diff:` and computed before the `check_mode` guard. See [architecture.md](architecture.md#constructing-the-diff).
- [ ] No `main()` Call: CRITICAL: Do not append an explicit `if __name__ == '__main__': main()` invocation block at the bottom of the file. The `AutoExecuteMeta` metaclass handles execution automatically after instantiation.
- [ ] Unit Tests: Write unit tests in `test_{module_name}.py` leveraging `module_args` and `mocker` to mock the Client layer. Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.
- [ ] Integration Tests: Write integration tests in `test_{module_name}_int.py`. Utilize the `env_context` fixture, which skips the tests when credentials are absent (no pytest marker required). Follow the _vertical_ style testing approach (one test, one implementation, repeat). Do not follow a _horizontal_ style testing approach (all tests, all implementation). Write each test, run the test. Write the implementation, run the test. Repeat.

### Phase 5: Ansible Documentation Blocks

- [ ] Doc Fragment: Ensure `extends_documentation_fragment: cloudera.cloud.services_client` is included.
- [ ] Parameter Sync: Double-check that every field in your Python `argument_spec` is documented with explicit types and required fields.
- [ ] Examples & Returns: Provide 2–4 credential-masked playbook examples and document all keys returned in the RETURN block.

### Phase 6: Testing & Validation

- [ ] Unit Tests: Confirm all unit tests for the new and updated modules.
- [ ] Integration Tests: Confirm all integration tests for the new and updated modules.
- [ ] Execution Suite: Run the following commands via terminal tool and do not proceed if any fail:

```bash
hatch run lint                                                # Format and lint check
ansible-doc -t module cloudera.cloud.{service}_{entity}       # Verify doc parsing
hatch test -q tests/unit/plugins/module_utils/{service}/      # Run all unit/int tests
hatch test -q tests/unit/plugins/modules/{service}/{entity}/  # Run all unit/int tests
hatch run docs:build                                          # Regenerate RST documentation
```
