# Project Folder Structure

This document describes the reorganized folder structure of the Jarvis AI Windows Use Autonomous Agent project.

## Root Directory Structure

```
windows_use_autonomous_agent/
├── src/                    # Source code (main application)
│   └── windows_use/        # Core Windows automation modules
├── scripts/                # Executable scripts and batch files
├── data/                   # Data files and models
│   ├── models/            # Machine learning models
│   └── learning_data/     # Learning and training data
├── config/                 # Configuration files
├── docs/                   # Documentation
├── tests/                  # Test files
├── cookbook/               # Example implementations
└── .github/                # GitHub workflows and templates
```

## Source Code Organization (`src/windows_use/`)

### Core Modules
- **agent/** - Main automation agent and tools
- **desktop/** - Desktop interaction and UI automation
- **jarvis_ai/** - AI personality and conversation management
- **llm/** - Language model providers and routing (includes EVI, NLU)
- **web/** - Web automation and scraping
- **office/** - Microsoft Office automation
- **security/** - Security, authentication, and guardrails
- **tools/** - System tools and utilities
- **utils/** - Common utilities (includes logging, screenshots)
- **evolution/** - Self-improvement and learning algorithms
- **tree/** - UI element tree parsing
- **examples/** - Usage examples and demos

### Module Consolidation

The following modules have been merged for better organization:
- `evi/` → merged into `llm/` (Empathic Voice Interface)
- `nlu/` → merged into `llm/` (Natural Language Understanding)
- `observability/` → merged into `utils/` (Logging and monitoring)

## Import Path Changes

### Before Restructuring
```python
from windows_use.jarvis_ai import JarvisPersonality
from windows_use.web import SearchEngine
from windows_use.observability.logger import setup_logger
```

### After Restructuring
```python
from src.windows_use.jarvis_ai import JarvisPersonality
from src.windows_use.web import SearchEngine
from src.windows_use.utils.logger import setup_logger
```

## Scripts Directory

All executable scripts are now centralized in the `scripts/` folder:
- `jarvis_main.py` - Main application entry point
- `test_installation.py` - Installation verification
- `run_tests.py` - Test runner
- `install_jarvis_auto.bat` - Automated installation
- `start_jarvis.bat` - Application launcher

## Data Directory

Consolidated data storage:
- `data/models/` - All ML models (command_classifier.pkl, etc.)
- `data/learning_data/` - Training data and user profiles

## Benefits of New Structure

1. **Clearer Separation**: Source code is isolated in `src/`
2. **Logical Grouping**: Related functionality is grouped together
3. **Reduced Complexity**: Fewer top-level directories
4. **Better Scalability**: Easier to add new modules
5. **Standard Conventions**: Follows Python packaging best practices

## Migration Notes

- All import statements have been updated to use the new paths
- Internal module imports use relative imports where possible
- External scripts reference `src.windows_use` for imports
- Configuration and data files remain accessible at their new locations

## Development Guidelines

1. **New Features**: Add to appropriate module in `src/windows_use/`
2. **Scripts**: Place executable scripts in `scripts/`
3. **Tests**: Mirror the `src/` structure in `tests/`
4. **Documentation**: Update relevant docs when adding features
5. **Imports**: Use relative imports within modules, absolute imports from external scripts