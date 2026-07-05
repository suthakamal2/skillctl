"""skillctl — dependency resolver and bundle manager for Agent Skills / Cursor Rules / CLAUDE.md.

Public API:

    from skillctl import (
        # registry
        load_registry,
        get_rule,
        read_rule_body,
        # matching
        MatchResult,
        match_by_topic,
        suggest_topics,
        suggest_bundles,
        explain_match,
        # loading
        load_topics,
        load_bundle,
        resolve_deps,
        # audit
        audit_registry,
        # building
        build_registry,
        # migrate
        migrate_agents,
        migrate_cursor,
        migrate_skill_md,
    )

Determinism note: skillctl is intentionally **not** a semantic retriever.
Keyword match + explicit topics + dep resolution. No silent injection. Rules
are deterministic contracts; RAG is probabilistic. "Loaded the wrong rule"
is worse than "loaded no rule."
"""

from __future__ import annotations

__version__ = "0.1.0"

from ._audit import audit_registry
from ._build import build_registry
from ._inject import inject
from ._loader import load_bundle, load_topics, resolve_deps
from ._matching import (
    MatchResult,
    explain_match,
    match_by_topic,
    suggest_bundles,
    suggest_topics,
)
from ._migrate import migrate_agents, migrate_cursor, migrate_skill_md
from ._registry import (
    DEFAULT_MAX_TOKENS,
    get_rule,
    get_rules_by_tier,
    load_registry,
    read_rule_body,
)

__all__ = [
    "__version__",
    # registry
    "DEFAULT_MAX_TOKENS",
    "get_rule",
    "get_rules_by_tier",
    "load_registry",
    "read_rule_body",
    # matching
    "MatchResult",
    "explain_match",
    "match_by_topic",
    "suggest_bundles",
    "suggest_topics",
    # loading
    "load_bundle",

    "inject",
    "load_topics",
    "resolve_deps",
    # audit
    "audit_registry",
    # building
    "build_registry",
    # migrate
    "migrate_agents",
    "migrate_cursor",
    "migrate_skill_md",

]
