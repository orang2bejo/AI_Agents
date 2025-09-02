@echo off
echo ========================================
echo         JARVIS AI - Startup
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "jarvis_env\Scripts\activate.bat" (
    echo [ERROR] Virtual environment tidak ditemukan!
    echo Silakan jalankan install_jarvis_auto.bat terlebih dahulu.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Mengaktifkan virtual environment...
call jarvis_env\Scripts\activate.bat

:: Check if .env file exists
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan!
    echo Silakan setup API keys terlebih dahulu.
    echo.
    echo Membuka file .env untuk konfigurasi...
    if exist "config\.env-example" (
        copy "config\.env-example" ".env"
        notepad .env
    ) else (
        echo # Jarvis AI Environment Configuration > .env
        echo OPENAI_API_KEY=your_openai_api_key_here >> .env
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here >> .env
        echo GOOGLE_API_KEY=your_google_api_key_here >> .env
        echo OPENROUTER_API_KEY=your_openrouter_api_key_here >> .env
        notepad .env
    )
    echo.
    echo Silakan edit file .env dan jalankan script ini lagi.
    pause
    exit /b 1
)

:: Check if main script exists
if exist "scripts\jarvis_main.py" (
    echo [INFO] Memulai Jarvis AI...
    echo.
    python scripts\jarvis_main.py
) else (
    echo [ERROR] Script utama tidak ditemukan!
    echo Mencari file Python yang tersedia...
    echo.
    
    if exist "examples\complete_demo.py" (
        echo [INFO] Menjalankan demo lengkap...
        python examples\complete_demo.py
    ) else (
        echo [ERROR] Tidak ada script yang dapat dijalankan!
        echo Silakan periksa instalasi Anda.
    )
fi

echo.
echo Jarvis AI telah berhenti.
pause