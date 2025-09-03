# 🚀 Panduan Instalasi Jarvis AI

## Selamat Datang!

Panduan ini akan membantu Anda menginstal Jarvis AI dengan mudah dan cepat. Versi terbaru mendukung **15+ LLM providers**, **EVI (Empathic Voice Interface)**, dan **96+ optimized dependencies** untuk performa maksimal.

---

## 🆕 Fitur Terbaru (Januari 2025)

- **Multi-Provider LLM Support**: OpenRouter, Gemini, Anthropic, Groq, Ollama
- **EVI Integration**: Empathic Voice Interface dengan emotion detection
- **Optimized Dependencies**: 96 core packages, 99 development packages
- **Enhanced Voice Processing**: WebRTC VAD, Piper TTS
- **Modular Installation**: Install hanya komponen yang dibutuhkan
- **Auto-Configuration**: Deteksi hardware dan optimasi otomatis

---

## 📋 Daftar Isi

1. [Persiapan Sebelum Instalasi](#persiapan-sebelum-instalasi)
2. [Konfigurasi API Keys](#konfigurasi-api-keys)
3. [Metode 1: Instalasi Otomatis (Direkomendasikan)](#metode-1-instalasi-otomatis-direkomendasikan)
4. [Metode 2: Instalasi Semi-Otomatis](#metode-2-instalasi-semi-otomatis)
5. [Metode 3: Instalasi Manual Lengkap](#metode-3-instalasi-manual-lengkap)
6. [Konfigurasi LLM Providers](#konfigurasi-llm-providers)
7. [Verifikasi Instalasi](#verifikasi-instalasi)
8. [Mengatasi Masalah Instalasi](#mengatasi-masalah-instalasi)
9. [Uninstall (Hapus Instalasi)](#uninstall-hapus-instalasi)

---

## 🔍 Persiapan Sebelum Instalasi

### Periksa Persyaratan Sistem

**Sistem Operasi:**
- ✅ Windows 10 (versi 1903 atau lebih baru)
- ✅ Windows 11 (semua versi)
- ❌ Windows 8.1 atau lebih lama (tidak didukung)

**Hardware Minimum:**
- **RAM:** 8 GB (16 GB direkomendasikan untuk multi-provider LLM)
- **Storage:** 5 GB ruang kosong (10 GB untuk full features + models)
- **Processor:** Intel Core i5 atau AMD Ryzen 5 (generasi 2018+)
- **GPU:** 
  - **CPU-only mode:** Integrated graphics sufficient
  - **GPU acceleration:** NVIDIA GTX 1660+ atau AMD RX 6600+
  - **CUDA support:** NVIDIA GPU dengan CUDA 12.0+ untuk optimal ML performance
  - **Local LLM:** NVIDIA RTX 4060+ dengan 8GB+ VRAM untuk Ollama models
- **Audio:** Mikrofon dan speaker/headphone untuk EVI features
- **Network:** Broadband internet untuk cloud LLM providers

**Hardware Direkomendasikan untuk Performa Optimal:**
- **RAM:** 32 GB+ untuk large model processing dan multi-provider switching
- **Storage:** NVMe SSD dengan 20 GB+ ruang kosong
- **Processor:** Intel Core i7-12700K/AMD Ryzen 7 5800X atau lebih tinggi
- **GPU:** NVIDIA RTX 4070+ dengan 12GB+ VRAM untuk local LLM inference
- **Network:** Fiber internet (100+ Mbps) untuk real-time AI features

**Koneksi Internet:**
- Diperlukan untuk download dependencies (2-5 GB)
- Diperlukan untuk fitur AI online dan model updates
- Bandwidth minimum: 10 Mbps untuk real-time AI features

**Deteksi Hardware Otomatis:**
Jarvis AI akan secara otomatis mendeteksi:
- ✅ Ketersediaan GPU dan CUDA support
- ✅ Kapasitas RAM dan storage
- ✅ CPU cores dan performance capabilities
- ✅ Audio devices untuk voice features
- ⚙️ Optimasi konfigurasi berdasarkan hardware yang tersedia

### Persiapan Akun dan Izin

1. **Akun Administrator:**
   - Pastikan Anda memiliki akses administrator di Windows
   - Klik kanan pada Command Prompt → "Run as administrator"

2. **Antivirus/Windows Defender:**
   - Sementara disable real-time protection selama instalasi
   - Atau tambahkan folder Jarvis AI ke whitelist

3. **Firewall:**
   - Pastikan Python dan pip tidak diblokir firewall

---

## 🔑 Konfigurasi API Keys

> **PENTING:** Sebelum instalasi, siapkan API keys untuk LLM providers yang ingin Anda gunakan.

### Pilihan LLM Providers

**Gratis/Local (Direkomendasikan untuk pemula):**
- **Ollama** - Local LLM, tidak perlu API key
- **Groq** - Free tier dengan rate limit
- **Google Gemini** - Free tier tersedia

**Berbayar (Untuk penggunaan intensif):**
- **OpenRouter** - Akses 100+ model dengan satu API key
- **OpenAI** - GPT-4o, GPT-4o-mini
- **Anthropic** - Claude-3.5-Sonnet, Claude-3.5-Haiku

### Cara Mendapatkan API Keys

#### 1. OpenRouter (Direkomendasikan)
```
1. Kunjungi: https://openrouter.ai/
2. Daftar akun baru
3. Masuk ke dashboard
4. Klik "API Keys" → "Create Key"
5. Copy API key (format: sk-or-v1-...)
```

#### 2. Google Gemini
```
1. Kunjungi: https://makersuite.google.com/app/apikey
2. Login dengan Google account
3. Klik "Create API Key"
4. Copy API key
```

#### 3. Groq
```
1. Kunjungi: https://console.groq.com/
2. Daftar akun baru
3. Masuk ke "API Keys"
4. Klik "Create API Key"
5. Copy API key
```

#### 4. Anthropic Claude
```
1. Kunjungi: https://console.anthropic.com/
2. Daftar akun dan verifikasi
3. Masuk ke "API Keys"
4. Klik "Create Key"
5. Copy API key
```

### Setup File .env

1. **Copy template:**
   ```cmd
   copy config\.env-example .env
   ```

2. **Edit file .env:**
   ```bash
   # LLM Providers (pilih minimal satu)
   OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
   GOOGLE_API_KEY=your-gemini-api-key
   GROQ_API_KEY=your-groq-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   
   # Voice Services (opsional)
   ELEVENLABS_API_KEY=your-elevenlabs-key
   AZURE_SPEECH_KEY=your-azure-speech-key
   
   # Search Services (opsional)
   GOOGLE_SEARCH_API_KEY=your-google-search-key
   BING_SEARCH_API_KEY=your-bing-search-key
   ```

3. **Simpan file** dan lanjutkan ke instalasi

> **Tips:** Anda bisa menambahkan API keys setelah instalasi jika belum siap.

---

## 🎯 Metode 1: Instalasi Otomatis (Direkomendasikan)

> **Cocok untuk:** Pengguna pemula yang ingin instalasi cepat dan mudah

### Langkah 1: Lokasi File Installer

1. **File installer tersedia di:**
   - File `install_jarvis_auto.bat` sudah tersedia di folder root proyek
   - Lokasi: `windows_use_autonomous_agent\install_jarvis_auto.bat`

2. **Cara mengakses:**
   - Buka folder proyek Jarvis AI
   - Cari file `install_jarvis_auto.bat` di folder utama
   - File ini akan menginstall semua dependencies secara otomatis

### Langkah 2: Jalankan Installer

1. **Klik kanan** pada file `install_jarvis_auto.bat`
2. Pilih **"Run as administrator"**
3. Jika muncul peringatan Windows Defender:
   - Klik **"More info"**
   - Klik **"Run anyway"**

### Langkah 3: Ikuti Wizard Instalasi

```
=== JARVIS AI INSTALLER ===

[1] Pilih bahasa instalasi:
    1. Bahasa Indonesia
    2. English
    
Pilihan Anda: 1

[2] Pilih lokasi instalasi:
    Default: C:\Program Files\Jarvis AI
    Custom: [Ketik path baru atau tekan Enter]
    
Lokasi: [Enter untuk default]

[3] Komponen yang akan diinstall:
    ✅ Python 3.11 (jika belum ada)
    ✅ Jarvis AI Core
    ✅ Voice Recognition
    ✅ Office Integration
    ✅ Dependencies
    
Lanjutkan? (Y/n): Y
```

### Langkah 4: Proses Instalasi

**Tahap 1: Deteksi Sistem (1-2 menit)**
```
[INFO] Memeriksa sistem operasi... ✅ Windows 11
[INFO] Memeriksa Python... ❌ Tidak ditemukan
[INFO] Memeriksa Git... ✅ Ditemukan
[INFO] Memeriksa ruang disk... ✅ 15 GB tersedia
```

**Tahap 2: Install Python (3-5 menit)**
```
[INFO] Downloading Python 3.11.7...
[████████████████████████████████] 100%
[INFO] Installing Python...
[INFO] Menambahkan Python ke PATH...
[INFO] Python berhasil diinstall ✅
```

**Tahap 3: Download Jarvis AI (2-3 menit)**
```
[INFO] Cloning Jarvis AI repository...
[INFO] Extracting files...
[INFO] Setting up project structure...
```

**Tahap 4: Install Dependencies (5-10 menit)**
```
[INFO] Installing core dependencies...
[████████████████████████████████] 100%
[INFO] Installing voice recognition...
[████████████████████████████████] 100%
[INFO] Installing office integration...
[████████████████████████████████] 100%
```

**Tahap 5: Konfigurasi (1-2 menit)**
```
[INFO] Creating configuration files...
[INFO] Setting up environment variables...
[INFO] Creating desktop shortcuts...
[INFO] Registering file associations...
```

### Langkah 5: Selesai!

```
🎉 INSTALASI BERHASIL! 🎉

Jarvis AI telah terinstall di:
C:\Program Files\Jarvis AI

Cara menjalankan:
1. Klik shortcut "Jarvis AI" di desktop
2. Atau buka Command Prompt dan ketik: jarvis

Tekan Enter untuk melanjutkan ke setup awal...
```

---

## ⚙️ Metode 2: Instalasi Semi-Otomatis

> **Cocok untuk:** Pengguna yang ingin kontrol lebih dalam proses instalasi

### Langkah 1: Install Python Manual

1. **Download Python:**
   - Kunjungi [python.org/downloads](https://python.org/downloads)
   - Download Python 3.8+ (direkomendasikan 3.11)

2. **Install Python:**
   - Jalankan installer
   - ⚠️ **PENTING:** Centang "Add Python to PATH"
   - Pilih "Install Now"
   - Tunggu hingga selesai

3. **Verifikasi Python:**
   ```cmd
   python --version
   pip --version
   ```

### Langkah 2: Download Jarvis AI

**Opsi A: Download ZIP**
1. Download repository sebagai ZIP
2. Extract ke folder pilihan (contoh: `D:\Jarvis AI`)

**Opsi B: Git Clone**
```cmd
git clone https://github.com/your-repo/jarvis-ai.git
cd jarvis-ai
```

### Langkah 3: Jalankan Setup Semi-Otomatis

1. **Buka Command Prompt sebagai Administrator**
2. **Navigasi ke folder Jarvis AI:**
   ```cmd
   cd "D:\Jarvis AI\advanced_ai_agents\windows_use_autonomous_agent"
   ```

3. **Jalankan setup script:**
   ```cmd
   python setup_semi_auto.py
   ```

4. **Ikuti prompt interaktif:**
   ```
   === JARVIS AI SEMI-AUTO SETUP ===
   
   [1] Install dependencies? (Y/n): Y
   [2] Setup voice recognition? (Y/n): Y
   [3] Configure Office integration? (Y/n): Y
   [4] Create shortcuts? (Y/n): Y
   [5] Setup environment variables? (Y/n): Y
   ```

---

## 🔧 Metode 3: Instalasi Manual Lengkap

> **Cocok untuk:** Developer atau pengguna advanced yang ingin kontrol penuh

### Langkah 1: Persiapan Environment

1. **Install Python 3.8+:**
   - Download dari python.org
   - Pastikan pip terinstall
   - Tambahkan ke PATH

2. **Install Git (opsional):**
   - Download dari git-scm.com
   - Untuk clone repository

3. **Install Visual C++ Redistributable:**
   - Download dari Microsoft
   - Diperlukan untuk beberapa dependencies

### Langkah 2: Setup Project

1. **Buat folder proyek:**
   ```cmd
   mkdir "C:\Jarvis AI"
   cd "C:\Jarvis AI"
   ```

2. **Download source code:**
   ```cmd
   git clone https://github.com/your-repo/jarvis-ai.git .
   ```
   
   Atau extract ZIP ke folder ini.

3. **Navigasi ke folder utama:**
   ```cmd
   cd advanced_ai_agents\windows_use_autonomous_agent
   ```

### Langkah 3: Setup Virtual Environment (Direkomendasikan)

1. **Buat virtual environment:**
   ```cmd
   python -m venv jarvis_env
   ```

2. **Aktivasi virtual environment:**
   ```cmd
   jarvis_env\Scripts\activate
   ```

3. **Upgrade pip:**
   ```cmd
   python -m pip install --upgrade pip
   ```

### Langkah 4: Install Dependencies

1. **Install core dependencies (WAJIB):**
   ```cmd
   pip install -r requirements.txt
   ```
   
   **Dependencies yang terinstall:**
   - AI & LLM: `langchain`, `pydantic`
   - Data Processing: `numpy`, `scikit-learn`
   - Web & HTTP: `requests`, `beautifulsoup4`, `aiohttp`
   - Desktop Automation: `uiautomation`, `pyautogui`, `humancursor`
   - Voice Processing: `sounddevice`, `websockets`, `webrtcvad`
   - System: `psutil`, `termcolor`

2. **Install development dependencies (OPSIONAL):**
   ```cmd
   pip install -r requirements-dev.txt
   ```
   
   **Dependencies yang terinstall:**
   - Testing: `pytest`, `pytest-cov`, `pytest-asyncio`
   - Code Quality: `black`, `flake8`, `mypy`, `pylint`
   - Documentation: `sphinx`, `mkdocs`
   - Optional Features: `openai`, `selenium`, `torch`, `pandas`

3. **Verifikasi instalasi:**
   ```cmd
   pip list | findstr langchain
   pip list | findstr numpy
   pip list | findstr requests
   ```

3. **Install development tools (opsional):**
   ```cmd
   pip install pytest black flake8
   ```

### Langkah 5: Konfigurasi Manual

1. **Buat file environment:**
   ```cmd
   copy .env-example .env
   ```

2. **Edit file .env:**
   ```ini
   # Basic Configuration
   DEFAULT_LANGUAGE=id
   DEBUG_MODE=false
   
   # Voice Settings
   VOICE_ENABLED=true
   TTS_ENABLED=true
   VOICE_LANGUAGE=id-ID
   
   # API Keys (optional)
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   
   # Office Integration
   OFFICE_ENABLED=true
   OFFICE_SAFE_MODE=true
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=jarvis_ai.log
   ```

3. **Setup folder struktur:**
   ```cmd
   mkdir logs
   mkdir models
   mkdir learning_data
   mkdir temp
   ```

### Langkah 6: Download Model Files (Opsional)

1. **Voice recognition models:**
   ```cmd
   python -c "import speech_recognition as sr; sr.Microphone.list_microphone_names()"
   ```

2. **TTS models:**
   ```cmd
   # Download Piper TTS models
   mkdir models\tts
   # Manual download dari Piper repository
   ```

---

## ⚙️ Konfigurasi LLM Providers

> **Setelah instalasi selesai**, konfigurasikan LLM providers sesuai kebutuhan Anda.

### Edit Konfigurasi LLM

1. **Buka file konfigurasi:**
   ```cmd
   notepad config\llm_config.yaml
   ```

2. **Konfigurasi providers:**
   ```yaml
   providers:
     # Local LLM (tidak perlu API key)
     ollama:
       enabled: true
       priority: 1
       base_url: "http://localhost:11434"
       models: ["llama3.2:3b", "qwen2.5:7b", "gemma2:9b"]
       timeout: 30
       max_retries: 3
   
     # Cloud LLM dengan API keys
     openrouter:
       enabled: true
       priority: 2
       models: ["openai/gpt-4o", "anthropic/claude-3-5-sonnet"]
       timeout: 30
       max_retries: 3
   
     gemini:
       enabled: true
       priority: 3
       models: ["gemini-1.5-pro", "gemini-1.5-flash"]
       timeout: 30
       max_retries: 3
   
     groq:
       enabled: true
       priority: 4
       models: ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
       timeout: 15
       max_retries: 2
   
     anthropic:
       enabled: false  # Set true jika punya API key
       priority: 5
       models: ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
       timeout: 30
       max_retries: 3
   ```

### Setup Ollama (Local LLM)

**Jika ingin menggunakan local LLM:**

1. **Install Ollama:**
   ```cmd
   # Download dari https://ollama.ai/
   # Atau gunakan winget:
   winget install Ollama.Ollama
   ```

2. **Download model:**
   ```cmd
   ollama pull llama3.2:3b
   ollama pull qwen2.5:7b
   ```

3. **Test Ollama:**
   ```cmd
   ollama run llama3.2:3b
   # Ketik pesan test, lalu exit dengan /bye
   ```

### Prioritas Provider

**Cara kerja prioritas:**
- Priority 1 = Dicoba pertama
- Jika gagal, lanjut ke priority 2, dst.
- Provider dengan `enabled: false` akan dilewati

**Rekomendasi prioritas:**
1. **Ollama** (gratis, cepat, offline)
2. **OpenRouter** (banyak pilihan model)
3. **Gemini** (gratis tier bagus)
4. **Groq** (sangat cepat)
5. **Anthropic** (kualitas tinggi)

### Test Konfigurasi

```cmd
# Test koneksi ke semua providers
python test_llm_providers.py

# Test provider specific
python -c "from jarvis_ai.llm import test_provider; test_provider('ollama')"
```

---

## ✅ Verifikasi Instalasi

### Quick System Check
```cmd
# Run system diagnostic
python test_installation.py --full-check
```

### Hardware Verification
```cmd
# Check GPU availability
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU Count:', torch.cuda.device_count())"

# Check system resources
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().total//1024**3}GB'); print(f'CPU Cores: {psutil.cpu_count()}')"

# Check audio devices
python -c "import sounddevice as sd; print('Audio Devices:'); print(sd.query_devices())"
```

### Test Dasar

1. **Test Python dan dependencies:**
   ```cmd
   python -c "import jarvis_ai; print('Jarvis AI imported successfully')"
   ```

2. **Test integration:**
   ```cmd
   python test_integration.py
   ```

3. **Test voice (jika enabled):**
   ```cmd
   python -c "from jarvis_ai.voice_interface import VoiceInterface; vi = VoiceInterface(); print('Voice OK')"
   ```

### Test Fungsional

1. **Jalankan Jarvis AI:**
   ```cmd
   python windows_use\jarvis_main.py
   ```

2. **Test perintah sederhana:**
   ```
   > help
   > version
   > status
   ```

3. **Test voice (jika ada mikrofon):**
   - Tekan Space
   - Ucapkan "Hello Jarvis"
   - Lepas Space

### Expected Output

```
2024-01-20 10:30:15,123 - JarvisAI - INFO - Jarvis AI Main Controller initialized
2024-01-20 10:30:15,124 - JarvisAI - INFO - Initializing Jarvis AI System...
2024-01-20 10:30:15,125 - jarvis_ai.personality - INFO - Jarvis personality engine initialized
2024-01-20 10:30:15,126 - jarvis_ai.conversation - INFO - Conversation manager initialized
2024-01-20 10:30:15,127 - jarvis_ai.voice_interface - INFO - Voice interface initialized
2024-01-20 10:30:15,128 - jarvis_ai.task_coordinator - INFO - Task Coordinator initialized
2024-01-20 10:30:15,129 - jarvis_ai.learning_engine - INFO - Learning Engine initialized

🤖 Jarvis AI siap digunakan!
Ketik 'help' untuk melihat perintah yang tersedia.

jarvis> 
```

---

## ⚙️ Konfigurasi Awal

### Setup Wizard Pertama Kali

Setelah instalasi berhasil, jalankan setup wizard:

```cmd
python setup_wizard.py
```

### Langkah-langkah Setup:

**1. Pilih Bahasa:**
```
=== JARVIS AI SETUP WIZARD ===

Pilih bahasa default:
1. Bahasa Indonesia
2. English
3. Bilingual (ID + EN)

Pilihan: 1
```

**2. Konfigurasi Suara:**
```
Setup Voice Recognition:

[1] Test mikrofon...
    Silakan bicara: "Testing mikrofon satu dua tiga"
    ✅ Mikrofon terdeteksi dengan baik

[2] Rekam suara admin untuk keamanan...
    Ucapkan: "Saya adalah admin Jarvis AI"
    ✅ Voice signature tersimpan

[3] Test Text-to-Speech...
    🔊 "Halo, saya Jarvis AI. Setup berhasil!"
    ✅ TTS berfungsi normal
```

**3. Konfigurasi Office:**
```
Setup Microsoft Office Integration:

[1] Deteksi Office installation...
    ✅ Microsoft Office 2021 ditemukan
    ✅ Excel, Word, PowerPoint tersedia

[2] Test Office automation...
    ✅ COM interface berfungsi
    ✅ Siap untuk otomatisasi Office
```

**4. Konfigurasi API (Opsional):**
```
Setup AI API Keys (opsional):

[1] OpenAI API Key:
    Masukkan key (atau Enter untuk skip): [Enter]
    ⚠️ Dilewati - akan menggunakan AI lokal

[2] Anthropic API Key:
    Masukkan key (atau Enter untuk skip): [Enter]
    ⚠️ Dilewati - akan menggunakan AI lokal
```

**5. Selesai:**
```
🎉 SETUP SELESAI! 🎉

Konfigurasi tersimpan di: .env
Log file: jarvis_ai.log

Cara menjalankan:
- Mode GUI: python gui\main_window.py
- Mode CLI: python windows_use\jarvis_main.py
- Mode Voice: python voice_mode.py

Tekan Enter untuk melanjutkan...
```

---

## 🔧 Mengatasi Masalah Instalasi

### Masalah Umum dan Solusi

#### 1. Python Tidak Ditemukan

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solusi:**
1. **Reinstall Python dengan PATH:**
   - Download Python installer
   - ✅ Centang "Add Python to PATH"
   - Install ulang

2. **Manual add to PATH:**
   - Buka System Properties → Environment Variables
   - Edit PATH, tambahkan:
     - `C:\Python311`
     - `C:\Python311\Scripts`

3. **Restart Command Prompt** setelah perubahan PATH

#### 2. Pip Install Gagal

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solusi:**
1. **Jalankan sebagai Administrator:**
   ```cmd
   # Buka CMD as Administrator
   pip install -r requirements.txt
   ```

2. **Update pip:**
   ```cmd
   python -m pip install --upgrade pip
   ```

3. **Install satu per satu:**
   ```cmd
   pip install numpy
   pip install pandas
   pip install scikit-learn
   # dst...
   ```

4. **Gunakan cache offline:**
   ```cmd
   pip install --no-index --find-links ./wheels -r requirements.txt
   ```

#### 3. Mikrofon Tidak Terdeteksi

**Error:**
```
OSError: No Default Input Device Available
```

**Solusi:**
1. **Periksa Windows Settings:**
   - Settings → Privacy → Microphone
   - Allow apps to access microphone: ON

2. **Install audio drivers:**
   ```cmd
   # Install PyAudio dengan wheel
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Test mikrofon manual:**
   ```cmd
   python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
   ```

#### 4. Office COM Error

**Error:**
```
com_error: (-2147221164, 'Class not registered')
```

**Solusi:**
1. **Repair Office installation:**
   - Control Panel → Programs → Microsoft Office
   - Change → Quick Repair

2. **Register COM components:**
   ```cmd
   # Jalankan sebagai Administrator
   regsvr32 "C:\Program Files\Microsoft Office\root\vfs\ProgramFilesCommonX86\Microsoft Shared\VBA\VBA7\VBE7.DLL"
   ```

3. **Install pywin32 post-install:**
   ```cmd
   python Scripts/pywin32_postinstall.py -install
   ```

#### 5. GPU/CUDA Issues

**Gejala:**
- "CUDA not available" warning
- Slow AI processing performance
- GPU not detected errors
- Memory allocation errors

**Solusi:**
1. **Periksa GPU compatibility:**
   ```cmd
   # Check GPU info
   nvidia-smi
   # Or check in Device Manager
   ```

2. **Install CUDA Toolkit (untuk NVIDIA GPU):**
   - Download dari [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
   - Install CUDA 11.8 atau 12.x
   - Restart komputer setelah instalasi

3. **Install GPU-specific dependencies:**
   ```cmd
   # For NVIDIA GPU
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # For AMD GPU (ROCm)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
   
   # For CPU-only (fallback)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

4. **Verify GPU detection:**
   ```cmd
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"
   ```

5. **GPU Memory issues:**
   - Tutup aplikasi lain yang menggunakan GPU
   - Kurangi batch size dalam konfigurasi
   - Enable memory optimization dalam settings

#### 6. CPU Performance Issues

**Gejala:**
- Proses AI sangat lambat
- High CPU usage (>90%)
- System freezing during AI tasks

**Solusi:**
1. **Optimize CPU usage:**
   ```cmd
   # Set CPU affinity untuk Jarvis AI
   # Dalam Task Manager → Details → Set Affinity
   ```

2. **Enable multiprocessing:**
   - Edit `config/jarvis_config.json`
   - Set `"cpu_cores": "auto"` atau specify number
   - Set `"enable_multiprocessing": true`

3. **Memory optimization:**
   ```cmd
   # Increase virtual memory
   # System Properties → Advanced → Performance → Settings → Advanced → Virtual Memory
   ```

4. **Background processes:**
   - Tutup aplikasi tidak perlu
   - Disable startup programs
   - Check for malware/virus

#### 7. Audio/Voice Issues

**Gejala:**
- Microphone tidak terdeteksi
- Audio output tidak berfungsi
- Voice recognition errors

**Solusi:**
1. **Check audio devices:**
   ```cmd
   # Test audio devices
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

2. **Install audio dependencies:**
   ```cmd
   pip install sounddevice pyaudio whisper
   # For Windows, might need:
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Audio driver issues:**
   - Update audio drivers
   - Check Windows Sound settings
   - Test with different audio devices

#### 8. Antivirus Blocking

**Gejala:**
- File hilang setelah download
- Installer tidak bisa dijalankan
- Python script di-quarantine

**Solusi:**
1. **Tambahkan ke whitelist:**
   - Folder Jarvis AI
   - Python.exe
   - pip.exe

2. **Disable real-time protection sementara:**
   - Hanya selama instalasi
   - Aktifkan kembali setelah selesai

3. **Gunakan Windows Defender exclusion:**
   - Windows Security → Virus & threat protection
   - Add exclusion → Folder
   - Pilih folder Jarvis AI

### Instalasi Ulang Bersih

Jika semua solusi gagal:

1. **Uninstall semua komponen:**
   ```cmd
   pip uninstall -r requirements.txt -y
   rmdir /s "C:\Jarvis AI"
   ```

2. **Bersihkan registry (opsional):**
   - Gunakan CCleaner atau tool serupa
   - Bersihkan Python dan Office entries

3. **Restart komputer**

4. **Install ulang dari awal:**
   - Ikuti Metode 1 (Instalasi Otomatis)
   - Atau Metode 3 (Manual) untuk kontrol lebih

---

## 🗑️ Uninstall (Hapus Instalasi)

### Uninstall Otomatis

1. **Jalankan uninstaller:**
   ```cmd
   python uninstall.py
   ```

2. **Pilih komponen yang akan dihapus:**
   ```
   === JARVIS AI UNINSTALLER ===
   
   Pilih yang akan dihapus:
   [✓] Jarvis AI Core
   [✓] Configuration files
   [✓] Learning data
   [✓] Log files
   [ ] Python (keep for other apps)
   [✓] Desktop shortcuts
   
   Lanjutkan? (y/N): y
   ```

### Uninstall Manual

1. **Hapus virtual environment:**
   ```cmd
   rmdir /s jarvis_env
   ```

2. **Hapus folder proyek:**
   ```cmd
   rmdir /s "C:\Jarvis AI"
   ```

3. **Hapus shortcuts:**
   - Desktop: `Jarvis AI.lnk`
   - Start Menu: `Jarvis AI` folder

4. **Bersihkan environment variables:**
   - Hapus JARVIS_HOME dari PATH
   - Hapus JARVIS_CONFIG_PATH

5. **Hapus registry entries (opsional):**
   ```cmd
   reg delete "HKCU\Software\Jarvis AI" /f
   ```

---

## 📞 Bantuan Lebih Lanjut

### Jika Masih Bermasalah

1. **Periksa log file:**
   ```
   jarvis_ai.log
   installation.log
   ```

2. **Jalankan diagnostic:**
   ```cmd
   python diagnostic.py
   ```

3. **Hubungi support:**
   - Email: support@jarvis-ai.com
   - GitHub Issues: [Repository Link]
   - Discord: [Server Link]

### Informasi untuk Support

Sertakan informasi berikut:
- Versi Windows
- Versi Python
- Log file error
- Langkah yang sudah dicoba
- Spesifikasi hardware

---

**Selamat! Jarvis AI siap digunakan! 🎉**

*Lanjutkan ke [PANDUAN_PENGGUNA.md](PANDUAN_PENGGUNA.md) untuk mempelajari cara menggunakan Jarvis AI.*