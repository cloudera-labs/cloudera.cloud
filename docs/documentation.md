> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Documentation Standards

## Doc Fragments

Use `extends_documentation_fragment: cloudera.cloud.services_client` for:

- Standard HTTP client parameters (url/endpoint, username, password, certs)
- Avoids duplicating common parameter docs

Create new fragments in `plugins/doc_fragments/` for shared parameter groups for a module as needed.

## DOCUMENTATION Block

- Include all parameters from `argument_spec`
- Specify accurate types: `str`, `int`, `bool`, `list`, `dict`, `path`
- Add `required: true/false` and `default:` values
- Use `choices:` for enums
- Mark deprecated params appropriately

## EXAMPLES Block

- Use variables for credentials: `{{ endpoint }}`, `{{ username }}`
- Show 2-4 common use cases (not exhaustive)
- Include task `name:` to explain each example's purpose
- Show state transitions (present/absent) where applicable

## RETURN Block

- Document all module return values
- Specify `returned:` condition (always, on success, when changed, etc.)
- Include nested structure for dicts with `contains:`

## Validation

After updating plugin docs:

```bash
ansible-doc -t <plugin type> cloudera.cloud.<plugin name>  # Validate parsing
hatch run docs:build  # Regenerate RST docs
```
