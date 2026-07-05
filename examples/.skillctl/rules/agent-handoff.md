---
id: agent-handoff
title: Agent handoff notes
tier: 2
triggers: [handoff, baton, context transfer, agent transition, resume]
deps: []
summary: Write a handoff note when transferring work. State, next action, blockers.
---

# Agent handoff notes

When work moves between agents (or from agent to human), write a **handoff note** before stopping. Skipping this step is the single biggest source of repeated work in multi-agent systems — the next worker re-derives context the last one already had.

A good handoff note answers three questions in order:

1. **What is the current state?** Not the history. The state. "Tests pass locally; the deploy script is staged but not run; PR is open as #142." Three sentences, not a journal.
2. **What is the next concrete action?** One step. Not "continue debugging." Specifically: "Run `pytest tests/test_auth.py::test_token_refresh` and decide whether the 401 is a server clock skew or a JWT exp claim issue." If you can't write the next action, you haven't finished thinking yet.
3. **What is blocked, and on what?** Name the dependency. "Blocked on schema migration approval from the data team — pinged in #data-eng." If nothing is blocked, say so explicitly.

Keep it under 200 words. Put it in a known location (a `HANDOFF.md` at the workspace root, or a comment on the PR). The reader should be able to pick up cold and start in under a minute.

A handoff note that takes longer to read than it would have taken to re-derive the context is a failure of the format. Be ruthless about length.
