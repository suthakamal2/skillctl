"""Topic matching and suggestion logic.

Deterministic by design — keyword match against rule triggers, no semantic
similarity, no LLM in the loop. The whole point is that ``skillctl why X``
gives the same answer every time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ._registry import load_registry


@dataclass
class MatchResult:
    rule_id: str
    tier: int
    matched_triggers: list[str]
    reason: str


def match_by_topic(topic: str, home: Path | None = None) -> list[MatchResult]:
    """Match a single topic keyword/phrase against rule triggers.

    Scoring:
      - Exact id match -> always wins
      - Trigger exact match -> match
      - Trigger substring of topic (len >= 4) -> match
      - Topic substring of trigger (len >= 4) -> match
    """
    topic_lc = topic.lower().strip()
    reg = load_registry(home)
    matches: list[MatchResult] = []

    for r in reg["rules"]:
        if r["id"].lower() == topic_lc:
            matches.append(MatchResult(r["id"], r["tier"], [r["id"]], "exact-id"))
            continue

        triggers_matched: list[str] = []
        for t in r.get("triggers", []):
            t_lc = t.lower()
            if t_lc == topic_lc or t_lc in topic_lc and len(t_lc) >= 4 or topic_lc in t_lc and len(topic_lc) >= 4:
                triggers_matched.append(t)

        if triggers_matched:
            matches.append(
                MatchResult(
                    r["id"],
                    r["tier"],
                    triggers_matched,
                    f"trigger-match:{triggers_matched[0]}",
                )
            )

    return matches


def suggest_topics(prompt: str, home: Path | None = None) -> list[MatchResult]:
    """Scan a full prompt for trigger matches. Word-boundary, case-insensitive."""
    reg = load_registry(home)
    prompt_lc = prompt.lower()
    seen: dict[str, MatchResult] = {}

    for r in reg["rules"]:
        matched: list[str] = []
        for t in r.get("triggers", []):
            t_lc = t.lower()
            if len(t_lc) < 3:
                continue
            if re.search(r"\b" + re.escape(t_lc) + r"\b", prompt_lc):
                matched.append(t)
        if matched:
            seen[r["id"]] = MatchResult(r["id"], r["tier"], matched, "prompt-scan")

    # Sort by tier (lower = higher priority), then by match count.
    return sorted(seen.values(), key=lambda m: (m.tier, -len(m.matched_triggers)))


def suggest_bundles(
    prompt: str,
    rule_suggestions: list[MatchResult],
    home: Path | None = None,
) -> list[tuple[str, int]]:
    """Find named bundles whose members overlap with the suggested rules.

    A bundle is suggested if at least 50% of its members matched.
    Returns (bundle_name, overlap_count), sorted by overlap then ratio.
    """
    reg = load_registry(home)
    bundles = reg.get("bundles", {})
    matched_ids = {m.rule_id for m in rule_suggestions}

    candidates: list[tuple[str, int, float]] = []
    for name, members in bundles.items():
        overlap = sum(1 for m in members if m in matched_ids)
        ratio = overlap / max(1, len(members))
        if overlap >= 1 and ratio >= 0.5:
            candidates.append((name, overlap, ratio))

    candidates.sort(key=lambda x: (-x[1], -x[2], x[0]))
    return [(name, overlap) for name, overlap, _ in candidates]


def explain_match(topic: str, home: Path | None = None) -> dict:
    """Explain why a topic matches (or doesn't) — backs ``skillctl why``."""
    matches = match_by_topic(topic, home)
    near_misses: list[dict] = []
    reg = load_registry(home)
    for r in reg["rules"]:
        for t in r.get("triggers", []):
            if t.lower() in topic.lower() or topic.lower() in t.lower():
                near_misses.append({"rule": r["id"], "trigger": t, "tier": r["tier"]})

    return {
        "topic": topic,
        "matched_rules": [
            {
                "rule": m.rule_id,
                "tier": m.tier,
                "reason": m.reason,
                "triggers": m.matched_triggers,
            }
            for m in matches
        ],
        "near_misses": near_misses[:10],
    }
