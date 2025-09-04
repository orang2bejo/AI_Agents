from __future__ import annotations

from enum import Enum
from typing import Callable, Sequence, Tuple
from urllib.parse import urlparse

from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError  # type: ignore


class Mode(str, Enum):
    ASSISTIVE = "ASSISTIVE"
    SEMI_AUTO = "SEMI_AUTO"
    FULL_AUTO = "FULL_AUTO"


def check_allowlist(url: str, allowlist: Sequence[str]) -> None:
    domain = urlparse(url).hostname or ""
    if domain not in allowlist:
        raise ValueError("Domain not allowed")


def require_confirmation(
    mode: Mode, require: bool, confirmer: Callable[[], bool]
) -> None:
    if mode in (Mode.ASSISTIVE, Mode.SEMI_AUTO) and require:
        if not confirmer():
            raise PermissionError("User confirmation required")


def handle_otp(mode: Mode, otp_detected: bool) -> Tuple[Mode, bool]:
    if otp_detected and mode == Mode.FULL_AUTO:
        return Mode.SEMI_AUTO, True
    return mode, False


async def goto_with_security(page, url: str, allowlist: Sequence[str]) -> None:
    check_allowlist(url, allowlist)
    try:
        await page.goto(url)
    except PlaywrightTimeoutError:
        raise
    except PlaywrightError:
        raise
