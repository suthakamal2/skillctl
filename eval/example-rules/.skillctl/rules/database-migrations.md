---
id: database-migrations
title: "Database Migrations"
tier: 2
triggers: [migration, schema, alter table, ddl]
deps: [rollback]
summary: "Additive + backward-compatible first; expand/contract; never destructive in one step."
---

# Database Migrations

Additive + backward-compatible first; expand/contract; never destructive in one step.

## When this applies
Loads when the prompt mentions: migration, schema, alter table, ddl.

## Guidance
- Additive + backward-compatible first; expand/contract; never destructive in one step.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
