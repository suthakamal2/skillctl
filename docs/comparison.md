# How skillctl compares

This page exists so you can decide quickly whether skillctl solves a real problem for you, or whether you already have what you need.

skillctl is **not** a replacement for any of the systems below. It reads them, indexes them, and adds four things they don't: named bundles, transitive dependency resolution, deterministic keyword triggers, and a token-budget-aware loader callable from outside the agent.

If those four things don't matter for your project, you don't need skillctl. The existing tools are good.

---

## At a glance

|  | [Anthropic Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | [Cursor Rules (`.mdc`)](https://docs.cursor.com/context/rules) | [Ruler](https://github.com/intellectronica/ruler) | [dotagent](https://github.com/johnlindquist/dotagent) | [AGENTS.md](https://agents.md) | **skillctl** |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Progressive disclosure (frontmatter → body → linked files) | ✓ | partial | — | — | — | ✓ |
| Cross-agent file portability | ✓ | — (Cursor only) | ✓ | ✓ | ✓ | ✓ |
| Per-file YAML frontmatter triggers | ✓ (description) | ✓ (description, globs, alwaysApply) | — | ✓ | — | ✓ |
| Deterministic keyword triggers | — (LLM scoring) | partial (file globs) | — | — | — | **✓** |
| `why <topic>` introspection | — | — | — | — | — | **✓** |
| Named bundles | — | — | — | — | — | **✓** |
| Transitive dependency resolution | — | — | — | — | — | **✓** |
| Token-budget enforcement | silent truncation @ ~15K chars | — | — | — | — | **✓** |
| Callable as a Python library | — (agent-runtime only) | — | — | partial | — | **✓** |
| Reads existing SKILL.md unchanged | n/a | — | — | partial | — | **✓** |
| Reads existing `.cursor/rules/*.mdc` | — | n/a | — | partial | — | **✓** (frontmatter-compatible) |
| Auto-injects via SessionStart / prompt-submit hook | runtime-side only | — | — | — | — | **✓** (Claude Code) |
| Registry integrity audit | — | — | — | — | — | **✓** |

A `✓` in the rightmost column means "skillctl 0.1 ships this." A `—` means the system doesn't do it (or does it so partially it's not useful).

---

## 1. vs. Anthropic Agent Skills (the canonical reference)

**Anthropic Agent Skills** ([docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) shipped December 2025 and is now the cross-agent standard — Codex CLI, Gemini CLI, Copilot, Cursor, and Antigravity all read SKILL.md. If you're not familiar with the format, read Anthropic's intro first.

| Where they overlap |
|---|
| Progressive disclosure (name+description → body → linked files). |
| YAML frontmatter as the rule contract. |
| Filesystem-native — no servers, no SDK. |

| Where skillctl is different |
|---|
| **Skills activation is non-deterministic.** Anthropic's loader scores skill descriptions against the user prompt using the model itself. It works most of the time and fails in ways that are hard to debug — there's [an entire DEV.to article](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h) called *"Why Claude Code Skills Don't Trigger."* skillctl uses **word-boundary keyword match** against your declared triggers. The match is deterministic and `skillctl why <topic>` explains exactly why a rule fired or didn't. |
| **No bundles or dependency graph in Skills.** If your "deploy" workflow needs `safe-deploy`, `docker-control`, and `branch-management` together, you cross-reference them in prose. skillctl declares the bundle once and resolves transitive deps. |
| **Skills budget is silent.** Anthropic's loader truncates Level-1 descriptions at ~15K characters with no visible warning. skillctl makes the budget explicit (`--max-tokens`) and shows you exactly what was loaded and what was dropped. |
| **Skills are for the LLM to call.** skillctl is also a Python library — useful from SessionStart hooks, evals, server jobs, and your own tooling. |

**skillctl reads SKILL.md unchanged.** Drop a SKILL.md anywhere under your rules directory and `skillctl build` indexes it with `tier: 2` default. Anthropic-only fields (`name`, `description`) are honoured; skillctl-only fields (`tier`, `triggers`, `deps`) are simply ignored by Anthropic's loader. **You don't have to choose.**

---

## 2. vs. Cursor Rules (`.cursor/rules/*.mdc`)

Cursor's rules ([docs](https://docs.cursor.com/context/rules)) use MDC — Markdown with a YAML frontmatter block. Four activation modes:

- `alwaysApply: true` — always loaded
- `globs: "*.ts"` — auto-attached when the editor is on a matching file
- `description: "..."` — agent-requested (model decides, like Skills)
- Manual: `@rule-name` in the chat

| Where they overlap |
|---|
| Per-file YAML frontmatter. |
| Multiple activation modes. |
| Markdown body. |

| Where skillctl is different |
|---|
| **Cursor's `globs` mode is genuinely useful and skillctl doesn't replicate it** — globs are a different question (file context, not prompt content). If your needs are mostly "load this rule when editing TypeScript," stay with Cursor. |
| **Cursor's agent-requested mode is the same opaque scoring as Skills.** skillctl's deterministic triggers + `why` give you a debuggable alternative. |
| **No bundles, no dep graph, no token budget, no library access.** Same gap as Skills. |
| **Cursor-only.** Rules don't travel to Claude Code or Codex. skillctl reads them transparently (the MDC frontmatter is compatible) so you can use the same rule files across agents. |

If you're a Cursor user and you want to keep using the editor-glob triggers, **skillctl complements Cursor rather than replacing it.** Use `globs` for file-context rules; use skillctl for prompt-keyword rules and bundles.

---

## 3. vs. Ruler

[Ruler](https://github.com/intellectronica/ruler) is a single-source-of-truth tool: it concatenates Markdown files from `.ruler/` and writes the result into each agent's native rule file (`CLAUDE.md`, `.cursorrules`, `copilot-instructions.md`, etc.). It solves the "five agents, five different rule files, all out of sync" problem cleanly.

| Where they overlap |
|---|
| Polyglot agent goal: one source, multiple targets. |
| Filesystem-native. |

| Where skillctl is different |
|---|
| **Ruler is a write-out tool, not a runtime.** It bakes rules into static files at apply time. skillctl reads its registry at runtime and decides what to load based on the current prompt. |
| **No triggers in Ruler.** Whatever you write gets concatenated and shipped to every agent for every prompt. That's by design — Ruler trusts agents to ignore irrelevant content. skillctl assumes agent context is precious and only injects what was triggered. |
| **No dep graph, no bundles, no budget.** |

**Use them together.** Ruler can write your `CLAUDE.md` / `AGENTS.md` headers from a canonical source. skillctl handles the dynamic loading once the agent is running. They don't fight.

---

## 4. vs. dotagent

[dotagent](https://github.com/johnlindquist/dotagent) is a converter between agent rule formats — `.agent/` canonical → Claude / Cursor / Cline / Windsurf / Zed / Codex / Aider / Gemini / Qodo / Junie / Roo / OpenCode. Supports priority metadata in YAML frontmatter.

| Where they overlap |
|---|
| Multi-agent file format awareness. |
| YAML frontmatter as the metadata carrier. |

| Where skillctl is different |
|---|
| **dotagent is conversion plumbing.** It translates one rule file into N agent-native formats. skillctl is a loader: given N rule files, decide which to inject this turn. |
| **No runtime, no triggers, no dep graph.** |

dotagent is the right tool if your problem is "I want to author rules once and have them appear correctly in nine different agents." skillctl is the right tool if your problem is "I have a lot of rules and I want only the relevant ones loaded right now."

---

## 5. vs. AGENTS.md (the convention)

[AGENTS.md](https://agents.md) is not a tool — it's a convention. A single Markdown file at the project root that every agent reads for general guidance. Adopted in 60K+ repositories.

| Where they overlap |
|---|
| Project-level instructions for agents. |
| Plain Markdown. |

| Where skillctl is different |
|---|
| **AGENTS.md is one file.** Once it grows past a few thousand tokens, you've recreated the "150K-token CLAUDE.md" problem skillctl was originally built to solve. |
| **AGENTS.md has no activation logic.** Always loaded, fully. That's the point of the convention. skillctl is for when your project has enough rules that "always loaded fully" stops being affordable. |

**Use them together.** Keep an AGENTS.md for the always-on essentials (~few hundred tokens). Use skillctl for the long tail of conditional rules.

---

## Decision tree

```
Are your rules small enough to fit in one always-on Markdown file?
├─ Yes  → AGENTS.md or CLAUDE.md is fine. Skip skillctl.
└─ No
   ├─ Do you need cross-agent (Claude + Cursor + Codex) support?
   │  ├─ Yes → consider Ruler or dotagent for authoring
   │  └─ No  → stay with your agent's native format (SKILL.md / .mdc)
   │
   └─ Do you have:
      ├─ Groups of rules that always go together?     → skillctl bundles
      ├─ Rules with dependencies on other rules?      → skillctl deps
      ├─ "Why didn't my skill trigger?" problems?     → skillctl why
      ├─ A token budget that matters?                 → skillctl --max-tokens
      └─ Need to call rule-loading from non-LLM code? → skillctl library API
```

---

## A note on positioning

skillctl was extracted from a private polyglot harness where Claude Code, Codex, Cursor, and Gemini CLI all read the same registry through the same Python loader. The "five agents, one truth" guarantee is stronger than file-format portability — it's the same code making the same decisions. That's the design constraint that produced the four headline features. If you only run one agent, you may not need all of them.

Found a comparison error? File an issue. The goal is to help readers pick the right tool, not to win.
