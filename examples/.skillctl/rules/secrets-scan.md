---
id: secrets-scan
title: Secrets scanning and remediation
tier: 2
triggers: [secret, credential, api key, leak, gitleaks, trufflehog]
deps: []
summary: A leaked secret is leaked forever. Rotate first, sanitise history second.
---

# Secrets scanning and remediation

**Prevention.** Run `gitleaks` (or `trufflehog`) as a pre-commit hook on every repository. The pre-commit pass is fast, cheap, and catches the everyday accidents — a `.env` paste, a hardcoded API key in a debug commit, an SSH private key in a config directory.

**Detection.** Run the same scanner in CI on every PR. A pre-commit hook protects developers who installed it; CI protects everyone else.

**If a secret leaks:**

1. **Rotate first.** Always. Before you touch git history, before you message anyone, before you investigate the blast radius — invalidate the credential. A secret that has been pushed to a public mirror is exposed within seconds; assume it's already been scraped.
2. **Then sanitise history.** Use `git filter-repo` (not the deprecated `git filter-branch`). Coordinate with everyone who has a clone — they must re-clone, not pull, after the history rewrite. The old commits live in their reflog otherwise.
3. **Notify.** Document what leaked, when, who was affected. If user data is involved, follow your incident playbook.

**Do not** revert the commit. Reverting hides the secret in `main`'s history but doesn't remove it from the commit graph — `git log -p` still shows it.

**Do not** rely on history rewrite as the fix. Rotation is the fix. History rewrite is hygiene.
