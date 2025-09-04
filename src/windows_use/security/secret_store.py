"""Simple wrapper around Windows Credential Manager via keyring."""

from __future__ import annotations

from typing import Optional

try:
    import keyring
except Exception:  # pragma: no cover - keyring may not be available on CI
    keyring = None

_SERVICE = "jarvis-ai"


def get_secret(name: str) -> Optional[str]:
    if not keyring:
        return None
    try:
        return keyring.get_password(_SERVICE, name)
    except Exception:
        return None


def set_secret(name: str, value: str) -> None:
    if not keyring:
        raise RuntimeError("keyring backend not available")
    keyring.set_password(_SERVICE, name, value)


def delete_secret(name: str) -> None:
    if not keyring:
        return
    try:
        keyring.delete_password(_SERVICE, name)
    except Exception:
        pass
