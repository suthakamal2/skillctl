"""Tests for the bundled example rule set in `examples/.skillctl/`.

These prove that the example registry shipped with skillctl builds cleanly,
audits clean, and that every documented bundle resolves end-to-end.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skillctl import (
    audit_registry,
    build_registry,
    load_bundle,
    load_registry,
)
from skillctl._registry import clear_cache

EXAMPLES_HOME = Path(__file__).resolve().parent.parent / "examples" / ".skillctl"

EXPECTED_BUNDLES = {"deploy", "multi-agent", "security-review", "refactor", "debug"}
EXPECTED_RULE_IDS = {
    # deploy
    "safe-deploy", "docker-control", "branch-management",
    # multi-agent (shares branch-management)
    "workspace-isolation", "agent-handoff",
    # security-review
    "security-review", "dependency-audit", "secrets-scan",
    # refactor
    "scope-freeze", "test-coverage", "incremental-edits",
    # debug
    "repro-first", "hypothesis-tracking", "three-strikes",
}


@pytest.fixture()
def home(tmp_path: Path) -> Path:
    """Copy the shipped examples into a tmp dir and rebuild the index."""
    h = tmp_path / ".skillctl"
    shutil.copytree(EXAMPLES_HOME, h)
    # Force a fresh build so checksums match the (copied) files.
    build_registry(h / "rules", h)
    clear_cache()
    return h


def test_all_expected_rules_present(home: Path) -> None:
    reg = load_registry(home=home)
    actual = {r["id"] for r in reg["rules"]}
    assert actual == EXPECTED_RULE_IDS, (
        f"missing: {EXPECTED_RULE_IDS - actual}, extra: {actual - EXPECTED_RULE_IDS}"
    )


def test_all_expected_bundles_present(home: Path) -> None:
    reg = load_registry(home=home)
    assert set(reg["bundles"].keys()) == EXPECTED_BUNDLES


def test_audit_clean(home: Path) -> None:
    issues = audit_registry(home=home)
    assert not any(issues.values()), f"audit issues: {issues}"


@pytest.mark.parametrize("bundle", sorted(EXPECTED_BUNDLES))
def test_bundle_loads_with_all_members(home: Path, bundle: str) -> None:
    text = load_bundle(bundle, max_tokens=20000, home=home)
    reg = load_registry(home=home)
    members = reg["bundles"][bundle]
    for member_id in members:
        rule = next(r for r in reg["rules"] if r["id"] == member_id)
        assert rule["title"] in text, (
            f"bundle {bundle!r} missing member {member_id!r} in loaded brief"
        )


def test_tier_distribution(home: Path) -> None:
    """branch-management and workspace-isolation are tier 1; rest are tier 2."""
    reg = load_registry(home=home)
    by_tier: dict[int, set[str]] = {}
    for r in reg["rules"]:
        by_tier.setdefault(r["tier"], set()).add(r["id"])
    assert by_tier[1] == {"branch-management", "workspace-isolation"}
    assert len(by_tier.get(2, set())) == 12
    assert 3 not in by_tier
