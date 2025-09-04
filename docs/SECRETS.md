# Secrets Management

Jarvis uses the Windows Credential Manager via the `secret_store` module to keep API keys and tokens out of source control.

## Storing a Secret
```python
from windows_use.security.secret_store import set_secret
set_secret("OPENAI_API_KEY", "sk-...")
```

## Using a Secret in Config
`security.yaml` values can reference `${OPENAI_API_KEY}`. If the environment variable is not set, the loader resolves it from the secret store.

## Rotation
Update the secret with `set_secret` and restart the agent. Use `delete_secret` to remove old keys.

## Auditing
Secrets are never logged. Review access through Windows Credential Manager's audit logs.
