# Action Plan

## P0 – Immediate
- Remove secrets from `jarvis_config.json`; load from environment.
- Fix `desktop.execute_command` to avoid `command.split()` injection.
- Add domain allowlist & confirmation prompts in web automation.
- Resolve `jarvis_demo.py` syntax error to restore build.

## P1 – Near Term
- Implement `obs/device_telemetry.py` and `scripts/healthcheck.py` for CPU/GPU metrics.
- Add CI workflow running `ruff`, `black --check`, `mypy`, `pytest` (skip Office if unavailable).
- Refactor large modules (`web_form_automation.py`, `hitl.py`).
- Ensure `personality_state.json` and other runtime data are gitignored.

## P2 – Later
- Consolidate dependency management in `pyproject.toml` with extras for voice/office/web/security.
- Split monolithic web modules into smaller components and add retry/backoff utilities.
- Centralize logging and PII masking utilities.
