# skillctl One-Pager

**The missing dependency resolver and bundle manager for Agent Skills.**

- **Deterministic keyword triggers:** Rules activate by word-boundary match against the user's prompt, avoiding opaque similarity scoring.
- **Named bundles and transitive resolution:** Define groups of rules that load together (e.g., `bundle: deploy -> [safe-deploy, docker-control, branch-management]`).
- **Token-budget enforcement:** A strict cap on the context injected into the agent, complete with a manifest of what was loaded and dropped.

Anthropic Agent Skills and Cursor Rules have become essential, but their behaviour relies on unpredictable model scoring, and there is no native way to group rules or cap context length. skillctl exists to solve these four gaps. It is not a competitor to Anthropic Agent Skills—it reads them, alongside Cursor `.mdc` rules and `CLAUDE.md` files. By sitting on top of your existing files, it adds triggers, bundle semantics, introspection via `skillctl why`, and a Python library you can call from outside the agent.

**Get it:** `pip install skillctl`

**Links:**
- GitHub: https://github.com/suthakamal2/skillctl
- License: MIT
