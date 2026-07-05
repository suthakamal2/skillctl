# skillctl

**The missing dependency resolver and bundle manager for Agent Skills, Cursor Rules, and `CLAUDE.md`.**

`skillctl` sits on top of the rule/skill systems your AI coding agent already uses ([Anthropic Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Cursor Rules](https://docs.cursor.com/context/rules), [`CLAUDE.md`](https://docs.claude.com/en/docs/claude-code/memory), [`AGENTS.md`](https://agents.md)) and adds the four things they don't ship:

1. **Named bundles with transitive dependency resolution.** Define `bundle: deploy → [safe-deploy, docker-control, branch-management]` once; load the closure with one command.
2. **Deterministic keyword triggers.** Rules activate by word-boundary match against the user's prompt, not by opaque description-similarity scoring inside the model. Includes `why <topic>` for debuggable matches.
3. **Token-budget enforcement.** Hard cap on what gets stitched into the agent's context, with a manifest of what was dropped.
4. **A library you can call from outside the agent.** `from skillctl import load_topics, load_bundle, suggest_topics` — usable from hooks, server jobs, and your own code, not just the LLM.

Built for polyglot harnesses — the same registry feeds Claude Code, Codex, Cursor, Gemini CLI, and Copilot without divergence.

---

## Why this exists

Anthropic shipped [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) in December 2025 and the whole agent ecosystem adopted progressive disclosure within weeks. It's table-stakes now. But four real problems remained:

| Problem | What's broken | What `skillctl` does |
|---|---|---|
| **"Which skills do I load for X?"** | Skill activation is description-similarity scoring inside the model. Non-deterministic. There's a [whole DEV.to article](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h) titled *"Why Claude Code Skills Don't Trigger."* | Keyword triggers in YAML frontmatter. Deterministic match. `skillctl why <topic>` shows exactly why a rule fired (or didn't). |
| **"How do I group related skills?"** | No bundles, no dependency graph. Authors cross-reference in prose. | Named bundles + transitive dep resolution. `skillctl bundle deploy` returns the closure. |
| **"How much context did I just inject?"** | Silent truncation at ~15K chars for Level-1 descriptions. No visibility. | Token budget you control. Manifest of loaded + dropped rules with each call. |
| **"How do I use this from non-LLM code?"** | Skills assume the consumer is an agent runtime. | Python library + JSON output. Call from SessionStart hooks, server jobs, evals. |

`skillctl` is not a replacement for Agent Skills, Cursor Rules, or `CLAUDE.md`. It reads them, indexes them, resolves dependencies between them, and loads them on demand with deterministic triggers.

---

## Quickstart

### Migrating from Cursor / AGENTS.md / SKILL.md

```bash
# import from .cursor/rules/
skillctl migrate cursor

# import from an AGENTS.md file
skillctl migrate agents

# import from a directory of SKILL.md files
skillctl migrate skill-md path/to/skills/
```



```bash
pip install skillctl

# initialise a rules directory (creates .skillctl/rules/)
skillctl init

# index your rules (defaults to .skillctl/rules/; pass a path to index elsewhere)
skillctl build

# suggest what to load for a given prompt
skillctl suggest "I want to deploy to production"

# load a bundle
skillctl bundle deploy

# explain why a topic matched
skillctl why deploy
```

*(Note: Human-readable CLI outputs are styled with colours by default. Set `NO_COLOR=1` to disable.)*

### As a Python library

```python
from skillctl import load_topics, load_bundle, suggest_topics

# Suggest rules to load for a user prompt
matches = suggest_topics("ship the v2 API to staging")
# → [MatchResult(rule_id='safe-deploy', triggers=['ship', 'staging']), ...]

# Load a bundle by name, with transitive dep resolution and token budget
markdown_brief = load_bundle("deploy", max_tokens=10000)

# Or load by explicit topics
markdown_brief = load_topics(["docker", "kubernetes"], max_tokens=5000)
```

### As a Claude Code prompt-submit hook

```bash
skillctl install claude-code
```

This reads or creates `.claude/settings.json` and adds a `UserPromptSubmit` hook that runs `skillctl inject`. The relevant rule bodies are auto-injected into a `<dynamic-rule-context>` block based on what the user typed — without the agent having to call any tool.

For Cursor, run `skillctl install cursor` for instructions on manual injection, as Cursor doesn't support a synchronous prompt hook.
For Codex CLI, run `skillctl install codex` for piping instructions.

---

## Rule format

A `skillctl` rule is a Markdown file with YAML frontmatter. **It is intentionally a superset of [`SKILL.md`](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):** existing skills work as-is; the additional fields (`tier`, `triggers`, `deps`, `bundles`) are ignored by Anthropic's skill loader but used by `skillctl`.

```markdown
---
id: safe-deploy
title: Safe deployment protocol
tier: 2
triggers: [deploy, ship, production, rollout, canary]
deps: [docker-control, branch-management]
summary: How we ship code without breaking production.
---

# Safe deployment protocol

...
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique within the registry. |
| `title` | yes | Human-readable. |
| `tier` | no (default 2) | `1` = always-on, `2` = trigger-loaded, `3` = on-demand only. |
| `triggers` | when `tier: 2` | Keywords. Word-boundary match against the user prompt. |
| `deps` | no | Other rule IDs to load transitively. |
| `summary` | no | One-line description (used in `list` and `suggest` output). |
| `description` | no | SKILL.md-compatible field. Used as `summary` fallback. |

Bundles live in `.skillctl/bundles.yaml` — a top-level map of `name: [rule-ids]`, no wrapper key:

```yaml
# .skillctl/bundles.yaml
deploy: [safe-deploy, docker-control, branch-management]
multi-agent: [agent-handoff, workspace-required, branch-management]
security-review: [security-review, dependency-audit, secrets-scan]
```

---

## Comparison

See [`docs/comparison.md`](docs/comparison.md) for a feature matrix vs. Anthropic Agent Skills, Cursor Rules, Ruler, dotagent, and Aider conventions.

| | Anthropic Skills | Cursor Rules | Ruler | dotagent | **skillctl** |
|---|:-:|:-:|:-:|:-:|:-:|
| Progressive disclosure | ✓ | partial | — | — | ✓ |
| Cross-agent file portability | ✓ | — | ✓ | ✓ | ✓ |
| Deterministic keyword triggers | — | partial (globs) | — | — | **✓** |
| Named bundles | — | — | — | — | **✓** |
| Transitive dependency resolution | — | — | — | — | **✓** |
| Token-budget enforcement | silent truncation | — | — | — | **✓** |
| Debug introspection (`why`) | — | — | — | — | **✓** |
| Callable as a library | — | — | — | partial | **✓** |
| Reads existing SKILL.md | n/a | — | — | partial | **✓** |

---

## Status

**v0.1 — early access.** The core (registry, loader, matcher, audit) ran as the live rule-loader across five agent harnesses (Claude Code, Codex, Cursor, Gemini CLI, Copilot) in a private codebase for a month before extraction — every prompt logged against the legacy loader it replaced. That dogfooding earned its keep: it caught a real bug where the hook preferred the new engine even when its index had drifted from canonical, under-firing on a fraction of prompts (deploy-safety rules among them) until a freshness guard closed it. The packaging, CLI polish, and SKILL.md interop are newer. Expect rough edges. File issues.

## License

MIT. See [LICENSE](LICENSE).
