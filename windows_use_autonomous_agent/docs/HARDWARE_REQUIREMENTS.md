# 🖥️ Hardware Requirements & Optimization Guide

## Overview

This guide provides detailed hardware requirements, optimization tips, and troubleshooting for Jarvis AI to ensure optimal performance across different system configurations.

---

## 📊 System Requirements Matrix

### Minimum Requirements (Basic Functionality)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 10 (1903+) / Windows 11 | Core compatibility |
| **CPU** | Intel Core i3-8100 / AMD Ryzen 3 2200G | Basic AI processing |
| **RAM** | 4 GB | Core system operations |
| **Storage** | 3 GB free space (HDD) | Basic installation |
| **GPU** | Integrated graphics | CPU-only AI processing |
| **Network** | 5 Mbps | Dependency downloads |

### Recommended Requirements (Optimal Performance)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 11 (latest) | Best compatibility |
| **CPU** | Intel Core i7-10700K / AMD Ryzen 7 3700X | Fast AI processing |
| **RAM** | 16 GB DDR4 | Large model handling |
| **Storage** | 10 GB free space (SSD) | Fast I/O operations |
| **GPU** | NVIDIA RTX 3060 (8GB VRAM) | GPU acceleration |
| **Network** | 25+ Mbps | Real-time AI features |

### Professional Requirements (Maximum Performance)

| Component | Specification | Purpose |
|-----------|---------------|----------|
| **OS** | Windows 11 Pro (latest) | Enterprise features |
| **CPU** | Intel Core i9-12900K / AMD Ryzen 9 5900X | Maximum processing power |
| **RAM** | 32+ GB DDR4/DDR5 | Large-scale AI operations |
| **Storage** | 50+ GB free space (NVMe SSD) | Ultra-fast operations |
| **GPU** | NVIDIA RTX 4070+ (12GB+ VRAM) | Advanced AI acceleration |
| **Network** | 100+ Mbps | Cloud AI integration |

---

## 🎯 GPU Configuration Guide

### NVIDIA GPU Setup

#### Supported GPUs
- **Entry Level:** GTX 1060 6GB, GTX 1660 Super
- **Mid Range:** RTX 3060, RTX 3070, RTX 4060
- **High End:** RTX 3080, RTX 4070, RTX 4080, RTX 4090
- **Professional:** RTX A4000, RTX A5000, RTX A6000

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

#### Basic Usage (Text Processing)
- **CPU:** Any modern quad-core
- **RAM:** 8 GB
- **GPU:** Not required
- **Storage:** Standard SSD

#### Voice Processing
- **CPU:** 6+ cores recommended
- **RAM:** 12+ GB
- **GPU:** Optional but helpful
- **Audio:** Dedicated sound card recommended

#### Advanced AI Features
- **CPU:** 8+ cores
- **RAM:** 16+ GB
- **GPU:** NVIDIA RTX 3060+ required
- **Storage:** Fast NVMe SSD

#### Enterprise/Professional
- **CPU:** 12+ cores (i9/Ryzen 9)
- **RAM:** 32+ GB
- **GPU:** RTX 4070+ or multiple GPUs
- **Storage:** Enterprise NVMe SSD
- **Network:** Dedicated high-speed connection

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