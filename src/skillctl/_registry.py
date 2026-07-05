"""Registry access — load and cache the on-disk index."""

from __future__ import annotations

from pathlib import Path

import yaml

from ._config import find_home, index_path, require_home

DEFAULT_MAX_TOKENS = 20000

_REGISTRY_CACHE: dict[str, dict] = {}


def load_registry(home: Path | None = None) -> dict:
    """Load and cache ``index.yaml`` for the given (or auto-detected) home."""
    h = (home or require_home()).resolve()
    key = str(h)
    if key not in _REGISTRY_CACHE:
        idx = index_path(h)
        if not idx.exists():
            raise FileNotFoundError(
                f"Registry not found at {idx}. Run `skillctl build` to "
                f"generate it from your rule files."
            )
        with idx.open() as f:
            _REGISTRY_CACHE[key] = yaml.safe_load(f)
    return _REGISTRY_CACHE[key]


def clear_cache() -> None:
    """Reset the registry cache. Useful in tests and after `build`."""
    _REGISTRY_CACHE.clear()


def get_rule(rule_id: str, home: Path | None = None) -> dict | None:
    reg = load_registry(home)
    for r in reg["rules"]:
        if r["id"] == rule_id:
            return r
    return None


def get_rules_by_tier(tier: int, home: Path | None = None) -> list[dict]:
    reg = load_registry(home)
    return [r for r in reg["rules"] if r["tier"] == tier]


def read_rule_body(rule_id: str, home: Path | None = None) -> str:
    """Return the rule's body text, with YAML frontmatter stripped.

    Frontmatter is only metadata — agents should see clean Markdown.
    """
    rule = get_rule(rule_id, home)
    if not rule:
        raise ValueError(f"Unknown rule: {rule_id}")
    h = (home or require_home()).resolve()
    p = (h / rule["path"]).resolve() if not Path(rule["path"]).is_absolute() else Path(rule["path"])
    text = p.read_text()
    return _strip_frontmatter(text)


def _strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block (between ``---`` lines)."""
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    after = text[end + 4 :]
    return after.lstrip("\n")


def auto_home() -> Path | None:
    """Public re-export of find_home for callers that want the optional path."""
    return find_home()
