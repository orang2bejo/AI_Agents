# 🔌 Panduan Integrasi API Jarvis AI

> **Panduan lengkap untuk mengintegrasikan berbagai API provider dengan Jarvis AI, termasuk contoh kode dan best practices.**

## 📋 Daftar Isi

1. [Overview](#-overview)
2. [LLM Router System](#-llm-router-system)
3. [Provider Integrations](#-provider-integrations)
4. [Code Examples](#-code-examples)
5. [Error Handling](#-error-handling)
6. [Performance Optimization](#-performance-optimization)
7. [Testing & Validation](#-testing--validation)
8. [Best Practices](#-best-practices)

---

## 🎯 Overview

### Arsitektur Multi-Provider

Jarvis AI menggunakan sistem **LLM Router** yang memungkinkan:
- **Automatic Fallback**: Jika satu provider gagal, otomatis beralih ke provider lain
- **Load Balancing**: Distribusi request berdasarkan prioritas dan performa
- **Cost Optimization**: Routing berdasarkan biaya per request
- **Task-Specific Routing**: Provider berbeda untuk task berbeda

### Supported Providers

| Provider | Type | Cost | Speed | Quality | Features |
|----------|------|------|-------|---------|----------|
| **Ollama** | Local | Free | ⭐⭐⭐⭐ | ⭐⭐⭐ | Offline, Privacy |
| **Groq** | Cloud | Free/Paid | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Ultra-fast inference |
| **Gemini** | Cloud | Free/Paid | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Multimodal, Vision |
| **Anthropic** | Cloud | Paid | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Best reasoning |
| **OpenRouter** | Cloud | Paid | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 100+ models |
| **DeepSeek** | Cloud | Paid | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Coding specialist |
| **Qwen** | Cloud | Paid | ⭐⭐⭐ | ⭐⭐⭐⭐ | Multilingual |

---

## 🔄 LLM Router System

### Core Components

```python
from windows_use.llm.router import LLMRouter
from windows_use.llm.manager import LLMManager
from windows_use.llm.adapters import (
    OllamaAdapter,
    GeminiAdapter,
    AnthropicAdapter,
    GroqAdapter,
    OpenRouterAdapter
)

# Initialize router
router = LLMRouter()
manager = LLMManager(router)

# Auto-configure from config files
manager.load_config("config/llm_config.yaml")
```

### Routing Policies

```python
# 1. Offline First (Default)
response = manager.generate(
    prompt="Explain quantum computing",
    policy="offline_first"  # Ollama → Groq → Gemini
)

# 2. Cost Optimized
response = manager.generate(
    prompt="Write a simple function",
    policy="cost_optimized"  # Cheapest providers first
)

# 3. Speed Optimized
response = manager.generate(
    prompt="Quick answer needed",
    policy="speed_optimized"  # Groq → Ollama → DeepSeek
)

# 4. Quality Optimized
response = manager.generate(
    prompt="Complex analysis required",
    policy="quality_optimized"  # Anthropic → Gemini → OpenRouter
)
```

### Task-Specific Routing

```python
# Automatic task detection and routing
response = manager.generate_for_task(
    prompt="Create a Python web scraper",
    task_type="coding"  # Routes to DeepSeek → Anthropic → Qwen
)

response = manager.generate_for_task(
    prompt="Plan a marketing strategy",
    task_type="planning"  # Routes to Anthropic → Gemini → Qwen
)

response = manager.generate_for_task(
    prompt="Analyze this image",
    task_type="vision",  # Routes to Gemini → Anthropic
    image_path="screenshot.png"
)
```

---

## 🔌 Provider Integrations

### 1. Ollama (Local LLM)

#### Setup
```bash
# Install Ollama
winget install Ollama.Ollama

# Download models
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull gemma2:2b

# Start server
ollama serve
```

#### Integration Code
```python
from windows_use.llm.adapters.ollama import OllamaAdapter

# Initialize adapter
ollama = OllamaAdapter(
    base_url="http://localhost:11434",
    default_model="llama3.2:3b",
    timeout=30
)

# Simple generation
response = ollama.generate(
    prompt="Hello, how are you?",
    model="llama3.2:3b"
)

# Streaming response
for chunk in ollama.generate_stream(
    prompt="Write a story about AI",
    model="qwen2.5:7b"
):
    print(chunk, end="", flush=True)

# With parameters
response = ollama.generate(
    prompt="Explain machine learning",
    model="gemma2:2b",
    temperature=0.7,
    max_tokens=1000,
    top_p=0.9
)
```

#### Model Management
```python
# List available models
models = ollama.list_models()
print("Available models:", models)

# Check model status
status = ollama.check_model("llama3.2:3b")
print(f"Model status: {status}")

# Download new model
ollama.pull_model("mistral:7b")

# Remove model
ollama.remove_model("old-model:tag")
```

### 2. Google Gemini

#### Setup
```bash
# Get API key from https://makersuite.google.com/app/apikey
# Add to .env file
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### Integration Code
```python
from windows_use.llm.adapters.gemini import GeminiAdapter
import os

# Initialize adapter
gemini = GeminiAdapter(
    api_key=os.getenv("GOOGLE_API_KEY"),
    default_model="gemini-1.5-flash"
)

# Text generation
response = gemini.generate(
    prompt="Explain the theory of relativity",
    model="gemini-1.5-pro"
)

# Multimodal (text + image)
response = gemini.generate_multimodal(
    prompt="What do you see in this image?",
    image_path="screenshot.png",
    model="gemini-1.5-flash"
)

# Function calling
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
]

response = gemini.generate_with_tools(
    prompt="What's the weather in Jakarta?",
    tools=tools
)
```

#### Advanced Features
```python
# Safety settings
safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE"
}

response = gemini.generate(
    prompt="Generate content",
    safety_settings=safety_settings
)

# System instruction
response = gemini.generate(
    prompt="User question here",
    system_instruction="You are a helpful coding assistant. Always provide working code examples."
)
```

### 3. Anthropic Claude

#### Setup
```bash
# Get API key from https://console.anthropic.com/
# Add to .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### Integration Code
```python
from windows_use.llm.adapters.anthropic import AnthropicAdapter
import os

# Initialize adapter
anthropic = AnthropicAdapter(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_model="claude-3-5-haiku-20241022"
)

# Basic generation
response = anthropic.generate(
    prompt="Analyze this business proposal",
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000
)

# With system message
response = anthropic.generate(
    prompt="User: How do I implement a binary search?",
    system="You are an expert programming tutor. Provide clear explanations with code examples.",
    model="claude-3-5-haiku-20241022"
)

# Tool use
tools = [
    {
        "name": "calculator",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            }
        }
    }
]

response = anthropic.generate_with_tools(
    prompt="Calculate 15% of 2,450",
    tools=tools
)
```

### 4. Groq (Ultra-Fast Inference)

#### Setup
```bash
# Get API key from https://console.groq.com/
# Add to .env file
GROQ_API_KEY=your_groq_api_key_here
```

#### Integration Code
```python
from windows_use.llm.adapters.groq import GroqAdapter
import os

# Initialize adapter
groq = GroqAdapter(
    api_key=os.getenv("GROQ_API_KEY"),
    default_model="llama-3.1-8b-instant"
)

# Ultra-fast generation
response = groq.generate(
    prompt="Quick answer: What is Python?",
    model="llama-3.1-8b-instant",
    max_tokens=500
)

# Streaming for real-time responses
for chunk in groq.generate_stream(
    prompt="Write a Python function to sort a list",
    model="llama-3.1-70b-versatile"
):
    print(chunk, end="", flush=True)

# JSON mode
response = groq.generate(
    prompt="Generate a JSON object with user profile data",
    model="mixtral-8x7b-32768",
    response_format={"type": "json_object"}
)
```

### 5. OpenRouter (Unified Access)

#### Setup
```bash
# Get API key from https://openrouter.ai/
# Add to .env file
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
```

#### Integration Code
```python
from windows_use.llm.adapters.openrouter import OpenRouterAdapter
import os

# Initialize adapter
openrouter = OpenRouterAdapter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Access OpenAI models
response = openrouter.generate(
    prompt="Explain quantum computing",
    model="openai/gpt-4o"
)

# Access Anthropic models
response = openrouter.generate(
    prompt="Write a business plan",
    model="anthropic/claude-3-5-sonnet"
)

# Access Meta models
response = openrouter.generate(
    prompt="Code a web scraper",
    model="meta-llama/llama-3.1-70b-instruct"
)

# Cost tracking
response = openrouter.generate(
    prompt="Generate content",
    model="openai/gpt-3.5-turbo",
    track_cost=True
)
print(f"Cost: ${response.cost}")
```

### 6. DeepSeek (Coding Specialist)

#### Setup
```bash
# Get API key from https://platform.deepseek.com/
# Add to .env file
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

#### Integration Code
```python
from windows_use.llm.adapters.deepseek import DeepSeekAdapter
import os

# Initialize adapter
deepseek = DeepSeekAdapter(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    default_model="deepseek-coder"
)

# Code generation
response = deepseek.generate(
    prompt="Create a Python class for managing a database connection",
    model="deepseek-coder"
)

# Code explanation
response = deepseek.generate(
    prompt="Explain this code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    model="deepseek-chat"
)

# Code review
code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

response = deepseek.generate(
    prompt=f"Review this code and suggest improvements:\n{code}",
    model="deepseek-coder"
)
```

---

## 💻 Code Examples

### Complete Integration Example

```python
# main.py - Complete Jarvis AI integration
from windows_use.llm.manager import LLMManager
from windows_use.llm.router import LLMRouter
import asyncio
import os

class JarvisAI:
    def __init__(self):
        # Initialize LLM system
        self.router = LLMRouter()
        self.manager = LLMManager(self.router)
        
        # Load configuration
        self.manager.load_config("config/llm_config.yaml")
        self.manager.load_env_vars()
        
        # Setup fallback chain
        self.setup_fallback_chain()
    
    def setup_fallback_chain(self):
        """Setup automatic fallback between providers"""
        fallback_order = [
            "ollama",      # Local first (free, fast)
            "groq",        # Cloud fast (free tier)
            "gemini",      # Google (free tier)
            "deepseek",    # Coding specialist (cheap)
            "anthropic",   # High quality (paid)
            "openrouter"   # Unified access (paid)
        ]
        self.manager.set_fallback_order(fallback_order)
    
    async def process_request(self, prompt: str, task_type: str = "general"):
        """Process user request with automatic provider selection"""
        try:
            # Task-specific routing
            if task_type == "coding":
                response = await self.manager.generate_async(
                    prompt=prompt,
                    preferred_providers=["deepseek", "anthropic", "qwen"],
                    require_tools=True
                )
            elif task_type == "analysis":
                response = await self.manager.generate_async(
                    prompt=prompt,
                    preferred_providers=["gemini", "anthropic", "qwen"],
                    min_context_length=16384
                )
            elif task_type == "creative":
                response = await self.manager.generate_async(
                    prompt=prompt,
                    preferred_providers=["anthropic", "gemini", "qwen"],
                    temperature=0.8
                )
            else:
                # General purpose
                response = await self.manager.generate_async(
                    prompt=prompt,
                    policy="offline_first"
                )
            
            return {
                "response": response.text,
                "provider": response.provider,
                "model": response.model,
                "cost": response.cost,
                "latency": response.latency,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def get_provider_status(self):
        """Get status of all providers"""
        return self.manager.get_provider_status()
    
    def get_usage_stats(self):
        """Get usage statistics"""
        return self.manager.get_usage_stats()

# Usage example
async def main():
    jarvis = JarvisAI()
    
    # Test different task types
    tasks = [
        ("Write a Python function to calculate fibonacci numbers", "coding"),
        ("Analyze the pros and cons of renewable energy", "analysis"),
        ("Write a creative story about time travel", "creative"),
        ("What is the capital of Indonesia?", "general")
    ]
    
    for prompt, task_type in tasks:
        print(f"\n🤖 Task: {task_type}")
        print(f"📝 Prompt: {prompt}")
        
        result = await jarvis.process_request(prompt, task_type)
        
        if result["success"]:
            print(f"✅ Provider: {result['provider']}")
            print(f"🔧 Model: {result['model']}")
            print(f"💰 Cost: ${result['cost']:.4f}")
            print(f"⚡ Latency: {result['latency']:.2f}s")
            print(f"📄 Response: {result['response'][:200]}...")
        else:
            print(f"❌ Error: {result['error']}")
    
    # Show provider status
    print("\n📊 Provider Status:")
    status = jarvis.get_provider_status()
    for provider, info in status.items():
        print(f"  {provider}: {info['status']} ({info['latency']:.2f}ms)")

if __name__ == "__main__":
    asyncio.run(main())
```

### Voice Integration Example

```python
# voice_jarvis.py - Voice-enabled Jarvis AI
from windows_use.llm.manager import LLMManager
from windows_use.tools.voice_input import VoiceInput
from windows_use.tools.tts_piper import PiperTTS
from windows_use.evi.interface import EVIInterface
import asyncio

class VoiceJarvis:
    def __init__(self):
        # Initialize components
        self.llm_manager = LLMManager()
        self.voice_input = VoiceInput()
        self.tts = PiperTTS()
        self.evi = EVIInterface()  # Empathic Voice Interface
        
        # Load configurations
        self.llm_manager.load_config("config/llm_config.yaml")
    
    async def voice_conversation_loop(self):
        """Main voice conversation loop"""
        print("🎤 Voice Jarvis AI started. Say 'exit' to quit.")
        
        while True:
            try:
                # Listen for voice input
                print("\n🎧 Listening...")
                user_input = await self.voice_input.listen()
                
                if not user_input or user_input.lower() in ['exit', 'quit', 'stop']:
                    break
                
                print(f"👤 You: {user_input}")
                
                # Process with LLM
                response = await self.llm_manager.generate_async(
                    prompt=user_input,
                    policy="speed_optimized",  # Fast response for voice
                    max_tokens=500  # Keep responses concise
                )
                
                print(f"🤖 Jarvis: {response.text}")
                
                # Convert to speech with emotion
                emotion = self.evi.detect_emotion(response.text)
                await self.tts.speak_async(
                    text=response.text,
                    emotion=emotion,
                    voice="en_US-lessac-medium"  # Natural voice
                )
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await self.tts.speak_async("Sorry, I encountered an error. Please try again.")
        
        print("👋 Voice Jarvis AI stopped.")
    
    async def voice_command_mode(self):
        """Voice command mode for system control"""
        commands = {
            "open browser": self.open_browser,
            "take screenshot": self.take_screenshot,
            "check weather": self.check_weather,
            "read emails": self.read_emails,
            "system status": self.system_status
        }
        
        while True:
            command = await self.voice_input.listen()
            
            if command.lower() in commands:
                await commands[command.lower()]()
            else:
                # Use LLM to interpret command
                interpretation = await self.llm_manager.generate_async(
                    prompt=f"Interpret this voice command and suggest action: '{command}'",
                    task_type="execution"
                )
                
                await self.tts.speak_async(interpretation.text)

# Usage
async def main():
    voice_jarvis = VoiceJarvis()
    await voice_jarvis.voice_conversation_loop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Web Integration Example

```python
# web_jarvis.py - Web-enabled Jarvis AI
from windows_use.llm.manager import LLMManager
from windows_use.web.search_engine import SearchEngine
from windows_use.web.browser_automation import BrowserAutomation
from windows_use.web.web_scraper import WebScraper
import asyncio

class WebJarvis:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.search_engine = SearchEngine()
        self.browser = BrowserAutomation()
        self.scraper = WebScraper()
        
        # Load configurations
        self.llm_manager.load_config("config/llm_config.yaml")
    
    async def web_search_and_analyze(self, query: str):
        """Search web and analyze results"""
        try:
            # Search for information
            search_results = await self.search_engine.search(query, max_results=5)
            
            # Scrape content from top results
            content = []
            for result in search_results[:3]:
                try:
                    scraped = await self.scraper.scrape_url(result['url'])
                    content.append({
                        'title': result['title'],
                        'url': result['url'],
                        'content': scraped['text'][:1000]  # Limit content
                    })
                except Exception as e:
                    print(f"Failed to scrape {result['url']}: {e}")
            
            # Analyze with LLM
            analysis_prompt = f"""
            Based on the following web search results for "{query}", provide a comprehensive analysis:
            
            {chr(10).join([f"Title: {c['title']}\nURL: {c['url']}\nContent: {c['content']}\n" for c in content])}
            
            Please provide:
            1. Key findings
            2. Summary of main points
            3. Credibility assessment
            4. Recommendations for further research
            """
            
            analysis = await self.llm_manager.generate_async(
                prompt=analysis_prompt,
                task_type="analysis",
                preferred_providers=["gemini", "anthropic", "qwen"]
            )
            
            return {
                "query": query,
                "search_results": search_results,
                "scraped_content": content,
                "analysis": analysis.text,
                "provider": analysis.provider
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def automated_web_task(self, task_description: str):
        """Perform automated web tasks"""
        # Use LLM to break down the task
        task_breakdown = await self.llm_manager.generate_async(
            prompt=f"""
            Break down this web automation task into specific steps:
            "{task_description}"
            
            Provide steps in this format:
            1. Navigate to [URL]
            2. Click on [element]
            3. Fill form field [field] with [value]
            4. Submit form
            etc.
            """,
            task_type="planning"
        )
        
        # Execute the steps
        steps = self.parse_automation_steps(task_breakdown.text)
        results = []
        
        for step in steps:
            try:
                result = await self.browser.execute_step(step)
                results.append({"step": step, "result": result, "success": True})
            except Exception as e:
                results.append({"step": step, "error": str(e), "success": False})
                break
        
        return {
            "task": task_description,
            "breakdown": task_breakdown.text,
            "steps": results
        }
    
    def parse_automation_steps(self, breakdown_text: str):
        """Parse LLM output into automation steps"""
        # Implementation to parse the breakdown into executable steps
        lines = breakdown_text.split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Extract action from numbered/bulleted list
                step = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                steps.append(step)
        
        return steps

# Usage example
async def main():
    web_jarvis = WebJarvis()
    
    # Web search and analysis
    result = await web_jarvis.web_search_and_analyze(
        "Latest developments in artificial intelligence 2024"
    )
    
    if "error" not in result:
        print(f"🔍 Query: {result['query']}")
        print(f"📊 Found {len(result['search_results'])} results")
        print(f"🤖 Analysis by {result['provider']}:")
        print(result['analysis'])
    else:
        print(f"❌ Error: {result['error']}")
    
    # Automated web task
    task_result = await web_jarvis.automated_web_task(
        "Search for Python tutorials on YouTube and bookmark the top 3 results"
    )
    
    print(f"\n🤖 Task: {task_result['task']}")
    print(f"📋 Breakdown: {task_result['breakdown']}")
    print(f"✅ Completed {sum(1 for s in task_result['steps'] if s['success'])} steps")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚠️ Error Handling

### Comprehensive Error Handling

```python
from windows_use.llm.exceptions import (
    LLMProviderError,
    APIKeyError,
    RateLimitError,
    ModelNotFoundError,
    NetworkError
)
import logging

class RobustLLMManager:
    def __init__(self):
        self.manager = LLMManager()
        self.logger = logging.getLogger(__name__)
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2,
            "retry_delays": [1, 2, 4]  # seconds
        }
    
    async def generate_with_retry(self, prompt: str, **kwargs):
        """Generate with comprehensive error handling and retry logic"""
        last_error = None
        
        for attempt in range(self.retry_config["max_retries"]):
            try:
                response = await self.manager.generate_async(prompt, **kwargs)
                return response
                
            except APIKeyError as e:
                self.logger.error(f"API key error: {e}")
                # Try next provider
                kwargs["exclude_providers"] = kwargs.get("exclude_providers", []) + [e.provider]
                last_error = e
                
            except RateLimitError as e:
                self.logger.warning(f"Rate limit hit for {e.provider}, waiting {e.retry_after}s")
                await asyncio.sleep(e.retry_after)
                last_error = e
                
            except ModelNotFoundError as e:
                self.logger.error(f"Model not found: {e.model} on {e.provider}")
                # Try with default model
                kwargs["model"] = None
                last_error = e
                
            except NetworkError as e:
                self.logger.warning(f"Network error: {e}, retrying in {self.retry_config['retry_delays'][attempt]}s")
                await asyncio.sleep(self.retry_config['retry_delays'][attempt])
                last_error = e
                
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                last_error = e
        
        # All retries failed
        raise LLMProviderError(f"All providers failed after {self.retry_config['max_retries']} attempts. Last error: {last_error}")
    
    async def health_check(self):
        """Check health of all providers"""
        providers = self.manager.get_available_providers()
        health_status = {}
        
        for provider in providers:
            try:
                # Simple test request
                response = await self.manager.generate_async(
                    prompt="Hello",
                    preferred_providers=[provider],
                    max_tokens=10,
                    timeout=5
                )
                health_status[provider] = {
                    "status": "healthy",
                    "latency": response.latency,
                    "model": response.model
                }
            except Exception as e:
                health_status[provider] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status
```

### Error Recovery Strategies

```python
class ErrorRecoveryManager:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.fallback_strategies = {
            "api_key_error": self.handle_api_key_error,
            "rate_limit": self.handle_rate_limit,
            "model_error": self.handle_model_error,
            "network_error": self.handle_network_error
        }
    
    async def handle_api_key_error(self, error, context):
        """Handle API key errors"""
        # Remove provider with invalid key
        invalid_provider = error.provider
        
        # Try with remaining providers
        remaining_providers = [
            p for p in self.llm_manager.get_available_providers() 
            if p != invalid_provider
        ]
        
        if remaining_providers:
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                preferred_providers=remaining_providers,
                **context.get("kwargs", {})
            )
        else:
            raise LLMProviderError("No providers with valid API keys available")
    
    async def handle_rate_limit(self, error, context):
        """Handle rate limiting"""
        # Wait for rate limit reset
        wait_time = getattr(error, 'retry_after', 60)
        
        # Try with different provider immediately
        other_providers = [
            p for p in self.llm_manager.get_available_providers() 
            if p != error.provider
        ]
        
        if other_providers:
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                preferred_providers=other_providers,
                **context.get("kwargs", {})
            )
        else:
            # Wait and retry with same provider
            await asyncio.sleep(wait_time)
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                **context.get("kwargs", {})
            )
    
    async def handle_model_error(self, error, context):
        """Handle model not found errors"""
        # Try with default model for the provider
        provider_config = self.llm_manager.get_provider_config(error.provider)
        default_model = provider_config.get("default_model")
        
        if default_model:
            context["kwargs"]["model"] = default_model
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                **context["kwargs"]
            )
        else:
            # Try with different provider
            return await self.handle_api_key_error(error, context)
    
    async def handle_network_error(self, error, context):
        """Handle network errors"""
        # Try local providers first
        local_providers = ["ollama"]
        available_local = [
            p for p in local_providers 
            if p in self.llm_manager.get_available_providers()
        ]
        
        if available_local:
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                preferred_providers=available_local,
                **context.get("kwargs", {})
            )
        else:
            # Wait and retry
            await asyncio.sleep(5)
            return await self.llm_manager.generate_async(
                prompt=context["prompt"],
                **context.get("kwargs", {})
            )
```

---

## 🚀 Performance Optimization

### Caching System

```python
from windows_use.llm.cache import LLMCache
import hashlib
import json

class OptimizedLLMManager:
    def __init__(self):
        self.manager = LLMManager()
        self.cache = LLMCache(
            cache_type="redis",  # or "memory", "file"
            ttl=3600,  # 1 hour
            max_size=1000
        )
        self.performance_monitor = PerformanceMonitor()
    
    async def generate_cached(self, prompt: str, **kwargs):
        """Generate with caching"""
        # Create cache key
        cache_key = self.create_cache_key(prompt, kwargs)
        
        # Check cache first
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            self.performance_monitor.record_cache_hit()
            return cached_response
        
        # Generate new response
        start_time = time.time()
        response = await self.manager.generate_async(prompt, **kwargs)
        end_time = time.time()
        
        # Cache the response
        await self.cache.set(cache_key, response)
        
        # Record performance metrics
        self.performance_monitor.record_generation(
            provider=response.provider,
            latency=end_time - start_time,
            tokens=response.token_count,
            cost=response.cost
        )
        
        return response
    
    def create_cache_key(self, prompt: str, kwargs: dict):
        """Create deterministic cache key"""
        # Include relevant parameters in cache key
        cache_data = {
            "prompt": prompt,
            "model": kwargs.get("model"),
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens"),
            "top_p": kwargs.get("top_p", 0.9)
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
```

### Batch Processing

```python
class BatchLLMProcessor:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.batch_size = 10
        self.concurrent_limit = 5
    
    async def process_batch(self, prompts: list, **kwargs):
        """Process multiple prompts efficiently"""
        results = []
        
        # Process in batches
        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i:i + self.batch_size]
            
            # Process batch concurrently
            semaphore = asyncio.Semaphore(self.concurrent_limit)
            
            async def process_single(prompt):
                async with semaphore:
                    return await self.llm_manager.generate_async(prompt, **kwargs)
            
            batch_results = await asyncio.gather(
                *[process_single(prompt) for prompt in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
        
        return results
    
    async def process_with_load_balancing(self, prompts: list):
        """Process with intelligent load balancing"""
        # Get provider performance stats
        provider_stats = self.llm_manager.get_performance_stats()
        
        # Sort providers by performance (latency + availability)
        sorted_providers = sorted(
            provider_stats.items(),
            key=lambda x: (x[1]['avg_latency'], 1 - x[1]['availability'])
        )
        
        # Distribute prompts across providers
        provider_queues = {provider: [] for provider, _ in sorted_providers}
        
        for i, prompt in enumerate(prompts):
            provider = sorted_providers[i % len(sorted_providers)][0]
            provider_queues[provider].append(prompt)
        
        # Process each provider's queue
        all_tasks = []
        for provider, provider_prompts in provider_queues.items():
            if provider_prompts:
                tasks = [
                    self.llm_manager.generate_async(
                        prompt=prompt,
                        preferred_providers=[provider]
                    )
                    for prompt in provider_prompts
                ]
                all_tasks.extend(tasks)
        
        return await asyncio.gather(*all_tasks, return_exceptions=True)
```

---

## 🧪 Testing & Validation

### Provider Testing Suite

```python
# tests/test_providers.py
import pytest
import asyncio
from windows_use.llm.manager import LLMManager
from windows_use.llm.exceptions import *

class TestLLMProviders:
    @pytest.fixture
    async def llm_manager(self):
        manager = LLMManager()
        manager.load_config("config/llm_config.yaml")
        return manager
    
    @pytest.mark.asyncio
    async def test_ollama_connection(self, llm_manager):
        """Test Ollama local connection"""
        try:
            response = await llm_manager.generate_async(
                prompt="Hello, test message",
                preferred_providers=["ollama"],
                max_tokens=10
            )
            assert response.text
            assert response.provider == "ollama"
        except Exception as e:
            pytest.skip(f"Ollama not available: {e}")
    
    @pytest.mark.asyncio
    async def test_gemini_api(self, llm_manager):
        """Test Gemini API integration"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")
        
        response = await llm_manager.generate_async(
            prompt="What is 2+2?",
            preferred_providers=["gemini"],
            max_tokens=50
        )
        
        assert response.text
        assert "4" in response.text
        assert response.provider == "gemini"
    
    @pytest.mark.asyncio
    async def test_anthropic_api(self, llm_manager):
        """Test Anthropic Claude API"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")
        
        response = await llm_manager.generate_async(
            prompt="Explain photosynthesis in one sentence.",
            preferred_providers=["anthropic"],
            max_tokens=100
        )
        
        assert response.text
        assert len(response.text) > 10
        assert response.provider == "anthropic"
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, llm_manager):
        """Test automatic fallback between providers"""
        # Force failure of first provider
        response = await llm_manager.generate_async(
            prompt="Test fallback",
            preferred_providers=["invalid_provider", "ollama", "gemini"],
            max_tokens=20
        )
        
        assert response.text
        assert response.provider in ["ollama", "gemini"]
    
    @pytest.mark.asyncio
    async def test_task_routing(self, llm_manager):
        """Test task-specific provider routing"""
        # Coding task should prefer coding-optimized providers
        response = await llm_manager.generate_for_task(
            prompt="Write a Python function to reverse a string",
            task_type="coding"
        )
        
        assert response.text
        assert "def" in response.text or "function" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, llm_manager):
        """Test performance monitoring"""
        response = await llm_manager.generate_async(
            prompt="Quick test",
            max_tokens=10
        )
        
        assert hasattr(response, 'latency')
        assert hasattr(response, 'cost')
        assert hasattr(response, 'token_count')
        assert response.latency > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, llm_manager):
        """Test concurrent request handling"""
        prompts = [f"Test message {i}" for i in range(5)]
        
        tasks = [
            llm_manager.generate_async(prompt, max_tokens=10)
            for prompt in prompts
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        assert all(r.text for r in responses)
    
    def test_config_validation(self, llm_manager):
        """Test configuration validation"""
        config = llm_manager.get_config()
        
        assert "providers" in config
        assert "routing" in config
        assert "fallback" in config
        
        # Validate provider configs
        for provider_name, provider_config in config["providers"].items():
            assert "enabled" in provider_config
            assert "priority" in provider_config
            assert "models" in provider_config
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from windows_use.jarvis_ai import JarvisAI

class TestJarvisIntegration:
    @pytest.fixture
    def jarvis(self):
        return JarvisAI()
    
    @pytest.mark.asyncio
    async def test_voice_to_text_to_speech(self, jarvis):
        """Test complete voice interaction flow"""
        # Simulate voice input
        test_audio = "tests/fixtures/test_audio.wav"
        
        # Process voice input
        text_input = await jarvis.voice_input.transcribe(test_audio)
        assert text_input
        
        # Generate response
        response = await jarvis.process_request(text_input)
        assert response["success"]
        
        # Convert to speech
        audio_output = await jarvis.tts.synthesize(response["response"])
        assert audio_output
    
    @pytest.mark.asyncio
    async def test_web_search_integration(self, jarvis):
        """Test web search and analysis"""
        result = await jarvis.web_search_and_analyze(
            "Python programming tutorials"
        )
        
        assert "error" not in result
        assert result["search_results"]
        assert result["analysis"]
    
    @pytest.mark.asyncio
    async def test_office_automation(self, jarvis):
        """Test Office automation integration"""
        # Create test Excel file
        test_data = [
            ["Name", "Age", "City"],
            ["John", 25, "Jakarta"],
            ["Jane", 30, "Surabaya"]
        ]
        
        result = await jarvis.office.excel.create_spreadsheet(
            data=test_data,
            filename="test_output.xlsx"
        )
        
        assert result["success"]
        assert os.path.exists("test_output.xlsx")
    
    def test_security_features(self, jarvis):
        """Test security and authentication"""
        # Test input sanitization
        malicious_input = "<script>alert('xss')</script>"
        sanitized = jarvis.security.sanitize_input(malicious_input)
        assert "<script>" not in sanitized
        
        # Test voice authentication
        auth_result = jarvis.security.voice_auth.verify_speaker(
            "tests/fixtures/user_voice.wav"
        )
        assert "confidence" in auth_result
```

---

## 📋 Best Practices

### 1. API Key Management

```python
# ✅ Good: Use environment variables
import os
from pathlib import Path

class SecureConfig:
    def __init__(self):
        # Load from .env file
        self.load_env_file()
        
        # Validate required keys
        self.validate_api_keys()
    
    def load_env_file(self):
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    def validate_api_keys(self):
        required_keys = [
            "GOOGLE_API_KEY",
            "GROQ_API_KEY"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key) or os.getenv(key).startswith("your_"):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing API keys: {missing_keys}")

# ❌ Bad: Hardcoded API keys
# api_key = "sk-1234567890abcdef"  # Never do this!
```

### 2. Error Handling

```python
# ✅ Good: Comprehensive error handling
async def robust_generation(prompt: str):
    try:
        response = await llm_manager.generate_async(prompt)
        return {"success": True, "data": response}
    except APIKeyError as e:
        logger.error(f"API key error: {e}")
        return {"success": False, "error": "Invalid API key", "retry": False}
    except RateLimitError as e:
        logger.warning(f"Rate limit: {e}")
        return {"success": False, "error": "Rate limit exceeded", "retry": True, "wait": e.retry_after}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "error": "Internal error", "retry": True}

# ❌ Bad: Generic exception handling
# try:
#     response = await llm_manager.generate_async(prompt)
# except Exception:
#     return "Error occurred"
```

### 3. Performance Optimization

```python
# ✅ Good: Async with proper resource management
class OptimizedJarvis:
    def __init__(self):
        self.session_pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100),
            timeout=aiohttp.ClientTimeout(total=30)
        )
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    async def process_multiple(self, prompts: list):
        async def process_single(prompt):
            async with self.semaphore:
                return await self.llm_manager.generate_async(prompt)
        
        return await asyncio.gather(
            *[process_single(p) for p in prompts],
            return_exceptions=True
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session_pool.close()

# Usage
async with OptimizedJarvis() as jarvis:
    results = await jarvis.process_multiple(prompts)
```

### 4. Monitoring and Logging

```python
# ✅ Good: Structured logging with metrics
import structlog
from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests', ['provider', 'model'])
REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'LLM request duration', ['provider'])

logger = structlog.get_logger()

class MonitoredLLMManager:
    async def generate_async(self, prompt: str, **kwargs):
        start_time = time.time()
        provider = None
        
        try:
            response = await self.manager.generate_async(prompt, **kwargs)
            provider = response.provider
            
            # Record metrics
            REQUEST_COUNT.labels(provider=provider, model=response.model).inc()
            REQUEST_DURATION.labels(provider=provider).observe(time.time() - start_time)
            
            # Structured logging
            logger.info(
                "llm_request_completed",
                provider=provider,
                model=response.model,
                tokens=response.token_count,
                cost=response.cost,
                latency=response.latency
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "llm_request_failed",
                provider=provider,
                error=str(e),
                prompt_length=len(prompt)
            )
            raise
```

### 5. Configuration Management

```python
# ✅ Good: Hierarchical configuration with validation
from pydantic import BaseModel, validator
from typing import Dict, List, Optional

class ProviderConfig(BaseModel):
    name: str
    enabled: bool = True
    priority: int
    api_key_env: Optional[str]
    base_url: Optional[str]
    timeout: int = 30
    max_retries: int = 3
    models: List[str]
    default_model: str
    
    @validator('priority')
    def priority_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Priority must be positive')
        return v
    
    @validator('default_model')
    def default_model_must_be_in_models(cls, v, values):
        if 'models' in values and v not in values['models']:
            raise ValueError('Default model must be in models list')
        return v

class LLMConfig(BaseModel):
    providers: Dict[str, ProviderConfig]
    routing: Dict[str, dict]
    fallback: dict
    defaults: dict
    
    @classmethod
    def load_from_file(cls, config_path: str):
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
```

---

## 📚 Additional Resources

### Documentation Links
- [Ollama Documentation](https://ollama.ai/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [OpenRouter API](https://openrouter.ai/docs)

### Community & Support
- **GitHub Repository**: [Jarvis AI Project](https://github.com/your-repo)
- **Discord Community**: [Join Discord](https://discord.gg/your-invite)
- **Documentation**: [Full Documentation](../README.md)

### Tools & Utilities
- **API Testing**: [Postman Collection](./postman/jarvis-ai.json)
- **Configuration Validator**: `python scripts/validate_config.py`
- **Performance Monitor**: `python scripts/monitor_performance.py`

---

> **💡 Pro Tip**: Start with local providers (Ollama) for development, then add cloud providers for production. Use the routing policies to optimize for your specific use case (cost, speed, or quality).