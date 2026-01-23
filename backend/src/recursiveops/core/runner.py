from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List

from recursiveops.core.whitelist import validate_command


class CommandNotAllowed(Exception):
    pass


class CommandFailed(Exception):
    pass


@dataclass
class CommandResult:
    argv: List[str]
    returncode: int
    stdout: str
    stderr: str


class CommandRunner:
    def run(
        self, argv: List[str], timeout: int = 30, check: bool = False, use_sudo: bool = False
    ) -> CommandResult:
        if use_sudo:
            argv = ["sudo", "-n"] + argv
        decision = validate_command(argv)
        if not decision.allowed:
            raise CommandNotAllowed(decision.reason)
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        result = CommandResult(
            argv=argv,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if check and completed.returncode != 0:
            raise CommandFailed(completed.stderr or "command failed")
        return result
