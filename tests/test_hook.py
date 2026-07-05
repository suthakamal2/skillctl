"""Tests for skillctl.inject() and the Claude Code hook installer."""

from __future__ import annotations

import json
from pathlib import Path

from skillctl import inject
from skillctl._build import build_registry
from skillctl._install import (
    HOOK_COMMAND,
    install_claude_code,
    uninstall_claude_code,
)


def _seed_rules(tmp_path: Path) -> Path:
    home = tmp_path / ".skillctl"
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "safe-deploy.md").write_text(
        "---\n"
        "id: safe-deploy\n"
        "title: Safe deploy\n"
        "tier: 2\n"
        "triggers: [deploy, production]\n"
        "---\n"
        "body text\n"
    )
    build_registry(rules_dir, home)
    return home


def test_inject_matches(tmp_path: Path) -> None:
    home = _seed_rules(tmp_path)
    result = inject("deploy v2 to production", home=home)
    assert "<dynamic-rule-context>" in result
    assert 'id="safe-deploy"' in result
    assert "body text" in result


def test_inject_no_matches(tmp_path: Path) -> None:
    home = _seed_rules(tmp_path)
    assert inject("hello world", home=home) == ""


def test_install_writes_canonical_hook_shape(tmp_path: Path) -> None:
    """The hook entry must be a list of objects with `hooks: [{type, command, timeout}]`,
    not a flat string. Claude Code silently ignores the flat-string shape."""
    install_claude_code(start=tmp_path)

    settings_path = tmp_path / ".claude" / "settings.json"
    hook_script = tmp_path / ".claude" / "hooks" / "skillctl-inject.sh"
    assert settings_path.exists()
    assert hook_script.exists()
    assert hook_script.stat().st_mode & 0o111, "hook script must be executable"

    settings = json.loads(settings_path.read_text())
    entries = settings["hooks"]["UserPromptSubmit"]
    assert isinstance(entries, list), "UserPromptSubmit must be a list"
    assert len(entries) == 1
    assert isinstance(entries[0], dict)
    inner = entries[0]["hooks"]
    assert isinstance(inner, list)
    assert inner[0]["type"] == "command"
    assert inner[0]["command"] == HOOK_COMMAND
    assert isinstance(inner[0]["timeout"], int)


def test_install_is_idempotent(tmp_path: Path) -> None:
    install_claude_code(start=tmp_path)
    install_claude_code(start=tmp_path)
    install_claude_code(start=tmp_path)
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    entries = settings["hooks"]["UserPromptSubmit"]
    skillctl_entries = [
        h for outer in entries for h in outer.get("hooks", [])
        if h.get("command") == HOOK_COMMAND
    ]
    assert len(skillctl_entries) == 1, f"expected 1 skillctl entry, got {len(skillctl_entries)}"


def test_install_preserves_existing_hooks(tmp_path: Path) -> None:
    """Pre-existing UserPromptSubmit entries must not be clobbered."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    settings_path = claude_dir / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "UserPromptSubmit": [
                        {"hooks": [{"type": "command", "command": "echo existing", "timeout": 5}]}
                    ]
                }
            }
        )
    )

    install_claude_code(start=tmp_path)
    settings = json.loads(settings_path.read_text())
    entries = settings["hooks"]["UserPromptSubmit"]

    all_commands = [
        h["command"]
        for outer in entries
        for h in outer.get("hooks", [])
    ]
    assert "echo existing" in all_commands
    assert HOOK_COMMAND in all_commands


def test_uninstall_removes_only_skillctl(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    settings_path = claude_dir / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "hooks": {
                    "UserPromptSubmit": [
                        {"hooks": [{"type": "command", "command": "echo existing", "timeout": 5}]}
                    ]
                }
            }
        )
    )
    install_claude_code(start=tmp_path)
    uninstall_claude_code(start=tmp_path)

    settings = json.loads(settings_path.read_text())
    entries = settings["hooks"]["UserPromptSubmit"]
    commands = [h["command"] for outer in entries for h in outer.get("hooks", [])]
    assert "echo existing" in commands
    assert HOOK_COMMAND not in commands
    assert not (claude_dir / "hooks" / "skillctl-inject.sh").exists()


def test_uninstall_handles_legacy_flat_string(tmp_path: Path) -> None:
    """Pre-fix installs left UserPromptSubmit as a string; uninstall must clean it."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    settings_path = claude_dir / "settings.json"
    settings_path.write_text(json.dumps({"hooks": {"UserPromptSubmit": "sh some-old.sh"}}))
    uninstall_claude_code(start=tmp_path)
    settings = json.loads(settings_path.read_text())
    assert "UserPromptSubmit" not in settings.get("hooks", {})
