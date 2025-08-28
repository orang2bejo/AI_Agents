@echo off
echo ========================================
echo     JARVIS AI - Installer Otomatis
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python 3.8+ terlebih dahulu dari https://python.org
    pause
    exit /b 1
)

echo [INFO] Python ditemukan, melanjutkan instalasi...
echo.

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Versi Python: %PYTHON_VERSION%
echo.

:: Create virtual environment
echo [STEP 1] Membuat virtual environment...
python -m venv jarvis_env
if %errorlevel% neq 0 (
    echo [ERROR] Gagal membuat virtual environment!
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment berhasil dibuat!
echo.

:: Activate virtual environment
echo [STEP 2] Mengaktifkan virtual environment...
call jarvis_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Gagal mengaktifkan virtual environment!
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment aktif!
echo.

:: Upgrade pip
echo [STEP 3] Mengupgrade pip...
python -m pip install --upgrade pip
echo.

:: Install requirements
echo [STEP 4] Menginstall dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal menginstall dependencies!
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies berhasil diinstall!
) else (
    echo [WARNING] File requirements.txt tidak ditemukan!
    echo Menginstall dependencies dasar...
    pip install openai anthropic google-generativeai groq requests python-dotenv pyyaml
)
echo.

:: Install Jarvis AI package
echo [STEP 5] Menginstall Jarvis AI package...
pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Gagal menginstall Jarvis AI package!
    pause
    exit /b 1
)
echo [SUCCESS] Jarvis AI package berhasil diinstall!
echo.

:: Setup environment file
echo [STEP 6] Setup konfigurasi environment...
if not exist .env (
    if exist config\.env-example (
        copy config\.env-example .env
        echo [INFO] File .env dibuat dari template.
        echo [IMPORTANT] Silakan edit file .env dan tambahkan API keys Anda!
    ) else (
        echo # Jarvis AI Environment Configuration > .env
        echo OPENAI_API_KEY=your_openai_api_key_here >> .env
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here >> .env
        echo GOOGLE_API_KEY=your_google_api_key_here >> .env
        echo OPENROUTER_API_KEY=your_openrouter_api_key_here >> .env
        echo [INFO] File .env dasar telah dibuat.
    )
echo.

:: Create startup script
echo [STEP 7] Membuat script startup...
echo @echo off > start_jarvis.bat
echo call jarvis_env\Scripts\activate.bat >> start_jarvis.bat
echo python scripts\jarvis_main.py >> start_jarvis.bat
echo pause >> start_jarvis.bat
echo [SUCCESS] Script startup 'start_jarvis.bat' telah dibuat!
echo.

echo ========================================
echo        INSTALASI SELESAI!
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Edit file .env dan tambahkan API keys Anda
echo 2. Jalankan 'start_jarvis.bat' untuk memulai Jarvis AI
echo 3. Atau aktifkan virtual environment dengan: jarvis_env\Scripts\activate.bat
echo 4. Kemudian jalankan: python scripts\jarvis_main.py
echo.
echo Dokumentasi lengkap tersedia di folder 'docs'
echo.
pause