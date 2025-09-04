from __future__ import annotations

import json
import os
import time

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

try:
    import onnxruntime as ort
except Exception:  # pragma: no cover
    ort = None


def main() -> None:
    providers = []
    if ort:
        providers = ort.get_available_providers()
    gpu = "CPU"
    if torch and torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
    stt_device = os.getenv("JARVIS_STT_DEVICE", "auto")

    info = {"providers": providers, "gpu": gpu, "stt_device": stt_device}
    print(json.dumps(info, indent=2))

    try:
        import ollama  # type: ignore

        start = time.time()
        ollama.generate(
            model="llama2", prompt="healthcheck", options={"num_predict": 10}
        )
        latency = time.time() - start
        print(f"Ollama generated 10 tokens in {latency:.2f}s")
    except Exception as e:  # pragma: no cover - ollama optional
        print(f"Ollama check skipped: {e}")


if __name__ == "__main__":
    main()
