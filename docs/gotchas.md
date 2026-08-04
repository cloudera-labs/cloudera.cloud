> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Common Gotchas

1. **`AutoExecuteMeta` metaclass**: Modules with `ServicesModule` base auto-run `process()` on instantiation — but you **still need** a `main()` (instantiate the class, then `exit_json`) and the `if __name__ == "__main__": main()` block. `AutoExecuteMeta` never calls `exit_json`, so without `main()` the module emits no output
2. **NULLABLE vs None**: Use `NULLABLE` for unset optional fields, `None` for explicitly null values
3. **Immutable fields**: Validate immutable fields don't change; fail with a clear message if they do
4. **RST docs are generated**: Never edit `docsbuild/rst/*.rst` files directly — they're auto-generated from module DOCUMENTATION strings
5. **Collection path**: For `ansible-doc` and doc building, the collection must be in `ANSIBLE_COLLECTIONS_PATHS`
6. **Integration tests**: Need environment variables for service endpoints — tests will be skipped if not set via the `env_context` fixture
7. **Pre-commit hooks**: Run automatically on commit — use `hatch run lint` to run manually on all files
8. **Use `hatch test`, not raw `pytest`**: `hatch test` is the project's `pytest` wrapper — do not run `tests/unit/` files with `pytest` directly (see [testing.md](testing.md))
9. **`diff` only under `--diff`**: populate `self.diff` only inside `if self.module._diff:`, and compute it *before* the `check_mode` guard so `--check --diff` shows the plan without mutating (see [architecture.md](architecture.md#constructing-the-diff))
