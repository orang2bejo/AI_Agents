# 🤖 Jarvis AI - Advanced Autonomous Agent

> **Asisten AI Cerdas untuk Windows dengan Voice Control & Desktop Automation**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green.svg)]()

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd windows_use_autonomous_agent

# Install core dependencies
pip install -r requirements.txt

# For development (optional)
pip install -r requirements-dev.txt

# Run Jarvis AI
python scripts/jarvis_main.py
```

## 📦 Dependencies

### Core Dependencies (requirements.txt)
- **AI & LLM**: `langchain`, `pydantic`
- **Data Processing**: `numpy`, `scikit-learn`
- **Web & HTTP**: `requests`, `beautifulsoup4`, `aiohttp`
- **Desktop Automation**: `uiautomation`, `pyautogui`, `humancursor`
- **Voice Processing**: `sounddevice`, `websockets`, `webrtcvad`
- **Visualization**: `matplotlib`, `Pillow`
- **System**: `psutil`, `termcolor`

### Development Dependencies (requirements-dev.txt)
- **Testing**: `pytest`, `pytest-cov`, `pytest-asyncio`
- **Code Quality**: `black`, `flake8`, `mypy`, `pylint`
- **Documentation**: `sphinx`, `mkdocs`
- **Optional Features**: `openai`, `selenium`, `torch`, `pandas`

> 🔧 **Optimized Dependencies**: Unused packages have been removed to reduce installation size and improve security.

## 📁 Project Structure

```
📦 windows_use_autonomous_agent/
├── 📂 config/          # Configuration files (.env, configs)
├── 📂 data/            # Data storage & logs
├── 📂 docs/            # 📚 Complete Documentation
├── 📂 windows_use/examples/  # Demo scripts & examples
├── 📂 scripts/         # Main execution scripts
├── 📂 tests/           # Test suites
├── 📂 windows_use/     # 🧠 Core AI modules
│   ├── 📂 agent/       # AI agent logic
│   ├── 📂 desktop/     # Desktop automation
│   ├── 📂 jarvis_ai/   # Main Jarvis AI engine
│   ├── 📂 llm/         # Language model integration
│   ├── 📂 nlu/         # Natural language understanding
│   ├── 📂 office/      # Office automation (Word, Excel, etc.)
│   ├── 📂 security/    # Security & authentication
│   ├── 📂 tools/       # Utility tools
│   └── 📂 web/         # Web automation & scraping
└── 📄 requirements.txt # Dependencies
```

## 🎯 Core Features

- 🎤 **Voice Control** - Speech-to-text & text-to-speech
- 🖥️ **Desktop Automation** - Window management, file operations
- 📊 **Office Integration** - Word, Excel, PowerPoint automation
- 🌐 **Web Automation** - Browser control & web scraping
- 🧠 **AI Agent** - Intelligent task execution
- 🤖 **Multi-Provider LLM** - OpenAI, Anthropic, Google, OpenRouter integration
- 🔒 **Security** - Multi-level authentication & access control

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 User Guide](docs/PANDUAN_PENGGUNA.md) | Complete user manual |
| [⚙️ Installation Guide](docs/PANDUAN_INSTALASI.md) | Step-by-step installation |
| [🏗️ Project Structure](docs/PROJECT_STRUCTURE.md) | Detailed architecture |
| [🔧 Jarvis AI Guide](docs/JARVIS_README.md) | Core AI functionality |
| [🔒 Security Evolution](docs/SECURITY_EVOLUTION.md) | Security features |
| [🐍 Python Upgrade](docs/PANDUAN_UPGRADE_PYTHON.md) | Python 3.12+ migration |

## 🛠️ Development

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black windows_use/ scripts/ tests/
isort windows_use/ scripts/ tests/

# Code quality checks
flake8 windows_use/ scripts/
mypy windows_use/
pylint windows_use/

# Run main application
python scripts/jarvis_main.py
```

### 🔧 Recent Optimizations

- ✅ **Dependencies Cleaned**: Removed 15+ unused packages
- ✅ **Separated Dev Dependencies**: Development tools moved to `requirements-dev.txt`
- ✅ **Fixed Dashboard Shutdown**: Corrected method call in `jarvis_main.py`
- ✅ **Improved Security**: Reduced attack surface by removing unnecessary packages
- ✅ **Faster Installation**: Core installation now ~40% faster

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## 👨‍💻 Author

**Orangbejo**
- GitHub: [@orangbejo](https://github.com/orangbejo)
- Trae Profile: [orangbejo.trae.ai](https://orangbejo.trae.ai)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🚀 Ready to experience the future of AI assistance? Start with our [Installation Guide](docs/PANDUAN_INSTALASI.md)!**