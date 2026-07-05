---
id: safe-deploy
title: Safe deployment protocol
tier: 2
triggers: [deploy, ship, production, rollout, canary, staging]
deps: [docker-control, branch-management]
summary: Canary first, watch p95, automate rollback on signal.
---

# Safe deployment protocol

Every production deploy moves through three gates: canary, full rollout, post-deploy watch. None are optional.

**1. Canary.** Route 1–5% of production traffic to the new build for a minimum of 10 minutes. Compare p95 latency, error rate, and any business KPI that has a real-time signal against the previous build. If anything regresses outside a noise band you've agreed in advance, automated rollback fires — no human decision in the loop.

**2. Full rollout.** Only after a clean canary, ramp to 100%. Stagger across regions if you have them; do not flip all of them at once.

**3. Post-deploy watch.** The first hour after a deploy is the highest-risk window. Whoever shipped owns the watch. Dashboards open. Alerts unmuted. No second deploy starts during this window without an explicit hand-off.

Roll back, do not roll forward, when something breaks. "Push a fix" under stress is how small incidents become big ones. Rollback is cheap; debugging at 3 a.m. is not.
