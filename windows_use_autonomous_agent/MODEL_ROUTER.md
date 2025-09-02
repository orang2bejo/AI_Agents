# 🧠 Model Router & Policy Documentation

> **Intelligent LLM Routing and Selection System for Jarvis AI**

[![Status: Implemented](https://img.shields.io/badge/Status-Implemented-green.svg)]()
[![Version: 1.0](https://img.shields.io/badge/Version-1.0-blue.svg)]()
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Integrated-blue.svg)](https://openrouter.ai/)

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔄 Routing Policies](#-routing-policies)
- [📊 Task-Based Routing](#-task-based-routing)
- [⚙️ Configuration](#️-configuration)
- [🚀 Usage Examples](#-usage-examples)
- [📈 Performance Tracking](#-performance-tracking)
- [🔧 Advanced Features](#-advanced-features)
- [🛠️ Troubleshooting](#️-troubleshooting)

## 🎯 Overview

The **LLM Router** is an intelligent routing system that automatically selects the best AI model for each task based on:

- **Task Type**: Different models excel at different tasks (planning, coding, vision, etc.)
- **Routing Policy**: Cost optimization, speed optimization, quality optimization, etc.
- **Performance History**: Real-time tracking of model latency and failure rates
- **Requirements**: Tool support, vision capabilities, streaming, context length
- **Availability**: Provider status and API health

### 🏗️ Architecture

```
User Request
    ↓
LLMRouter.route()
    ↓
Candidate Selection → Scoring → Ranking → Selection
    ↓
Primary Provider → Fallback Options → Response
```

## 🔄 Routing Policies

### 1. **BALANCED** (Default)
Balances cost, speed, and quality for optimal overall performance.

```python
from windows_use.llm import LLMRouter, RoutingPolicy, RoutingConfig

router = LLMRouter(registry)
config = RoutingConfig(policy=RoutingPolicy.BALANCED)
```

### 2. **COST_OPTIMIZED**
Prioritizes free local models and low-cost cloud models.

```python
config = RoutingConfig(
    policy=RoutingPolicy.COST_OPTIMIZED,
    max_cost_per_request=0.01  # Maximum $0.01 per request
)
```

**Model Preferences:**
- 🥇 Local models (Ollama) - Free
- 🥈 Low-cost models (<$1/1K tokens)
- 🥉 Moderate-cost models (<$5/1K tokens)

### 3. **SPEED_OPTIMIZED**
Minimizes latency for real-time applications.

```python
config = RoutingConfig(
    policy=RoutingPolicy.SPEED_OPTIMIZED,
    max_latency_ms=1000  # Maximum 1 second
)
```

**Model Preferences:**
- 🥇 Very fast models (<500ms)
- 🥈 Fast models (<1000ms)
- 🥉 Moderate speed (<2000ms)

### 4. **QUALITY_OPTIMIZED**
Selects the highest quality models regardless of cost or speed.

```python
config = RoutingConfig(
    policy=RoutingPolicy.QUALITY_OPTIMIZED
)
```

**Model Preferences:**
- 🥇 Large models (70B+, Claude Sonnet)
- 🥈 Medium models (8B-70B)
- 🥉 Small models (<8B)

### 5. **OFFLINE_ONLY**
Uses only local models for privacy and offline operation.

```python
config = RoutingConfig(
    policy=RoutingPolicy.OFFLINE_ONLY
)
```

**Model Preferences:**
- ✅ Ollama models only
- ❌ Cloud models heavily penalized

### 6. **PRIVACY_FIRST**
Prefers local models, falls back to privacy-focused cloud providers.

```python
config = RoutingConfig(
    policy=RoutingPolicy.PRIVACY_FIRST
)
```

**Model Preferences:**
- 🥇 Local models (Ollama)
- 🥈 Privacy-focused providers
- 🥉 Standard cloud providers

## 📊 Task-Based Routing

The router automatically optimizes model selection based on task type:

### 🎯 **PLANNING**
Quick decision making and task planning.

```python
from windows_use.llm import TaskType

result = router.route(
    task_type=TaskType.PLANNING,
    messages=messages
)
```

**Preferred Models:**
- `groq/llama-3.1-8b` - Fast inference
- `ollama/llama3.2:3b` - Local option
- `claude-3.5-haiku` - Balanced quality/speed

**Requirements:**
- ⚡ Max latency: 1000ms
- 🛠️ Tool support: Required

### ⚙️ **EXECUTION**
Tool calling and action execution.

```python
result = router.route(
    task_type=TaskType.EXECUTION,
    messages=messages
)
```

**Preferred Models:**
- `groq/llama-3.1-70b` - High capability
- `claude-3.5-sonnet` - Excellent tool use
- `gemini-1.5-flash` - Fast and capable

**Requirements:**
- ⚡ Max latency: 2000ms
- 🛠️ Tool support: Required

### 🤔 **REFLECTION**
Analysis and evaluation tasks.

```python
result = router.route(
    task_type=TaskType.REFLECTION,
    messages=messages
)
```

**Preferred Models:**
- `claude-3.5-sonnet` - Superior reasoning
- `deepseek-r1` - Specialized reasoning
- `qwen2.5-72b-instruct` - Large context

**Requirements:**
- ⚡ Max latency: 5000ms
- 🛠️ Tool support: Optional

### 👁️ **VISION**
Image and screenshot analysis.

```python
result = router.route(
    task_type=TaskType.VISION,
    messages=messages_with_images
)
```

**Preferred Models:**
- `gemini-1.5-flash` - Excellent vision
- `claude-3.5-sonnet` - High-quality analysis
- `ollama/llama3.2-vision:11b` - Local vision

**Requirements:**
- 👁️ Vision support: Required

### 💬 **CONVERSATION**
General chat and Q&A.

```python
result = router.route(
    task_type=TaskType.CONVERSATION,
    messages=messages
)
```

**Preferred Models:**
- `ollama/llama3.2:3b` - Fast local chat
- `groq/llama-3.1-8b` - Quick responses
- `claude-3.5-haiku` - Balanced option

**Requirements:**
- ⚡ Max latency: 1500ms

### 🧠 **REASONING**
Complex reasoning and problem-solving.

```python
result = router.route(
    task_type=TaskType.REASONING,
    messages=messages
)
```

**Preferred Models:**
- `deepseek-r1` - Specialized reasoning
- `claude-3.5-sonnet` - Superior logic
- `qwen2.5-72b-instruct` - Large context

**Requirements:**
- ⚡ Max latency: 10000ms

### 💻 **CODING**
Code generation and analysis.

```python
result = router.route(
    task_type=TaskType.CODING,
    messages=messages
)
```

**Preferred Models:**
- `claude-3.5-sonnet` - Excellent coding
- `deepseek-chat` - Code-specialized
- `qwen2.5-72b-instruct` - Large context

**Requirements:**
- ⚡ Max latency: 5000ms
- 🛠️ Tool support: Required

## ⚙️ Configuration

### Basic Configuration

```python
from windows_use.llm import RoutingConfig, RoutingPolicy

config = RoutingConfig(
    policy=RoutingPolicy.BALANCED,
    max_cost_per_request=0.05,
    max_latency_ms=3000,
    require_tools=True,
    require_vision=False,
    require_streaming=False,
    fallback_enabled=True,
    retry_attempts=3
)
```

### Provider Preferences

```python
config = RoutingConfig(
    preferred_providers=["groq", "anthropic", "ollama"],
    blocked_providers=["expensive_provider"]
)
```

### YAML Configuration

Edit `config/llm_config.yaml`:

```yaml
routing:
  default_policy: "balanced"
  policies:
    cost_optimized:
      description: "Minimize costs"
      order: ["ollama", "groq", "deepseek", "openrouter"]
    
    speed_optimized:
      description: "Minimize latency"
      order: ["groq", "gemini", "openrouter", "anthropic"]
    
    quality_optimized:
      description: "Best quality models"
      order: ["anthropic", "openrouter", "gemini", "groq"]
```

## 🚀 Usage Examples

### Simple Routing

```python
from windows_use.llm import LLMRouter, TaskType

# Initialize router
router = LLMRouter(registry)

# Route a planning task
result = router.route(
    task_type=TaskType.PLANNING,
    messages=[
        {"role": "user", "content": "Plan a data analysis workflow"}
    ]
)

print(f"Selected: {result.model_name}")
print(f"Provider: {result.provider.name}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning: {result.reasoning}")
```

### Chat with Automatic Routing

```python
response = router.chat_with_routing(
    task_type=TaskType.CODING,
    messages=[
        {"role": "user", "content": "Write a Python function to sort a list"}
    ],
    tools=coding_tools,
    routing_config=RoutingConfig(policy=RoutingPolicy.QUALITY_OPTIMIZED)
)

print(f"Response: {response.content}")
print(f"Model used: {response.model}")
print(f"Latency: {response.latency_ms}ms")
```

### Advanced Routing with Fallback

```python
config = RoutingConfig(
    policy=RoutingPolicy.SPEED_OPTIMIZED,
    max_latency_ms=1000,
    fallback_enabled=True,
    preferred_providers=["groq", "gemini"]
)

response = router.chat_with_routing(
    task_type=TaskType.EXECUTION,
    messages=messages,
    tools=tools,
    routing_config=config
)
```

## 📈 Performance Tracking

The router automatically tracks performance metrics:

### Get Performance Statistics

```python
stats = router.get_performance_stats()

for model, metrics in stats.items():
    print(f"Model: {model}")
    print(f"  Average Latency: {metrics['avg_latency_ms']}ms")
    print(f"  Failure Count: {metrics['failure_count']}")
    print(f"  Total Requests: {metrics['total_requests']}")
```

### Performance Factors

- **Latency History**: Last 10 requests tracked per model
- **Failure Counts**: Models with >2 recent failures are penalized
- **Success Rate**: Successful requests boost model scores
- **Context Usage**: Models near context limits are penalized

## 🔧 Advanced Features

### Custom Scoring

The router uses a sophisticated scoring system:

```python
# Scoring factors:
# - Base availability: +10 points
# - Policy alignment: +20 points (cost/speed/quality)
# - Performance history: +5 points for good latency
# - Failure penalty: -10 points for recent failures
# - Context length: -20 points if near limit, +5 for large context
```

### Dynamic Model Selection

```python
# Router adapts based on:
# 1. Real-time provider availability
# 2. Historical performance data
# 3. Current system load
# 4. Cost constraints
# 5. Quality requirements
```

### Integration with OpenRouter

The router seamlessly integrates with OpenRouter for access to 100+ models:

```python
# OpenRouter models are automatically included in routing decisions
# Examples:
# - "openai/gpt-4o" via OpenRouter
# - "anthropic/claude-3-5-sonnet" via OpenRouter
# - "meta-llama/llama-3.1-70b-instruct" via OpenRouter
```

## 🛠️ Troubleshooting

### Common Issues

#### No Suitable Models Found

```python
# Problem: RuntimeError: No suitable models found
# Solution: Check requirements and available providers

config = RoutingConfig(
    require_tools=False,  # Relax requirements
    fallback_enabled=True
)
```

#### High Latency

```python
# Problem: Responses are too slow
# Solution: Use speed-optimized policy

config = RoutingConfig(
    policy=RoutingPolicy.SPEED_OPTIMIZED,
    max_latency_ms=1000
)
```

#### High Costs

```python
# Problem: API costs are too high
# Solution: Use cost-optimized policy

config = RoutingConfig(
    policy=RoutingPolicy.COST_OPTIMIZED,
    max_cost_per_request=0.01,
    preferred_providers=["ollama", "groq"]
)
```

#### Provider Failures

```python
# Problem: Frequent provider failures
# Solution: Enable fallback and check API keys

config = RoutingConfig(
    fallback_enabled=True,
    retry_attempts=3
)

# Check provider status
for provider_name in ["openai", "anthropic", "groq"]:
    provider = registry.get_provider(provider_name)
    if provider:
        print(f"{provider_name}: {'✅' if provider.is_available() else '❌'}")
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.getLogger('windows_use.llm.router').setLevel(logging.DEBUG)

# Check routing decision
result = router.route(task_type, messages)
print(f"Routing decision: {result.reasoning}")
print(f"Fallback options: {result.fallback_options}")
```

### Performance Optimization

```python
# Clear performance history if needed
router.performance_history.clear()
router.failure_counts.clear()

# Monitor routing decisions
stats = router.get_performance_stats()
print(f"Best performing model: {max(stats.items(), key=lambda x: x[1]['total_requests'])}")
```

---

## 📚 Related Documentation

- [OpenRouter Integration Guide](docs/OPENROUTER_INTEGRATION.md)
- [Security Documentation](SECURITY.md)
- [Performance Monitoring](PERFORMANCE.md)
- [Main README](readme.md)

---

**🚀 Ready to optimize your AI model selection? Start with the LLM Router today!**