---
id: database-indexing
title: "Database Indexing"
tier: 2
triggers: [index, indexing, composite index]
summary: "Index for the query, not the table; concurrent creation in prod; drop unused."
---

# Database Indexing

Index for the query, not the table; concurrent creation in prod; drop unused.

## When this applies
Loads when the prompt mentions: index, indexing, composite index.

## Guidance
- Index for the query, not the table; concurrent creation in prod; drop unused.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
