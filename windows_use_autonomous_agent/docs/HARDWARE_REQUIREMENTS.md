# 🖥️ Hardware Requirements & Optimization Guide

## Overview

This guide provides detailed hardware requirements, optimization tips, and troubleshooting for Jarvis AI to ensure optimal performance across different system configurations.

---

## 📊 System Requirements Matrix

### Minimum Requirements (Basic Functionality)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 10 (1903+) / Windows 11 | Core compatibility |
| **CPU** | Intel Core i5-8400 / AMD Ryzen 5 2600 | Multi-provider LLM processing |
| **RAM** | 8 GB DDR4 | Core system + LLM operations |
| **Storage** | 5 GB free space (SSD recommended) | Basic installation + models |
| **GPU** | Integrated graphics (Intel UHD 630+) | CPU-only AI processing |
| **Network** | 10 Mbps | Cloud LLM providers + EVI |
| **Audio** | Built-in microphone/speakers | Voice interaction (EVI) |

### Recommended Requirements (Optimal Performance)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 11 (latest) | Best compatibility + features |
| **CPU** | Intel Core i7-12700K / AMD Ryzen 7 5800X | Multi-provider switching + local LLM |
| **RAM** | 16 GB DDR4/DDR5 | Large model handling + caching |
| **Storage** | 15 GB free space (NVMe SSD) | Fast model loading + caching |
| **GPU** | NVIDIA RTX 4060 (8GB VRAM) | Local LLM inference + acceleration |
| **Network** | 50+ Mbps | Real-time cloud AI + EVI streaming |
| **Audio** | Dedicated USB microphone + headset | High-quality voice processing |

### Professional Requirements (Maximum Performance)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 11 Pro (latest) | Enterprise features + security |
| **CPU** | Intel Core i9-13900K / AMD Ryzen 9 7900X | Maximum multi-provider performance |
| **RAM** | 32+ GB DDR5 | Large-scale local LLM + multi-tasking |
| **Storage** | 100+ GB free space (Gen4 NVMe SSD) | Multiple local models + fast caching |
| **GPU** | NVIDIA RTX 4080+ (16GB+ VRAM) | Multiple local LLM + GPU acceleration |
| **Network** | 1 Gbps+ | Enterprise cloud AI + real-time features |
| **Audio** | Professional audio interface | Studio-quality voice processing |

---

## 🤖 Multi-Provider LLM Requirements

### Local LLM (Ollama) Requirements

| Model Size | RAM Required | GPU VRAM | Storage | Performance |
|------------|--------------|----------|---------|-------------|
| **7B models** | 8 GB | 6 GB+ | 5 GB | Good for basic tasks |
| **13B models** | 16 GB | 10 GB+ | 8 GB | Better reasoning |
| **30B+ models** | 32 GB | 20 GB+ | 20 GB | Professional quality |
| **70B+ models** | 64 GB | 40 GB+ | 50 GB | Enterprise grade |

### Cloud Provider Optimization

| Provider | Latency Priority | Bandwidth | Concurrent Requests |
|----------|------------------|-----------|--------------------|
| **OpenRouter** | Medium | 25+ Mbps | 5-10 |
| **Groq** | Ultra-low | 50+ Mbps | 10-20 |
| **Gemini** | Low | 10+ Mbps | 3-5 |
| **Anthropic** | Medium | 20+ Mbps | 5-10 |
| **OpenAI** | Medium | 15+ Mbps | 5-15 |

### Multi-Provider Switching Performance

- **CPU:** 8+ cores for seamless provider switching
- **RAM:** 16+ GB for caching multiple provider responses
- **Network:** Stable 50+ Mbps for failover scenarios
- **Storage:** Fast SSD for response caching

---

## 🎙️ EVI Integration Requirements

### Voice Processing Hardware

| Component | Minimum | Recommended | Professional |
|-----------|---------|-------------|-------------|
| **Microphone** | Built-in laptop mic | USB condenser mic | XLR audio interface |
| **Audio Interface** | Integrated sound | Dedicated USB audio | Professional audio interface |
| **Processing** | 4 cores | 6+ cores | 8+ cores |
| **RAM** | 4 GB | 8 GB | 16+ GB |
| **Latency** | <500ms | <200ms | <100ms |

### Real-time Voice Features

- **Network:** 25+ Mbps for real-time EVI streaming
- **CPU:** Low-latency audio processing capabilities
- **Audio Drivers:** ASIO drivers recommended for professional use
- **Background Noise:** Noise cancellation hardware/software

---

## 🎯 GPU Configuration Guide

### NVIDIA GPU Setup

#### Supported GPUs (Updated for Local LLM)
- **Entry Level:** GTX 1660 Super (6GB), RTX 3060 (8GB)
- **Mid Range:** RTX 4060 (8GB), RTX 4060 Ti (16GB), RTX 3070 (8GB)
- **High End:** RTX 4070 (12GB), RTX 4080 (16GB), RTX 4090 (24GB)
- **Professional:** RTX A4000 (16GB), RTX A5000 (24GB), RTX A6000 (48GB)
- **Data Center:** H100 (80GB), A100 (40GB/80GB), V100 (32GB)

#### CUDA Installation
```bash
# Check current CUDA version
nvidia-smi

# Install CUDA Toolkit 11.8 (recommended)
# Download from: https://developer.nvidia.com/cuda-11-8-0-download-archive

# Verify installation
nvcc --version
```

#### PyTorch GPU Setup
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU detection
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"}')"
```

### AMD GPU Setup

#### Supported GPUs
- **Entry Level:** RX 580, RX 5500 XT
- **Mid Range:** RX 6600, RX 6700 XT, RX 7600
- **High End:** RX 6800 XT, RX 7800 XT, RX 7900 XTX

#### ROCm Installation
```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2

# Note: ROCm support on Windows is limited
# Consider using CPU mode for AMD GPUs on Windows
```

### Intel GPU Setup

#### Supported GPUs
- **Integrated:** Intel Iris Xe, Intel UHD Graphics
- **Discrete:** Intel Arc A380, A750, A770

#### Intel Extension for PyTorch
```bash
# Install Intel Extension
pip install intel-extension-for-pytorch

# Verify installation
python -c "import intel_extension_for_pytorch as ipex; print('Intel GPU available:', ipex.xpu.is_available())"
```

---

## 🚀 Performance Optimization

### CPU Optimization

#### Multi-threading Configuration
```json
// config/jarvis_config.json
{
  "performance": {
    "cpu_cores": "auto",  // or specify number
    "enable_multiprocessing": true,
    "thread_pool_size": 4,
    "enable_cpu_optimization": true
  }
}
```

#### Windows Power Settings
```bash
# Set high performance mode
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable CPU throttling
powercfg /setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100
```

### Memory Optimization

#### Virtual Memory Settings
1. **System Properties** → **Advanced** → **Performance Settings**
2. **Advanced** → **Virtual Memory** → **Change**
3. Set custom size: Initial = RAM size, Maximum = 2x RAM size

#### Memory Configuration
```json
// config/jarvis_config.json
{
  "memory": {
    "max_memory_usage": "80%",
    "enable_memory_optimization": true,
    "garbage_collection_threshold": 0.8,
    "cache_size_mb": 1024
  }
}
```

### GPU Memory Optimization

#### NVIDIA GPU Settings
```python
# In Python configuration
import torch

# Enable memory fraction
torch.cuda.set_per_process_memory_fraction(0.8)

# Enable memory growth
torch.cuda.empty_cache()

# Enable mixed precision
torch.backends.cudnn.benchmark = True
```

#### Memory Monitoring
```bash
# Monitor GPU memory usage
nvidia-smi -l 1

# Check memory in Python
python -c "import torch; print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')"
```

---

## 🔧 Hardware Diagnostics

### System Information Script
```python
# hardware_check.py
import psutil
import platform
import subprocess
import sys

def check_system_info():
    print("=== SYSTEM INFORMATION ===")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
    
    memory = psutil.virtual_memory()
    print(f"RAM: {memory.total / 1024**3:.1f} GB total, {memory.available / 1024**3:.1f} GB available")
    
    disk = psutil.disk_usage('/')
    print(f"Disk: {disk.total / 1024**3:.1f} GB total, {disk.free / 1024**3:.1f} GB free")

def check_gpu_info():
    print("\n=== GPU INFORMATION ===")
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu = torch.cuda.get_device_properties(i)
                print(f"GPU {i}: {gpu.name}")
                print(f"  Memory: {gpu.total_memory / 1024**3:.1f} GB")
                print(f"  Compute Capability: {gpu.major}.{gpu.minor}")
        else:
            print("No CUDA-capable GPU detected")
    except ImportError:
        print("PyTorch not installed - cannot check GPU")

def check_audio_devices():
    print("\n=== AUDIO DEVICES ===")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']} ({'input' if device['max_input_channels'] > 0 else 'output'})")
    except ImportError:
        print("sounddevice not installed - cannot check audio")

if __name__ == "__main__":
    check_system_info()
    check_gpu_info()
    check_audio_devices()
```

### Performance Benchmark
```python
# performance_test.py
import time
import torch
import numpy as np

def cpu_benchmark():
    print("=== CPU BENCHMARK ===")
    start_time = time.time()
    
    # Matrix multiplication test
    a = np.random.rand(1000, 1000)
    b = np.random.rand(1000, 1000)
    c = np.dot(a, b)
    
    cpu_time = time.time() - start_time
    print(f"CPU Matrix Multiplication (1000x1000): {cpu_time:.2f} seconds")
    return cpu_time

def gpu_benchmark():
    print("\n=== GPU BENCHMARK ===")
    if not torch.cuda.is_available():
        print("No GPU available for testing")
        return None
    
    device = torch.device('cuda')
    start_time = time.time()
    
    # GPU matrix multiplication test
    a = torch.rand(1000, 1000, device=device)
    b = torch.rand(1000, 1000, device=device)
    c = torch.mm(a, b)
    torch.cuda.synchronize()
    
    gpu_time = time.time() - start_time
    print(f"GPU Matrix Multiplication (1000x1000): {gpu_time:.2f} seconds")
    return gpu_time

if __name__ == "__main__":
    cpu_time = cpu_benchmark()
    gpu_time = gpu_benchmark()
    
    if gpu_time:
        speedup = cpu_time / gpu_time
        print(f"\nGPU Speedup: {speedup:.1f}x faster than CPU")
```

---

## 🛠️ Troubleshooting Guide

### Common GPU Issues

#### Issue: "CUDA out of memory"
**Solutions:**
```bash
# Reduce batch size
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"

# Monitor GPU usage
watch -n 1 nvidia-smi
```

#### Issue: "No CUDA-capable device"
**Solutions:**
1. Check GPU compatibility: `nvidia-smi`
2. Reinstall CUDA drivers
3. Verify PyTorch CUDA version
4. Check Windows Device Manager

#### Issue: "GPU not detected"
**Solutions:**
1. Update GPU drivers
2. Check PCIe connection
3. Verify power supply
4. Test with different PCIe slot

### CPU Performance Issues

#### Issue: High CPU usage
**Solutions:**
```bash
# Check running processes
tasklist /svc

# Set process priority
wmic process where name="python.exe" CALL setpriority "high priority"

# Limit CPU cores for other processes
# Use Task Manager → Details → Set Affinity
```

#### Issue: Slow processing
**Solutions:**
1. Enable CPU optimization in config
2. Close unnecessary applications
3. Check for thermal throttling
4. Increase virtual memory

### Memory Issues

#### Issue: "Out of memory" errors
**Solutions:**
```bash
# Check memory usage
tasklist /fi "imagename eq python.exe" /fo table

# Increase virtual memory
# System Properties → Advanced → Performance → Virtual Memory

# Enable memory optimization
# Edit config/jarvis_config.json
```

#### Issue: Memory leaks
**Solutions:**
1. Restart Jarvis AI periodically
2. Enable garbage collection
3. Monitor memory usage
4. Check for memory-intensive processes

---

## 📈 Performance Monitoring

### Real-time Monitoring
```python
# monitor.py
import psutil
import time
import torch

def monitor_system():
    while True:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # GPU usage (if available)
        gpu_usage = "N/A"
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
            gpu_usage = f"{gpu_memory:.1f}%"
        
        print(f"CPU: {cpu_percent:5.1f}% | RAM: {memory_percent:5.1f}% | GPU: {gpu_usage}")
        time.sleep(1)

if __name__ == "__main__":
    monitor_system()
```

### Performance Logging
```json
// config/logging.yaml
loggers:
  performance:
    level: INFO
    handlers: [performance_file]
    
handlers:
  performance_file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/performance.log
    maxBytes: 10485760
    backupCount: 5
```

---

## 🎯 Optimization Recommendations

### For Different Use Cases

#### Cloud-Only LLM Usage
- **CPU:** Intel i5-8400 / AMD Ryzen 5 2600
- **RAM:** 8 GB
- **GPU:** Not required (integrated graphics sufficient)
- **Storage:** Standard SSD (5 GB)
- **Network:** 25+ Mbps stable connection

#### Hybrid Cloud + Local LLM
- **CPU:** Intel i7-12700K / AMD Ryzen 7 5800X
- **RAM:** 16 GB DDR4/DDR5
- **GPU:** NVIDIA RTX 4060 (8GB VRAM)
- **Storage:** NVMe SSD (20 GB)
- **Network:** 50+ Mbps for seamless switching

#### Local LLM + EVI Integration
- **CPU:** Intel i9-13900K / AMD Ryzen 9 7900X
- **RAM:** 32 GB DDR5
- **GPU:** NVIDIA RTX 4080 (16GB VRAM)
- **Storage:** Gen4 NVMe SSD (50 GB)
- **Audio:** Professional USB audio interface
- **Network:** 100+ Mbps for cloud fallback

#### Enterprise Multi-Provider Setup
- **CPU:** Intel i9-13900KS / AMD Ryzen 9 7950X
- **RAM:** 64+ GB DDR5
- **GPU:** Multiple RTX 4090 or H100
- **Storage:** Enterprise NVMe RAID (200+ GB)
- **Network:** Dedicated 1 Gbps+ connection
- **Audio:** Professional XLR audio setup

#### Development & Testing Environment
- **CPU:** 12+ cores for parallel testing
- **RAM:** 32+ GB for multiple model loading
- **GPU:** RTX 4070+ for model testing
- **Storage:** Fast NVMe with 100+ GB free
- **Network:** Stable high-speed for API testing

---

## 📊 Performance Benchmarks

### LLM Inference Speed (Tokens/Second)

| Hardware Configuration | 7B Model | 13B Model | 30B Model | 70B Model |
|------------------------|----------|-----------|-----------|----------|
| **RTX 3060 (8GB)** | 25-30 | 15-20 | N/A | N/A |
| **RTX 4060 (8GB)** | 35-40 | 20-25 | N/A | N/A |
| **RTX 4070 (12GB)** | 45-50 | 30-35 | 15-20 | N/A |
| **RTX 4080 (16GB)** | 60-70 | 40-50 | 25-30 | 10-15 |
| **RTX 4090 (24GB)** | 80-100 | 60-70 | 40-50 | 20-25 |
| **H100 (80GB)** | 150-200 | 120-150 | 80-100 | 50-60 |

### Multi-Provider Response Times

| Provider | Average Latency | 95th Percentile | Throughput (req/min) |
|----------|-----------------|-----------------|---------------------|
| **Groq** | 200-500ms | 800ms | 100-200 |
| **OpenRouter** | 1-3s | 5s | 50-100 |
| **Gemini** | 2-4s | 8s | 30-60 |
| **Anthropic** | 3-6s | 10s | 20-40 |
| **Local Ollama** | 500ms-5s | 10s | 10-30 |

### EVI Voice Processing Latency

| Hardware Setup | Voice-to-Text | Processing | Text-to-Speech | Total Latency |
|----------------|---------------|------------|----------------|---------------|
| **Basic Setup** | 200-500ms | 1-3s | 200-500ms | 1.4-4s |
| **Recommended** | 100-200ms | 500ms-1s | 100-200ms | 700ms-1.4s |
| **Professional** | 50-100ms | 200-500ms | 50-100ms | 300-700ms |

---

## 💰 Cost Analysis & ROI

### Hardware Investment Tiers

| Tier | Initial Cost | Monthly Cloud Cost | Break-even | Use Case |
|------|--------------|-------------------|------------|----------|
| **Cloud-Only** | $0-500 | $50-200 | Immediate | Light usage |
| **Hybrid Setup** | $1,500-3,000 | $20-100 | 6-12 months | Regular usage |
| **Local-First** | $3,000-8,000 | $10-50 | 12-24 months | Heavy usage |
| **Enterprise** | $10,000+ | $0-100 | 24+ months | Professional |

### Operating Cost Comparison (Monthly)

| Usage Pattern | Cloud-Only | Hybrid | Local-First |
|---------------|------------|--------|-------------|
| **Light (100 requests/day)** | $30-50 | $20-30 | $15-25 |
| **Medium (500 requests/day)** | $100-200 | $50-100 | $25-50 |
| **Heavy (2000 requests/day)** | $400-800 | $100-200 | $50-100 |
| **Enterprise (10k+ requests/day)** | $2000+ | $500-1000 | $100-300 |

### Power Consumption

| Hardware | Idle Power | Load Power | Monthly Cost (24/7) |
|----------|------------|------------|--------------------|
| **CPU-only setup** | 50-100W | 150-250W | $15-30 |
| **RTX 4060 setup** | 80-120W | 200-300W | $25-40 |
| **RTX 4080 setup** | 100-150W | 350-450W | $40-60 |
| **RTX 4090 setup** | 120-180W | 450-600W | $50-80 |

---

## 📞 Support Resources

### Hardware Compatibility Check
- Run `python hardware_check.py` for detailed analysis
- Check [Hardware Compatibility Database](link)
- Contact support with system specifications

### Performance Optimization Services
- Professional system tuning available
- Custom configuration for enterprise deployments
- Hardware upgrade recommendations

### Community Resources
- Hardware discussion forum
- Performance optimization guides
- User-contributed benchmarks

---

**Need help with hardware optimization? Check our [Performance Monitoring Guide](PERFORMANCE.md) or contact our support team!**