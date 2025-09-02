# 🚀 Panduan Instalasi Jarvis AI

## Selamat Datang!

Panduan ini akan membantu Anda menginstal Jarvis AI dengan mudah dan cepat. Kami menyediakan beberapa metode instalasi untuk memastikan Anda dapat menjalankan Jarvis AI di sistem Anda.

---

## 📋 Daftar Isi

1. [Persiapan Sebelum Instalasi](#persiapan-sebelum-instalasi)
2. [Metode 1: Instalasi Otomatis (Direkomendasikan)](#metode-1-instalasi-otomatis-direkomendasikan)
3. [Metode 2: Instalasi Semi-Otomatis](#metode-2-instalasi-semi-otomatis)
4. [Metode 3: Instalasi Manual Lengkap](#metode-3-instalasi-manual-lengkap)
5. [Verifikasi Instalasi](#verifikasi-instalasi)
6. [Konfigurasi Awal](#konfigurasi-awal)
7. [Mengatasi Masalah Instalasi](#mengatasi-masalah-instalasi)
8. [Uninstall (Hapus Instalasi)](#uninstall-hapus-instalasi)

---

## 🔍 Persiapan Sebelum Instalasi

### Periksa Persyaratan Sistem

**Sistem Operasi:**
- ✅ Windows 10 (versi 1903 atau lebih baru)
- ✅ Windows 11 (semua versi)
- ❌ Windows 8.1 atau lebih lama (tidak didukung)

**Hardware Minimum:**
- **RAM:** 4 GB (8 GB direkomendasikan)
- **Storage:** 3 GB ruang kosong
- **Processor:** Intel Core i3 atau AMD Ryzen 3 (generasi 2017+)
- **Mikrofon:** Untuk fitur voice control
- **Speaker/Headphone:** Untuk feedback audio

**Koneksi Internet:**
- Diperlukan untuk download dependencies
- Diperlukan untuk fitur AI online (opsional)

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

## ✅ Verifikasi Instalasi

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

#### 5. Antivirus Blocking

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