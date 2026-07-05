import json

import pytest

from skillctl._audit import audit_registry
from skillctl._build import build_registry
from skillctl._errors import Reporter


@pytest.fixture
def temp_home(tmp_path):
    home = tmp_path / ".skillctl"
    home.mkdir()
    rules_dir = home / "rules"
    rules_dir.mkdir()
    return home, rules_dir

def test_build_no_frontmatter_is_warning_not_error(temp_home):
    home, rules_dir = temp_home
    (rules_dir / "bad.md").write_text("Just some markdown.")
    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    assert reporter.skipped_count == 1
    assert not reporter.has_errors()
    assert any(w["category"] == "skipped" for w in reporter.warnings)

def test_build_yaml_parse_error_shows_line_number(temp_home):
    home, rules_dir = temp_home
    (rules_dir / "bad.md").write_text("---\nid: foo\n\tbad_indent: yes\n---\nbody")
    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    assert reporter.has_errors()
    err = reporter.errors[0]
    assert err["category"] == "yaml_parse"
    assert err["line"] is not None
    assert "tabs" in err["suggested_fix"]
    assert "invalid YAML frontmatter" in err["message"]

def test_build_missing_id_aborts_one_rule_not_all(temp_home):
    home, rules_dir = temp_home
    (rules_dir / "bad.md").write_text("---\ntitle: missing id\n---\nbody")
    (rules_dir / "good.md").write_text("---\nid: good\ntier: 3\n---\nbody")
    reporter = Reporter()
    reg = build_registry(rules_dir, home, reporter=reporter)
    assert reporter.has_errors()
    assert len(reporter.errors) == 1
    assert reporter.errors[0]["category"] == "missing_id"
    assert reg["total_rules"] == 1
    assert reg["rules"][0]["id"] == "good"

def test_build_duplicate_id_lists_both_paths(temp_home):
    home, rules_dir = temp_home
    (rules_dir / "a.md").write_text("---\nid: clash\ntier: 3\n---\nbody")
    (rules_dir / "b.md").write_text("---\nid: clash\ntier: 3\n---\nbody")
    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    assert reporter.has_errors()
    assert len(reporter.errors) == 1
    err = reporter.errors[0]
    assert err["category"] == "duplicate_id"
    assert "Duplicate rule id clash" in err["message"]
    assert "a.md" in err["message"]
    assert "b.md" in err["message"]

def test_build_tier_2_no_triggers_is_warning_not_error(temp_home):
    """Tier 2 with no triggers is a warning, not a hard error.

    Rationale: vanilla Anthropic SKILL.md files default to tier 2 and have
    no triggers (they use `description`). Rejecting them at build would
    break SKILL.md interop (see CONTRIBUTING.md — "SKILL.md interop is
    sacred"). The rule still gets indexed; audit surfaces it for users
    who care.
    """
    home, rules_dir = temp_home
    (rules_dir / "bad.md").write_text("---\nid: bad\ntier: 2\n---\nbody")
    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    assert not reporter.has_errors()
    warnings_with_category = [w for w in reporter.warnings if w.get("category") == "tier_2_no_triggers"]
    assert len(warnings_with_category) == 1
    assert "tier 2 rule has no 'triggers'" in warnings_with_category[0]["message"]

def test_audit_unreachable_rules_is_warning(temp_home):
    home, rules_dir = temp_home
    (rules_dir / "unreachable.md").write_text("---\nid: unreach\ntier: 2\ntriggers: [a, the]\n---\nbody")
    reporter = Reporter()
    build_registry(rules_dir, home, reporter=reporter)
    issues = audit_registry(home)
    assert len(issues["unreachable_rules"]) == 2
    triggers = {i["trigger"] for i in issues["unreachable_rules"]}
    assert "a" in triggers
    assert "the" in triggers

def test_errors_json_shape(temp_home, capsys):
    home, rules_dir = temp_home
    (rules_dir / "bad.md").write_text("---\ntitle: foo\n---\n")
    
    # Running as sub-process to test cli
    import argparse
    import io
    from contextlib import redirect_stdout

    import skillctl._cli
    
    args = argparse.Namespace(rules=str(rules_dir), home=str(home), json=False)
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        try:
            skillctl._cli.cmd_build(args)
        except SystemExit as e:
            assert e.code == 1
    assert "missing required field 'id'" in stdout.getvalue()
    
    args = argparse.Namespace(rules=str(rules_dir), home=str(home), json=True)
    stdout2 = io.StringIO()
    with redirect_stdout(stdout2):
        try:
            skillctl._cli.cmd_build(args)
        except SystemExit as e:
            assert e.code == 1
    
    res2 = argparse.Namespace(returncode=1, stdout=stdout2.getvalue())
    data = json.loads(res2.stdout)
    assert "errors" in data
    assert "warnings" in data
    assert len(data["errors"]) == 1
    err = data["errors"][0]
    assert "path" in err
    assert "category" in err
    assert "message" in err
    assert "suggested_fix" in err
