import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from skillctl import build_registry
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

def test_list_includes_totals(home: Path):
    import os
    env = os.environ.copy()
    env["SKILLCTL_HOME"] = str(home)
    res = subprocess.run([sys.executable, "-m", "skillctl._cli", "list"], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "Tier 1 rules" in res.stdout or "Tier 1 total" in res.stdout or "tier 1" in res.stdout.lower()
    assert "safe-deploy" in res.stdout

def test_suggest_json_baseline(home: Path):
    import os
    env = os.environ.copy()
    env["SKILLCTL_HOME"] = str(home)
    res = subprocess.run([sys.executable, "-m", "skillctl._cli", "suggest", "--json", "deploy"], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "bundles" in data
    assert "rules" in data

def test_why_deploy_mention(home: Path):
    import os
    env = os.environ.copy()
    env["SKILLCTL_HOME"] = str(home)
    res = subprocess.run([sys.executable, "-m", "skillctl._cli", "why", "deploy"], capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "deploy" in res.stdout.lower()

def test_audit_clean_exit(home: Path):
    import os
    env = os.environ.copy()
    env["SKILLCTL_HOME"] = str(home)
    res = subprocess.run([sys.executable, "-m", "skillctl._cli", "audit"], capture_output=True, text=True, env=env)
    assert res.returncode == 0

def test_bundles_with_missing_rule_does_not_crash(tmp_path: Path):
    """Regression: `skillctl bundles` formatted a missing rule's token count as
    f'{tok:,}' where tok was the string '?', raising ValueError and crashing the
    command. A bundle that references an unbuilt/typo'd rule must render, not crash."""
    import os
    h = tmp_path / ".skillctl"
    rules_dir = h / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "safe-deploy.md").write_text(SAMPLE_RULES["safe-deploy.md"])
    # bundle references a rule that does not exist in the registry
    (h / "bundles.yaml").write_text("deploy: [safe-deploy, does-not-exist]\n")
    build_registry(rules_dir, h)
    clear_cache()
    env = os.environ.copy()
    env["SKILLCTL_HOME"] = str(h)
    res = subprocess.run([sys.executable, "-m", "skillctl._cli", "bundles"], capture_output=True, text=True, env=env)
    assert res.returncode == 0, f"bundles crashed: {res.stderr}"
    assert "missing" in res.stdout.lower()
