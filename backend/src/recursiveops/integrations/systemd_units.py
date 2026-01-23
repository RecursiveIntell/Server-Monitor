from __future__ import annotations

from recursiveops.core.parsing.systemd import parse_systemctl_list
from recursiveops.core.runner import CommandRunner


def list_services(runner: CommandRunner) -> list[dict]:
    result = runner.run(
        ["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--no-pager"],
        check=True,
    )
    return parse_systemctl_list(result.stdout)
