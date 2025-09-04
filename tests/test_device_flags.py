import pytest
from unittest import mock

pytest.importorskip("whisper")
from windows_use.tools.voice_input import VoiceInput


def test_stt_device_env(monkeypatch):
    called = {}

    def fake_load(model, device="cpu"):
        called["device"] = device

        class M:
            pass

        return M()

    monkeypatch.setenv("JARVIS_STT_DEVICE", "cpu")
    with mock.patch("windows_use.tools.voice_input.whisper.load_model", fake_load):
        VoiceInput()
    assert called["device"] == "cpu"
