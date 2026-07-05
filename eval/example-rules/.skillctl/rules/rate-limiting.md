---
id: rate-limiting
title: "Rate Limiting"
tier: 2
triggers: [rate limit, throttle, quota, 429]
summary: "Per-principal limits; return 429 + Retry-After; token bucket over fixed window."
---

# Rate Limiting

Per-principal limits; return 429 + Retry-After; token bucket over fixed window.

## When this applies
Loads when the prompt mentions: rate limit, throttle, quota, 429.

## Guidance
- Per-principal limits; return 429 + Retry-After; token bucket over fixed window.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
