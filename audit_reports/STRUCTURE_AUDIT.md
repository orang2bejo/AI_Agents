# Structure Audit

## Repository Tree (top 2 levels)
```
.
├── config/
├── cookbook/
├── data/
├── docs/
├── scripts/
├── src/
│   ├── data/
│   └── windows_use/
└── tests/
```

## `src/windows_use` Modules
```
agent/  desktop/  evolution/  examples/  jarvis_ai/
llm/    office/   security/   tools/     tree/
utils/  web/
```

## Missing or Claimed-but-Missing Components
- README.md (root) – not found
- actions/, backends/, nlu/, modes/, memory/, obs/, recovery/, vision/, ui/ – no corresponding folders under `src/windows_use`
- reports/ – referenced in instructions but not present

## Naming & Duplication Notes
- `learning_data` and `data/learning_data` both exist
- `personality_state.json` is committed despite .gitignore rule
