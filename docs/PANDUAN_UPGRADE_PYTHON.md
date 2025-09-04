# Panduan Upgrade Python dari 3.10 ke 3.12

## 📋 Persiapan Sebelum Upgrade

### 1. Backup Proyek
```bash
# Backup seluruh folder proyek
cp -r "d:\Project Jarvis" "d:\Project Jarvis_backup_$(date +%Y%m%d)"

# Atau menggunakan PowerShell
Copy-Item "d:\Project Jarvis" "d:\Project Jarvis_backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### 2. Cek Versi Python Saat Ini
```bash
python --version
python -c "import sys; print(sys.version)"
```

### 3. Export Dependencies
```bash
cd "d:\Project Jarvis\advanced_ai_agents\windows_use_autonomous_agent"
pip freeze > requirements_python310.txt
```

## 🔍 Cek Kompatibilitas

### Dependencies yang Perlu Diperiksa:
- **scikit-learn**: ✅ Kompatibel dengan Python 3.12
- **langchain**: ✅ Kompatibel dengan Python 3.12
- **pywin32**: ✅ Kompatibel dengan Python 3.12
- **whisper**: ✅ Kompatibel dengan Python 3.12
- **piper-tts**: ⚠️ Perlu verifikasi

## 📥 Download dan Install Python 3.12

### Opsi 1: Download dari Python.org (Direkomendasikan)

1. **Kunjungi situs resmi Python**
   - Buka: https://www.python.org/downloads/windows/
   - Pilih "Python 3.12.10" (versi stabil terakhir)

2. **Download Installer**
   - Pilih "Windows installer (64-bit)" untuk sistem 64-bit
   - Atau "Windows installer (32-bit)" untuk sistem 32-bit

3. **Jalankan Installer**
   ```
   ✅ Centang "Add Python 3.12 to PATH"
   ✅ Centang "Install for all users" (opsional)
   ✅ Pilih "Customize installation"
   ```

4. **Konfigurasi Advanced**
   ```
   ✅ Install for all users
   ✅ Associate files with Python
   ✅ Create shortcuts for installed applications
   ✅ Add Python to environment variables
   ✅ Precompile standard library
   ```

### Opsi 2: Microsoft Store

1. Buka Microsoft Store
2. Cari "Python 3.12"
3. Klik "Install"

### Opsi 3: Menggunakan Chocolatey

```powershell
# Install Chocolatey jika belum ada
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python 3.12
choco install python312
```

## ⚙️ Konfigurasi Setelah Instalasi

### 1. Verifikasi Instalasi
```bash
# Cek versi Python baru
python --version
# Harus menampilkan: Python 3.12.x

# Cek pip
pip --version
```

### 2. Update pip
```bash
python -m pip install --upgrade pip
```

### 3. Buat Virtual Environment Baru
```bash
cd "d:\Project Jarvis\advanced_ai_agents\windows_use_autonomous_agent"

# Hapus virtual environment lama (opsional)
rmdir /s venv

# Buat virtual environment baru dengan Python 3.12
python -m venv venv_py312

# Aktifkan virtual environment
venv_py312\Scripts\activate
```

### 4. Install Dependencies
```bash
# Install dari requirements.txt
pip install -r requirements.txt

# Atau install package secara editable
pip install -e .
```

## 🧪 Testing dan Verifikasi

### 1. Test Import Modules
```python
# Test script: test_python312.py
import sys
print(f"Python version: {sys.version}")

try:
    import jarvis_ai
    print("✅ jarvis_ai imported successfully")
except ImportError as e:
    print(f"❌ jarvis_ai import failed: {e}")

try:
    import sklearn
    print(f"✅ scikit-learn {sklearn.__version__} imported successfully")
except ImportError as e:
    print(f"❌ scikit-learn import failed: {e}")

try:
    import langchain
    print(f"✅ langchain imported successfully")
except ImportError as e:
    print(f"❌ langchain import failed: {e}")
```

### 2. Test Jarvis AI
```bash
# Test menjalankan Jarvis AI
python jarvis_main.py
```

## 🔧 Troubleshooting

### Masalah Umum dan Solusi

#### 1. Python 3.10 Masih Aktif
```bash
# Cek semua versi Python yang terinstall
where python

# Gunakan py launcher untuk memilih versi
py -3.12 --version
py -3.12 -m pip install -r requirements.txt
```

#### 2. PATH Environment Variable
```powershell
# Tambahkan Python 3.12 ke PATH secara manual
$env:PATH = "C:\Python312;C:\Python312\Scripts;" + $env:PATH

# Atau edit secara permanen melalui System Properties
```

#### 3. Dependencies Tidak Kompatibel
```bash
# Update semua packages ke versi terbaru
pip install --upgrade -r requirements.txt

# Atau install satu per satu
pip install --upgrade scikit-learn langchain pywin32
```

#### 4. Virtual Environment Issues
```bash
# Hapus dan buat ulang virtual environment
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 📝 Checklist Upgrade

- [ ] Backup proyek lengkap
- [ ] Export dependencies Python 3.10
- [ ] Download Python 3.12 installer
- [ ] Install Python 3.12 dengan konfigurasi yang benar
- [ ] Verifikasi instalasi Python 3.12
- [ ] Update pip ke versi terbaru
- [ ] Buat virtual environment baru
- [ ] Install dependencies di virtual environment baru
- [ ] Test import semua modules
- [ ] Test menjalankan Jarvis AI
- [ ] Verifikasi semua fitur berfungsi normal

## 🔄 Rollback Plan

Jika terjadi masalah:

1. **Restore dari backup**
   ```bash
   rmdir /s "d:\Project Jarvis"
   cp -r "d:\Project Jarvis_backup_YYYYMMDD" "d:\Project Jarvis"
   ```

2. **Uninstall Python 3.12**
   - Melalui Control Panel > Programs and Features
   - Atau menggunakan installer dengan opsi "Uninstall"

3. **Reinstall Python 3.10**
   - Download dari python.org
   - Install dengan konfigurasi yang sama

## 📞 Support

Jika mengalami masalah:
1. Cek log error di terminal
2. Verifikasi versi Python dan dependencies
3. Konsultasi dokumentasi resmi Python 3.12
4. Gunakan backup untuk rollback jika diperlukan

---

**Catatan**: Upgrade ini akan meningkatkan performa dan memberikan akses ke fitur-fitur terbaru Python 3.12, termasuk improved error messages, better typing support, dan performance improvements.