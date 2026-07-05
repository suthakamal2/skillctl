# I built a tool that solves the "why did my Skill not trigger?" problem

If you write Agent Skills for Claude Code, you have likely run into the problem where you ask for a task, and the agent completely ignores a perfectly good skill you wrote for it. This behaviour is due to activation relying on description-similarity scoring inside the model, which is fundamentally non-deterministic. There is a DEV.to article titled "Why Claude Code Skills Don't Trigger and How to Fix Them in 2026" discussing this. I wanted a way to know exactly what gets loaded and why, so I extracted a tool called skillctl from my private codebase. It is the missing dependency resolver and bundle manager for Agent Skills.

skillctl makes triggers deterministic by matching keyword triggers from YAML frontmatter against your prompt. If you want to know why something activated, you can ask the CLI directly to debug it. For example, running `skillctl why deploy` will show you exactly what triggered:

    $ skillctl why deploy
    # Why topic 'deploy' matches:
    
    ## Matched rules
      - safe-deploy (tier 2): Trigger word exact match — triggers: deploy, ship, production, rollout, canary

It also allows you to group related rules using named bundles and transitive dependency resolution. Instead of asking the agent to remember every relevant file, you can load a closure with one command.

    $ skillctl bundle deploy
    [Markdown content of safe-deploy, docker-control, and branch-management combined, within token budgets]

You can get started by installing it via pip: `pip install skillctl` and then running `skillctl init`. The source is MIT licensed and available at https://github.com/suthakamal2/skillctl. 

This is an early access v0.1 release. The core loader and matcher were production-tested, but the SKILL.md interoperability, CLI wrapper, and Claude Code prompt-submit hook installer are brand new. It is not a competitor to Anthropic Skills—it just reads your existing files and adds better triggers and budgets. What is missing right now is broad, battle-tested edge case handling for complex dependency graphs. I would appreciate feedback on the token budgeting and if the CLI fits naturally into your workflow.
