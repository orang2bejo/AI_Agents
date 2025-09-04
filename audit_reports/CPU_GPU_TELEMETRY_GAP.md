# CPU/GPU Telemetry Gap

## Current State
- **LLM (Ollama)**: HTTP client; no device telemetry. GPU usage determined by server.
- **STT (Whisper)**: `voice_input.py` loads model without specifying device (defaults to CPU)【b8a58e†L70-L75】
- **TTS (Piper)**: Uses ONNX model via CPU; no GPU acceleration or reporting【6b1380†L35-L80】
- No scripts for runtime health or hardware checks.

## Recommended Patches
```python
 codex/conduct-comprehensive-audit-for-jarvis-ai-project-8yncbg
# obs/device_telemetry.py (new)
=======
# utils/device_telemetry.py (new)
 main
import psutil, json

def snapshot() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(),
        "mem_percent": psutil.virtual_memory().percent,
    }
```
```python
# scripts/healthcheck.py (new)
 codex/conduct-comprehensive-audit-for-jarvis-ai-project-8yncbg
from obs.device_telemetry import snapshot
=======
from utils.device_telemetry import snapshot
 main

if __name__ == "__main__":
    stats = snapshot()
    print(json.dumps(stats, indent=2))
```

## Telemetry Plan
- Capture CPU/GPU metrics per component (LLM/STT/TTS) before and after operations.
- Emit JSON summary for CI dashboards.
- Extend to GPU via `torch.cuda` or `onnxruntime` when available.
