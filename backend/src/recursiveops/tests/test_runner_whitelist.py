from recursiveops.core.whitelist import validate_command


def test_whitelist_allows_expected_systemctl_list() -> None:
    decision = validate_command(
        [
            "systemctl",
            "list-units",
            "--type=service",
            "--all",
            "--no-legend",
            "--no-pager",
        ]
    )
    assert decision.allowed is True


def test_whitelist_blocks_shell_and_rm() -> None:
    decision = validate_command(["bash", "-c", "echo hi"])
    assert decision.allowed is False
    assert "not allowed" in decision.reason

    decision = validate_command(["rm", "-rf", "/"])
    assert decision.allowed is False


def test_whitelist_allows_journalctl_global_tail() -> None:
    decision = validate_command(["journalctl", "-n", "200", "--no-pager", "-o", "short-iso"])
    assert decision.allowed is True
