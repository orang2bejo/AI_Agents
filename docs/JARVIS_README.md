# 🤖 Jarvis AI System

**Advanced AI Assistant with Voice Interface, Task Management, and Learning Capabilities**

---

## 🌟 Overview

Jarvis AI is a comprehensive artificial intelligence system inspired by the fictional AI assistant from Iron Man. This system provides a complete AI assistant experience with voice interaction, intelligent task management, adaptive learning, and an intuitive dashboard interface.

### ✨ Key Features

- **🎤 Voice Interface**: Advanced speech-to-text and text-to-speech capabilities
- **🧠 Intelligent Personality**: Adaptive personality with contextual responses
- **💬 Conversation Management**: Context-aware dialog with memory
- **🌐 Dual Language Support**: English and Indonesian language support
- **📋 Task Coordination**: Intelligent task scheduling and execution
- **🎯 Learning Engine**: Adaptive learning from user interactions
- **📊 Dashboard Interface**: Real-time monitoring and control panel
- **🏢 Office Automation**: Integration with Microsoft Office applications
- **🔧 System Tools**: Windows system management capabilities
- **🌍 Web Search**: Intelligent web search and content extraction
- **🛡️ Security**: Built-in guardrails and safety measures
- **🔄 Self-Evolution**: Continuous improvement and adaptation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows 10/11** (for full functionality)
- **Microphone and Speakers** (for voice features)
- **Internet Connection** (for web features)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd advanced_ai_agents/windows_use_autonomous_agent
   ```

2. **Install core dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Core packages installed:**
   - AI & LLM: `langchain`, `pydantic`
   - Desktop Automation: `uiautomation`, `pyautogui`, `humancursor`
   - Voice Processing: `sounddevice`, `websockets`, `webrtcvad`
   - Web & HTTP: `requests`, `beautifulsoup4`, `aiohttp`
   - Data Processing: `numpy`, `scikit-learn`

3. **Install development dependencies (optional)**:
   ```bash
   pip install -r requirements-dev.txt
   ```
   
   **Development packages include:**
   - Testing: `pytest`, `pytest-cov`, `pytest-asyncio`
   - Code Quality: `black`, `flake8`, `mypy`, `pylint`
   - Optional Features: `openai`, `selenium`, `torch`, `pandas`

4. **Verify installation**:
   ```bash
   python -c "import langchain, numpy, requests; print('✅ Core dependencies installed')"
   ```

### Basic Usage

1. **Run the main system**:
   ```bash
   python jarvis_main.py
   ```

2. **Run with options**:
   ```bash
   # Run without GUI
   python jarvis_main.py --no-gui
   
   # Run without voice
   python jarvis_main.py --no-voice
   
   # Run demo mode
   python jarvis_main.py --demo
   
   # Use custom config
   python jarvis_main.py --config custom_config.json
   ```

3. **Run the demo**:
   ```bash
   python windows_use/examples/jarvis_demo.py
   ```

---

## 🏗️ Architecture

### Core Modules

```
jarvis_ai/
├── personality.py          # AI personality and response generation
├── conversation.py         # Dialog management and context
├── language_manager.py     # Multi-language support
├── voice_interface.py      # Voice input/output handling
├── task_coordinator.py     # Task scheduling and execution
├── learning_engine.py      # Adaptive learning system
└── dashboard.py           # GUI dashboard interface
```

### Extended Functionality

```
├── voice/                 # Voice processing modules
├── intent_parser/         # Natural language understanding
├── office_automation/     # Microsoft Office integration
├── windows_system_tools/  # System management tools
├── self_evolving_agent/   # Self-improvement capabilities
├── multi_provider_llm/    # LLM integration
├── guardrails/           # Safety and security
└── web/                  # Web search and automation
```

---

## 🎯 Usage Examples

### Voice Commands

```
# English Commands
"Hello Jarvis"
"What can you do?"
"Execute a task for me"
"Remember that I like coffee"
"Search for Python tutorials"
"Open Excel and create a new spreadsheet"
"What's my system status?"

# Indonesian Commands
"Halo Jarvis"
"Apa yang bisa kamu lakukan?"
"Jalankan tugas untuk saya"
"Ingat bahwa saya suka kopi"
"Cari tutorial Python"
"Buka Excel dan buat spreadsheet baru"
"Bagaimana status sistem saya?"
```

### Programming Interface

```python
from jarvis_ai import (
    JarvisPersonality,
    ConversationManager,
    VoiceInterface,
    TaskCoordinator,
    LearningEngine
)

# Initialize components
personality = JarvisPersonality()
conversation = ConversationManager()
voice = VoiceInterface()
tasks = TaskCoordinator()
learning = LearningEngine()

# Start systems
voice.initialize()
tasks.start()
learning.start()

# Process user input
response = personality.generate_greeting(Language.ENGLISH, "user")
voice.speak(response, Language.ENGLISH)
```

---

## ⚙️ Configuration

### Configuration File

The system uses `jarvis_config.json` for configuration. Key sections include:

```json
{
  "personality": {
    "traits": ["helpful", "professional", "adaptive"],
    "tone": "friendly",
    "proactive": true
  },
  "voice": {
    "input_mode": "voice_activation",
    "stt_engine": "whisper",
    "tts_engine": "piper"
  },
  "learning": {
    "enabled": true,
    "auto_save": true,
    "model_update_interval": 3600
  }
}
```

### Environment Variables

```bash
# Optional API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GROQ_API_KEY="your-groq-key"
export GOOGLE_API_KEY="your-google-key"

# Voice Settings
export JARVIS_VOICE_ENGINE="whisper"
export JARVIS_TTS_ENGINE="piper"

# System Settings
export JARVIS_LOG_LEVEL="INFO"
export JARVIS_DATA_DIR="./data"
```

---

## 🎨 Dashboard Interface

The Jarvis AI system includes a comprehensive dashboard with:

- **📊 System Overview**: Real-time metrics and status
- **🎤 Voice Visualizer**: Audio input visualization
- **💬 Chat Interface**: Text-based interaction
- **📝 Activity Logs**: System and user activity
- **📋 Task Manager**: Active and completed tasks
- **⚙️ Settings Panel**: Configuration management

### Dashboard Features

- **Dark/Light Themes**: Customizable appearance
- **Real-time Updates**: Live system monitoring
- **Interactive Controls**: Direct system interaction
- **Performance Metrics**: CPU, memory, and response times
- **Voice Activity**: Real-time audio visualization

---

## 🧠 Learning and Adaptation

### Learning Capabilities

- **User Preference Learning**: Adapts to user communication style
- **Command Success Prediction**: Learns which commands work best
- **Response Optimization**: Improves response quality over time
- **Behavioral Pattern Recognition**: Understands user habits
- **Context Awareness**: Learns from conversation context

### Machine Learning Models

- **Intent Classification**: Naive Bayes classifier
- **Sentiment Analysis**: Logistic regression
- **User Clustering**: K-means clustering
- **Response Optimization**: Linear regression

---

## 🔧 Advanced Features

### Office Automation

```python
# Excel automation
from office_automation import ExcelAutomation
excel = ExcelAutomation()
excel.create_workbook("data.xlsx")
excel.write_data("A1", "Hello World")

# Word automation
from office_automation import WordAutomation
word = WordAutomation()
word.create_document("report.docx")
word.add_paragraph("This is a test document")
```

### System Tools

```python
# System monitoring
from windows_system_tools import SystemMonitor
monitor = SystemMonitor()
stats = monitor.get_system_stats()
print(f"CPU Usage: {stats['cpu_percent']}%")
print(f"Memory Usage: {stats['memory_percent']}%")
```

### Web Search

```python
# Web search
from web import SearchEngine
search = SearchEngine()
results = search.search("Python tutorials", max_results=5)
for result in results:
    print(f"{result['title']}: {result['url']}")
```

---

## 🛡️ Security and Safety

### Built-in Guardrails

- **Input Validation**: Sanitizes user input
- **Output Filtering**: Prevents harmful responses
- **Rate Limiting**: Prevents abuse
- **Content Filtering**: Blocks inappropriate content
- **Human-in-the-Loop**: Manual approval for sensitive operations

### Privacy Protection

- **Local Processing**: Most operations run locally
- **Data Encryption**: Sensitive data is encrypted
- **Minimal Data Collection**: Only necessary data is stored
- **User Control**: Users control their data

---

## 🔄 Self-Evolution

The system includes self-improvement capabilities:

- **Performance Evaluation**: Continuous performance monitoring
- **Automatic Reflection**: Self-assessment of responses
- **Code Mutation**: Automatic code improvements
- **Memory Management**: Intelligent data retention
- **Adaptation Learning**: Learns from user feedback

---

## 📊 Monitoring and Metrics

### System Metrics

- **Response Time**: Average response latency
- **Task Success Rate**: Percentage of successful tasks
- **User Satisfaction**: Inferred from interactions
- **System Resource Usage**: CPU, memory, disk usage
- **Learning Progress**: Model accuracy improvements

### Logging

```python
# Structured logging
import logging
logger = logging.getLogger('JarvisAI')
logger.info("System started successfully")
logger.warning("Voice interface not available")
logger.error("Task execution failed")
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Voice not working**:
   - Check microphone permissions
   - Install audio dependencies: `pip install pyaudio`
   - Try different STT/TTS engines

2. **Dashboard not opening**:
   - Install tkinter: `pip install tk`
   - Run with `--no-gui` flag
   - Check display settings

3. **Office automation fails**:
   - Install pywin32: `pip install pywin32`
   - Ensure Office applications are installed
   - Run as administrator if needed

4. **Web search not working**:
   - Check internet connection
   - Verify API keys (if using paid services)
   - Try different search engines

### Debug Mode

```bash
# Enable debug logging
python jarvis_main.py --log-level DEBUG

# Check system status
python -c "from jarvis_ai import *; print('All modules imported successfully')"
```

---

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Install development dependencies**: `pip install -r requirements-dev.txt`
4. **Run tests**: `pytest tests/`
5. **Submit a pull request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to all functions
- Write unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** for speech recognition
- **Piper TTS** for text-to-speech
- **scikit-learn** for machine learning
- **tkinter** for GUI framework
- **Microsoft** for Office automation APIs
- **The open-source community** for various libraries and tools

---

## 📞 Support

For support, questions, or feature requests:

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check the wiki pages
- **Examples**: See the `windows_use/examples/` directory

---

**🤖 "I am Jarvis, your AI assistant. How may I help you today?"**