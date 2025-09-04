# Test Matrix

## Existing Tests
- `tests/test_llm.py`
- `tests/test_integration.py`
- `tests/test_security.py`
- `tests/test_evolution.py`
- `tests/test_web.py`
- `tests/test_gui.py`
- `tests/test_python312_upgrade.py`

## Gaps & Proposed Tests
| Area | Missing Coverage | Suggested Test |
| --- | --- | --- |
| Office COM | Interaction with Word/Excel/PowerPoint | Mock COM objects to validate API usage |
| Voice/STT/TTS | Whisper & Piper integration | Simulate audio input/output; check device selection |
| Configuration | Loading/parsing of YAML/JSON | Unit tests for `config/*` schema validation |
| Web Automation | Domain allowlist & form submission | Headless test ensuring prompts before submit |
| Recovery/Retry | Retry logic in `web_form_automation` | Unit test for retry/backoff on timeouts |
| Healthcheck | System telemetry | Test `scripts/healthcheck.py` returns CPU metrics |

## CI Recommendations
- Run `ruff`, `black --check`, `mypy`, and `pytest` in pipeline.
- Skip Office tests if dependencies unavailable; mark as `xfail`.
