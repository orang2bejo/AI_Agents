# Security Modes

| Mode | Description | Typical Use |
| --- | --- | --- |
| ASSISTIVE | Requires explicit user confirmation before actions that modify state. | Safe default for day-to-day use. |
| SEMI_AUTO | Proceeds with predefined checkpoints; user confirmation needed for critical steps or when OTP/CAPTCHA detected. | Batch tasks with oversight. |
| FULL_AUTO | Executes actions without user intervention. Should only run in controlled environments. | Trusted, sandboxed automation. |

Actions submitted in ASSISTIVE and SEMI_AUTO modes must be confirmed when `require_confirm_on_submit` is enabled.
