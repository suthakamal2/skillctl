---
id: workspace-isolation
title: Workspace isolation for parallel agents
tier: 1
triggers: [worktree, workspace, isolated, parallel agents, concurrent]
deps: []
summary: Each agent gets its own git worktree. Never share a checkout.
---

# Workspace isolation for parallel agents

When more than one agent edits the same repository at the same time, isolate every agent in its own **git worktree**. A worktree is a separate working directory backed by the shared object store — same `.git`, different file tree, different `HEAD`.

```
git worktree add ../repo-agent-A feature/agent-A
git worktree add ../repo-agent-B feature/agent-B
```

This prevents the most common multi-agent failure mode: two agents stomping each other's uncommitted changes on `main`. With worktrees, each agent can `git status`, edit, and commit without seeing the other's state.

**Lifecycle.** Treat worktrees as ephemeral. Create per task, delete when the work merges. A reaper that prunes worktrees older than 24h (or with no commits in 6h) keeps the disk under control.

**The branch is not the isolation.** A single checkout switching branches between agents will lose uncommitted work the moment one agent runs `git checkout`. The worktree gives you a real filesystem boundary; the branch alone does not.

**Sync-managed checkouts.** If your repo is automatically reset to `origin/main` by a sync daemon (a `/opt/...` deployment pattern), agents **must** work in worktrees. Editing the sync-managed tree is a silent data-loss bug waiting to fire.
