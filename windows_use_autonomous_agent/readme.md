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
│   ├── 📂 desktop/     # Desktop automation & GUI dashboard
│   ├── 📂 evi/         # Evolution Intelligence (self-evolving engine)
│   ├── 📂 evolution/   # Evolution engine components
│   ├── 📂 jarvis_ai/   # Main Jarvis AI engine
│   ├── 📂 llm/         # Language model integration
│   ├── 📂 nlu/         # Natural language understanding
│   ├── 📂 observability/ # Monitoring and logging
│   ├── 📂 office/      # Office automation (Word, Excel, etc.)
│   ├── 📂 security/    # Security guardrails & authentication
│   ├── 📂 tools/       # Utility tools
│   ├── 📂 tree/        # Decision tree components
│   ├── 📂 utils/       # Utility functions
│   └── 📂 web/         # Web automation, RPA & scraping
└── 📄 requirements.txt # Dependencies
```

## 🎯 Core Features

- 🎤 **Voice Control** - Speech-to-text & text-to-speech
- 🖥️ **Desktop Automation** - Window management, file operations
- 📊 **Office Integration** - Word, Excel, PowerPoint automation
- 🌐 **Web Automation** - Browser control & web scraping (Selenium + Playwright)
- 🧠 **AI Agent** - Intelligent task execution with autonomous decision making
- 🤖 **Multi-Provider LLM** - OpenAI, Anthropic, Google, OpenRouter integration
- 🔒 **Security Guardrails** - Multi-level authentication, command validation & access control
- 📊 **GUI Dashboard** - Real-time monitoring and configuration interface
- 🧬 **Self-Evolving Engine** - Adaptive learning and performance optimization
- 🤖 **Web RPA** - Robotic Process Automation for web workflows

## 🔥 Advanced Features

### 📊 GUI Dashboard
- **Real-time Monitoring**: Live system status and performance metrics
- **Configuration Interface**: Easy settings management through intuitive GUI
- **Task Visualization**: Visual representation of running processes and queues
- **Resource Monitoring**: CPU, memory, and GPU usage tracking

### 🧬 Self-Evolving Engine
- **Adaptive Learning**: Automatically improves performance based on usage patterns
- **Performance Optimization**: Dynamic resource allocation and task prioritization
- **Memory Store**: Persistent learning from user interactions and outcomes
- **Mutation & Reflection**: Continuous improvement through self-analysis

### 🤖 Web RPA (Robotic Process Automation)
- **Browser Automation**: Selenium and Playwright integration for robust web control
- **Form Processing**: Automated form filling and data extraction
- **Workflow Automation**: Complex multi-step web processes
- **Cross-browser Support**: Compatible with Chrome, Firefox, Edge, and Safari

### 🔒 Security Guardrails
- **Command Validation**: Pre-execution security checks for all operations
- **File Path Security**: Prevents unauthorized file system access
- **Dangerous Operation Detection**: Automatic blocking of potentially harmful commands
- **Multi-level Security**: Four configurable security levels (LOW, MEDIUM, HIGH, CRITICAL)
- **Domain Allowlist**: Controlled web access with whitelist management
- **Rate Limiting**: Prevents abuse through request throttling
- **Audit Logging**: Comprehensive security event tracking
- **Human-in-the-Loop**: Requires approval for sensitive operations

#### Security Levels

| Level | Use Case | Risk | Description |
|-------|----------|------|-------------|
| **LOW** | Development/Testing | High | Minimal validation, most operations allowed |
| **MEDIUM** | Standard Production | Moderate | Balanced security with functionality (Default) |
| **HIGH** | Sensitive Environments | Low | Strict validation, confirmation required |
| **CRITICAL** | High-Security Systems | Very Low | Maximum security, minimal automation |

#### Domain Allowlist Management

```python
from windows_use.security import GuardrailsEngine, SecurityLevel

# Initialize security engine
engine = GuardrailsEngine()

# Set security level
engine.set_security_level(SecurityLevel.HIGH)

# Manage domain allowlist
engine.add_allowed_domain("trusted-site.com")
engine.remove_allowed_domain("old-site.com")

# Check domain status
if engine.is_domain_allowed("github.com"):
    print("Domain is allowed")

# Get all allowed domains
allowed_domains = engine.get_allowed_domains()
```

**Default Allowed Domains**: `github.com`, `stackoverflow.com`, `python.org`, `microsoft.com`, `google.com`, `openai.com`, `huggingface.co`, `pypi.org`

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 User Guide](docs/PANDUAN_PENGGUNA.md) | Complete user manual |
| [⚙️ Installation Guide](docs/PANDUAN_INSTALASI.md) | Step-by-step installation |
| [🖥️ Hardware Requirements](docs/HARDWARE_REQUIREMENTS.md) | System requirements and optimization |
| [🏗️ Project Structure](docs/PROJECT_STRUCTURE.md) | Detailed architecture |
| [🔧 Jarvis AI Guide](docs/JARVIS_README.md) | Core AI functionality |
| [🤖 Model Router & Policy](MODEL_ROUTER.md) | LLM routing and policy management |
| [📊 Performance Monitoring](PERFORMANCE.md) | CPU/GPU performance monitoring and health checks |
| [🔒 Security Evolution](docs/SECURITY_EVOLUTION.md) | Security features |
| [🌐 OpenRouter Integration](docs/OPENROUTER_INTEGRATION.md) | OpenRouter API integration guide |
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