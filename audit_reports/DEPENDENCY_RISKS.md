# Dependency Risks

## Sources Reviewed
- `requirements.txt`
- `requirements-dev.txt`
- `pyproject.toml`

## Observations
- Many dependencies use `>=` without upper bounds; risk of future breaking changes.
- `requirements.txt` marks several optional packages commented out; better handled via extras.
- `pyproject.toml` already defines `voice` and `office` extras but lacks `web` or `security` groups.
- Duplicated dependencies between `requirements.txt` and `pyproject.toml` (e.g., langchain, numpy).
- Development requirements include heavy packages (`torch`, `tensorflow`) that drastically increase install size.

## Potential Vulnerabilities
- `requests` and `aiohttp` have frequent CVEs; ensure versions remain updated.
- `pyautogui` and `uiautomation` run with high privileges—monitor for updates.

## Recommendations
- Consolidate dependency management using `pyproject.toml` exclusively; generate lock file.
- Define extras: `[voice]`, `[office]`, `[web]`, `[security]`.
- Pin critical packages with upper bounds (e.g., `requests>=2.31,<3.0`).
- Run `pip-audit` or `safety` in CI to track CVEs.
