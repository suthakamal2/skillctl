---
id: three-strikes
title: Three strikes, build a tool
tier: 2
triggers: [three strikes, repeated failure, recurring bug, build a tool, automation]
deps: []
summary: Hit the same class of problem 3x? Stop fixing instances; build the tool.
---

# Three strikes, build a tool

If you hit the **same class of problem three times**, stop fixing instances and build the tool that prevents the class. The third instance is the signal that the cost of the tool is now lower than the cost of the next handful of instances.

**What counts as "the same class."** Not the same bug. The same *kind* of bug. "Three deploys broke because the migration ran on the wrong DB" is one class. "Three different deploys broke" is not.

**What counts as "the tool."** Whatever removes the foot-gun:

- A linter or pre-commit hook that catches the pattern before it lands.
- A wrapper that makes the safe path the default (or the only) path.
- A test that asserts the invariant the bug violated.
- A piece of documentation, if and only if it changes behaviour — most documentation does not.

**Track the strikes.** A repeated-failure log is cheap and powerful. Each strike: date, what failed, the class, the cost in time. When a class hits three, the entry is the case for building the tool. When a class doesn't recur, the log is still useful — it tells you which classes you've gotten right.

**The hard part is recognising you're on strike two.** Strike one looks like a bad day. Strike two looks like another bad day. Strike three is when the pattern is undeniable — and you've already paid two times the cost. A team that notices at strike two and builds the tool then is meaningfully more productive than one that waits.
