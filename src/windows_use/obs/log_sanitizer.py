from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[A-Za-z0-9]{32,}")
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+")
PHONE_RE = re.compile(r"\b\d{9,15}\b")


def redact(text: str) -> str:
    """Mask obvious secrets from log text."""
    text = TOKEN_RE.sub("[REDACTED]", text)
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text
