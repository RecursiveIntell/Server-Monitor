from recursiveops.core.log_bundle import format_log_bundle


def test_format_log_bundle_limits_lines() -> None:
    sections = {
        "systemd:ssh.service": [f"line {i}" for i in range(10)],
        "podman:abc": [f"pod {i}" for i in range(10)],
    }
    bundle = format_log_bundle(sections, limit=5)
    assert "systemd:ssh.service" in bundle
    assert "podman:abc" in bundle
    assert bundle.count("\n") <= 10
