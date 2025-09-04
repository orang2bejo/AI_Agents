# Security Audit

## Key Findings
- **Secrets in repo**: `evi_api_key` in `config/jarvis_config.json`【294e78†L31-L44】
- `personality_state.json` stores user interaction metadata committed to git【64a7f2†L1-L9】
- `desktop.execute_command` concatenates user commands with `command.split()` → susceptible to injection【23938c†L59-L63】
- `web_form_automation.py` lacks domain allowlist and uses bare `except` blocks【5d1671†L66-L75】
- No CAPTCHA/OTP handling; automation can run in Full-Auto without confirmation.
- Logging configuration writes to plain-text log files without PII masking.

## Guardrails & HITL
- HITL module (`security/hitl.py`) exists but contains unused variables and minimal logging.
- No explicit mode enforcement; config does not default to Assistive or Semi-Auto.

## Recommendations
- Remove committed secrets; use environment variables and secret managers.
- Sanitize PowerShell commands: avoid `command.split()`; use argument lists or shlex.
- Implement domain allowlist and confirm-before-submit in web automation.
- Add PII masking and log rotation policies.
- Enforce HITL prompts for destructive actions; default to **Assistive** mode.
- Document CAPTCHA/OTP fallback paths requiring Semi-Auto intervention.
