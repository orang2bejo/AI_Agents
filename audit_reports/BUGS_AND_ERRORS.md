# Bugs & Errors

| File/Line | Issue | Suggested Fix |
| --- | --- | --- |
| `src/windows_use/examples/jarvis_demo.py:272` | Syntax error: positional argument after keyword【ba1ebe†L1-L3】 | Reorder arguments per Python syntax |
| `src/windows_use/web/web_form_automation.py:466` | Bare `except` hides errors【5d1671†L66-L75】 | Catch `Exception` or specific Playwright errors |
| `src/windows_use/desktop/__init__.py:61` | `command.split()` may break quoted args, injection risk【23938c†L59-L63】 | Use `shlex.split` or pass list to subprocess |
| `config/jarvis_config.json` | Hard-coded API keys【294e78†L31-L44】 | Use env vars and remove from repo |
| `tests/test_installation.py` | Import name conflict causes pytest collection error【fd3edd†L1-L20】 | Rename script or test module |
| `security/hitl.py` | Multiple unused variables causing clutter【5d1671†L1-L40】 | Remove or log variables |
