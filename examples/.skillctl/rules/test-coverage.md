---
id: test-coverage
title: Test coverage before refactoring
tier: 2
triggers: [coverage, untested, regression test, characterisation test]
deps: []
summary: Write a test that pins existing behaviour before changing how it works.
---

# Test coverage before refactoring

The first thing to do when refactoring code you don't fully understand is **write a test that pins the current behaviour**. Not the documented behaviour — the actual behaviour. These are called *characterisation tests*, and they're the only safety net that catches the difference between "I refactored this" and "I refactored this and silently changed what it does."

**The pattern.**

1. Read the code you intend to change. Pick one input/output relationship that's load-bearing.
2. Write a test that exercises that relationship against the *current* implementation. Don't assert what you think it should do — assert what it currently does, even if that's surprising.
3. Confirm the test passes.
4. Refactor.
5. Confirm the test still passes.

If step 2 reveals behaviour that looks wrong, **stop and decide**: are you refactoring (preserve behaviour) or fixing a bug (change behaviour)? Combining the two in one diff is how reviewers miss things. Split them.

**Coverage metrics are necessary but not sufficient.** "90% line coverage" doesn't mean the code works — it means every line was executed during the test. A test that runs a function and asserts nothing still contributes to coverage. Look at *branch* coverage and *mutation* testing if you want a real signal.

**Untested code is unknown code.** If a code path has no test and you're about to change it, you don't know what you're changing. Add the test first.
