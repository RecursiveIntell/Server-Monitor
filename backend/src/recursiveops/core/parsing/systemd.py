from __future__ import annotations

UNIT_SUFFIXES = (".service", ".socket", ".timer", ".target", ".mount")


def _looks_like_unit(value: str) -> bool:
    return any(value.endswith(suffix) for suffix in UNIT_SUFFIXES)


def parse_systemctl_list(text: str) -> list[dict]:
    services = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        if len(parts) >= 5 and not _looks_like_unit(parts[0]) and _looks_like_unit(parts[1]):
            parts = parts[1:]
        if len(parts) < 4:
            continue
        unit, load, active, sub = parts[:4]
        description = " ".join(parts[4:]) if len(parts) > 4 else ""
        services.append(
            {
                "unit": unit,
                "load": load,
                "active": active,
                "sub": sub,
                "description": description,
            }
        )
    return services
