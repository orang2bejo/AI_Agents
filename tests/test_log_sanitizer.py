from windows_use.obs.log_sanitizer import redact


def test_redact_token_email_phone():
    text = "token abcdef0123456789abcdef0123456789 email test@example.com phone 081234567890"
    result = redact(text)
    assert "abcdef0123456789abcdef0123456789" not in result
    assert "test@example.com" not in result
    assert "081234567890" not in result
