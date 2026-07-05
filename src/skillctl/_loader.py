"""Dependency resolution and rule loading (stitch into markdown briefs)."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ._matching import match_by_topic
from ._registry import DEFAULT_MAX_TOKENS, get_rule, load_registry, read_rule_body


def resolve_deps(
    rule_ids: Iterable[str],
    home: Path | None = None,
    max_depth: int = 5,
) -> list[str]:
    """Expand a rule ID list to include transitive deps.

    Returns a deduplicated, stable-ordered list with the original rules
    first and their deps appended in DFS order.
    """
    reg = load_registry(home)
    rule_map = {r["id"]: r for r in reg["rules"]}

    resolved: list[str] = []
    seen: set[str] = set()

    def walk(rid: str, depth: int) -> None:
        if rid in seen or depth > max_depth:
            return
        if rid not in rule_map:
            return  # unknown — skip silently; audit will surface it
        seen.add(rid)
        resolved.append(rid)
        for dep in rule_map[rid].get("deps", []):
            walk(dep, depth + 1)

    for rid in rule_ids:
        walk(rid, 0)

    return resolved


def load_topics(
    topics: list[str],
    max_tokens: int = DEFAULT_MAX_TOKENS,
    include_deps: bool = True,
    home: Path | None = None,
) -> str:
    """Stitch matching rules into a single markdown brief.

    Includes a manifest of what was loaded, why, and what was dropped due
    to budget exhaustion. ~4 chars/token heuristic.
    """
    rule_ids: list[str] = []
    topic_trace: dict[str, str] = {}

    for topic in topics:
        matches = match_by_topic(topic, home)
        if not matches:
            topic_trace[f"__unmatched_{topic}__"] = f"No rules matched topic: {topic!r}"
            continue
        for m in matches:
            if m.rule_id not in rule_ids:
                rule_ids.append(m.rule_id)
                topic_trace[m.rule_id] = m.reason

    if include_deps:
        with_deps = resolve_deps(rule_ids, home)
        for rid in with_deps:
            topic_trace.setdefault(rid, "dep-of-matched-rule")
        rule_ids = with_deps

    max_chars = max_tokens * 4
    budget_used = 0
    loaded: list[str] = []
    dropped: list[str] = []
    loaded_ids: list[str] = []

    for rid in rule_ids:
        rule = get_rule(rid, home)
        if not rule:
            continue
        body = read_rule_body(rid, home)
        manifest_line = (
            f"\n\n---\n\n## {rule['title']} "
            f"(`{rule['path']}` • tier {rule['tier']})\n\n"
        )
        total_chars = len(manifest_line) + len(body)
        if budget_used + total_chars > max_chars:
            dropped.append(rid)
            continue
        loaded.append(manifest_line + body)
        loaded_ids.append(rid)
        budget_used += total_chars

    header_lines = [
        "# Rules loaded on-demand",
        f"Topics: {', '.join(topics)}",
        f"Budget: {max_tokens:,} tokens ({max_chars:,} chars); "
        f"used ~{budget_used // 4:,} tokens",
        "",
        "## Loaded rules",
    ]
    for rid in loaded_ids:
        reason = topic_trace.get(rid, "?")
        rule = get_rule(rid, home)
        header_lines.append(f"- {rid} (tier {rule['tier']}) — {reason}")

    if dropped:
        header_lines.append("")
        header_lines.append("## Dropped due to budget")
        for rid in dropped:
            rule = get_rule(rid, home)
            tok = rule.get("tokens_approx", 0)
            header_lines.append(f"- {rid} (~{tok:,} tokens)")

    return "\n".join(header_lines) + "".join(loaded)


def load_bundle(
    bundle_name: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    home: Path | None = None,
) -> str:
    """Load a named bundle (with transitive deps) into a single markdown brief."""
    reg = load_registry(home)
    bundles = reg.get("bundles", {})
    if bundle_name not in bundles:
        raise ValueError(f"Unknown bundle: {bundle_name}. Known: {sorted(bundles)}")
    return load_topics(
        bundles[bundle_name],
        max_tokens=max_tokens,
        include_deps=True,
        home=home,
    )
