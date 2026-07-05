# Show HN: skillctl – dependency resolver for Agent Skills and Cursor Rules

Agent Skills and Cursor Rules have become standard, but their behaviour is often unpredictable because activation relies on opaque similarity scoring. There is no way to group related skills into dependency trees, context injection happens with silent truncation, and the tools are inaccessible to non-LLM callers. I extracted skillctl from a private codebase to provide a missing dependency resolver and bundle manager that addresses these problems while operating on top of your existing rule systems.

To make activation deterministic, skillctl uses keyword triggers rather than similarity scoring. You can define named bundles with transitive dependency resolution (e.g., `bundle: deploy -> [safe-deploy, docker-control, branch-management]`). To debug why a skill fired, you can run `skillctl why <topic>` and inspect the exact matches. Here is an example of suggesting rules for a prompt:

    $ skillctl suggest "deploy the new container to production"
    ╭──── Suggested bundles ─────╮
    │ - deploy (overlap 2/3):    │
    │   `skillctl bundle deploy` │
    ╰────────────────────────────╯

       Suggested rules to load (in tier order)
    ┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
    ┃ Tier ┃ ID             ┃ Triggers           ┃
    ┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
    │    2 │ safe-deploy    │ deploy, production │
    │    2 │ docker-control │ container          │
    └──────┴────────────────┴────────────────────┘

    Or load specific rules:
    skillctl load safe-deploy docker-control

skillctl is not a competitor or replacement for Anthropic Agent Skills or Cursor `.mdc` rules. It reads them and acts as a superset. You can continue writing rules as usual, and skillctl simply adds metadata fields like triggers and deps to the YAML frontmatter, then handles indexing, resolving dependencies, and enforcing token budgets. 

This is v0.1 early access. The core ran as the live rule-loader across five agent harnesses (Claude Code, Codex, Cursor, Gemini CLI, Copilot) in a private codebase for a month before I extracted it — every prompt logged against the loader it replaced. That dogfooding caught a real bug I wouldn't have found otherwise: the hook preferred the new engine even when its index had drifted from canonical, silently under-firing on a fraction of prompts (deploy-safety rules among them) until a freshness guard closed it. The CLI packaging, SKILL.md interoperability, and prompt-submit hook installers are newer, so expect rough edges — please try it, break it, and share your feedback.

Source and instructions: https://github.com/suthakamal2/skillctl (MIT licensed).
