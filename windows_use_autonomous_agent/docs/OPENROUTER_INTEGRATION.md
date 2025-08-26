# 🌐 OpenRouter API Integration Guide

> **Panduan Lengkap Integrasi OpenRouter API dengan Jarvis AI**

[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-blue.svg)](https://openrouter.ai/)
[![Status: Implemented](https://img.shields.io/badge/Status-Implemented-green.svg)]()
[![Version: 1.0](https://img.shields.io/badge/Version-1.0-blue.svg)]()

## 📋 Daftar Isi

- [🎯 Overview](#-overview)
- [⚙️ Setup & Configuration](#️-setup--configuration)
- [🚀 Quick Start](#-quick-start)
- [📚 API Usage](#-api-usage)
- [🔧 Advanced Configuration](#-advanced-configuration)
- [🛡️ Security & Best Practices](#️-security--best-practices)
- [🐛 Troubleshooting](#-troubleshooting)
- [📊 Model Comparison](#-model-comparison)

## 🎯 Overview

OpenRouter API integration memberikan akses terpusat ke **100+ model AI** dari berbagai provider melalui satu API yang unified. Implementasi ini memungkinkan Jarvis AI untuk:

- **Akses Multi-Model**: GPT-4o, Claude-3.5, Llama-3.1, Gemini, dan banyak lagi
- **Cost Optimization**: Otomatis memilih model termurah untuk task tertentu
- **Automatic Fallback**: Jika satu model gagal, otomatis switch ke model lain
- **Unified Interface**: Konsisten dengan arsitektur LLM existing

### 🏗️ Arsitektur

```
Jarvis AI
    ↓
LLMRouter
    ↓
OpenRouterProvider (extends OpenAIProvider)
    ↓
OpenRouter API (https://openrouter.ai/api/v1)
    ↓
100+ AI Models (OpenAI, Anthropic, Meta, Google, dll.)
```

## ⚙️ Setup & Configuration

### 1. **Dapatkan API Key**

1. Kunjungi [OpenRouter.ai](https://openrouter.ai/)
2. Daftar akun atau login
3. Buat API key di dashboard
4. Copy API key (format: `sk-or-v1-...`)

### 2. **Set Environment Variable**

```bash
# Windows PowerShell
$env:OPENROUTER_API_KEY="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"

# Windows CMD
set OPENROUTER_API_KEY=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

# Linux/Mac
export OPENROUTER_API_KEY="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"
```

### 3. **Verifikasi Konfigurasi**

```python
import os
from windows_use.llm import create_openrouter_provider

# Check API key
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    print("✅ OpenRouter API key configured")
else:
    print("❌ OpenRouter API key not found")
```

## 🚀 Quick Start

### **Basic Usage**

```python
from windows_use.llm import create_openrouter_provider
import asyncio

async def main():
    # Initialize OpenRouter provider
    provider = create_openrouter_provider(
        api_key="sk-or-v1-your-api-key",
        model="openai/gpt-3.5-turbo"
    )
    
    # Generate response
    messages = [
        {"role": "user", "content": "Hello from Jarvis AI!"}
    ]
    
    response = await provider.generate_response(messages)
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.usage}")

asyncio.run(main())
```

### **Dengan LLM Router**

```python
from windows_use.llm import LLMRouter
import asyncio

async def main():
    # Initialize router dengan unified_access policy
    router = LLMRouter()
    
    response = await router.generate_response(
        messages=[{"role": "user", "content": "Explain quantum computing"}],
        policy="unified_access"  # Prioritize OpenRouter
    )
    
    print(f"Response: {response.content}")
    print(f"Provider: {response.provider}")

asyncio.run(main())
```

## 📚 API Usage

### **Available Models**

#### **OpenAI Models**
```python
# GPT-4o (Latest)
model = "openai/gpt-4o"
model = "openai/gpt-4o-mini"

# GPT-3.5
model = "openai/gpt-3.5-turbo"
```

#### **Anthropic Models**
```python
# Claude-3.5 (Latest)
model = "anthropic/claude-3-5-sonnet"
model = "anthropic/claude-3-5-haiku"

# Claude-3
model = "anthropic/claude-3-haiku"
```

#### **Meta Models**
```python
# Llama-3.1
model = "meta-llama/llama-3.1-70b-instruct"
model = "meta-llama/llama-3.1-8b-instruct"
```

#### **Google Models**
```python
# Gemini
model = "google/gemini-pro-1.5"
model = "google/gemini-flash-1.5"
```

#### **Other Popular Models**
```python
# Mixtral
model = "mistralai/mixtral-8x7b-instruct"

# Cohere
model = "cohere/command-r-plus"
```

### **Streaming Response**

```python
async def stream_example():
    provider = create_openrouter_provider(
        api_key="your-api-key",
        model="openai/gpt-4o"
    )
    
    messages = [{"role": "user", "content": "Write a story about AI"}]
    
    async for chunk in provider.generate_stream(messages):
        print(chunk, end="", flush=True)
```

### **Tool Calling**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }
]

response = await provider.generate_response(
    messages=[{"role": "user", "content": "What's the weather in Jakarta?"}],
    tools=tools
)
```

## 🔧 Advanced Configuration

### **Custom Headers**

```python
provider = create_openrouter_provider(
    api_key="your-api-key",
    model="openai/gpt-4o",
    custom_headers={
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "Your App Name"
    }
)
```

### **Timeout & Retry Configuration**

```python
from windows_use.llm import LLMConfig, OpenRouterProvider

config = LLMConfig(
    provider="openrouter",
    model="openai/gpt-4o",
    api_key="your-api-key",
    timeout=120,  # 2 minutes
    max_retries=5
)

provider = OpenRouterProvider(config)
```

### **Routing Policies**

Edit `config/llm_config.yaml`:

```yaml
routing:
  default_policy: "unified_access"  # Use OpenRouter first
  
  policies:
    unified_access:
      description: "Prefer OpenRouter for unified access"
      order: ["openrouter", "anthropic", "gemini", "groq"]
    
    cost_optimized:
      description: "Prefer cheaper models"
      order: ["groq", "deepseek", "openrouter", "gemini"]
```

## 🛡️ Security & Best Practices

### **API Key Management**

```python
# ✅ GOOD: Use environment variables
api_key = os.getenv("OPENROUTER_API_KEY")

# ❌ BAD: Hardcode in source code
api_key = "sk-or-v1-..."
```

### **Rate Limiting**

```python
import asyncio
from asyncio import Semaphore

# Limit concurrent requests
semaphore = Semaphore(5)  # Max 5 concurrent requests

async def rate_limited_request(provider, messages):
    async with semaphore:
        return await provider.generate_response(messages)
```

### **Error Handling**

```python
try:
    response = await provider.generate_response(messages)
except Exception as e:
    if "rate_limit" in str(e).lower():
        print("Rate limit exceeded, waiting...")
        await asyncio.sleep(60)
    elif "insufficient_quota" in str(e).lower():
        print("Insufficient credits")
    else:
        print(f"Unexpected error: {e}")
```

## 🐛 Troubleshooting

### **Common Issues**

#### **1. API Key Invalid**
```
Error: Invalid API key
```
**Solution:**
- Verify API key format: `sk-or-v1-...`
- Check environment variable: `echo $OPENROUTER_API_KEY`
- Regenerate API key di OpenRouter dashboard

#### **2. Model Not Found**
```
Error: Model 'invalid-model' not found
```
**Solution:**
- Check available models di [OpenRouter Models](https://openrouter.ai/models)
- Use correct model format: `provider/model-name`

#### **3. Rate Limit Exceeded**
```
Error: Rate limit exceeded
```
**Solution:**
- Implement exponential backoff
- Reduce request frequency
- Upgrade OpenRouter plan

#### **4. Insufficient Credits**
```
Error: Insufficient credits
```
**Solution:**
- Add credits di OpenRouter dashboard
- Check billing settings
- Monitor usage

### **Debug Mode**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("windows_use.llm")

# Test connection
provider = create_openrouter_provider(
    api_key="your-api-key",
    model="openai/gpt-3.5-turbo"
)

try:
    response = await provider.generate_response(
        messages=[{"role": "user", "content": "test"}]
    )
    print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## 📊 Model Comparison

| Model | Provider | Strengths | Use Cases | Cost |
|-------|----------|-----------|-----------|------|
| `openai/gpt-4o` | OpenAI | Latest, multimodal | Complex reasoning, vision | High |
| `openai/gpt-3.5-turbo` | OpenAI | Fast, reliable | General tasks | Low |
| `anthropic/claude-3-5-sonnet` | Anthropic | Long context, safety | Analysis, writing | Medium |
| `meta-llama/llama-3.1-70b` | Meta | Open source, capable | General tasks | Medium |
| `google/gemini-flash-1.5` | Google | Fast, efficient | Quick responses | Low |
| `mistralai/mixtral-8x7b` | Mistral | Multilingual | European languages | Medium |

### **Rekomendasi Penggunaan**

- **General Chat**: `openai/gpt-3.5-turbo`
- **Complex Analysis**: `anthropic/claude-3-5-sonnet`
- **Vision Tasks**: `openai/gpt-4o`
- **Fast Responses**: `google/gemini-flash-1.5`
- **Cost-Effective**: `meta-llama/llama-3.1-8b-instruct`

---

## 📞 Support

- **OpenRouter Documentation**: [docs.openrouter.ai](https://docs.openrouter.ai/)
- **Jarvis AI Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discord Community**: [Join Discord](https://discord.gg/your-invite)

---

**🚀 Ready to explore 100+ AI models? Start with OpenRouter integration today!**