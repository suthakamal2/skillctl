from __future__ import annotations

from pathlib import Path

from ._loader import resolve_deps
from ._matching import suggest_topics
from ._registry import get_rule, get_rules_by_tier, read_rule_body


def inject(prompt: str, max_tokens: int = 5000, top_n: int = 3, home: Path | None = None) -> str:
    """Return a <dynamic-rule-context> block ready for agent injection."""
    matches = suggest_topics(prompt, home)
    if not matches:
        return ""

    match_dict = {m.rule_id: m.matched_triggers for m in matches[:top_n]}

    # Build initial list of rules: Tier 1 + top N matches
    to_load = []
    tier1_rules = get_rules_by_tier(1, home)
    for r in tier1_rules:
        to_load.append(r["id"])
    
    for m in matches[:top_n]:
        if m.rule_id not in to_load:
            to_load.append(m.rule_id)

    # Resolve transitive dependencies
    to_load = resolve_deps(to_load, home)

    max_chars = max_tokens * 4
    budget_used = 0
    loaded_xml = []

    for rid in to_load:
        rule = get_rule(rid, home)
        if not rule:
            continue
            
        # Tier 3 skipped unless explicitly matched
        tier = rule.get("tier", 2)
        if tier == 3 and rid not in match_dict:
            continue
            
        body = read_rule_body(rid, home)
        chars = len(body)
        
        if budget_used + chars > max_chars:
            continue  # budget exhausted
            
        budget_used += chars
        
        # Determine trigger reason
        if rid in match_dict:
            triggered_on = ",".join(match_dict[rid])
        elif tier == 1:
            triggered_on = "always-on"
        else:
            triggered_on = "dependency"
            
        loaded_xml.append(
            f'<rule id="{rid}" triggered_on="{triggered_on}">\n{body}\n</rule>'
        )

    if not loaded_xml:
        return ""

    return "<dynamic-rule-context>\n" + "\n".join(loaded_xml) + "\n</dynamic-rule-context>"
