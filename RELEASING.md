# Releasing skillctl

skillctl releases are tag-driven. Pushing a tag matching `skillctl-v*` to `main` triggers the GitHub Actions release workflow, which builds, tests, publishes to PyPI via OIDC trusted publishing, and creates a GitHub Release.

---

## Per-release checklist

1. **Bump the version** in `packages/skillctl/pyproject.toml` under `[project] version`. Follow [SemVer](https://semver.org/spec/v2.0.0.html).
2. **Update `CHANGELOG.md`.** Move entries from `[Unreleased]` into a new `[X.Y.Z] — YYYY-MM-DD` section.
3. **Commit on `main`** (or the release branch).
   ```bash
   git add packages/skillctl/pyproject.toml packages/skillctl/CHANGELOG.md
   git commit -m "chore(skillctl): bump version to X.Y.Z"
   git push origin main
   ```
4. **Tag and push.** The tag must match `skillctl-v<version>`:
   ```bash
   git tag skillctl-vX.Y.Z
   git push origin skillctl-vX.Y.Z
   ```
5. **Watch the workflow.** `Actions → skillctl-release`. Three jobs run sequentially: `build` → `publish-pypi` → `github-release`. If `build` fails (twine check, version mismatch), nothing is published — fix and re-tag.
6. **Verify.** In a clean venv:
   ```bash
   python -m venv /tmp/skillctl-verify
   /tmp/skillctl-verify/bin/pip install skillctl==X.Y.Z
   /tmp/skillctl-verify/bin/skillctl --version
   ```
   You should see `skillctl X.Y.Z` and the CLI should respond to `--help`.
7. **Announce.** See `packages/skillctl/docs/launch/` for the v0.1 launch posts. For minor versions, a single CHANGELOG-derived post on the project README + release page is enough.

---

## One-time setup: PyPI trusted publisher

The release workflow uses [PyPI OIDC trusted publishing](https://docs.pypi.org/trusted-publishers/), not a long-lived API token. Configure it once:

1. Log into PyPI as the project owner.
2. Either:
   - **For a new project:** PyPI → *Your account* → *Publishing* → *Add a new pending publisher*. Fill in:
     - PyPI Project Name: `skillctl`
     - Owner: `suthakamal2`
     - Repository name: `brain`
     - Workflow filename: `skillctl-release.yml`
     - Environment: `pypi`
   - **For an existing project:** PyPI → *Manage* → *skillctl* → *Publishing* → *Add a new trusted publisher* with the same fields.
3. In GitHub: *Settings* → *Environments* → *New environment* → name it `pypi`. Optionally add a required reviewer / wait-timer / branch protection (only `main` and `skillctl-v*` tags can trigger releases via the workflow itself, but environment protection adds defence in depth).

After this, no `PYPI_API_TOKEN` is needed anywhere in the repo. OIDC short-lived credentials are minted per release.

---

## Emergency rollback

If a release was published with a bug bad enough to warrant pulling it:

1. **Yank the version on PyPI** (don't delete — yanking preserves audit trail and prevents new installs without breaking pinned installs of the bad version):
   ```bash
   # Via the web UI: PyPI → Manage → skillctl → Releases → X.Y.Z → Options → Yank
   ```
2. **Patch and re-release** as X.Y.Z+1. Never reuse a version number — PyPI rejects re-uploads of a yanked version anyway.
3. **Note the yank in the next CHANGELOG entry** under `### Yanked`.

---

## What gets shipped

- **PyPI:** sdist (`.tar.gz`) + universal wheel (`py3-none-any.whl`), built from `packages/skillctl/` only. The rest of the parent repo is not included in the distribution.
- **GitHub Release:** same two artefacts attached, plus auto-generated release notes pulled from `CHANGELOG.md`.
- **Not shipped here:** Homebrew formula (separate `brew bump-formula-pr` step), npm package (manual `npm publish` from `distribution/npm/`), Claude Code plugin (no central registry — users install the skill directory directly).
