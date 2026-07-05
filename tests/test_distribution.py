# MIT-licensed
"""Validate the distribution artefacts (Homebrew, npm, Claude Code plugin)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

DIST = Path(__file__).resolve().parent.parent / "distribution"


def test_npm_package_json() -> None:
    data = json.loads((DIST / "npm" / "package.json").read_text())
    assert data["name"] == "skillctl"
    assert data["version"] == "0.1.0"
    assert "bin" in data and "skillctl" in data["bin"]


def test_claude_skill_frontmatter() -> None:
    content = (DIST / "claude-code-plugin" / "skillctl" / "SKILL.md").read_text()
    parts = content.split("---")
    assert len(parts) >= 3, "SKILL.md must have YAML frontmatter"

    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["name"] == "skillctl"
    assert "description" in frontmatter
    assert len(frontmatter["description"]) > 20  # not a placeholder


def test_homebrew_formula_name() -> None:
    content = (DIST / "homebrew" / "skillctl.rb").read_text()
    assert "class Skillctl < Formula" in content
    # The URL should reference the canonical PyPI hosting path for skillctl 0.1.0.
    assert "skillctl-0.1.0.tar.gz" in content
