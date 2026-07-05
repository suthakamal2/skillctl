---
id: incremental-edits
title: Incremental refactors land in small commits
tier: 2
triggers: [incremental, small commits, atomic change, mechanical refactor]
deps: []
summary: Split a big refactor into reviewable commits. Each compiles. Each tests pass.
---

# Incremental refactors land in small commits

Big refactors fail in review for the same reason: the diff is too large for a human to hold in their head. The fix is mechanical: split the refactor into a sequence of small commits where each one is independently reviewable, compiles, and passes the full test suite.

**The pattern.**

- *Step 1: prepare.* Add the new abstraction alongside the old one. No call sites updated yet. Tests still pass — they exercise the old path.
- *Step 2: migrate one caller.* Switch a single call site to the new path. Tests still pass.
- *Step 3: migrate the rest.* Repeat for each call site, ideally one commit per logical group. Tests still pass at every commit.
- *Step 4: remove the old.* Delete the old abstraction once nothing references it. Tests still pass.

Each commit is small enough for a reviewer to read in two minutes. The combined PR is large, but the *review unit* is the commit, not the PR. Reviewers who use `git log -p` per commit catch bugs that reviewers who read the unified diff miss.

**The bar:** if a commit doesn't compile or fails tests, your refactor is not incremental. Squash, split, or bisect — but never push a "WIP, fix next commit" state through review. Bisect-ability is the load-bearing property; one broken commit ruins it for everyone who debugs the codebase later.
