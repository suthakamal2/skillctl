# Standalone CI for the extracted repo

These workflows are **inert inside the parent monorepo** — GitHub Actions only runs
`.github/workflows/` at the *repository root*, so a nested `packages/skillctl/.github/`
is ignored there. They activate when this package is extracted to its own repository
(`suthakamal2/skillctl`), where it becomes the repo root.

- `workflows/ci.yml` — lint + test matrix (py3.10–3.13 × linux/macos) + build/twine check, on `ubuntu-latest` (free for public repos).
- `workflows/release.yml` — on a `skillctl-v*` tag: build, publish to PyPI via OIDC trusted publisher, cut a GitHub Release from the CHANGELOG.

The monorepo keeps its own `skillctl-ci.yml` / `skillctl-release.yml` at its root (self-hosted runner) for in-monorepo validation; those are not copied out.

PyPI publish requires a one-time trusted-publisher config on PyPI for `suthakamal2/skillctl` (workflow `release.yml`, environment `pypi`).
