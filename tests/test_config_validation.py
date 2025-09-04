import tempfile
from pathlib import Path

import pytest

from windows_use.config_loader import load_models_config, load_security_config


def test_security_config_allowlist_empty():
    data = "mode_default: ASSISTIVE\nweb:\n  allowlist: []\n  require_confirm_on_submit: true\n"
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(data)
        path = Path(f.name)
    with pytest.raises(Exception):
        load_security_config(path)


def test_security_config_valid():
    data = "mode_default: ASSISTIVE\nweb:\n  allowlist: ['example.com']\n  require_confirm_on_submit: true\n"
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(data)
        path = Path(f.name)
    cfg = load_security_config(path)
    assert cfg.web.allowlist == ["example.com"]


def test_models_config_default_offline():
    data = "planner: gpt\n"
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(data)
        path = Path(f.name)
    cfg = load_models_config(path)
    assert cfg.offline == "safe"
