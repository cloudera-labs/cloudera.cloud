> Part of the cloudera.cloud agent guide — see [AGENTS.md](../AGENTS.md).

# Authentication

## Per-service auth patterns

**Modern modules (`ServicesModule`):**

- Parameters: `url`/`endpoint`, `url_username`, `url_password`
- Optional: `client_cert`, `client_key`, `validate_certs`
- Transport handled by `AnsibleCdpClient`

Shared client option docs live in the `cloudera.cloud.services_client` doc fragment
(see [documentation.md](documentation.md)).

## Credentials

- Never hardcode API credentials in code or tests.
- Use the `env_context` fixture or environment variables for integration tests.
