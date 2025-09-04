@echo off
setlocal enabledelayedexpansion
echo ========================================
echo     JARVIS AI - Installer Otomatis
echo ========================================
echo.

:: Initialize error tracking
set "INSTALL_ERRORS=0"
set "LOG_FILE=jarvis_install.log"
echo Installation started at %date% %time% > "%LOG_FILE%"

:: Function to log errors
:log_error
echo [ERROR] %~1
echo [ERROR] %~1 >> "%LOG_FILE%"
set /a INSTALL_ERRORS+=1
goto :eof

:: Function to log info
:log_info
echo [INFO] %~1
echo [INFO] %~1 >> "%LOG_FILE%"
goto :eof

:: Check if Python is installed
echo [STEP 0] Memeriksa sistem requirements...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Python tidak ditemukan!"
    echo Mencoba mencari Python dengan nama alternatif...
    py --version >nul 2>&1
    if !errorlevel! neq 0 (
        python3 --version >nul 2>&1
        if !errorlevel! neq 0 (
            call :log_error "Python tidak ditemukan dengan nama apapun (python, py, python3)"
            echo Silakan install Python 3.8+ terlebih dahulu dari https://python.org
            echo Pastikan Python ditambahkan ke PATH saat instalasi
            pause
            exit /b 1
        ) else (
            set "PYTHON_CMD=python3"
        )
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

call :log_info "Python ditemukan dengan command: %PYTHON_CMD%"
echo.

:: Check Python version and validate
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
call :log_info "Versi Python: %PYTHON_VERSION%"

:: Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

:: Check if Python version is 3.8+
if %PY_MAJOR% lss 3 (
    call :log_error "Python versi %PYTHON_VERSION% terlalu lama. Minimal Python 3.8 diperlukan"
    pause
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 8 (
    call :log_error "Python versi %PYTHON_VERSION% terlalu lama. Minimal Python 3.8 diperlukan"
    pause
    exit /b 1
)

call :log_info "Versi Python valid: %PYTHON_VERSION%"
echo.

:: Create virtual environment with error handling
echo [STEP 1] Membuat virtual environment...
if exist jarvis_env (
    call :log_info "Virtual environment sudah ada, menghapus yang lama..."
    rmdir /s /q jarvis_env
    if !errorlevel! neq 0 (
        call :log_error "Gagal menghapus virtual environment lama"
        echo Coba hapus folder jarvis_env secara manual dan jalankan ulang installer
        pause
        exit /b 1
    )
)

%PYTHON_CMD% -m venv jarvis_env
if %errorlevel% neq 0 (
    call :log_error "Gagal membuat virtual environment dengan %PYTHON_CMD%"
    echo Mencoba dengan virtualenv...
    %PYTHON_CMD% -m pip install virtualenv
    if !errorlevel! equ 0 (
        %PYTHON_CMD% -m virtualenv jarvis_env
        if !errorlevel! neq 0 (
            call :log_error "Gagal membuat virtual environment dengan virtualenv"
            pause
            exit /b 1
        )
    ) else (
        call :log_error "Gagal menginstall virtualenv"
        pause
        exit /b 1
    )
)
echo [SUCCESS] Virtual environment berhasil dibuat!
echo.

:: Activate virtual environment with validation
echo [STEP 2] Mengaktifkan virtual environment...
if not exist jarvis_env\Scripts\activate.bat (
    call :log_error "File aktivasi virtual environment tidak ditemukan"
    echo Struktur virtual environment mungkin rusak
    pause
    exit /b 1
)

call jarvis_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    call :log_error "Gagal mengaktifkan virtual environment"
    echo Coba jalankan sebagai administrator
    pause
    exit /b 1
)

:: Verify virtual environment is active
where python >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Python tidak ditemukan setelah aktivasi virtual environment"
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment aktif!
echo.

:: Upgrade pip with retry mechanism
echo [STEP 3] Mengupgrade pip...
set "PIP_RETRY=0"
:retry_pip_upgrade
python -m pip install --upgrade pip --timeout 60
if %errorlevel% neq 0 (
    set /a PIP_RETRY+=1
    if !PIP_RETRY! lss 3 (
        call :log_info "Pip upgrade gagal, mencoba lagi (!PIP_RETRY!/3)..."
        timeout /t 5 /nobreak >nul
        goto retry_pip_upgrade
    ) else (
        call :log_error "Gagal mengupgrade pip setelah 3 percobaan"
        echo Melanjutkan dengan pip versi saat ini...
    )
) else (
    call :log_info "Pip berhasil diupgrade"
)
echo.

:: Install requirements with comprehensive error handling
echo [STEP 4] Menginstall dependencies...
set "DEPS_INSTALLED=0"

if exist requirements.txt (
    call :log_info "Menginstall dari requirements.txt..."
    pip install -r requirements.txt --timeout 120 --retries 3
    if !errorlevel! neq 0 (
        call :log_error "Gagal menginstall dari requirements.txt"
        echo Mencoba install dependencies satu per satu...
        
        :: Try installing core dependencies individually
        set "CORE_DEPS=openai anthropic google-generativeai groq requests python-dotenv pyyaml"
        for %%d in (!CORE_DEPS!) do (
            echo Installing %%d...
            pip install %%d --timeout 60
            if !errorlevel! neq 0 (
                call :log_error "Gagal menginstall %%d"
            ) else (
                call :log_info "Berhasil menginstall %%d"
                set /a DEPS_INSTALLED+=1
            )
        )
    ) else (
        call :log_info "Dependencies dari requirements.txt berhasil diinstall"
        set "DEPS_INSTALLED=1"
    )
) else (
    call :log_info "File requirements.txt tidak ditemukan, menginstall dependencies dasar..."
    set "CORE_DEPS=openai anthropic google-generativeai groq requests python-dotenv pyyaml"
    for %%d in (!CORE_DEPS!) do (
        echo Installing %%d...
        pip install %%d --timeout 60
        if !errorlevel! neq 0 (
            call :log_error "Gagal menginstall %%d"
        ) else (
            call :log_info "Berhasil menginstall %%d"
            set /a DEPS_INSTALLED+=1
        )
    )
)

if %DEPS_INSTALLED% equ 0 (
    call :log_error "Tidak ada dependencies yang berhasil diinstall"
    echo Periksa koneksi internet dan coba lagi
    pause
    exit /b 1
)
echo.

:: Install Jarvis AI package with validation
echo [STEP 5] Menginstall Jarvis AI package...
if not exist pyproject.toml (
    if not exist setup.py (
        call :log_error "File pyproject.toml atau setup.py tidak ditemukan"
        echo Pastikan Anda berada di direktori root proyek Jarvis AI
        pause
        exit /b 1
    )
)

pip install -e . --timeout 120
if %errorlevel% neq 0 (
    call :log_error "Gagal menginstall Jarvis AI package dalam mode editable"
    echo Mencoba instalasi normal...
    pip install . --timeout 120
    if !errorlevel! neq 0 (
        call :log_error "Gagal menginstall Jarvis AI package"
        echo Periksa file pyproject.toml dan dependencies
        pause
        exit /b 1
    )
)
echo [SUCCESS] Jarvis AI package berhasil diinstall!
echo.

:: Setup environment file with comprehensive configuration
echo [STEP 6] Setup konfigurasi environment...
if not exist .env (
    if exist config\.env-example (
        copy config\.env-example .env >nul 2>&1
        if !errorlevel! equ 0 (
            call :log_info "File .env dibuat dari template config\.env-example"
        ) else (
            call :log_error "Gagal menyalin config\.env-example ke .env"
            goto create_basic_env
        )
    ) else (
        :create_basic_env
        call :log_info "Membuat file .env dasar..."
        (
            echo # Jarvis AI Environment Configuration
            echo # Generated on %date% %time%
            echo.
            echo # Core API Keys
            echo OPENAI_API_KEY=your_openai_api_key_here
            echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
            echo GOOGLE_API_KEY=your_google_api_key_here
            echo GROQ_API_KEY=your_groq_api_key_here
            echo OPENROUTER_API_KEY=your_openrouter_api_key_here
            echo.
            echo # Optional API Keys
            echo DEEPSEEK_API_KEY=your_deepseek_api_key_here
            echo QWEN_API_KEY=your_qwen_api_key_here
            echo.
            echo # Configuration
            echo DEBUG=false
            echo LOG_LEVEL=INFO
            echo VOICE_ENABLED=true
            echo SECURITY_LEVEL=medium
        ) > .env
        if !errorlevel! equ 0 (
            call :log_info "File .env dasar berhasil dibuat"
        ) else (
            call :log_error "Gagal membuat file .env"
        )
    )
    echo [IMPORTANT] Silakan edit file .env dan tambahkan API keys Anda!
) else (
    call :log_info "File .env sudah ada, tidak akan ditimpa"
)
echo.

:: Create startup script with error handling
echo [STEP 7] Membuat script startup...
(
    echo @echo off
    echo setlocal enabledelayedexpansion
    echo echo Starting Jarvis AI...
    echo.
    echo :: Check if virtual environment exists
    echo if not exist jarvis_env\Scripts\activate.bat (
    echo     echo [ERROR] Virtual environment tidak ditemukan!
    echo     echo Silakan jalankan install_jarvis_auto.bat terlebih dahulu.
    echo     pause
    echo     exit /b 1
    echo ^\)
    echo.
    echo :: Activate virtual environment
    echo call jarvis_env\Scripts\activate.bat
    echo if %%errorlevel%% neq 0 (
    echo     echo [ERROR] Gagal mengaktifkan virtual environment!
    echo     pause
    echo     exit /b 1
    echo ^\)
    echo.
    echo :: Check if main script exists
    echo if exist scripts\jarvis_main.py (
    echo     python scripts\jarvis_main.py
    echo ^) else (
    echo     echo [ERROR] Script utama tidak ditemukan!
    echo     echo Mencari file Python yang dapat dijalankan...
    echo     if exist windows_use\examples\jarvis_demo.py (
    echo         echo Menjalankan demo Jarvis...
    echo         python windows_use\examples\jarvis_demo.py
    echo     ^) else (
    echo         echo [ERROR] Tidak ada script yang dapat dijalankan!
    echo         pause
    echo         exit /b 1
    echo     ^\)
    echo ^\)
    echo.
    echo pause
) > start_jarvis.bat

if %errorlevel% equ 0 (
    echo [SUCCESS] Script startup 'start_jarvis.bat' telah dibuat!
) else (
    call :log_error "Gagal membuat script startup"
)
echo.

:: Final validation and summary
echo [STEP 8] Validasi instalasi...
set "VALIDATION_ERRORS=0"

:: Check virtual environment
if not exist jarvis_env\Scripts\python.exe (
    call :log_error "Virtual environment tidak lengkap"
    set /a VALIDATION_ERRORS+=1
)

:: Check .env file
if not exist .env (
    call :log_error "File .env tidak ada"
    set /a VALIDATION_ERRORS+=1
)

:: Check startup script
if not exist start_jarvis.bat (
    call :log_error "Script startup tidak ada"
    set /a VALIDATION_ERRORS+=1
)

echo Installation completed at %date% %time% >> "%LOG_FILE%"
echo Total errors during installation: %INSTALL_ERRORS% >> "%LOG_FILE%"
echo Validation errors: %VALIDATION_ERRORS% >> "%LOG_FILE%"

echo ========================================
if %VALIDATION_ERRORS% equ 0 (
    echo        INSTALASI BERHASIL!
) else (
    echo     INSTALASI SELESAI DENGAN PERINGATAN
)
echo ========================================
echo.
echo Status Instalasi:
echo - Python: %PYTHON_VERSION% (%PYTHON_CMD%)
echo - Virtual Environment: %jarvis_env%
echo - Dependencies: Terinstall
echo - Jarvis AI Package: Terinstall
echo - Environment File: .env
echo - Startup Script: start_jarvis.bat
echo - Log File: %LOG_FILE%
echo.
if %INSTALL_ERRORS% gtr 0 (
    echo [WARNING] %INSTALL_ERRORS% error(s) terjadi selama instalasi.
    echo Periksa file log %LOG_FILE% untuk detail.
    echo.
)
if %VALIDATION_ERRORS% gtr 0 (
    echo [WARNING] %VALIDATION_ERRORS% validation error(s) ditemukan.
    echo Beberapa komponen mungkin tidak berfungsi dengan baik.
    echo.
)
echo Langkah selanjutnya:
echo 1. Edit file .env dan tambahkan API keys Anda
echo 2. Jalankan 'start_jarvis.bat' untuk memulai Jarvis AI
echo 3. Atau aktifkan virtual environment: jarvis_env\Scripts\activate.bat
echo 4. Kemudian jalankan script utama
echo.
echo Dokumentasi lengkap tersedia di folder 'docs'
echo Log instalasi tersimpan di: %LOG_FILE%
echo.
pause