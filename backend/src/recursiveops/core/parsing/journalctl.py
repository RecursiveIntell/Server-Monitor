from __future__ import annotations


def parse_journal_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]
