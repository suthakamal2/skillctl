---
id: scope-freeze
title: Scope freeze for surgical refactors
tier: 2
triggers: [refactor, scope creep, surgical, frozen, edit set]
deps: []
summary: Declare the file set before refactoring. Touch nothing else.
---

# Scope freeze for surgical refactors

Before starting a refactor, write down the **exact set of files you intend to modify**. Stick it somewhere visible — top of the PR description, a comment in the issue, a `FREEZE.md` in the workspace. This is your scope freeze.

A freeze is a commitment to yourself and your reviewer. Any file outside the freeze that ends up in your diff is a scope creep — either justify it explicitly (in a PR comment, naming the reason) or revert it.

**Why this matters.** Refactors that touch "while I'm here" code are the highest-bug-density patches in the codebase. Reviewers calibrate their attention to the stated scope; surprises slip past. A scoped diff is reviewed harder than an unscoped one.

**When the freeze needs to expand**, expand it explicitly. Update the freeze file, mention it in the PR ("expanded scope to include `auth/middleware.py` because the signature change broke a call site I hadn't predicted"). Document the surprise, then proceed. Don't pretend it didn't happen.

**Test every changed line.** If a line is in the diff, the existing tests should cover it. If they don't, that's not optional — write the test first, then make the change. Untested refactors are the second-highest-bug-density patches.

The bar: every changed line traces directly to the stated refactor goal. Three lines of unrelated cleanup is not "improving the codebase" — it's a different PR.
