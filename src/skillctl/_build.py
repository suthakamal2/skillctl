"""Scan a rules directory and generate ``.skillctl/index.yaml``.

A rule is any Markdown file with a YAML frontmatter block. The frontmatter
is intentionally a superset of Anthropic's ``SKILL.md`` format, so existing
skills are picked up unchanged.

Supported frontmatter fields:

  id          (required) unique within the registry
  title       (required) human-readable
  name        (alias for title — SKILL.md compatibility)
  tier        1 | 2 | 3 (default 2)
  triggers    list[str]  -- required when tier == 2
  deps        list[str]
  bundles     list[str]  -- the bundles this rule belongs to (alt to bundles.yaml)
  summary     one-line description
  description SKILL.md alias for summary
  status      active | deprecated (default active)

Bundles can be declared in two places:

  1. In a top-level ``bundles.yaml`` (or ``bundles.yml``) inside ``.skillctl/``:
       deploy: [safe-deploy, docker-control]
  2. Inline in any rule's ``bundles:`` field:
       bundles: [deploy, ship-day]
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from ._errors import Reporter

FRONTMATTER_FENCE = "---"


def build_registry(
    rules_dir: Path,
    home: Path,
    out_path: Path | None = None,
    reporter: Reporter | None = None,
) -> dict:
    """Scan ``rules_dir`` and write ``home/index.yaml``.

    Returns the registry dict that was written.
    """
    if reporter is None:
        reporter = Reporter()
        
    home = home.resolve()
    rules_dir = rules_dir.resolve()
    out = (out_path or (home / "index.yaml")).resolve()

    rules: list[dict] = []
    inline_bundles: dict[str, list[str]] = {}
    seen_ids: dict[str, str] = {}

    for md in sorted(rules_dir.rglob("*.md")):
        if md.name.startswith("."):
            continue
            
        try:
            rel = md.resolve().relative_to(home)
            path_str = str(rel)
        except ValueError:
            path_str = str(md.resolve())
            
        meta, _body, raw, err = _parse_frontmatter(md.read_text())
        if err:
            if err["type"] == "no_frontmatter":
                reporter.skipped(
                    path=path_str,
                    message="skipped — no YAML frontmatter found.",
                    suggested_fix="Add a `---`-delimited block at the top of the file."
                )
            elif err["type"] == "yaml_parse":
                reporter.error(
                    path=path_str,
                    line=err.get("line"),
                    category="yaml_parse",
                    message=f"invalid YAML frontmatter — {err['msg']}.",
                    suggested_fix="Check indentation (must be spaces, not tabs)."
                )
            continue
            
        if not meta:
            reporter.skipped(
                path=path_str,
                message="skipped — no YAML frontmatter found.",
                suggested_fix="Add a `---`-delimited block at the top of the file."
            )
            continue
            
        if "id" not in meta:
            reporter.error(
                path=path_str,
                category="missing_id",
                message="missing required field 'id'.",
                suggested_fix="Add `id: <slug>` to the frontmatter."
            )
            continue

        rid = str(meta["id"]).strip()
        
        if rid in seen_ids:
            reporter.error(
                path=path_str,
                category="duplicate_id",
                message=f"Duplicate rule id {rid} in:\n  {seen_ids[rid]}\n  {path_str}",
                suggested_fix="Rename one or merge."
            )
            continue
        else:
            seen_ids[rid] = path_str

        title = str(meta.get("title") or meta.get("name") or rid)
        
        try:
            tier = int(meta.get("tier", 2))
        except ValueError:
            tier = -1
        if tier not in (1, 2, 3):
            reporter.error(
                path=path_str,
                category="invalid_tier",
                message=f"invalid tier {meta.get('tier')}.",
                suggested_fix="Allowed: 1, 2, 3."
            )
            continue
            
        raw_triggers = meta.get("triggers")
        if raw_triggers is not None and not isinstance(raw_triggers, list):
            reporter.error(
                path=path_str,
                category="invalid_triggers",
                message=f"'triggers' must be a list. Got {type(raw_triggers).__name__}.",
                suggested_fix="Use YAML list syntax: triggers: [foo, bar]."
            )
            continue
            
        triggers = [str(t) for t in (raw_triggers or [])]

        # SKILL.md interop: vanilla skills default to tier 2 and have no triggers
        # (they use `description` instead). Warn but still index — audit will
        # surface tier-2-no-triggers in its own pass for users who care.
        if tier == 2 and not triggers and meta.get("tier") is not None:
            reporter.warning(
                path=path_str,
                category="tier_2_no_triggers",
                message="tier 2 rule has no 'triggers' field; it will never load via prompt match.",
                suggested_fix="Add triggers, or move to tier: 3 if it's reference-only."
            )

        deps = [str(d) for d in (meta.get("deps") or [])]
        bundles = [str(b) for b in (meta.get("bundles") or [])]
        summary = str(meta.get("summary") or meta.get("description") or "").strip()
        status = str(meta.get("status", "active"))

        body_bytes = raw.encode()
        rules.append(
            {
                "id": rid,
                "title": title,
                "path": path_str,
                "tier": tier,
                "triggers": triggers,
                "deps": deps,
                "summary": summary,
                "bytes": len(body_bytes),
                "tokens_approx": max(1, len(body_bytes) // 4),
                "checksum": "sha256:" + hashlib.sha256(body_bytes).hexdigest()[:16],
                "status": status,
            }
        )

        for b in bundles:
            inline_bundles.setdefault(b, []).append(rid)

    bundles_file = home / "bundles.yaml"
    if not bundles_file.exists():
        bundles_file = home / "bundles.yml"
    file_bundles: dict[str, list[str]] = {}
    if bundles_file.exists():
        try:
            loaded = yaml.safe_load(bundles_file.read_text()) or {}
            if isinstance(loaded, dict):
                file_bundles = {k: list(v) for k, v in loaded.items()}
        except yaml.YAMLError:
            pass

    bundles: dict[str, list[str]] = {**inline_bundles}
    for name, members in file_bundles.items():
        merged = list(dict.fromkeys([*bundles.get(name, []), *members]))
        bundles[name] = merged
        
    known_ids = {r["id"] for r in rules}
    for b_name, b_members in bundles.items():
        for member in b_members:
            if member not in known_ids:
                reporter.error(
                    path=str(bundles_file.name if bundles_file.exists() else "bundles.yaml"),
                    category="unknown_rule_in_bundle",
                    message=f"bundle '{b_name}' references unknown rule '{member}'.",
                    suggested_fix=f"Known ids: {', '.join(sorted(known_ids))}." if known_ids else "Known ids: none."
                )

    tier_totals = {
        f"tier_{t}": sum(1 for r in rules if r["tier"] == t) for t in (1, 2, 3)
    }
    token_totals = {
        f"tier_{t}": sum(r["tokens_approx"] for r in rules if r["tier"] == t)
        for t in (1, 2, 3)
    }

    from datetime import datetime, timezone

    registry = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_rules": len(rules),
        "tier_totals": tier_totals,
        "token_totals": token_totals,
        "rules": rules,
        "bundles": bundles,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        yaml.safe_dump(registry, f, sort_keys=False, default_flow_style=False)

    return registry


def _parse_frontmatter(text: str) -> tuple[dict | None, str, str, dict | None]:
    """Return (frontmatter_dict, body_without_fm, raw_full_text, error_dict)."""
    if not text.startswith(FRONTMATTER_FENCE):
        return None, text, text, {"type": "no_frontmatter"}
    end = text.find("\n" + FRONTMATTER_FENCE, len(FRONTMATTER_FENCE))
    if end == -1:
        return None, text, text, {"type": "no_frontmatter"}
    fm_raw = text[len(FRONTMATTER_FENCE) : end].strip()
    body = text[end + len(FRONTMATTER_FENCE) + 1 :].lstrip("\n")
    try:
        meta = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError as e:
        line = None
        if hasattr(e, "problem_mark") and e.problem_mark is not None: # type: ignore
            # e.problem_mark.line is 0-indexed relative to fm_raw.
            # fm_raw starts on line 2 (since line 1 is `---`).
            line = e.problem_mark.line + 2 # type: ignore
        return None, text, text, {"type": "yaml_parse", "msg": str(e), "line": line}
        
    if not isinstance(meta, dict):
        return None, text, text, {"type": "no_frontmatter"}
    return meta, body, text, None
