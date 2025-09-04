import pytest
from unittest.mock import AsyncMock

pytest.importorskip("playwright.async_api")
from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError  # type: ignore

from windows_use.web.security_utils import (
    Mode,
    check_allowlist,
    goto_with_security,
    handle_otp,
    require_confirmation,
)


def test_check_allowlist_rejects():
    with pytest.raises(ValueError):
        check_allowlist("https://evil.com", ["example.com"])


def test_require_confirmation():
    with pytest.raises(PermissionError):
        require_confirmation(Mode.ASSISTIVE, True, lambda: False)
    require_confirmation(Mode.ASSISTIVE, True, lambda: True)


def test_handle_otp_switches_mode():
    mode, paused = handle_otp(Mode.FULL_AUTO, True)
    assert mode == Mode.SEMI_AUTO and paused


@pytest.mark.asyncio
async def test_goto_with_security_propagates_timeout():
    page = AsyncMock()
    page.goto.side_effect = PlaywrightTimeoutError("timeout")
    with pytest.raises(PlaywrightTimeoutError):
        await goto_with_security(page, "https://example.com", ["example.com"])
    page.goto.side_effect = PlaywrightError("error")
    with pytest.raises(PlaywrightError):
        await goto_with_security(page, "https://example.com", ["example.com"])
