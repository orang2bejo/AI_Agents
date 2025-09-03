# 🔧 Panduan Konfigurasi Jarvis AI

> **Panduan lengkap untuk mengkonfigurasi Jarvis AI dengan berbagai provider LLM, API keys, dan pengaturan sistem.**

## 📋 Daftar Isi

1. [Konfigurasi Environment Variables](#-konfigurasi-environment-variables)
2. [Konfigurasi LLM Providers](#-konfigurasi-llm-providers)
3. [Konfigurasi Voice Services](#-konfigurasi-voice-services)
4. [Konfigurasi Web Search](#-konfigurasi-web-search)
5. [Konfigurasi Office Integration](#-konfigurasi-office-integration)
6. [Konfigurasi Security](#-konfigurasi-security)
7. [Konfigurasi Monitoring](#-konfigurasi-monitoring)
8. [Feature Flags](#-feature-flags)
9. [Troubleshooting](#-troubleshooting)

---

## 🔑 Konfigurasi Environment Variables

### Setup File .env

1. **Copy template:**
   ```cmd
   copy config\.env-example .env
   ```

2. **Edit file .env:**
   ```cmd
   notepad config\.env
   ```

### Struktur File .env

```bash
# =============================================================================
# LLM PROVIDER API KEYS
# =============================================================================

# Google Gemini (Gratis tier tersedia)
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI (Berbayar)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude (Berbayar)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Groq (Gratis tier tersedia)
GROQ_API_KEY=your_groq_api_key_here

# OpenRouter (Akses 100+ model)
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Cohere (Gratis tier tersedia)
COHERE_API_KEY=your_cohere_api_key_here

# Hugging Face (Gratis)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# DeepSeek (Berbayar, murah)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Qwen (Alibaba Cloud)
QWEN_API_KEY=your_qwen_api_key_here

# =============================================================================
# VOICE & SPEECH SERVICES
# =============================================================================

# Azure Speech Services
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=your_azure_region_here

# ElevenLabs TTS (Gratis tier tersedia)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# =============================================================================
# WEB SEARCH & INFORMATION
# =============================================================================

# Google Custom Search
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here

# Bing Search API
BING_SEARCH_API_KEY=your_bing_search_api_key_here

# Serper API (Alternative Google Search)
SERPER_API_KEY=your_serper_api_key_here

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

# Environment mode
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Feature flags
ENABLE_VOICE=true
ENABLE_GUI=true
ENABLE_WEB_SEARCH=true
ENABLE_OFFICE=true
ENABLE_EVOLUTION=true
ENABLE_SECURITY=true
```

---

## 🤖 Konfigurasi LLM Providers

### File Konfigurasi: `config/llm_config.yaml`

```yaml
# Multi-Provider LLM Configuration
providers:
  # Local LLM (Gratis, Offline)
  ollama:
    name: "ollama"
    enabled: true
    priority: 1
    base_url: "http://localhost:11434"
    timeout: 30
    max_retries: 3
    models:
      - "llama3.2:3b"      # Ringan, cepat
      - "llama3.2:1b"      # Sangat ringan
      - "qwen2.5:7b"       # Bagus untuk coding
      - "gemma2:2b"        # Efisien
    default_model: "llama3.2:3b"
  
  # Google Gemini (Gratis tier bagus)
  gemini:
    name: "gemini"
    enabled: true
    priority: 2
    api_key_env: "GOOGLE_API_KEY"
    timeout: 30
    max_retries: 3
    models:
      - "gemini-1.5-pro"   # Terbaik untuk analisis
      - "gemini-1.5-flash" # Cepat dan efisien
      - "gemini-1.0-pro"   # Stabil
    default_model: "gemini-1.5-flash"
  
  # Anthropic Claude (Kualitas tinggi)
  anthropic:
    name: "anthropic"
    enabled: true
    priority: 3
    api_key_env: "ANTHROPIC_API_KEY"
    timeout: 30
    max_retries: 3
    models:
      - "claude-3-5-sonnet-20241022"  # Terbaik overall
      - "claude-3-5-haiku-20241022"   # Cepat dan murah
      - "claude-3-haiku-20240307"     # Versi lama
    default_model: "claude-3-5-haiku-20241022"
  
  # Groq (Sangat cepat)
  groq:
    name: "groq"
    enabled: true
    priority: 4
    api_key_env: "GROQ_API_KEY"
    timeout: 15
    max_retries: 2
    models:
      - "llama-3.1-70b-versatile"  # Terbaik
      - "llama-3.1-8b-instant"     # Cepat
      - "mixtral-8x7b-32768"       # Context panjang
      - "gemma2-9b-it"             # Efisien
    default_model: "llama-3.1-8b-instant"
  
  # OpenRouter (Akses 100+ model)
  openrouter:
    name: "openrouter"
    enabled: true
    priority: 5
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: "OPENROUTER_API_KEY"
    timeout: 60
    max_retries: 3
    models:
      # OpenAI models
      - "openai/gpt-4o"
      - "openai/gpt-4o-mini"
      - "openai/gpt-3.5-turbo"
      # Anthropic models
      - "anthropic/claude-3-5-sonnet"
      - "anthropic/claude-3-5-haiku"
      # Meta models
      - "meta-llama/llama-3.1-70b-instruct"
      - "meta-llama/llama-3.1-8b-instruct"
      # Google models
      - "google/gemini-pro-1.5"
      - "google/gemini-flash-1.5"
    default_model: "openai/gpt-3.5-turbo"
    features:
      supports_tools: true
      supports_vision: true
      supports_streaming: true
      unified_api: true

# Routing policies
routing:
  default_policy: "offline_first"
  policies:
    offline_first:
      prefer_local: true
      max_cost_per_request: 0.01
      max_latency_ms: 5000
    
    cost_optimized:
      prefer_local: false
      max_cost_per_request: 0.005
      max_latency_ms: 10000
    
    speed_optimized:
      prefer_local: false
      max_cost_per_request: 0.05
      max_latency_ms: 1000
    
    quality_optimized:
      prefer_local: false
      max_cost_per_request: 0.10
      max_latency_ms: 15000

# Task-specific routing
task_routing:
  planning:
    preferred_providers: ["anthropic", "gemini", "qwen"]
    min_context_length: 32768
  
  execution:
    preferred_providers: ["groq", "deepseek", "ollama"]
    min_context_length: 8192
    require_tools: true
  
  coding:
    preferred_providers: ["deepseek", "anthropic", "qwen"]
    min_context_length: 16384
    require_tools: true
  
  analysis:
    preferred_providers: ["gemini", "anthropic", "qwen"]
  
  creative:
    preferred_providers: ["anthropic", "gemini", "qwen"]
    min_context_length: 16384
  
  general:
    preferred_providers: ["ollama", "groq", "deepseek"]
    min_context_length: 4096

# Fallback configuration
fallback:
  enabled: true
  max_attempts: 3
  retry_delay_seconds: 1
  escalation_order:
    - "ollama"
    - "groq"
    - "deepseek"
    - "gemini"
    - "anthropic"

# Performance settings
defaults:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 4096
  stream: false
  timeout_seconds: 30
```

### Prioritas Provider

**Rekomendasi berdasarkan kebutuhan:**

1. **Untuk Pemula (Gratis):**
   - Ollama (local) → Groq → Gemini

2. **Untuk Produktivitas:**
   - OpenRouter → Anthropic → Gemini

3. **Untuk Development:**
   - DeepSeek → Anthropic → Qwen

4. **Untuk Speed:**
   - Groq → Ollama → DeepSeek

5. **Untuk Quality:**
   - Anthropic → Gemini → OpenRouter

---

## 🗣️ Konfigurasi Voice Services

### Azure Speech Services

1. **Daftar Azure account:**
   - Kunjungi: https://azure.microsoft.com/
   - Buat Speech Service resource

2. **Dapatkan API key:**
   ```bash
   AZURE_SPEECH_KEY=your_key_here
   AZURE_SPEECH_REGION=eastus
   ```

### ElevenLabs TTS

1. **Daftar account:**
   - Kunjungi: https://elevenlabs.io/
   - Free tier: 10,000 karakter/bulan

2. **Setup API key:**
   ```bash
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

### Local TTS (Piper)

**Tidak perlu API key, sudah terintegrasi:**
```python
from windows_use.tools.tts_piper import PiperTTS

tts = PiperTTS()
tts.speak("Hello from Jarvis AI")
```

---

## 🔍 Konfigurasi Web Search

### Google Custom Search

1. **Setup Custom Search Engine:**
   - Kunjungi: https://cse.google.com/
   - Buat search engine baru
   - Dapatkan Search Engine ID

2. **Dapatkan API key:**
   - Kunjungi: https://console.developers.google.com/
   - Enable Custom Search API
   - Buat credentials

3. **Konfigurasi:**
   ```bash
   GOOGLE_SEARCH_API_KEY=your_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id
   ```

### Bing Search API

1. **Daftar Azure Cognitive Services:**
   - Buat Bing Search v7 resource

2. **Setup:**
   ```bash
   BING_SEARCH_API_KEY=your_bing_key
   ```

### Serper API (Alternative)

1. **Daftar account:**
   - Kunjungi: https://serper.dev/
   - Free tier: 2,500 queries

2. **Setup:**
   ```bash
   SERPER_API_KEY=your_serper_key
   ```

---

## 📄 Konfigurasi Office Integration

### Microsoft Graph API

1. **Daftar Azure AD App:**
   - Kunjungi: https://portal.azure.com/
   - Azure Active Directory → App registrations
   - New registration

2. **Setup permissions:**
   - Files.ReadWrite.All
   - Mail.ReadWrite
   - Calendars.ReadWrite

3. **Konfigurasi:**
   ```bash
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_client_secret
   MICROSOFT_TENANT_ID=your_tenant_id
   ```

### Local Office (Tanpa API)

**Untuk Office lokal, tidak perlu API key:**
```python
from windows_use.office.excel_handler import ExcelHandler
from windows_use.office.word_handler import WordHandler

excel = ExcelHandler()
word = WordHandler()
```

---

## 🔒 Konfigurasi Security

### Encryption Key

1. **Generate encryption key:**
   ```python
   import secrets
   key = secrets.token_urlsafe(32)
   print(f"ENCRYPTION_KEY={key}")
   ```

2. **Setup:**
   ```bash
   ENCRYPTION_KEY=your_32_character_key_here
   JWT_SECRET=your_jwt_secret_key_here
   ```

### Security Features

```bash
# Enable security features
ENABLE_SECURITY=true

# Voice authentication
ENABLE_VOICE_AUTH=true

# Human-in-the-loop for sensitive operations
ENABLE_HITL=true
```

---

## 📊 Konfigurasi Monitoring

### Sentry (Error Tracking)

1. **Daftar Sentry:**
   - Kunjungi: https://sentry.io/
   - Buat project baru

2. **Setup:**
   ```bash
   SENTRY_DSN=your_sentry_dsn_here
   ```

### Application Insights

1. **Setup Azure Application Insights:**
   - Buat Application Insights resource

2. **Konfigurasi:**
   ```bash
   APPINSIGHTS_INSTRUMENTATION_KEY=your_key_here
   ```

### Local Monitoring

```bash
# Enable observability
ENABLE_OBSERVABILITY=true

# Log level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING=true
```

---

## 🚩 Feature Flags

### Konfigurasi Fitur

```bash
# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Core features
ENABLE_VOICE=true          # Voice input/output
ENABLE_GUI=true            # GUI automation
ENABLE_WEB_SEARCH=true     # Web search capabilities
ENABLE_OFFICE=true         # Office automation

# Advanced features
ENABLE_EVOLUTION=true      # Self-learning capabilities
ENABLE_SECURITY=true       # Security features
ENABLE_OBSERVABILITY=true  # Monitoring and logging

# Experimental features
ENABLE_VISION=false        # Computer vision (experimental)
ENABLE_MULTIMODAL=false    # Multimodal AI (experimental)
ENABLE_PLUGINS=false       # Plugin system (experimental)
```

### Penjelasan Feature Flags

| Flag | Deskripsi | Default |
|------|-----------|----------|
| `ENABLE_VOICE` | Voice input/output dengan microphone dan speaker | `true` |
| `ENABLE_GUI` | Desktop automation dan UI control | `true` |
| `ENABLE_WEB_SEARCH` | Web search dan information retrieval | `true` |
| `ENABLE_OFFICE` | Microsoft Office automation | `true` |
| `ENABLE_EVOLUTION` | Self-learning dan adaptive behavior | `true` |
| `ENABLE_SECURITY` | Security features dan authentication | `true` |
| `ENABLE_OBSERVABILITY` | Monitoring, logging, dan analytics | `true` |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Tidak Valid

**Gejala:**
```
Error: Invalid API key for provider 'gemini'
```

**Solusi:**
1. Periksa format API key
2. Pastikan API key aktif
3. Cek quota dan billing

#### 2. Ollama Tidak Terhubung

**Gejala:**
```
ConnectionError: Cannot connect to Ollama server
```

**Solusi:**
1. Install Ollama: `winget install Ollama.Ollama`
2. Start service: `ollama serve`
3. Test: `ollama run llama3.2:3b`

#### 3. Voice Input Tidak Bekerja

**Gejala:**
- Microphone tidak terdeteksi
- Voice recognition error

**Solusi:**
1. Periksa microphone permissions
2. Install audio drivers
3. Test dengan: `python -c "import sounddevice; print(sounddevice.query_devices())"`

#### 4. Office Integration Error

**Gejala:**
```
COMError: Microsoft Office not found
```

**Solusi:**
1. Install Microsoft Office
2. Register COM objects: `regsvr32 /s "C:\Program Files\Microsoft Office\...\msword.olb"`
3. Run as administrator

### Debug Mode

**Enable debug logging:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

**Test configuration:**
```cmd
python scripts/test_configuration.py
```

### Validation Script

**Buat script untuk validasi konfigurasi:**
```python
# scripts/validate_config.py
import os
from pathlib import Path

def validate_config():
    """Validate Jarvis AI configuration"""
    config_file = Path("config/.env")
    
    if not config_file.exists():
        print("❌ File .env tidak ditemukan")
        print("💡 Jalankan: copy config\.env-example .env")
        return False
    
    # Check required API keys
    required_keys = [
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "OPENROUTER_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key) or os.getenv(key) == f"your_{key.lower()}_here":
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ API keys belum dikonfigurasi: {', '.join(missing_keys)}")
        return False
    
    print("✅ Konfigurasi valid")
    return True

if __name__ == "__main__":
    validate_config()
```

---

## 📚 Referensi

### Dokumentasi API

- [Google Gemini API](https://ai.google.dev/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Groq API](https://console.groq.com/docs)
- [OpenRouter API](https://openrouter.ai/docs)
- [Ollama Documentation](https://ollama.ai/docs)

### Tools & Utilities

- [API Key Generator](https://generate-random.org/api-key-generator)
- [YAML Validator](https://yamlchecker.com/)
- [Environment Variables Checker](https://github.com/motdotla/dotenv)

### Support

- **GitHub Issues:** [Project Issues](https://github.com/your-repo/issues)
- **Documentation:** [Full Documentation](../README.md)
- **Community:** [Discord/Telegram Link]

---

> **💡 Tips:** Mulai dengan konfigurasi minimal (Ollama + Groq + Gemini) untuk testing, lalu tambahkan provider lain sesuai kebutuhan.