from recursiveops.core.redact import redact_secrets


def test_redact_key_value_pairs() -> None:
    text = "password: supersecret\napi_key=abc123\nport: 8080\n"
    redacted = redact_secrets(text)
    assert "supersecret" not in redacted
    assert "abc123" not in redacted
    assert "password: <redacted>" in redacted
    assert "api_key=<redacted>" in redacted
    assert "port: 8080" in redacted


def test_redact_authorization_header() -> None:
    text = "Authorization: Bearer abc.def.ghi\n"
    redacted = redact_secrets(text)
    assert "Bearer <redacted>" in redacted
    assert "abc.def.ghi" not in redacted


def test_redact_basic_auth_urls() -> None:
    text = "origin: https://user:pass@example.com\n"
    redacted = redact_secrets(text)
    assert "https://user:<redacted>@example.com" in redacted
    assert "pass" not in redacted
