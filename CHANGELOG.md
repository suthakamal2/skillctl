# Changelog

All notable changes to skillctl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-17

### Added
- First public release.
- YAML-frontmatter-based rule registry. Each rule is a Markdown file with
  `id`, `title`, `tier`, `triggers`, `deps`, `summary` (or `name` /
  `description` for SKILL.md compatibility).
- **SKILL.md interop.** Vanilla Anthropic skill files (using `name` +
  `description`, no `tier`) are indexed transparently with `tier: 2` default.
- **Named bundles** declared in `bundles.yaml` or inline on rules, with
  transitive dependency resolution (`skillctl bundle <name>`).
- **Deterministic keyword triggers.** Word-boundary match against the user
  prompt. `skillctl why <topic>` explains why each rule matched (or didn't).
- **Token-budget enforcement.** `--max-tokens` caps what gets stitched into
  the agent's context; a manifest of dropped rules is included.
- **Python library API:** `from skillctl import load_topics, load_bundle, suggest_topics, inject, audit_registry, build_registry`.
- **CLI:** `init`, `build`, `list`, `show`, `load`, `suggest`, `why`,
  `bundles`, `bundle`, `audit`, `tier`, `inject`, `install`.
- **Rich output** for human-readable commands; `--json` for machine
  consumers; honours `NO_COLOR=1`.
- **Claude Code prompt-submit hook installer** (`skillctl install claude-code`)
  that writes the canonical nested `UserPromptSubmit` hook shape into
  `.claude/settings.json` and a portable shell script. Idempotent; preserves
  existing hooks; symmetric uninstall.
- **Distribution channels:** PyPI (primary), Homebrew tap, npm wrapper,
  Claude Code skill plugin.
- **Examples:** 5 generic bundles (`deploy`, `multi-agent`, `security-review`,
  `refactor`, `debug`) with 14 example rule files under `examples/.skillctl/`.

### Known limitations
- Homebrew formula ships with sha256 placeholders — they're filled at release
  time via `brew bump-formula-pr`.
- npm wrapper auto-installs via pip on first run if `skillctl` isn't on
  `PATH`. We may make this prompt-first in 0.2.
- Cursor doesn't expose a synchronous prompt-submit hook; integration there
  is documented but manual.
