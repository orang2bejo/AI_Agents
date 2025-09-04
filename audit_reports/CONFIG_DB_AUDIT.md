# Config & Database Audit

## Inspected Files
- `config/jarvis_config.json`
- `config/llm_config.yaml`
- `config/logging.yaml`
- `config/personality_config.json`
- `config/personality_state.json`
- `data/learning_data/learning_data.json`
- `.gitignore`

## Findings
- **Secrets committed**: `evi_api_key` and `evi.api_key` are hard-coded in `jarvis_config.json`.
- `personality_state.json` contains user state and is committed despite ignore rules.
- `llm_config.yaml` references API keys via environment variables (good practice).
- No `.env` file found; environment variable reliance not documented.
- No domain allowlist or Full-Auto default setting located in configs.
- No encryption or access control for JSON data files; data retention policies absent.

## Recommendations
- Move secrets to environment variables and remove from VCS.
- Ensure `personality_state.json` and other dynamic state files are gitignored and rotated.
- Add domain allowlist and explicit `mode` (Assistive/Semi/Full) flags in configs.
- Consider encrypting sensitive config sections or using a secrets manager.
