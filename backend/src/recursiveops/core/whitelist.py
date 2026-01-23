from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class WhitelistDecision:
    allowed: bool
    reason: str


CommandMatcher = Callable[[List[str]], bool]

UNIT_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]+\.(service|socket|timer|target|mount)$")


def _is_unit(name: str) -> bool:
    return bool(UNIT_PATTERN.match(name))


def _is_int(value: str) -> bool:
    return value.isdigit()


def _match_systemctl(args: List[str]) -> bool:
    if args == ["list-units", "--type=service", "--all", "--no-legend", "--no-pager"]:
        return True
    if len(args) == 3 and args[0] == "show" and _is_unit(args[1]) and args[2].startswith("--property="):
        return True
    if len(args) == 2 and args[0] in {"status", "restart", "reload", "stop", "start"} and _is_unit(args[1]):
        return True
    if args == ["daemon-reload"]:
        return True
    return False


def _match_journalctl(args: List[str]) -> bool:
    if (
        len(args) == 7
        and args[0] == "-u"
        and _is_unit(args[1])
        and args[2] == "-n"
        and _is_int(args[3])
        and args[4] == "--no-pager"
        and args[5] == "-o"
        and args[6] == "short-iso"
    ):
        return True
    if (
        len(args) == 5
        and args[0] == "-n"
        and _is_int(args[1])
        and args[2] == "--no-pager"
        and args[3] == "-o"
        and args[4] == "short-iso"
    ):
        return True
    return False


def _match_podman(args: List[str]) -> bool:
    if args in (["ps", "--all", "--format", "json"], ["ps", "--all", "--format=json"]):
        return True
    if len(args) == 4 and args[0] == "logs" and args[1] == "--tail" and _is_int(args[2]):
        return True
    return False


def _match_findmnt(args: List[str]) -> bool:
    return args == ["--json"]


def _match_ss(args: List[str]) -> bool:
    return args == ["-tulpen"]


def _match_firewall(args: List[str]) -> bool:
    return args == ["--list-all"]


@dataclass
class CommandSpec:
    name: str
    allow_sudo: bool
    matcher: CommandMatcher


COMMAND_SPECS = [
    CommandSpec("systemctl", True, _match_systemctl),
    CommandSpec("journalctl", True, _match_journalctl),
    CommandSpec("podman", True, _match_podman),
    CommandSpec("findmnt", False, _match_findmnt),
    CommandSpec("ss", False, _match_ss),
    CommandSpec("firewall-cmd", True, _match_firewall),
]


def validate_command(argv: List[str]) -> WhitelistDecision:
    if not argv:
        return WhitelistDecision(False, "empty command not allowed")
    use_sudo = False
    if argv[0] == "sudo":
        if len(argv) < 2 or argv[1] != "-n":
            return WhitelistDecision(False, "sudo requires -n")
        use_sudo = True
        argv = argv[2:]
    if not argv:
        return WhitelistDecision(False, "missing command after sudo")
    for spec in COMMAND_SPECS:
        if argv[0] != spec.name:
            continue
        if not spec.matcher(argv[1:]):
            return WhitelistDecision(False, "arguments not allowed")
        if use_sudo and not spec.allow_sudo:
            return WhitelistDecision(False, "sudo not allowed for command")
        return WhitelistDecision(True, "allowed")
    return WhitelistDecision(False, "command not allowed")
