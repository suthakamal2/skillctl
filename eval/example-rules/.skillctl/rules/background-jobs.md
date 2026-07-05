---
id: background-jobs
title: "Background Jobs"
tier: 2
triggers: [background job, worker, async task, job queue]
deps: [queue-processing]
summary: "Idempotent jobs, bounded retries, dead-letter on repeated failure."
---

# Background Jobs

Idempotent jobs, bounded retries, dead-letter on repeated failure.

## When this applies
Loads when the prompt mentions: background job, worker, async task, job queue.

## Guidance
- Idempotent jobs, bounded retries, dead-letter on repeated failure.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
