---
id: branch-management
title: Branch management
tier: 1
triggers: [git, branch, merge, push, main, trunk, rebase]
deps: []
summary: Trunk-based development. Short-lived branches. Merge to main daily.
---

# Branch management

Default to **trunk-based development**. Long-lived feature branches accumulate merge debt that nobody is paid to clean up. Aim for branch lifetimes under 24 hours.

**Branch naming.** Use a prefix that signals intent: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`. Include a short kebab-case slug, not a ticket ID — the slug is what a teammate reads in a `git log` six months from now.

**Rebase vs merge.** Rebase your feature branch onto `main` before opening a PR (cleaner history, easier review). Merge the PR with a merge commit or squash — pick one and stick with it across the repo. Mixing is confusing.

**Never force-push to `main`.** Force-push to your own feature branch is fine; force-push to a branch others have based work on requires coordination.

**PR size.** Aim for diffs under 400 lines. If your PR is bigger, split it. Reviewers stop catching real bugs past ~400 lines; you're trading review quality for convenience.

**Delete merged branches.** Both locally (`git branch -d`) and on the remote. A stale branch list is a tax on every `git fetch`.
