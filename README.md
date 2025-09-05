# Jarvis AI - Advanced Windows Desktop Agent 🤖

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.31-orange.svg)](pyproject.toml)

Jarvis AI adalah sistem agen AI canggih yang dirancang untuk berinteraksi dengan Windows OS pada level GUI. Sistem ini menggabungkan kemampuan voice interface, task coordination, learning engine, dan office automation untuk memberikan pengalaman AI assistant yang komprehensif.

## 🌟 Fitur Utama

### 🎤 Voice Interface
- **Speech-to-Text**: Konversi suara ke teks menggunakan OpenAI Whisper
- **Text-to-Speech**: Output suara natural
- **Voice Activity Detection**: Deteksi aktivitas suara real-time
- **EVI Integration**: Dukungan untuk Hume AI EVI (opsional)

### 🤖 Personality Engine
- **Dual Language Support**: Bahasa Indonesia dan Inggris
- **Adaptive Behavior**: Pembelajaran dari riwayat interaksi
- **Contextual Responses**: Respons yang disesuaikan dengan konteks
- **Sophisticated Patterns**: Pola respons yang canggih

### 🎯 Task Coordination
- **Task Prioritization**: Prioritas tugas otomatis
- **Progress Tracking**: Pelacakan kemajuan real-time
- **Error Recovery**: Penanganan error dan pemulihan otomatis
- **Multi-threading**: Eksekusi tugas paralel

### 📊 Dashboard & Monitoring
- **Real-time Metrics**: Metrik sistem real-time
- **Performance Monitoring**: Monitoring performa CPU/GPU
- **Health Checks**: Pemeriksaan kesehatan sistem
- **Visual Indicators**: Indikator status visual

### 🏢 Office Automation
- **Excel Integration**: Manipulasi spreadsheet otomatis
- **Word Processing**: Pembuatan dan editing dokumen
- **PowerPoint Automation**: Pembuatan presentasi otomatis
- **Cross-Office Workflows**: Workflow antar aplikasi Office

### 🌐 Web Capabilities
- **Search Engine**: Integrasi mesin pencari
- **Web Scraping**: Ekstraksi konten web
- **Form Automation**: Otomasi form web
- **Content Analysis**: Analisis konten web

### 🔒 Security & Safety
- **Command Validation**: Validasi perintah sistem
- **Domain Allowlist**: Daftar domain yang diizinkan
- **Confirmation Prompts**: Prompt konfirmasi untuk operasi sensitif
- **Secure API Handling**: Penanganan API key yang aman

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Windows 10/11**
- **4GB+ RAM** (8GB+ direkomendasikan)
- **Microphone & Speaker** (untuk fitur voice)

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/CursorTouch/advanced_ai_agents.git
   cd advanced_ai_agents
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv jarvis_env
   jarvis_env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Core installation
   pip install -e .
   
   # Install with specific features
   pip install -e ".[voice,office,web,security,telemetry]"
   
   # Install all features
   pip install -e ".[all]"
   ```

4. **Configure Environment**
   ```bash
   # Copy and edit configuration
   copy jarvis_config.json.example jarvis_config.json
   # Edit jarvis_config.json with your settings
   ```

5. **Run Jarvis**
   ```bash
   python scripts\jarvis_main.py
   ```

### Verification
```bash
# Test installation
python test_installation.py

# Run health check
python scripts\healthcheck.py
```

## 📦 Optional Dependencies

### Voice Features
```bash
pip install ".[voice]"
```
- OpenAI Whisper untuk speech-to-text
- SoundDevice untuk audio I/O
- WebRTC VAD untuk voice activity detection

### Office Automation
```bash
pip install ".[office]"
```
- PyWin32 untuk Windows COM integration
- OpenPyXL untuk Excel manipulation
- Python-docx untuk Word processing
- Python-pptx untuk PowerPoint automation

### Web Capabilities
```bash
pip install ".[web]"
```
- Selenium untuk web automation
- Aiohttp untuk async HTTP requests
- WebDriver Manager untuk browser drivers

### Security Features
```bash
pip install ".[security]"
```
- Cryptography untuk enkripsi
- BCrypt untuk password hashing
- PyJWT untuk token handling

### Telemetry & Monitoring
```bash
pip install ".[telemetry]"
```
- GPUtil untuk GPU monitoring
- PyNVML untuk NVIDIA GPU metrics

## 🎮 Usage Examples

### Voice Commands
```python
# Start voice interface
from windows_use.voice import VoiceInterface

voice = VoiceInterface()
voice.start_listening()

# Voice commands:
# "Jarvis, buka Excel"
# "Jarvis, cari informasi tentang AI"
# "Jarvis, buat presentasi baru"
```

### Programming Interface
```python
from windows_use import JarvisAI

# Initialize Jarvis
jarvis = JarvisAI()

# Task coordination
task_id = jarvis.create_task("Buat laporan Excel")
jarvis.execute_task(task_id)

# Office automation
jarvis.office.create_excel_report(data, "laporan.xlsx")
jarvis.office.create_powerpoint("presentasi.pptx")

# Web operations
results = jarvis.web.search("machine learning")
jarvis.web.scrape_content("https://example.com")
```

### Dashboard Monitoring
```python
# Start dashboard
from windows_use.dashboard import Dashboard

dashboard = Dashboard()
dashboard.start()  # Akses via http://localhost:8080
```

## ⚙️ Configuration

### Environment Variables
```bash
# API Keys (opsional)
set OPENAI_API_KEY=your_openai_key
set HUME_API_KEY=your_hume_key
set GOOGLE_API_KEY=your_google_key

# System Settings
set JARVIS_LOG_LEVEL=INFO
set JARVIS_VOICE_ENABLED=true
set JARVIS_DASHBOARD_PORT=8080
```

### Configuration File (jarvis_config.json)
```json
{
  "personality": {
    "language": "id",
    "formality": "casual",
    "enthusiasm": 0.8
  },
  "voice": {
    "enabled": true,
    "language": "id-ID",
    "voice_speed": 1.0
  },
  "dashboard": {
    "enabled": true,
    "port": 8080,
    "auto_open": true
  },
  "security": {
    "require_confirmation": true,
    "allowed_domains": ["*.trusted-site.com"]
  }
}
```

## 🏗️ Architecture

### Core Modules
- **`personality/`**: Personality engine dan response patterns
- **`conversation/`**: Conversation management dan session handling
- **`voice/`**: Voice interface dan audio processing
- **`tasks/`**: Task coordination dan execution
- **`learning/`**: Learning engine dan adaptive behavior
- **`dashboard/`**: Web dashboard dan monitoring

### Extended Functionality
- **`office/`**: Office automation (Excel, Word, PowerPoint)
- **`web/`**: Web scraping dan search capabilities
- **`security/`**: Security features dan validation
- **`utils/`**: Utilities, logging, dan telemetry

## 🔧 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install ".[dev]"

# Run tests
pytest tests/

# Code formatting
black .
ruff check .

# Type checking
mypy windows_use/
```

### Contributing
1. Fork repository
2. Create feature branch
3. Make changes dengan tests
4. Run quality checks
5. Submit pull request

## 📊 Performance & Monitoring

### System Requirements
- **Minimum**: 4GB RAM, dual-core CPU
- **Recommended**: 8GB+ RAM, quad-core CPU, dedicated GPU
- **Optimal**: 16GB+ RAM, 8-core CPU, NVIDIA GPU

### Monitoring Tools
```bash
# Health check
python scripts\healthcheck.py

# Performance metrics
python scripts\performance_monitor.py

# System telemetry
python -c "from windows_use.utils.device_telemetry import DeviceTelemetry; DeviceTelemetry().get_system_metrics()"
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```bash
# Pastikan virtual environment aktif
jarvis_env\Scripts\activate
pip install -e ".[all]"
```

**Voice Recognition Issues**
```bash
# Test microphone
python -c "import sounddevice; print(sounddevice.query_devices())"

# Install audio drivers
# Restart audio services
```

**Office Automation Errors**
```bash
# Install Office dan PyWin32
pip install ".[office]"

# Run as administrator jika diperlukan
```

**Performance Issues**
```bash
# Check system resources
python scripts\healthcheck.py

# Monitor GPU usage
python -c "from windows_use.utils.device_telemetry import GPUMetrics; print(GPUMetrics().get_gpu_info())"
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION_COMPLETE.md)**: Panduan instalasi lengkap
- **[API Integration](docs/API_INTEGRATION_GUIDE.md)**: Integrasi API eksternal
- **[Hardware Requirements](docs/HARDWARE_REQUIREMENTS.md)**: Spesifikasi hardware
- **[Performance Guide](PERFORMANCE.md)**: Optimasi performa
- **[Folder Structure](FOLDER_STRUCTURE.md)**: Struktur proyek

## 🔄 Recent Updates (v0.1.31)

### ✅ Security Enhancements
- Fixed command injection vulnerabilities
- Removed hard-coded API keys
- Added domain allowlist for web operations
- Implemented confirmation prompts for sensitive operations

### ✅ Code Quality Improvements
- Fixed syntax errors in core modules
- Replaced bare except blocks with specific exceptions
- Removed unused variables and imports
- Added comprehensive error handling

### ✅ Infrastructure Enhancements
- Added CI/CD workflow with automated testing
- Implemented telemetry and health monitoring
- Consolidated dependencies with optional extras
- Updated Git configuration and .gitignore

### ✅ Feature Additions
- Device telemetry with CPU/GPU monitoring
- Health check scripts for system validation
- Performance monitoring dashboard
- Improved logging and error tracking

## 📄 License

MIT License - lihat [LICENSE](LICENSE) untuk detail lengkap.

## 🙏 Acknowledgments

- **OpenAI** untuk Whisper speech recognition
- **Hume AI** untuk EVI emotional intelligence
- **LangChain** untuk AI framework
- **Microsoft** untuk Office automation APIs
- **Community contributors** untuk feedback dan improvements

## 📞 Support

Untuk bantuan dan pertanyaan:
1. **Issues**: [GitHub Issues]https://github.com/orang2bejo/AI_Agents
2. **Discussions**: [GitHub Discussions]https://github.com/orang2bejo/AI_Agents
3. **Email**: lagibejo5@gmail.com
4. **Documentation**: Lihat folder `docs/` untuk panduan lengkap

---

**Selamat menggunakan Jarvis AI! 🚀**

*"Your intelligent Windows desktop companion, powered by advanced AI."*
