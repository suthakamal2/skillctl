---
id: sql-optimization
title: "Sql Optimization"
tier: 2
triggers: [slow query, query plan, sql performance, explain]
deps: [database-indexing]
summary: "Read the plan; avoid N+1; select only needed columns; watch sequential scans."
---

# Sql Optimization

Read the plan; avoid N+1; select only needed columns; watch sequential scans.

## When this applies
Loads when the prompt mentions: slow query, query plan, sql performance, explain.

## Guidance
- Read the plan; avoid N+1; select only needed columns; watch sequential scans.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
