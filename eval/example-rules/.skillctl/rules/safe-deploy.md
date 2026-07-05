---
id: safe-deploy
title: "Safe Deploy"
tier: 2
triggers: [deploy, ship, release, rollout, production, staging]
deps: [docker, ci-cd, rollback]
summary: "Blue/green or canary; run the suite first; never deploy on red."
---

# Safe Deploy

Blue/green or canary; run the suite first; never deploy on red.

## When this applies
Loads when the prompt mentions: deploy, ship, release, rollout, production, staging.

## Guidance
- Blue/green or canary; run the suite first; never deploy on red.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
