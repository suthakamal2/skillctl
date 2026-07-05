"""Installers for the skillctl prompt-injection hook across agent hosts."""

from __future__ import annotations

import json
from pathlib import Path

HOOK_COMMAND = 'sh "$CLAUDE_PROJECT_DIR/.claude/hooks/skillctl-inject.sh"'
HOOK_TIMEOUT_SECONDS = 5
SCRIPT_NAME = "skillctl-inject.sh"


def get_claude_dir(start: Path | None = None) -> Path:
    """Find the nearest ``.claude/`` ancestor, or place one in cwd."""
    cwd = (start or Path.cwd()).resolve()
    for candidate in [cwd, *cwd.parents]:
        marker = candidate / ".claude"
        if marker.is_dir():
            return marker
    return cwd / ".claude"


def _load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _has_skillctl_entry(entries: list) -> bool:
    """True if any nested hook entry already references our command."""
    for outer in entries:
        if not isinstance(outer, dict):
            continue
        for inner in outer.get("hooks", []):
            if isinstance(inner, dict) and inner.get("command") == HOOK_COMMAND:
                return True
    return False


def _remove_skillctl_entry(entries: list) -> list:
    """Return a copy of the UserPromptSubmit array with skillctl entries stripped."""
    cleaned = []
    for outer in entries:
        if not isinstance(outer, dict):
            cleaned.append(outer)
            continue
        inner_hooks = [
            h for h in outer.get("hooks", [])
            if not (isinstance(h, dict) and h.get("command") == HOOK_COMMAND)
        ]
        if inner_hooks:
            new_outer = {**outer, "hooks": inner_hooks}
            cleaned.append(new_outer)
        # else: drop the outer wrapper entirely
    return cleaned


def install_claude_code(start: Path | None = None) -> Path:
    """Wire skillctl into Claude Code's UserPromptSubmit hook.

    Returns the path to the installed hook script. Idempotent.
    """
    claude_dir = get_claude_dir(start)
    claude_dir.mkdir(parents=True, exist_ok=True)

    settings_path = claude_dir / "settings.json"
    settings = _load_settings(settings_path)

    hooks = settings.setdefault("hooks", {})
    raw = hooks.get("UserPromptSubmit", [])
    if isinstance(raw, str):
        # Legacy/incorrect shape — drop it; the canonical shape is an array.
        entries: list = []
    elif isinstance(raw, list):
        entries = raw
    else:
        entries = []

    if not _has_skillctl_entry(entries):
        entries.append(
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": HOOK_COMMAND,
                        "timeout": HOOK_TIMEOUT_SECONDS,
                    }
                ]
            }
        )
    hooks["UserPromptSubmit"] = entries

    settings_path.write_text(json.dumps(settings, indent=2) + "\n")

    hooks_dir = claude_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    script_path = hooks_dir / SCRIPT_NAME
    script_path.write_text(
        "#!/bin/sh\n"
        '# Auto-installed by `skillctl install claude-code`.\n'
        '# Injects matching rule bodies into the model context for this turn.\n'
        'skillctl inject "$CLAUDE_USER_PROMPT" 2>/dev/null || true\n'
    )
    script_path.chmod(script_path.stat().st_mode | 0o111)

    print(f"Installed Claude Code hook at {script_path}")
    print(f"  settings.json updated at {settings_path}")
    print(
        "Verify: open a new Claude Code session in this project and prompt with "
        "something matching one of your rules. The dynamic-rule-context block "
        "will appear in the conversation."
    )
    return script_path


def uninstall_claude_code(start: Path | None = None) -> None:
    """Remove the skillctl hook entry and script. Idempotent."""
    claude_dir = get_claude_dir(start)
    settings_path = claude_dir / "settings.json"

    if settings_path.exists():
        settings = _load_settings(settings_path)
        hooks = settings.get("hooks", {})
        raw = hooks.get("UserPromptSubmit", [])
        if isinstance(raw, list):
            entries = _remove_skillctl_entry(raw)
            if entries:
                hooks["UserPromptSubmit"] = entries
            else:
                hooks.pop("UserPromptSubmit", None)
            if not hooks:
                settings.pop("hooks", None)
            settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        elif isinstance(raw, str):
            # Legacy flat-string installs from pre-fix builds: drop the key.
            hooks.pop("UserPromptSubmit", None)
            if not hooks:
                settings.pop("hooks", None)
            settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        print(f"Removed skillctl hook from {settings_path}")

    script_path = claude_dir / "hooks" / SCRIPT_NAME
    if script_path.exists():
        script_path.unlink()
        print(f"Deleted {script_path}")


def print_cursor_docs() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs" / "install-cursor.md"
    if docs.exists():
        print(docs.read_text())
    else:
        print(
            "Cursor does not expose a synchronous prompt-submit hook. Run "
            '`skillctl suggest "<your prompt>"` ahead of a task and paste the '
            "relevant rule bodies into Cursor's chat, or wire a pre-task shell "
            "script that pipes `skillctl bundle <name>` into your prompt."
        )


def print_codex_docs() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs" / "install-codex.md"
    if docs.exists():
        print(docs.read_text())
    else:
        print(
            "Codex CLI accepts `--instructions @-` from stdin. Pipe relevant "
            "rule bodies into it: `skillctl bundle deploy | codex --instructions @- ...`"
        )
