"""Smoke tests covering the round-trip: init → build → suggest → load → audit."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from skillctl import (
    audit_registry,
    build_registry,
    get_rule,
    load_bundle,
    load_topics,
    match_by_topic,
    read_rule_body,
    resolve_deps,
    suggest_bundles,
    suggest_topics,
)
from skillctl._registry import clear_cache

SAMPLE_RULES: dict[str, str] = {
    "safe-deploy.md": textwrap.dedent(
        """\
        ---
        id: safe-deploy
        title: Safe deployment protocol
        tier: 2
        triggers: [deploy, ship, production, rollout]
        deps: [docker-control]
        summary: How we ship without breaking production.
        ---

        # Safe deployment protocol

        Canary first.
        """
    ),
    "docker-control.md": textwrap.dedent(
        """\
        ---
        id: docker-control
        title: Docker operations
        tier: 2
        triggers: [docker, container, image]
        summary: How we operate Docker safely.
        ---

        # Docker operations

        Pin tags.
        """
    ),
    "branch-management.md": textwrap.dedent(
        """\
        ---
        id: branch-management
        title: Branch management
        tier: 1
        triggers: [git, branch, merge, push]
        summary: Main is the source of truth.
        ---

        # Branch management

        Always merge to main.
        """
    ),
    # Vanilla SKILL.md format — no tier, uses name+description
    "legacy/SKILL.md": textwrap.dedent(
        """\
        ---
        id: legacy
        name: A SKILL.md-formatted rule
        description: Demonstrates SKILL.md interop.
        triggers: [legacy, anthropic]
        ---

        # Legacy

        Hello.
        """
    ),
}


@pytest.fixture()
def home(tmp_path: Path) -> Path:
    """Build a .skillctl/ home with sample rules and bundles."""
    h = tmp_path / ".skillctl"
    rules_dir = h / "rules"
    rules_dir.mkdir(parents=True)
    for rel, body in SAMPLE_RULES.items():
        p = rules_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (h / "bundles.yaml").write_text(
        "deploy: [safe-deploy, docker-control, branch-management]\n"
    )
    build_registry(rules_dir, h)
    clear_cache()
    return h


def test_build_emits_registry(home: Path) -> None:
    idx = home / "index.yaml"
    assert idx.exists()
    text = idx.read_text()
    assert "safe-deploy" in text
    assert "docker-control" in text
    assert "legacy" in text


def test_get_rule_returns_metadata(home: Path) -> None:
    r = get_rule("safe-deploy", home=home)
    assert r is not None
    assert r["tier"] == 2
    assert "deploy" in r["triggers"]


def test_read_rule_body_strips_frontmatter(home: Path) -> None:
    body = read_rule_body("safe-deploy", home=home)
    assert body.lstrip().startswith("# Safe deployment protocol")
    assert "id: safe-deploy" not in body


def test_match_by_topic_finds_exact_trigger(home: Path) -> None:
    matches = match_by_topic("deploy", home=home)
    ids = {m.rule_id for m in matches}
    assert "safe-deploy" in ids


def test_suggest_topics_word_boundary(home: Path) -> None:
    """`ship` should match safe-deploy but `shipping` (different word) shouldn't."""
    assert any(m.rule_id == "safe-deploy" for m in suggest_topics("let us ship it", home=home))
    # "shippable" contains "ship" as substring but the word boundary should exclude it
    assert not any(
        m.rule_id == "safe-deploy"
        for m in suggest_topics("call it shippable code", home=home)
    )


def test_resolve_deps_transitively(home: Path) -> None:
    """`safe-deploy` lists `docker-control` as a dep; resolve should pull it in."""
    resolved = resolve_deps(["safe-deploy"], home=home)
    assert "safe-deploy" in resolved
    assert "docker-control" in resolved


def test_load_topics_includes_deps(home: Path) -> None:
    text = load_topics(["deploy"], max_tokens=10000, home=home)
    assert "Safe deployment protocol" in text
    assert "Docker operations" in text
    assert "dep-of-matched-rule" in text


def test_load_bundle_resolves_all_members(home: Path) -> None:
    text = load_bundle("deploy", max_tokens=10000, home=home)
    assert "Safe deployment protocol" in text
    assert "Docker operations" in text
    assert "Branch management" in text


def test_token_budget_drops_overflow(home: Path) -> None:
    """A 50-token budget can't fit all three; expect dropped entries."""
    text = load_bundle("deploy", max_tokens=50, home=home)
    assert "Dropped due to budget" in text


def test_audit_is_clean_on_fresh_build(home: Path) -> None:
    issues = audit_registry(home=home)
    assert not any(issues.values()), f"Expected clean audit, got {issues}"


def test_audit_catches_drift(home: Path) -> None:
    """Editing a rule body without rebuilding should be detected."""
    rule_path = home / "rules" / "safe-deploy.md"
    rule_path.write_text(rule_path.read_text() + "\n\nextra content\n")
    issues = audit_registry(home=home)
    assert issues["checksum_mismatches"], "Expected drift detection"


def test_audit_catches_orphan_deps(tmp_path: Path) -> None:
    h = tmp_path / ".skillctl"
    rules_dir = h / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "x.md").write_text(
        "---\nid: x\ntitle: X\ntier: 2\ntriggers: [x]\ndeps: [does-not-exist]\n---\n\nbody\n"
    )
    build_registry(rules_dir, h)
    clear_cache()
    issues = audit_registry(home=h)
    assert issues["orphan_deps"], "Expected orphan dep detection"


def test_skill_md_interop_uses_description_as_summary(home: Path) -> None:
    r = get_rule("legacy", home=home)
    assert r is not None
    assert r["summary"] == "Demonstrates SKILL.md interop."
    assert r["tier"] == 2  # default when not specified


def test_suggest_bundles_recommends_overlapping_bundle(home: Path) -> None:
    matches = suggest_topics("we need to deploy and push docker images", home=home)
    bundles = suggest_bundles("deploy and push docker", matches, home=home)
    names = {b[0] for b in bundles}
    assert "deploy" in names
