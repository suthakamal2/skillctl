---
id: repro-first
title: Reproduce before you fix
tier: 2
triggers: [bug, repro, reproduce, intermittent, flake]
deps: []
summary: Get a deterministic reproduction before changing any code.
---

# Reproduce before you fix

Do not start changing code until you have a **deterministic reproduction** of the bug. This sounds obvious; it is the single most-skipped step in real bug fixing.

A deterministic reproduction has two properties:

1. You can trigger the bug on demand. Not "sometimes it fails" — "this command, on this branch, with these inputs, fails every time."
2. The reproduction is the size you need it to be. Smaller is better; minimal is best.

Without a reproduction, you cannot verify your fix. You can ship code that *might* fix the bug, but you cannot demonstrate that it does. "It hasn't recurred for two days" is not a fix — it is hope.

**For intermittent bugs**, the reproduction is the hard part. Strategies that help:

- Increase load (loop the test, add latency, throttle network).
- Decrease isolation (run against a real DB, real network, real concurrency).
- Capture state when it does happen (core dumps, request logs, panic-time tracebacks). Once you have a captured state, replay against it.

**Once you have a reproduction:** write it down as a failing test. The fix is then "make this test pass." This is the only definition of "fixed" that holds up under pressure.

A bug that you cannot reproduce is not a bug you can fix; it is a hypothesis you have not tested.
