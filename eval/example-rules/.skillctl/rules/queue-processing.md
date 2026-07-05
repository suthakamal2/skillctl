---
id: queue-processing
title: "Queue Processing"
tier: 2
triggers: [queue, message queue, consumer, kafka, sqs]
summary: "At-least-once by default; idempotent consumers; monitor lag and DLQ depth."
---

# Queue Processing

At-least-once by default; idempotent consumers; monitor lag and DLQ depth.

## When this applies
Loads when the prompt mentions: queue, message queue, consumer, kafka, sqs.

## Guidance
- At-least-once by default; idempotent consumers; monitor lag and DLQ depth.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
