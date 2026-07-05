---
id: hypothesis-tracking
title: Track hypotheses during debugging
tier: 2
triggers: [hypothesis, theory, debug, intermittent, troubleshoot]
deps: []
summary: Write hypotheses down with what would falsify each, before guessing.
---

# Track hypotheses during debugging

When a bug isn't obvious, the temptation is to start trying things. Resist. Instead, take 60 seconds to write down your **hypotheses** with a falsification criterion for each.

```
Bug: requests/api/users sometimes returns 502.
Hypotheses:
  H1: upstream service rate-limits us.
      Falsified if: rate-limit headers are absent during a 502.
  H2: connection pool is exhausting.
      Falsified if: pool.in_use < pool.max during a 502.
  H3: TLS renegotiation race.
      Falsified if: 502s happen with HTTP/1.0 (no TLS) test rig.
```

This forces three things:
1. You name your assumptions, which makes them inspectable.
2. You write a *cheap* test for each — the falsification criterion. Not "check the whole system" but "check this one signal."
3. You can rank hypotheses by cost-to-test, and start with the cheapest. Most bugs fall to a five-minute check, not a five-hour investigation.

**Update the list as you go.** Tick off falsified ones. Add new ones. After three rounds of "everything I tried failed," look at the list — you're likely missing a class of explanation entirely.

The discipline beats raw intelligence here. Smart engineers who guess randomly take longer than methodical engineers who don't. The artefact (the hypothesis list, written down) is what carries the discipline.
