---
id: cron-jobs
title: "Cron Jobs"
tier: 2
triggers: [cron, scheduled task, scheduler]
deps: [background-jobs]
summary: "Idempotent + overlap-safe; alert on missed runs; record last success."
---

# Cron Jobs

Idempotent + overlap-safe; alert on missed runs; record last success.

## When this applies
Loads when the prompt mentions: cron, scheduled task, scheduler.

## Guidance
- Idempotent + overlap-safe; alert on missed runs; record last success.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
