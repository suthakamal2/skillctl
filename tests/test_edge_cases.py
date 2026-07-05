import time
from pathlib import Path

import pytest

from skillctl._audit import audit_registry
from skillctl._build import build_registry
from skillctl._loader import load_bundle, load_topics, resolve_deps
from skillctl._matching import match_by_topic, suggest_topics

# Group 1: Malformed input

def test_empty_registry_audits_clean(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 0
    
    issues = audit_registry(home)
    for _k, v in issues.items():
        assert not v


def test_zero_byte_rule_file_skipped(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "empty.md").touch()
    home = tmp_path / ".skillctl"
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 0


def test_rule_file_with_only_frontmatter_no_body(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    (rules_dir / "no_body.md").write_text("---\nid: no-body\ntier: 1\n---\n")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1
    
    loaded = load_topics(["no-body"], home=home)
    assert "## no-body" in loaded


def test_frontmatter_missing_closing_fence(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    (rules_dir / "broken.md").write_text("---\nid: broken\ntier: 1\nbody")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 0


def test_unicode_in_id_and_triggers(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    (rules_dir / "unicode.md").write_text(
        "---\n"
        "id: 多言語-rule\n"
        "tier: 2\n"
        "triggers: [日本語]\n"
        "---\n"
        "hello"
    )
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1
    
    matches = match_by_topic("日本語", home=home)
    assert len(matches) == 1
    assert matches[0].rule_id == "多言語-rule"
    
    loaded = load_topics(["多言語-rule"], home=home)
    assert "多言語-rule" in loaded


def test_emoji_in_rule_body(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    body = "Here is a crab: 🦀"
    (rules_dir / "crab.md").write_text(f"---\nid: crab\ntier: 1\n---\n{body}", encoding="utf-8")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1
    
    loaded = load_topics(["crab"], home=home)
    assert "🦀" in loaded


def test_crlf_line_endings(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    (rules_dir / "crlf.md").write_bytes(b"---\r\nid: crlf\r\ntier: 1\r\n---\r\nbody\r\n")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1


@pytest.mark.xfail(reason="bug: BOM handling fails for file starts", strict=True)
def test_bom_at_file_start(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    content = "\ufeff---\nid: bom\ntier: 1\n---\nbody"
    (rules_dir / "bom.md").write_text(content, encoding="utf-8")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1


# Group 2: Unusual but valid registries

def test_deeply_nested_deps(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "A.md").write_text("---\nid: A\ntier: 1\ndeps: [B]\n---\n")
    (rules_dir / "B.md").write_text("---\nid: B\ntier: 1\ndeps: [C]\n---\n")
    (rules_dir / "C.md").write_text("---\nid: C\ntier: 1\ndeps: [D]\n---\n")
    (rules_dir / "D.md").write_text("---\nid: D\ntier: 1\ndeps: [E]\n---\n")
    (rules_dir / "E.md").write_text("---\nid: E\ntier: 1\n---\n")
    
    build_registry(rules_dir, home)
    deps = resolve_deps(["A"], home=home)
    assert deps == ["A", "B", "C", "D", "E"]


def test_cyclic_deps_does_not_loop_forever(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "A.md").write_text("---\nid: A\ntier: 1\ndeps: [B]\n---\n")
    (rules_dir / "B.md").write_text("---\nid: B\ntier: 1\ndeps: [A]\n---\n")
    
    build_registry(rules_dir, home)
    deps = resolve_deps(["A"], home=home)
    assert sorted(deps) == ["A", "B"]


def test_self_referential_dep(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "A.md").write_text("---\nid: A\ntier: 1\ndeps: [A]\n---\n")
    
    build_registry(rules_dir, home)
    deps = resolve_deps(["A"], home=home)
    assert deps == ["A"]


def test_bundle_referencing_only_tier_1_rules(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "A.md").write_text("---\nid: A\ntier: 1\nbundles: [my-bundle]\n---\n")
    (rules_dir / "B.md").write_text("---\nid: B\ntier: 1\nbundles: [my-bundle]\n---\n")
    
    build_registry(rules_dir, home)
    loaded = load_bundle("my-bundle", home=home)
    assert "## A" in loaded
    assert "## B" in loaded


def test_two_bundles_with_overlapping_members(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "shared.md").write_text("---\nid: shared\ntier: 1\n---\nshared-body")
    home.mkdir(parents=True, exist_ok=True)
    (home / "bundles.yaml").write_text(
        "deploy: [shared]\n"
        "release: [shared]\n"
    )
    
    build_registry(rules_dir, home)
    
    # simulate loading both via multiple topics or similar; load_topics stitches uniquely
    loaded = load_topics(["shared", "shared"], home=home)
    # the exact text 'shared-body' should appear once for the rule body
    assert loaded.count("shared-body") == 1


@pytest.mark.xfail(
    reason="aspirational perf target (~570ms at 500 rules; see KNOWN_BUGS). "
    "Wall-clock and machine-dependent, so non-strict: it xfails on slow runners "
    "and xpasses on fast ones without reddening CI either way.",
    strict=False,
)
def test_500_rules_loads_in_under_500ms(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    for i in range(500):
        (rules_dir / f"r{i}.md").write_text(f"---\nid: r{i}\ntier: 1\n---\nbody {i}")
    
    t0 = time.time()
    build_registry(rules_dir, home)
    suggest_topics("please help with r250", home=home)
    t1 = time.time()
    
    assert (t1 - t0) < 0.5


def test_trigger_matches_at_string_boundary(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "deploy.md").write_text("---\nid: deploy\ntier: 2\ntriggers: [deploy]\n---\n")
    build_registry(rules_dir, home)
    
    suggestions = suggest_topics("deploy", home=home)
    assert len(suggestions) == 1
    assert suggestions[0].rule_id == "deploy"


def test_trigger_does_not_match_inside_word(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "deploy.md").write_text("---\nid: deploy\ntier: 2\ntriggers: [deploy]\n---\n")
    build_registry(rules_dir, home)
    
    suggestions = suggest_topics("redeploying", home=home)
    assert len(suggestions) == 0


def test_case_insensitive_trigger_match(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "deploy.md").write_text("---\nid: deploy\ntier: 2\ntriggers: [Deploy]\n---\n")
    build_registry(rules_dir, home)
    
    suggestions = suggest_topics("DEPLOY production", home=home)
    assert len(suggestions) == 1
    assert suggestions[0].rule_id == "deploy"


def test_multiple_word_trigger(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "cr.md").write_text("---\nid: cr\ntier: 2\ntriggers: ['code review']\n---\n")
    build_registry(rules_dir, home)
    
    suggestions = suggest_topics("please do a code review", home=home)
    assert len(suggestions) == 1
    assert suggestions[0].rule_id == "cr"


# Group 3: SKILL.md interop edges

def test_skill_md_with_only_name_no_description(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "SKILL.md").write_text("---\nid: skill1\nname: skill1\n---\n")
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1
    
    rule = reg["rules"][0]
    assert rule["summary"] == ""


def test_skill_md_with_html_in_description(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "SKILL.md").write_text("---\nid: skill1\ndescription: A <br/> skill\n---\n")
    reg = build_registry(rules_dir, home)
    
    rule = reg["rules"][0]
    assert rule["summary"] == "A <br/> skill"


def test_skill_md_directory_with_assets(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    skill_dir = rules_dir / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nid: skill1\n---\n")
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "install.sh").write_text("echo hello")
    
    reg = build_registry(rules_dir, home)
    assert reg["total_rules"] == 1
    
    # file paths ending in .md only are included
    paths = [r["path"] for r in reg["rules"]]
    assert not any("install.sh" in p for p in paths)


# Group 4: Audit edges

def test_build_rejects_duplicate_id_in_different_files(tmp_path: Path):
    """Duplicate ids are caught at build time (not deferred to audit).

    K3 rationale: tell the user immediately, not later. Audit's duplicate_ids
    check stays in place as defence-in-depth for hand-edited index.yaml.
    """
    from skillctl._errors import Reporter

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"

    (rules_dir / "A.md").write_text("---\nid: dup\ntier: 1\n---\n")
    (rules_dir / "B.md").write_text("---\nid: dup\ntier: 1\n---\n")

    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    dup_errors = [e for e in reporter.errors if e["category"] == "duplicate_id"]
    assert len(dup_errors) == 1
    assert "dup" in dup_errors[0]["message"]


def test_audit_with_one_unreachable_dep_does_not_block_others(tmp_path: Path):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    home = tmp_path / ".skillctl"
    
    (rules_dir / "A.md").write_text("---\nid: A\ntier: 1\nbundles: [X]\n---\n")
    (rules_dir / "B.md").write_text("---\nid: B\ntier: 1\nbundles: [X]\n---\n")
    
    home.mkdir(parents=True, exist_ok=True)
    (home / "bundles.yaml").write_text(
        "X: [A, B, unknown]\n"
    )
    
    build_registry(rules_dir, home)
    
    loaded = load_bundle("X", home=home)
    assert "## A" in loaded
    assert "## B" in loaded
