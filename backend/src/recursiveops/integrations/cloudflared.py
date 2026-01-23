from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class CloudflaredRoute:
    hostname: str | None
    service: str



def parse_cloudflared_yaml(text: str) -> list[CloudflaredRoute]:
    data = yaml.safe_load(text) or {}
    ingress = data.get("ingress", [])
    routes: list[CloudflaredRoute] = []
    for entry in ingress:
        if not isinstance(entry, dict):
            continue
        service = entry.get("service")
        if not service:
            continue
        hostname = entry.get("hostname")
        routes.append(CloudflaredRoute(hostname=hostname, service=service))
    return routes


def load_cloudflared_config(path: str) -> list[CloudflaredRoute]:
    return parse_cloudflared_yaml(Path(path).read_text())


def build_health_targets(routes: list[CloudflaredRoute], scheme: str = "https") -> list[dict]:
    targets: list[dict] = []
    for route in routes:
        if not route.hostname:
            continue
        if route.hostname.startswith("*."):
            continue
        targets.append(
            {
                "hostname": route.hostname,
                "service": route.service,
                "url": f"{scheme}://{route.hostname}",
            }
        )
    return targets
