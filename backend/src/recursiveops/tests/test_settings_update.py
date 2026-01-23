from recursiveops.settings_update import apply_llm_update


def test_apply_llm_update_merges_fields() -> None:
    config = {
        "llm": {
            "enabled": True,
            "provider": "ollama",
            "ollama": {"base_url": "http://127.0.0.1:11434", "model": "qwen"},
            "cloud": {"enabled": False, "provider": "stub"},
        }
    }
    updated = apply_llm_update(
        config,
        {
            "enabled": False,
            "ollama": {"model": "qwen2.5:7b"},
        },
    )
    assert updated["llm"]["enabled"] is False
    assert updated["llm"]["ollama"]["model"] == "qwen2.5:7b"
    assert updated["llm"]["ollama"]["base_url"] == "http://127.0.0.1:11434"


def test_apply_llm_update_creates_llm_block() -> None:
    config = {}
    updated = apply_llm_update(config, {"enabled": True, "provider": "ollama"})
    assert updated["llm"]["enabled"] is True
    assert updated["llm"]["provider"] == "ollama"
