"""Eval-suite tests against the synthetic example corpus.

The old tests here exercised codebase-specific migration scripts and a fixture built
from a private codebase's real rules. Both were removed when the package was decoupled
for open-sourcing. These tests validate the generated `eval/example-rules/` corpus
instead: its internal integrity, and that skillctl builds + audits it cleanly and
suggests sensibly.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
GEN = PKG / "scripts" / "gen_example_corpus.py"
CORPUS_HOME = PKG / "eval" / "example-rules" / ".skillctl"  # source: rules/ + bundles.yaml
CORPUS_RULES = CORPUS_HOME / "rules"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_example_corpus", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_in_tmp(tmp_path: Path) -> tuple[Path, dict]:
    """Copy the corpus source (rules/ + bundles.yaml) into a tmp home and build it.
    Copying brings bundles.yaml along so bundle suggestions are exercised."""
    home = tmp_path / ".skillctl"
    shutil.copytree(CORPUS_HOME, home)
    env = {**os.environ, "SKILLCTL_HOME": str(home)}
    build = subprocess.run(
        [sys.executable, "-m", "skillctl._cli", "build", str(home / "rules")],
        capture_output=True, text=True, env=env,
    )
    assert build.returncode == 0, build.stderr
    assert "0 error" in build.stdout, build.stdout
    return home, env


def test_example_corpus_integrity():
    """Every dep and every bundle member must reference a defined rule id, ids unique,
    and all three tiers represented. This catches the orphan-dep / missing-bundle-member
    class of bug before it reaches a build."""
    gen = _load_generator()
    ids = [r[0] for r in gen.RULES]
    assert len(ids) == len(set(ids)), "duplicate rule ids"
    id_set = set(ids)
    tiers = {r[1] for r in gen.RULES}
    assert tiers == {1, 2, 3}, f"expected all three tiers, got {tiers}"
    for rule_id, _tier, _trig, deps, _summary in gen.RULES:
        for d in deps:
            assert d in id_set, f"{rule_id} deps on undefined rule {d}"
    for name, members in gen.BUNDLES.items():
        for m in members:
            assert m in id_set, f"bundle {name} references undefined rule {m}"


def test_example_corpus_builds_and_audits_clean(tmp_path: Path):
    """The committed corpus builds with no errors and audits clean."""
    _home, env = _build_in_tmp(tmp_path)
    audit = subprocess.run(
        [sys.executable, "-m", "skillctl._cli", "audit"],
        capture_output=True, text=True, env=env,
    )
    assert audit.returncode == 0, audit.stderr
    assert "no integrity issues" in audit.stdout.lower(), audit.stdout


def test_suggest_fires_bundle_on_overlap(tmp_path: Path):
    """A prompt hitting >=2 rules of a bundle surfaces that bundle suggestion."""
    _home, env = _build_in_tmp(tmp_path)
    res = subprocess.run(
        [sys.executable, "-m", "skillctl._cli", "suggest", "--json",
         "ship the docker image and roll out to production"],
        capture_output=True, text=True, env=env,
    )
    assert res.returncode == 0, res.stderr
    data = json.loads(res.stdout)
    assert any(b["name"] == "deploy" for b in data.get("bundles", [])), data.get("bundles")
