from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FstabEntry:
    source: str
    mount_point: str
    fs_type: str
    options: str
    dump: str
    passno: str



def parse_fstab(text: str) -> list[FstabEntry]:
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        entries.append(FstabEntry(*parts[:6]))
    return entries
