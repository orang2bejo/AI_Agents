# 🤖 Jarvis AI - Advanced Windows Autonomous Agent

**Sistem AI Assistant Canggih dengan Interface Suara, Manajemen Tugas, dan Kemampuan Pembelajaran**

---

## 🌟 Gambaran Umum

Jarvis AI adalah sistem kecerdasan buatan komprehensif yang terinspirasi dari asisten AI fiksi Iron Man. Sistem ini menyediakan pengalaman asisten AI lengkap dengan interaksi suara, manajemen tugas cerdas, pembelajaran adaptif, dan interface dashboard yang intuitif.

### ✨ Fitur Utama

- **🎤 Interface Suara**: Kemampuan speech-to-text dan text-to-speech canggih
- **🧠 Kepribadian Cerdas**: Kepribadian adaptif dengan respons kontekstual
- **💬 Manajemen Percakapan**: Dialog sadar konteks dengan memori
- **🌐 Dukungan Dual Bahasa**: Dukungan bahasa Inggris dan Indonesia
- **📋 Koordinasi Tugas**: Penjadwalan dan eksekusi tugas cerdas
- **🎯 Mesin Pembelajaran**: Pembelajaran adaptif dari interaksi pengguna
- **📊 Interface Dashboard**: Panel monitoring dan kontrol real-time
- **🏢 Otomasi Office**: Integrasi dengan aplikasi Microsoft Office
- **🔧 Tools Sistem**: Kemampuan manajemen sistem Windows
- **🌍 Pencarian Web**: Pencarian web cerdas dan ekstraksi konten
- **🛡️ Keamanan**: Guardrails dan langkah-langkah keamanan built-in
- **🔄 Self-Evolution**: Peningkatan dan adaptasi berkelanjutan
- **🔐 Autentikasi Suara**: Sistem keamanan berbasis suara
- **🌐 Kontrol Web Suara**: Navigasi dan interaksi web dengan suara

---

## 🚀 Quick Start

### Prasyarat

- **Python 3.12+** (Direkomendasikan)
- **Windows 10/11** (untuk fungsionalitas penuh)
- **Microphone dan Speakers** (untuk fitur suara)
- **Microsoft Office** (opsional, untuk otomasi office)

### Instalasi

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd windows_use_autonomous_agent
   ```

2. **Buat virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Konfigurasi environment**:
   ```bash
   copy .env-example .env
   # Edit .env dengan API keys Anda
   ```

5. **Jalankan sistem**:
   ```bash
   python main.py
   ```

---

## 📁 Struktur Proyek

```
windows_use_autonomous_agent/
├── main.py                    # Entry point utama
├── requirements.txt           # Dependencies Python
├── .env-example              # Template konfigurasi environment
├── jarvis_ai/                # Core AI modules
│   ├── personality.py        # Kepribadian AI dan generasi respons
│   ├── conversation.py       # Manajemen dialog dan konteks
│   ├── language_manager.py   # Dukungan multi-bahasa
│   ├── voice_interface.py    # Handling input/output suara
│   ├── task_coordinator.py   # Penjadwalan dan eksekusi tugas
│   ├── learning_engine.py    # Sistem pembelajaran adaptif
│   └── dashboard.py          # Interface dashboard GUI
├── windows_use/              # Extended functionality
│   ├── voice/                # Modul pemrosesan suara
│   ├── intent_parser/        # Natural language understanding
│   ├── office_automation/    # Integrasi Microsoft Office
│   ├── windows_system_tools/ # Tools manajemen sistem
│   ├── self_evolving_agent/  # Kemampuan self-improvement
│   ├── multi_provider_llm/   # Integrasi LLM
│   ├── guardrails/          # Keamanan dan safety
│   ├── security/            # Autentikasi dan keamanan
│   └── web/                 # Pencarian dan otomasi web
├── examples/                 # Contoh penggunaan
├── config/                   # File konfigurasi
├── learning_data/           # Data pembelajaran
└── models/                  # Model machine learning
```

---

## 🎯 Contoh Penggunaan

### Perintah Suara

```
# Perintah Bahasa Inggris
"Hello Jarvis"
"What can you do?"
"Execute a task for me"
"Remember that I like coffee"
"Search for Python tutorials"
"Open Excel and create a new spreadsheet"
"What's my system status?"

# Perintah Bahasa Indonesia
"Halo Jarvis"
"Apa yang bisa kamu lakukan?"
"Jalankan tugas untuk saya"
"Ingat bahwa saya suka kopi"
"Cari tutorial Python"
"Buka Excel dan buat spreadsheet baru"
"Bagaimana status sistem saya?"
```

### Interface Programming

```python
from jarvis_ai import (
    JarvisPersonality,
    ConversationManager,
    VoiceInterface,
    TaskCoordinator,
    LearningEngine
)

# Inisialisasi komponen
personality = JarvisPersonality()
conversation = ConversationManager()
voice = VoiceInterface()
tasks = TaskCoordinator()
learning = LearningEngine()

# Start sistem
voice.initialize()
tasks.start()
learning.start()

# Proses input pengguna
response = personality.generate_greeting(Language.ENGLISH, "user")
voice.speak(response, Language.ENGLISH)
```

---

## ⚙️ Konfigurasi

### File Konfigurasi

Sistem menggunakan `jarvis_config.json` untuk konfigurasi. Bagian utama meliputi:

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
# API Keys Opsional
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GROQ_API_KEY="your-groq-key"
export GOOGLE_API_KEY="your-google-key"

# Pengaturan Suara
export JARVIS_VOICE_ENGINE="whisper"
export JARVIS_TTS_ENGINE="piper"

# Pengaturan Sistem
export JARVIS_LOG_LEVEL="INFO"
export JARVIS_DATA_DIR="./data"
export DEVELOPMENT_MODE="false"
```

---

## 🎨 Interface Dashboard

Sistem Jarvis AI menyertakan dashboard komprehensif dengan:

- **📊 System Overview**: Metrik dan status real-time
- **🎤 Voice Visualizer**: Visualisasi input audio
- **💬 Chat Interface**: Interaksi berbasis teks
- **📝 Activity Logs**: Aktivitas sistem dan pengguna
- **📋 Task Manager**: Tugas aktif dan selesai
- **⚙️ Settings Panel**: Manajemen konfigurasi

### Fitur Dashboard

- **Dark/Light Themes**: Tampilan yang dapat disesuaikan
- **Real-time Updates**: Monitoring sistem live
- **Interactive Controls**: Interaksi sistem langsung
- **Performance Metrics**: CPU, memori, dan waktu respons
- **Voice Activity**: Visualisasi audio real-time

---

## 🧠 Pembelajaran dan Adaptasi

### Kemampuan Pembelajaran

- **User Preference Learning**: Beradaptasi dengan gaya komunikasi pengguna
- **Command Success Prediction**: Mempelajari perintah mana yang paling efektif
- **Response Optimization**: Meningkatkan kualitas respons dari waktu ke waktu
- **Behavioral Pattern Recognition**: Memahami kebiasaan pengguna
- **Context Awareness**: Belajar dari konteks percakapan

### Model Machine Learning

- **Intent Classification**: Naive Bayes classifier
- **Sentiment Analysis**: Logistic regression
- **User Clustering**: K-means clustering
- **Response Optimization**: Linear regression

---

## 🔧 Fitur Lanjutan

### Otomasi Office

```python
from windows_use.office_automation import OfficeAutomation

office = OfficeAutomation()

# Excel automation
office.excel.create_workbook()
office.excel.add_data([['Name', 'Age'], ['John', 25]])
office.excel.save_as('data.xlsx')

# Word automation
office.word.create_document()
office.word.add_text('Hello from Jarvis!')
office.word.save_as('document.docx')

# PowerPoint automation
office.powerpoint.create_presentation()
office.powerpoint.add_slide('Title Slide')
office.powerpoint.save_as('presentation.pptx')
```

### Tools Sistem Windows

```python
from windows_use.windows_system_tools import WindowsSystemTools

system = WindowsSystemTools()

# Informasi sistem
info = system.get_system_info()
print(f"OS: {info['os']}, CPU: {info['cpu']}")

# Manajemen proses
processes = system.list_processes()
system.kill_process('notepad.exe')

# Manajemen file
system.create_folder('C:/temp/jarvis')
system.copy_file('source.txt', 'destination.txt')
```

### Pencarian Web dan Otomasi

```python
from windows_use.web import SearchEngine, WebScraper

# Pencarian web
search = SearchEngine()
results = search.search('Python tutorials')

# Web scraping
scraper = WebScraper()
content = scraper.extract_content('https://example.com')
```

### Keamanan dan Autentikasi

```python
from windows_use.security import VoiceAuthentication

auth = VoiceAuthentication()

# Registrasi pengguna
auth.register_user('john_doe', voice_sample)

# Autentikasi
is_authenticated = auth.authenticate(voice_input)
```

---

## 🚨 Troubleshooting

### Masalah Umum

1. **Suara tidak berfungsi**:
   - Periksa izin microphone
   - Install dependencies audio: `pip install pyaudio`
   - Coba engine STT/TTS yang berbeda

2. **Dashboard tidak terbuka**:
   - Install tkinter: `pip install tk`
   - Jalankan dengan flag `--no-gui`
   - Periksa pengaturan display

3. **Otomasi office gagal**:
   - Install pywin32: `pip install pywin32`
   - Pastikan aplikasi Office terinstall
   - Jalankan sebagai administrator jika diperlukan

4. **Pencarian web tidak berfungsi**:
   - Periksa koneksi internet
   - Verifikasi API keys (jika menggunakan layanan berbayar)
   - Coba search engine yang berbeda

### Mode Debug

```bash
# Enable debug logging
python main.py --log-level DEBUG

# Periksa status sistem
python -c "from jarvis_ai import *; print('All modules imported successfully')"

# Test integrasi
python test_integration.py
```

---

## 🤝 Contributing

### Setup Development

1. **Fork repository**
2. **Buat feature branch**: `git checkout -b feature/new-feature`
3. **Install development dependencies**: `pip install -r requirements-dev.txt`
4. **Jalankan tests**: `pytest tests/`
5. **Submit pull request**

### Code Style

- Ikuti guidelines PEP 8
- Gunakan type hints jika memungkinkan
- Tambahkan docstrings ke semua fungsi
- Tulis unit tests untuk fitur baru

---

## 👨‍💻 Author

**Orangbejo**
- GitHub: [https://github.com/Orangbejo](https://github.com/Orangbejo)
- Trae URL: [https://trae.ai/@orangbejo](https://trae.ai/@orangbejo)

---

## 📄 License

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** untuk speech recognition
- **Piper TTS** untuk text-to-speech
- **scikit-learn** untuk machine learning
- **tkinter** untuk GUI framework
- **Microsoft** untuk Office automation APIs
- **Komunitas open-source** untuk berbagai library dan tools

---

## 📞 Support

Untuk support, pertanyaan, atau permintaan fitur:

- **Issues**: Buat issue di GitHub
- **Discussions**: Gunakan GitHub Discussions
- **Documentation**: Periksa halaman wiki
- **Examples**: Lihat direktori `examples/`

---

**🤖 "I am Jarvis, your AI assistant. How may I help you today?"**

---

## 📊 Status Proyek

- ✅ **Python 3.12 Support**: Fully supported
- ✅ **Core AI Modules**: Implemented
- ✅ **Voice Interface**: Functional
- ✅ **Dashboard**: Available
- ✅ **Office Automation**: Implemented
- ✅ **Web Integration**: Available
- ✅ **Security Features**: Implemented
- ✅ **Learning Engine**: Active
- ✅ **Multi-language**: Indonesian & English
- ✅ **Documentation**: Complete

**Last Updated**: January 2025
**Version**: 1.0.0
**Python Version**: 3.12.10