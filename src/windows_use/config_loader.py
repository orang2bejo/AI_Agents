from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml

from .config_schema import ModelsConfig, SecurityConfig
from .security.secret_store import get_secret


_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _resolve(value: Any) -> Any:
    if isinstance(value, str):
        match = _ENV_PATTERN.fullmatch(value)
        if match:
            name = match.group(1)
            return os.getenv(name) or get_secret(name)
    return value


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return _traverse(data)


def _traverse(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _traverse(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_traverse(v) for v in obj]
    return _resolve(obj)


def load_security_config(path: str | Path = "config/security.yaml") -> SecurityConfig:
    data = _load_yaml(Path(path))
    config = SecurityConfig(**data)
    if not config.web.allowlist:
        raise ValueError("allowlist must not be empty")
    if config.mode_default != config.mode_default.__class__.ASSISTIVE:
        raise ValueError("mode_default must be ASSISTIVE")
    return config


def load_models_config(path: str | Path = "config/models.yaml") -> ModelsConfig:
    data = _load_yaml(Path(path))
    config = ModelsConfig(**data)
    if not config.offline:
        config.offline = "safe"
    return config
