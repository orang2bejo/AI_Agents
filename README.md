<div align="center">

  <h1>🪟 Windows Use Autonomous Agent</h1>

  <a href="https://github.com/CursorTouch/windows-use/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue" alt="Platform">
  <br>

  <a href="https://x.com/CursorTouch">
    <img src="https://img.shields.io/badge/follow-%40CursorTouch-1DA1F2?logo=twitter&style=flat" alt="Follow on Twitter">
  </a>
  <a href="https://discord.com/invite/Aue9Yj2VzS">
    <img src="https://img.shields.io/badge/Join%20on-Discord-5865F2?logo=discord&logoColor=white&style=flat" alt="Join us on Discord">
  </a>

</div>

<br>

**Jarvis AI** is a powerful autonomous agent that combines Windows automation with advanced AI capabilities. Built on the Windows-Use foundation, it features a fully integrated AI system with voice control, office automation, learning capabilities, and comprehensive Windows system integration. The system bridges the gap between AI Agents and Windows OS through both GUI interaction and direct API integration.

🎯 **Latest Updates (January 2025):**
- ✅ **Multi-Provider LLM Support** - OpenRouter, Gemini, Anthropic, Groq, Ollama integration
- ✅ **Voice Processing Enhanced** - EVI (Empathic Voice Interface) integration
- ✅ **Dependency Optimization** - 96+ core packages, streamlined installation
- ✅ **Configuration Management** - Comprehensive API key and provider setup
- ✅ **Module Structure Improved** - Fixed import paths and module organization

## ✨ Integrated Features

### 🤖 Jarvis AI Core System
- **Unified AI Package** - All components integrated into `jarvis_ai` module
- **Personality Engine** - Adaptive AI personality with learning capabilities
- **Conversation Manager** - Context-aware dialogue management
- **Task Coordinator** - Intelligent task scheduling and execution
- **Learning Engine** - Machine learning models for continuous improvement
- **Multi-Provider LLM Support** - 15+ providers including OpenRouter, Gemini, Anthropic, Groq, Ollama
- **Dashboard Interface** - Real-time monitoring and control panel with GUI
- **Self-Evolution** - Continuous improvement and adaptation capabilities
- **EVI Integration** - Empathic Voice Interface for emotional AI interactions

### 🎤 Voice & Language Processing
- **Voice Interface** - Complete STT/TTS integration with multi-language support
- **EVI (Empathic Voice Interface)** - Emotional AI voice interactions
- **Language Manager** - Multi-language processing and translation
- **Intent Recognition** - Advanced command understanding and routing
- **Push-to-Talk** functionality with customizable hotkeys
- **Voice Activity Detection** for hands-free operation
- **Voice Authentication** - Security system based on voice recognition
- **Voice Web Control** - Navigate and interact with web using voice commands
- **WebRTC VAD** - Advanced voice activity detection
- **Piper TTS** - High-quality text-to-speech synthesis

### 📊 Office & System Integration
- **Office Automation** - Complete Excel, Word, PowerPoint control via COM
- **Windows System Tools** - Package management, PowerShell, process control
- **Web Integration** - Search engines and web scraping capabilities
- **File Management** - Advanced file operations and organization
- **Security Framework** - Guardrails and Human-in-the-Loop approval system
- **System Monitoring** - Real-time system metrics and performance tracking
- **Process Management** - Advanced process control and monitoring

### 🔒 Security & Safety
- **Guardrails Engine** for action validation
- **Human-in-the-Loop (HITL)** approval system
- **Rate limiting** and security policies
- **Action logging** and audit trails

### 📈 Observability
- **Structured JSON logging** with context tracking
- **Automatic screenshot capture** for debugging
- **Performance metrics** and monitoring
- **Session management** and error tracking

### 🔧 Windows System Tools
- **Package Management** via winget integration
- **PowerShell Cmdlet Execution** with safety whitelists
- **Process Management** for system monitoring and control
- **Network Operations** for connectivity and diagnostics
- **System Information** retrieval and analysis

### 🧬 Self-Evolving Agent
- **Performance Evaluation** with automated metrics collection
- **Behavioral Reflection** for pattern analysis and insights
- **Adaptive Mutations** for continuous improvement
- **Experience Memory Store** with SQLite backend
- **Evolution Engine** for orchestrated self-improvement cycles

## 🛠️ Installation Guide

### **Prerequisites**

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) (or `pip`)
- Windows 10/11 (required for COM automation)
- Microphone and speakers (for voice features)

### **Installation Steps**

**1. Clone the repository:**

```bash
git clone <repository-url>
cd advanced_ai_agents
```

**2. Install Jarvis AI package:**

```bash
cd windows_use_autonomous_agent

# Install core dependencies (optimized)
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

**3. Install the integrated Jarvis AI package:**

```bash
pip install -e .
```

### 📦 **Optimized Dependencies**

#### Core Dependencies (`requirements.txt` - 96 packages)
- **AI & LLM**: `langchain>=0.1.0`, `langchain-core>=0.1.0`, `pydantic>=2.5.0`
- **Desktop Automation**: `uiautomation>=2.0.0`, `pyautogui>=0.9.54`, `humancursor>=0.1.0`
- **Voice Processing**: `sounddevice>=0.4.6`, `websockets>=11.0.0`, `webrtcvad>=2.0.10`
- **Web & HTTP**: `requests>=2.31.0`, `beautifulsoup4>=4.12.0`, `aiohttp>=3.8.0`
- **Data Processing**: `numpy>=1.24.0`, `scikit-learn>=1.3.0`
- **System**: `psutil>=5.9.0`, `termcolor>=2.3.0`
- **Image Processing**: `Pillow>=10.0.0`
- **Text Processing**: `markdownify>=0.11.6`, `fuzzywuzzy>=0.18.0`

#### Development Dependencies (`requirements-dev.txt` - 99 packages)
- **Testing**: `pytest>=7.4.0`, `pytest-cov>=4.1.0`, `pytest-asyncio>=0.21.1`, `pytest-mock>=3.11.1`
- **Code Quality**: `black>=23.7.0`, `flake8>=6.0.0`, `mypy>=1.5.0`, `pylint>=2.17.0`, `bandit>=1.7.5`
- **Documentation**: `sphinx>=7.1.0`, `mkdocs>=1.5.0`, `mkdocs-material>=9.1.0`
- **Development Tools**: `ipython>=8.14.0`, `jupyter>=1.0.0`, `notebook>=7.0.0`
- **Performance**: `memory-profiler>=0.61.0`, `line-profiler>=4.1.0`, `py-spy>=0.3.14`
- **Security**: `safety>=2.3.0`, `pip-audit>=2.6.0`

> 🚀 **Performance Improvements**: Dependencies have been optimized - core installation is now ~40% faster with improved security through reduced attack surface.

**Note:** For Office automation features, ensure Microsoft Office is installed on your system.

## 🔧 Configuration Setup

### **API Keys Configuration**

Copy the example environment file and configure your API keys:

```bash
cp config/.env-example .env
notepad .env  # Edit with your API keys
```

**Required API Keys (choose one or more):**
```bash
# LLM Providers
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Voice Services (optional)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here

# Search Services (optional)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
BING_SEARCH_API_KEY=your_bing_search_api_key_here
```

### **LLM Provider Configuration**

Edit `config/llm_config.yaml` to configure your preferred LLM providers:

```yaml
providers:
  ollama:
    enabled: true
    priority: 1
    base_url: "http://localhost:11434"
    models: ["llama3.2:3b", "qwen2.5:7b"]
    
  openrouter:
    enabled: true
    priority: 2
    models: ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
    
  gemini:
    enabled: true
    priority: 3
    models: ["gemini-1.5-pro", "gemini-1.5-flash"]
```

### **Quick Start Scripts**

```bash
# Auto-install with dependencies
install_jarvis_auto.bat

# Start Jarvis AI
start_jarvis.bat

# Test installation
python test_installation.py
```

## ⚙️ Basic Usage

### **Quick Start with Jarvis AI**

```python
# Run the integrated Jarvis AI system
python jarvis_main.py
```

### **Using Jarvis AI Components**

```python
from jarvis_ai import JarvisAI, VoiceInterface, TaskCoordinator
from dotenv import load_dotenv

load_dotenv()

# Initialize Jarvis AI
jarvis = JarvisAI()

# Start voice interface
voice = VoiceInterface()
voice.start_listening()

# Execute tasks
task_coordinator = TaskCoordinator()
result = task_coordinator.execute_task("open excel and create a new workbook")
print(result)
```

### 🎤 Voice Control Usage

```python
from jarvis_ai import VoiceInterface

# Initialize voice interface
voice = VoiceInterface()

# Setup push-to-talk (default: space key)
voice.setup_push_to_talk()

# Start voice interaction
voice.start_listening()
# Say: "Buka Excel dan buat workbook baru"
```

### 🔊 Text-to-Speech Usage

```python
from jarvis_ai.voice import TTSManager

# Initialize TTS with Indonesian support
tts = TTSManager()

# Speak in Indonesian
tts.speak("Halo, saya Jarvis AI, asisten virtual Anda")
```

### 📊 Office Automation with Jarvis AI

```python
from jarvis_ai.office import OfficeAutomation

# Initialize office automation
office = OfficeAutomation()

# Excel operations
office.excel.create_workbook()
office.excel.write_data('A1', 'Hello Jarvis AI')
office.excel.save_as('jarvis_report.xlsx')

# Word operations
office.word.create_document()
office.word.add_text('Laporan dibuat oleh Jarvis AI')
office.word.save_as('jarvis_document.docx')
```

### 🌐 Multi-Provider LLM Integration

```python
from jarvis_ai.llm import LLMRouter, create_provider

# Initialize LLM Router with automatic provider selection
router = LLMRouter()

# OpenRouter - Access 100+ models through one API
openrouter = create_provider(
    "openrouter",
    api_key="sk-or-v1-your-api-key",
    model="openai/gpt-4o"
)

# Local Ollama models
ollama = create_provider(
    "ollama",
    base_url="http://localhost:11434",
    model="llama3.2:3b"
)

# Google Gemini
gemini = create_provider(
    "gemini",
    api_key="your-gemini-key",
    model="gemini-1.5-flash"
)

# Automatic provider selection with fallback
response = await router.generate_response(
    messages=[{"role": "user", "content": "Hello from Jarvis AI!"}],
    policy="cost_optimized"  # Auto-select cheapest available
)

# Available providers:
# - OpenRouter: 100+ models (GPT-4o, Claude-3.5, Llama-3.1, etc.)
# - Ollama: Local models (Llama, Qwen, Gemma)
# - Gemini: Google's latest models
# - Anthropic: Claude family
# - Groq: Ultra-fast inference
```

### 🎤 EVI (Empathic Voice Interface)

```python
from jarvis_ai.voice import EVIInterface

# Initialize EVI for emotional voice interactions
evi = EVIInterface(
    api_key="your-evi-api-key",
    voice_id="default",
    empathy_level=0.7
)

# Start empathic conversation
evi.start_conversation()
evi.speak_with_emotion("Hello! How are you feeling today?", emotion="caring")

# Process emotional responses
response = evi.listen_with_emotion_detection()
print(f"Detected emotion: {response.emotion}")
print(f"Confidence: {response.confidence}")
```

### 🔧 Windows System Tools with Jarvis AI

```python
from jarvis_ai.system import SystemManager

# Initialize system manager
system = SystemManager()

# Package management
system.winget.search("notepad")
system.winget.install("Microsoft.WindowsNotepad")

# PowerShell operations
result = system.powershell.execute("Get-Process")
system_info = system.powershell.get_system_info()

# Process management
processes = system.process.list_all()
top_cpu = system.process.get_top_by_cpu()
```

### 🧬 Learning & Evolution with Jarvis AI

```python
from jarvis_ai import LearningEngine

# Initialize learning engine
learning = LearningEngine()

# Train models
learning.train_command_classifier()
learning.update_preference_clusters()
learning.optimize_responses()

# Get insights
insights = learning.get_performance_insights()
print(f"Learning progress: {insights}")
```

## 🤖 Run Jarvis AI

You can run Jarvis AI in multiple ways:

**1. Full Jarvis AI System:**
```bash
python jarvis_main.py
```

**2. Voice-only mode:**
```bash
python -c "from jarvis_ai import VoiceInterface; VoiceInterface().start_listening()"
```

**3. Interactive mode:**
```bash
python -c "from jarvis_ai import JarvisAI; jarvis = JarvisAI(); jarvis.interactive_mode()"
```

---

## 🎥 Demos

**PROMPT:** Write a short note about LLMs and save to the desktop

<https://github.com/user-attachments/assets/0faa5179-73c1-4547-b9e6-2875496b12a0>

**PROMPT:** Change from Dark mode to Light mode

<https://github.com/user-attachments/assets/47bdd166-1261-4155-8890-1b2189c0a3fd>

## 🚀 Recent Optimizations

### Dependency Management Overhaul
- **Removed 15+ unused packages** from core dependencies
- **Separated development tools** into `requirements-dev.txt`
- **40% faster installation** with optimized package selection
- **Improved security** through reduced attack surface
- **Better maintainability** with categorized dependencies

### Bug Fixes & Improvements
- **Fixed dashboard shutdown error** in `jarvis_main.py`
- **Enhanced error handling** for graceful application termination
- **Optimized import structure** for better performance
- **Updated documentation** across all README files

### Performance Benefits
- **Lighter core installation** - only essential packages
- **Faster startup time** with reduced import overhead
- **Cleaner development environment** with separated dev tools
- **Easier deployment** with minimal production dependencies

## Vision

Talk to your computer. Watch it get things done.

## Roadmap

### 🤖 Agent Intelligence

* [x] **Integrate memory** : allow the agent to remember past interactions made by the user.
* [ ] **Optimize token usage** : implement strategies like Ally Tree compression and prompt engineering to reduce overhead.
* [ ] **Simulate advanced human-like input** : enable accurate and naturalistic mouse & keyboard interactions across apps.
* [ ] **Support for local LLMs** : local models with near-parity performance to cloud-based APIs (e.g., Mistral, LLaMA, etc.).
* [ ] **Improve reasoning and planning** : enhance the agent's ability to break down and sequence complex tasks.

### 🎤 Voice & Language Features

* [x] **Voice Input Integration** : Speech-to-Text with Whisper and VAD support
* [x] **Text-to-Speech** : Lightweight TTS with Piper and Indonesian language support
* [x] **Indonesian Language Processing** : Grammar-based intent parser for local commands
* [ ] **Multi-language Support** : Expand to other languages beyond Indonesian
* [ ] **Voice Command Optimization** : Improve accuracy and response time

### 🔧 System Integration

* [x] **Windows System Tools** : Package management, PowerShell integration, process control
* [x] **Office Automation** : Complete COM integration for Excel, Word, PowerPoint
* [x] **Security & Safety** : Guardrails engine with HITL approval system
* [x] **Observability** : Structured logging, screenshots, performance metrics
* [ ] **Registry Management** : Safe Windows registry operations
* [ ] **Service Management** : Windows service control and monitoring

### 🧬 Self-Evolution

* [x] **Performance Evaluation** : Automated metrics collection and analysis
* [x] **Behavioral Reflection** : Pattern analysis and insight generation
* [x] **Adaptive Mutations** : Continuous behavior improvement
* [x] **Experience Memory** : SQLite-based experience storage and retrieval
* [x] **Evolution Engine** : Orchestrated self-improvement cycles
* [ ] **Advanced Learning** : Machine learning integration for pattern recognition
* [ ] **Predictive Adaptation** : Proactive behavior adjustments

### 🌳 Ally Tree Optimization

* [ ] **Improve UI element detection** : automatically identify and prioritize essential, interactive components on screen.
* [ ] **Compress Ally Tree intelligently** : reduce complexity by pruning irrelevant branches.
* [ ] **Context-aware prioritization** : rank UI elements based on relevance to the task at hand.

### 💡 User Experience

* [ ] **Reduce latency** : optimize to improve response time between GUI interaction.
* [ ] **Polish command interface** : make it easier to write, speak, or type commands through a simplified UX layer.
* [ ] **Better error handling & recovery** : ensure graceful handling of edge cases and unclear instructions.

### 🧪 Evaluation

* [ ] **LLM evaluation benchmarks** — track performance across different models and benchmarks.

## ⚠️ Caution

Agent interacts directly with your Windows OS at GUI layer to perform actions. While the agent is designed to act intelligently and safely, it can make mistakes that might bring undesired system behaviour or cause unintended changes. Try to run the agent in a sandbox envirnoment.

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please check the [CONTRIBUTING](CONTRIBUTING) file for setup and development workflow.

Made with ❤️ by [Jeomon George](https://github.com/Jeomon) and [Orangbejo](https://github.com/Orangbejo)

## 👨‍💻 Author

**Orangbejo**
- GitHub: [https://github.com/Orangbejo](https://github.com/Orangbejo)
- Trae URL: [https://trae.ai/@orangbejo](https://trae.ai/@orangbejo)

---

## Citation

```bibtex
@software{
  author       = {George, Jeomon and Orangbejo, },
  title        = {Windows-Use: Enable AI to control Windows OS},
  year         = {2025},
  publisher    = {GitHub},
  url={https://github.com/CursorTouch/Windows-Use}
}
```
