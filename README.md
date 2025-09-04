# Jarvis Windows Agent

![CI](https://github.com/CursorTouch/AI_Agents/actions/workflows/ci.yml/badge.svg)

Jarvis is an autonomous agent for Windows automation, integrating voice, web, and desktop controls.

## Security & Compliance
- Default automation mode is **ASSISTIVE**; other modes are documented in [Security Modes](docs/SECURITY_MODES.md).
- Secrets are stored via Windows Credential Manager; see [SECRETS.md](docs/SECRETS.md).
- Logs are sanitized and rotated every 14 days. Use `scripts/healthcheck.py` to inspect device providers.

## Healthcheck
```bash
python scripts/healthcheck.py
```
