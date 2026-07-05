"""Registry integrity audit — catches drift, orphan deps, and unloadable rules."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ._config import require_home
from ._registry import load_registry


def audit_registry(home: Path | None = None) -> dict:
    """Integrity-check the registry against the filesystem."""
    h = (home or require_home()).resolve()
    reg = load_registry(h)
    rule_ids = {r["id"] for r in reg["rules"]}
    issues: dict[str, list] = {
        "checksum_mismatches": [],
        "missing_files": [],
        "orphan_deps": [],
        "orphan_bundle_refs": [],
        "over_broad_triggers": [],
        "no_triggers_in_tier_2": [],
        "duplicate_ids": [],
        "unreachable_rules": [],
    }

    seen_ids: dict[str, int] = {}
    for r in reg["rules"]:
        seen_ids[r["id"]] = seen_ids.get(r["id"], 0) + 1
        p = h / r["path"] if not Path(r["path"]).is_absolute() else Path(r["path"])
        if not p.exists():
            issues["missing_files"].append(r["id"])
            continue

        actual = "sha256:" + hashlib.sha256(p.read_text().encode()).hexdigest()[:16]
        if actual != r["checksum"]:
            issues["checksum_mismatches"].append(
                {"id": r["id"], "expected": r["checksum"], "actual": actual}
            )

        for dep in r.get("deps", []):
            if dep not in rule_ids:
                issues["orphan_deps"].append({"id": r["id"], "dep": dep})

        for t in r.get("triggers", []):
            if len(t) < 3:
                issues["over_broad_triggers"].append({"id": r["id"], "trigger": t})
                
        if r["tier"] == 2 and r.get("triggers"):
            stopwords = {"the", "and", "for", "are", "but", "not", "you", "all", "any", "can", "has", "him", "his", "how", "its", "out", "see", "she", "too", "use", "was", "who", "why"}
            for t in r.get("triggers", []):
                if len(t) == 1 or (len(t) == 3 and t.lower() in stopwords):
                    issues["unreachable_rules"].append({"path": r["path"], "id": r["id"], "trigger": t})

        if r["tier"] == 2 and not r.get("triggers"):
            issues["no_triggers_in_tier_2"].append(r["id"])

    for rid, count in seen_ids.items():
        if count > 1:
            issues["duplicate_ids"].append({"id": rid, "count": count})

    for bundle_name, members in reg.get("bundles", {}).items():
        for m in members:
            if m not in rule_ids:
                issues["orphan_bundle_refs"].append({"bundle": bundle_name, "member": m})

    return issues
