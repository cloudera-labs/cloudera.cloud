> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Architecture Patterns

## Module Base Classes

The collection's plugins should:

- Inherit from `ServicesModule` in `plugins/module_utils/common.py`
- Use `AnsibleCdpClient` for HTTP operations
- Implement `AutoExecuteMeta` metaclass (auto-calls `execute()` after `__init__`)
- Place business logic in the abstract `process()` method
- Use built-in pagination via the `@paginated()` decorator

## Data Model Pattern

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

## Client Separation

Separate concerns:

- **Module class**: Ansible orchestration, parameter handling, state management
- **Client class**: REST API operations, HTTP calls
- **Model dataclass**: Data structure definition

```python
class ExampleModule(ServicesModule):
    def process(self):
        client = ExampleClient(self.api_client)
        # Use client for operations

class ExampleClient:
    def create_resource(self, resource: ExampleResource) -> ExampleResource:
        # API calls here
```

## State Management

- Standard states: `present`, `absent`
- Some modules: `started`, `stopped`, `synced`, `published`
- Implement idempotency through existence checks
- Use `diff_dict()` to detect changes
- Validate immutable fields and fail if they change after creation
- Restrict to declarative state management rather than imperative actions

## Constructing the `diff`

**Every mutation module** (any module that creates, updates, or deletes — i.e. `state=present`/`absent` and variants like `started`/`stopped`/`synced`) must populate `self.diff` so `ansible-playbook --diff` and check mode show what changed. Read-only `*_info` modules do not.

Reference implementation: `plugins/modules/iam_user.py`; the CML `ml_project` module (`cloudera.services`) is the canonical shape mirrored below.

Rules:

- **Initialize** in `__init__`: `self.diff = {"before": {}, "after": {}}`.
- **Guard every population** with `if self.module._diff:` — Ansible sets this only when run with `--diff`. Never build the diff unconditionally.
- **Compute the diff *before* the `if not self.module.check_mode:` guard** so `--check --diff` reports the plan without mutating anything.
- Set `self.changed` alongside the diff.
- Populate by operation:
  - **Create**: `before = {}`, `after = to_dict(incoming)` (the intended resource).
  - **Delete**: `before = to_dict(existing)`, `after = {}`.
  - **Update**: `prev, next = diff_dict(existing, desired)` → `before = prev`, `after = next`. `diff_dict()` returns only the changed keys; treat empty `prev`/`next` as "no change" (leave `self.changed` false).
- Emit it from `main()` via `exit_json`, keyed as `diff`:

```python
from ansible_collections.cloudera.cloud.plugins.module_utils.common import (
    diff_dict,
    to_dict,
)

def process(self):
    client = ExampleClient(self.api_client)
    existing = client.find(...)  # None if absent

    if self.state == "absent":
        if existing:
            self.changed = True
            if self.module._diff:
                self.diff["before"] = to_dict(existing)
            if not self.module.check_mode:
                client.delete(existing.id)
        return

    if not existing:  # create
        incoming = ExampleResource(name=self.name, ...)
        self.changed = True
        if self.module._diff:
            self.diff["after"] = to_dict(incoming)
        self.resource = incoming if self.module.check_mode else client.create(incoming)
        return

    # update
    desired = replace(existing, name=self.name, ...)
    prev, next = diff_dict(existing, desired)
    if prev or next:
        self.changed = True
        if self.module._diff:
            self.diff["before"] = prev
            self.diff["after"] = next
        self.resource = desired if self.module.check_mode else client.update(desired)
    else:
        self.resource = existing


def main():
    result = ExampleModule()
    output = dict(
        changed=result.changed,
        resource=to_dict(result.resource) if result.resource else {},
        diff=result.diff,
    )
    result.module.exit_json(**output)
```

For dict-shaped (non-dataclass) APIs — e.g. `iam_user` — `diff_dict()` accepts an `exclude_keys=` argument to drop server-managed fields (timestamps, CRNs) from the comparison, and pair it with `camel_dict_to_snake_dict()` so the `before`/`after` render in snake_case.

See [authentication.md](authentication.md) for auth/transport wiring.
