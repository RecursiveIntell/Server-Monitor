from __future__ import annotations

from typing import Dict, Iterable, List


def format_log_bundle(sections: Dict[str, Iterable[str]], limit: int = 500) -> str:
    lines: List[str] = []
    for name, entries in sections.items():
        lines.append(f"=== {name} ===")
        max_entries = max(limit - 1, 0)
        count = 0
        for entry in entries:
            if count >= max_entries:
                break
            lines.append(entry)
            count += 1
    return "\n".join(lines).strip()
