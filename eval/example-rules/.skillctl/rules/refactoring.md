---
id: refactoring
title: "Refactoring"
tier: 2
triggers: [refactor, cleanup, tech debt]
deps: [testing-strategy]
summary: "Green tests before and after; one refactor per commit; no behaviour change."
---

# Refactoring

Green tests before and after; one refactor per commit; no behaviour change.

## When this applies
Loads when the prompt mentions: refactor, cleanup, tech debt.

## Guidance
- Green tests before and after; one refactor per commit; no behaviour change.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
