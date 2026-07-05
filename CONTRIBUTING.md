# Contributing to skillctl

Short and serious. skillctl is a small, sharp tool — contributions should keep it that way.

---

## Scope

skillctl is **a registry + dependency resolver + loader for AI-agent rules and skills**. It is intentionally not:

- A semantic retriever (use RAG for that).
- A skill authoring environment (use your editor).
- A skill marketplace (Anthropic already has one).
- An agent framework (use the SDK of your choice).

If a proposed feature pushes skillctl toward any of those, it's probably a separate project. Open an issue first so we can talk about scope.

---

## Before you open a PR

1. **There must be an issue first.** For anything larger than a one-line typo fix. Sketch the problem in the issue; we'll figure out the right shape together. This is to save your time, not to gate-keep.
2. **Read [README.md](README.md), [docs/comparison.md](docs/comparison.md), and at least skim [docs/extraction-inventory.md](docs/extraction-inventory.md)** so you know the positioning. Many "should we add X?" questions are answered by what skillctl deliberately doesn't do.
3. **Look at recent PRs** for the local style.

---

## Development setup

```bash
git clone https://github.com/suthakamal2/skillctl.git
cd skillctl
pip install -e .[dev]
python -m pytest tests/ -v
```

You need Python 3.10+. The package has two runtime deps (`pyyaml`, `rich`) and we'd like to keep it that way — please open an issue before adding a third.

---

## The bar

| Area | Standard |
|---|---|
| Tests | Every behaviour change ships with tests. No exceptions. The smoke test suite (`tests/test_smoke.py`) is the contract — if your change requires editing those tests, that's a yellow flag worth discussing in the PR. |
| Determinism | The matcher is intentionally deterministic. Don't introduce probabilistic ranking, similarity scoring, or model calls into the trigger path. If your idea needs those, build it as a separate layer. |
| Library boundary | The library (`src/skillctl/*.py`) must not import anything from the CLI (`_cli.py`). The CLI is allowed to depend on the library; never the reverse. |
| JSON output | All commands that emit JSON must keep their JSON shape stable. JSON output is a public API. Bumping a JSON field requires a minor version bump and a CHANGELOG entry. |
| Dependencies | Two runtime deps total: `pyyaml`, `rich`. Adding a third needs an issue. |
| Style | `ruff check .` passes. We use the project's pyproject ruff config. |
| Type hints | New code is typed. `from __future__ import annotations` at the top of every module. |
| Comments | Default to none. Only add a comment for *why*, never *what*. Public functions get a one-line docstring; complex internals get a short paragraph if the why is genuinely non-obvious. |
| Commits | One logical change per commit, present-tense imperative, scope tag in the subject (e.g. `feat(loader): support multi-home registries`). |
| British English | The codebase uses British spelling in docs and user-facing strings (`-ise`, `-our`, `-re`). Identifiers and library names follow upstream conventions. |
| Emojis | No. |

---

## How rule schemas evolve

The YAML frontmatter schema is a public contract. Changes require:

1. A migration story for existing rule files (silent backward compatibility, or a `skillctl migrate` command).
2. A note in `CHANGELOG.md`.
3. An update to `README.md` and `docs/comparison.md` if the change affects positioning.
4. Tests covering both the old and new shape.

The same rule applies to the registry format (`index.yaml`). Adding fields is fine; renaming or removing fields needs a `schema_version` bump and a migration.

---

## SKILL.md interop is sacred

skillctl is positioned as "on top of Anthropic Agent Skills, not a replacement." Any change that breaks reading a vanilla SKILL.md (one using only `name` + `description`, no `tier`, no `triggers`) is rejected by default. There is a test for this; don't delete it.

---

## Reporting bugs

Include:

- skillctl version (`skillctl --version`)
- Python version
- OS
- Minimal repro (the smallest set of rule files that demonstrates the issue — please don't paste your entire registry)
- What you expected
- What happened

Bug reports that include a failing test are merged in 24 hours when feasible.

---

## Security

Don't open public issues for security problems. Email instead: see the project root for current contact. Coordinate disclosure on a reasonable timeline.

---

## License

By contributing you agree that your contributions are licensed under the project's [MIT license](LICENSE).
