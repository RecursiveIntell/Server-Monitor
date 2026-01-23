from __future__ import annotations

import re

KEYS = [
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "token",
    "auth_token",
    "authorization",
    "jwt",
]

KEY_PATTERN = re.compile(
    rf"(?i)^(?P<key>\s*\"?(?:{'|'.join(KEYS)})\"?)(?P<sep>\s*[:=]\s*)(?P<value>.+)$"
)
BEARER_PATTERN = re.compile(r"(?i)^\s*Authorization\s*:\s*Bearer\s+\S+\s*$")
BASIC_AUTH_URL_PATTERN = re.compile(r"(https?://)([^:@/]+):([^@/]+)@")


def redact_secrets(text: str) -> str:
    lines = text.splitlines()
    redacted_lines = []
    for line in lines:
        if BEARER_PATTERN.match(line):
            redacted_lines.append("Authorization: Bearer <redacted>")
            continue
        line = BASIC_AUTH_URL_PATTERN.sub(r"\1\2:<redacted>@", line)
        match = KEY_PATTERN.match(line)
        if match:
            redacted_lines.append(f"{match.group('key')}{match.group('sep')}<redacted>")
            continue
        redacted_lines.append(line)
    result = "\n".join(redacted_lines)
    if text.endswith("\n"):
        result += "\n"
    return result
