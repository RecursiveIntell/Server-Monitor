from __future__ import annotations


def parse_ss(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = lines[0]
    entries = []
    for line in lines[1:]:
        entries.append({"line": line, "header": header})
    return entries
