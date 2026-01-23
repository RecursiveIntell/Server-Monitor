from recursiveops.core.parsing.systemd import parse_systemctl_list


def test_parse_systemctl_list_basic() -> None:
    text = "sshd.service loaded active running OpenSSH server daemon\n"
    services = parse_systemctl_list(text)
    assert services == [
        {
            "unit": "sshd.service",
            "load": "loaded",
            "active": "active",
            "sub": "running",
            "description": "OpenSSH server daemon",
        }
    ]


def test_parse_systemctl_list_with_marker() -> None:
    text = "* sshd.service loaded failed failed OpenSSH server daemon\n"
    services = parse_systemctl_list(text)
    assert services == [
        {
            "unit": "sshd.service",
            "load": "loaded",
            "active": "failed",
            "sub": "failed",
            "description": "OpenSSH server daemon",
        }
    ]
