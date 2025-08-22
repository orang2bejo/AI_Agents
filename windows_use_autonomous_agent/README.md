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

**Windows-Use** is a powerful automation agent that interact directly with the Windows at GUI layer. It bridges the gap between AI Agents and the Windows OS to perform tasks such as opening apps, clicking buttons, typing, executing shell commands, and capturing UI state all without relying on traditional computer vision models. Enabling any LLM to perform computer automation instead of relying on specific models for it.

## ✨ New Features

### 🎤 Voice Input & TTS
- **Speech-to-Text (STT)** with Whisper integration
- **Voice Activity Detection (VAD)** for hands-free operation
- **Push-to-talk** functionality
- **Lightweight TTS** using Piper with Indonesian language support
- **Fallback to Windows SAPI** for text-to-speech

### 🧠 Indonesian Language Support
- **Grammar-based Intent Parser** for Indonesian commands
- **Direct command mapping** without LLM processing for faster response
- **Context-aware routing** between different processing backends

### 📊 Office Automation
- **Excel Automation** via COM (pywin32)
  - Workbook and worksheet management
  - Cell operations and data manipulation
  - Chart insertion and formatting
- **Word Automation** via COM
  - Document creation and editing
  - Text formatting and styling
  - PDF export functionality
- **PowerPoint Automation** via COM
  - Slide creation and management
  - Content insertion and editing
  - Presentation export

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

## 🛠️Installation Guide

### **Prerequisites**

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) (or `pip`)
- Windows 10 or 11

### **Installation Steps**

**Install using `uv`:**

```bash
uv pip install windows-use
````

Or with pip:

```bash
pip install windows-use
```

**Install additional dependencies for new features:**

```bash
pip install -r requirements.txt
```

**Note:** For Office automation features, ensure Microsoft Office is installed on your system.

## ⚙️Basic Usage

```python
# main.py
from langchain_google_genai import ChatGoogleGenerativeAI
from windows_use.agent import Agent
from dotenv import load_dotenv

load_dotenv()

llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash')
agent = Agent(llm=llm,use_vision=True)
query=input("Enter your query: ")
agent_result=agent.invoke(query=query)
print(agent_result.content)
```

### 🎤 Voice Input Usage

```python
from windows_use.tools.voice_input import VoiceInput

# Initialize voice input with push-to-talk
voice_input = VoiceInput()
voice_input.setup_push_to_talk(key='space')

# Start listening
text = voice_input.listen_with_push_to_talk()
print(f"You said: {text}")
```

### 🔊 TTS Usage

```python
from windows_use.tools.tts_piper import TTSPiper

# Initialize TTS
tts = TTSPiper()

# Speak text in Indonesian
tts.speak("Halo, saya adalah asisten AI Anda")
```

### 📊 Office Automation Usage

```python
from windows_use.office import ExcelHandler, WordHandler

# Excel automation
excel = ExcelHandler()
excel.open_excel()
workbook = excel.create_workbook()
excel.write_cell(workbook, 'Sheet1', 'A1', 'Hello World')
excel.save_workbook(workbook, 'output.xlsx')

# Word automation
word = WordHandler()
word.open_word()
doc = word.create_document()
word.write_text(doc, 'This is automated text')
word.save_document(doc, 'output.docx')
```

### 🔧 Windows System Tools Usage

```python
from windows_use.tools.winget import WingetManager
from windows_use.tools.ps_shell import PowerShellManager
from windows_use.tools.process import ProcessManager

# Package management
winget = WingetManager()
packages = winget.search_package("notepad")
winget.install_package("Microsoft.WindowsNotepad")

# PowerShell operations
ps = PowerShellManager()
result = ps.execute_command("Get-Process")
system_info = ps.get_system_info()

# Process management
proc_mgr = ProcessManager()
processes = proc_mgr.list_processes()
top_processes = proc_mgr.get_top_processes_by_cpu()
```

### 🧬 Self-Evolving Agent Usage

```python
from windows_use.evolution import EvolutionEngine, EvolutionConfig
from windows_use.evolution.memory import ExperienceType

# Initialize evolution engine
config = EvolutionConfig(evaluation_interval=1800)  # 30 minutes
engine = EvolutionEngine(config)

# Start evolution
await engine.start()

# Record experiences
await engine.record_experience(
    experience_type=ExperienceType.TASK_EXECUTION,
    context="User requested file search",
    action="Executed search command",
    outcome="Found 15 files in 2.3 seconds",
    success=True,
    confidence=0.9
)

# Get insights
insights = await engine.get_insights()
print(f"Success rate: {insights['performance']['success_rate']}")
```

## 🤖 Run Agent

You can use the following to run from a script:

```bash
python main.py
Enter your query: <YOUR TASK>
```

---

## 🎥 Demos

**PROMPT:** Write a short note about LLMs and save to the desktop

<https://github.com/user-attachments/assets/0faa5179-73c1-4547-b9e6-2875496b12a0>

**PROMPT:** Change from Dark mode to Light mode

<https://github.com/user-attachments/assets/47bdd166-1261-4155-8890-1b2189c0a3fd>

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

Made with ❤️ by [Jeomon George](https://github.com/Jeomon)

---

## Citation

```bibtex
@software{
  author       = {George, Jeomon},
  title        = {Windows-Use: Enable AI to control Windows OS},
  year         = {2025},
  publisher    = {GitHub},
  url={https://github.com/CursorTouch/Windows-Use}
}
```
