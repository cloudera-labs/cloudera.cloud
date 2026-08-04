# cloudera.cloud Collection - Agent Guidelines

This is an Ansible collection for Cloudera Data Platform (CDP) Public Cloud services.

This file is a **router**: the invariants below apply to all work; read the linked topic doc for the area you're touching rather than loading everything up front.

## Critical rules (always apply)

- **Persona**: You are an expert Ansible developer specializing in the CDP collection.
- **Idempotency**: Maintain idempotency at all costs.
- **Validation**: Never assume an API structure; always verify against `plugins/module_utils` models before writing code.
- Use **`hatch test`**, never raw `pytest`, never `ansible-test` — it wraps `pytest` for unit *and* integration tests. Do not run `tests/unit/` files with `pytest` directly.
- Python via **Hatch (uv-backed)**; Ansible in a **per-project venv**. No global installs.
- Small, reviewable diffs; write the failing test first (TDD).
- **Never edit generated `docsbuild/rst/*.rst`** — regenerate from module docstrings (`hatch run docs:build`).
- `NULLABLE` = unset, `None` = explicitly null. Don't conflate them.
- `ServicesModule` subclasses auto-run `process()` (`AutoExecuteMeta`) — no manual `main()` call.
- Mutation modules must populate `self.diff` (guarded by `self.module._diff`) — see [docs/architecture.md](docs/architecture.md).
- Do not modify `pyproject.toml` or other Hatch configuration without direct, human approval.
- Never hardcode API credentials in code or tests; use `env_context` or environment variables.

## Quick start commands

**Setup environment:**
```bash
pip install hatch
hatch shell  # Activates default environment with all dependencies
pre-commit install
```

**Run tests:**
```bash
hatch test  # Runs tests on first compatible environment of the hatch matrix
hatch -a test  # Run tests on all environments in the hatch matrix (sequentially)
hatch test <filter>  # Run a filtered subset (integration tests require env vars)
```

**Build:**
```bash
hatch run lint  # Lint and format
ansible-galaxy collection build
hatch run docs:build  # Generate API docs
```

## Guide map

| Topic | Read this when… | File |
|---|---|---|
| Architecture | adding/changing a module's base class, HTTP client, data model, or state handling | [docs/architecture.md](docs/architecture.md) |
| Authentication | wiring auth/transport or adding a service's credentials | [docs/authentication.md](docs/authentication.md) |
| Authoring modules | creating a new module — naming, scaffolding template, workflow, creation checklist | [docs/modules.md](docs/modules.md) |
| Documentation | writing DOCUMENTATION/EXAMPLES/RETURN or doc fragments | [docs/documentation.md](docs/documentation.md) |
| Testing | writing unit or integration tests, fixtures, test layout | [docs/testing.md](docs/testing.md) |
| Gotchas | quick check before you commit; debugging surprising behavior | [docs/gotchas.md](docs/gotchas.md) |

## Resources

- **API docs**: Run `hatch run docs:build` then open `docsbuild/build/html/index.html`
- **Testing guide**: See `tests/unit/conftest.py` for test fixtures and utilities
- **Hatch commands**: Run `hatch env show` to see available environments and scripts
