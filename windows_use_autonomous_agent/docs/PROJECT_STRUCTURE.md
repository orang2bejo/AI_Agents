# Struktur Proyek Windows Use Autonomous Agent

## Gambaran Umum
Proyek ini adalah sistem AI otonom yang dirancang untuk Windows dengan kemampuan desktop automation, web scraping, dan integrasi LLM. Struktur folder telah diorganisir berdasarkan fungsi dan kategori untuk memudahkan navigasi dan pemeliharaan.

## Struktur Direktori

### 📁 Root Directory
```
windows_use_autonomous_agent/
├── config/           # File konfigurasi
├── data/            # Data dan log
├── docs/            # Dokumentasi
├── examples/        # Contoh penggunaan
├── scripts/         # Script utama
├── tests/           # File testing
├── venv/            # Virtual environment
├── windows_use/     # Package utama
└── windows_use.egg-info/  # Package info
```

### 📁 config/
Berisi semua file konfigurasi sistem:
- `.env` - Environment variables
- `.env-example` - Template environment variables
- `jarvis_config.json` - Konfigurasi Jarvis AI
- `llm_config.yaml` - Konfigurasi LLM providers

### 📁 data/
Berisi data aplikasi dan log:
- `jarvis_ai.log` - Log file sistem
- `learning_data/` - Data pembelajaran AI
- `models/` - Model AI yang disimpan

### 📁 docs/
Berisi semua dokumentasi proyek:
- `JARVIS_README.md` - Dokumentasi khusus Jarvis AI
- `PANDUAN_INSTALASI.md` - Panduan instalasi
- `PANDUAN_PENGGUNA.md` - Panduan penggunaan
- `PANDUAN_UPGRADE_PYTHON.md` - Panduan upgrade Python
- `PROJECT_STRUCTURE.md` - Dokumentasi struktur proyek (file ini)
- `readme.md` - README utama proyek
- `SECURITY_EVOLUTION.md` - Dokumentasi keamanan dan evolusi

### 📁 examples/
Berisi contoh penggunaan dan demo script:
- `complete_demo.py` - Demo lengkap fitur
- `llm_demo.py` - Demo LLM integration

### 📁 scripts/
Berisi script utama untuk menjalankan sistem:
- `jarvis_main.py` - Script utama Jarvis AI

### 📁 tests/
Berisi file testing:
- `test_integration.py` - Test integrasi
- `test_python312_upgrade.py` - Test upgrade Python 3.12

### 📁 windows_use/
Package utama dengan struktur modular:

#### 🤖 agent/
Sistem agent AI:
- `service.py` - Service layer agent
- `utils.py` - Utility functions
- `views.py` - View layer
- `prompt/` - Template prompt
- `registry/` - Registry agent
- `tools/` - Tools agent

#### 🖥️ desktop/
Desktop automation:
- `config.py` - Konfigurasi desktop
- `views.py` - Desktop views

#### 🧬 evolution/
Sistem evolusi AI:
- `config.py` - Konfigurasi evolusi
- `engine.py` - Engine evolusi
- `evaluator.py` - Evaluator performa
- `evolution_engine.py` - Engine evolusi utama
- `memory.py` - Sistem memori
- `mutator.py` - Mutator algoritma
- `reflector.py` - Reflector sistem

#### 🤖 jarvis_ai/
Sistem Jarvis AI:
- `agent_manager.py` - Manager agent
- `conversation.py` - Sistem percakapan
- `dashboard.py` - Dashboard GUI
- `language_manager.py` - Manager bahasa
- `learning_engine.py` - Engine pembelajaran
- `personality.py` - Sistem kepribadian
- `task_coordinator.py` - Koordinator tugas
- `voice_interface.py` - Interface suara

#### 🧠 llm/
Integrasi Large Language Model:
- `base.py` - Base class LLM
- `llm_provider.py` - Provider LLM
- `manager.py` - Manager LLM
- `model_registry.py` - Registry model
- `registry.py` - Registry umum
- `router.py` - Router LLM
- `adapters/` - Adapter berbagai LLM

#### 🗣️ nlu/
Natural Language Understanding:
- `grammar_id.py` - Grammar Indonesia
- `router.py` - Router NLU

#### 📊 observability/
Monitoring dan observability:
- `logger.py` - Sistem logging
- `screenshot.py` - Screenshot utility

#### 📄 office/
Integrasi Microsoft Office:
- `excel_handler.py` - Handler Excel
- `powerpoint_handler.py` - Handler PowerPoint
- `word_handler.py` - Handler Word

#### 🔒 security/
Sistem keamanan:
- `guardrails.py` - Guardrails keamanan
- `hitl.py` - Human-in-the-loop
- `voice_authentication.py` - Autentikasi suara

#### 🛠️ tools/
Tools dan utilities:
- `net.py` - Network tools
- `process.py` - Process management
- `ps_shell.py` - PowerShell integration
- `tts_piper.py` - Text-to-speech
- `voice_input.py` - Voice input
- `winget.py` - Windows Package Manager

#### 🌳 tree/
Sistem tree structure:
- `config.py` - Konfigurasi tree
- `views.py` - Tree views

#### 🌐 web/
Web automation dan scraping:
- `browser_automation.py` - Automasi browser
- `html_parser.py` - Parser HTML
- `search_engine.py` - Search engine
- `voice_web_control.py` - Kontrol web dengan suara
- `web_form_automation.py` - Automasi form web
- `web_scraper.py` - Web scraper

## File Konfigurasi Utama

### pyproject.toml
Konfigurasi build dan metadata proyek.

### requirements.txt
Daftar dependensi Python yang diperlukan.

### requirements_backup.txt
Backup daftar dependensi.

### uv.lock
Lock file untuk uv package manager.

### MANIFEST.in
Manifest file untuk packaging.

## Cara Menjalankan

1. **Setup Environment:**
   ```bash
   cd windows_use_autonomous_agent
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Konfigurasi:**
   - Copy `config/.env-example` ke `config/.env`
   - Sesuaikan konfigurasi di `config/jarvis_config.json`
   - Atur LLM provider di `config/llm_config.yaml`

3. **Menjalankan Sistem:**
   ```bash
   # Menjalankan Jarvis AI dengan GUI
   python scripts/jarvis_main.py
   
   # Menjalankan tanpa GUI
   python scripts/jarvis_main.py --no-gui
   
   # Menjalankan tanpa voice
   python scripts/jarvis_main.py --no-voice
   

   ```

4. **Testing:**
   ```bash
   python tests/test_integration.py
   python tests/test_python312_upgrade.py
   ```

## Prinsip Organisasi

1. **Separation of Concerns:** Setiap modul memiliki tanggung jawab yang jelas
2. **Modular Design:** Komponen dapat digunakan secara independen
3. **Configuration Management:** Semua konfigurasi terpusat di folder `config/`
4. **Data Isolation:** Data dan log terpisah di folder `data/`
5. **Documentation First:** Dokumentasi lengkap di folder `docs/`
6. **Testing Support:** Testing terorganisir di folder `tests/`
7. **Script Organization:** Script utama terpisah di folder `scripts/`

## Kontribusi

Untuk berkontribusi pada proyek ini:
1. Fork repository
2. Buat branch fitur baru
3. Ikuti struktur folder yang ada
4. Tambahkan dokumentasi untuk fitur baru
5. Buat pull request

## Author

**Orangbejo**
- GitHub: [github.com/orangbejo](https://github.com/orangbejo)
- Trae AI: [trae.ai](https://trae.ai)

---

*Dokumentasi ini dibuat untuk memudahkan navigasi dan pemeliharaan proyek Windows Use Autonomous Agent.*