# I built a tool to manage and debug .mdc Cursor rules using deterministic triggers

As your collection of Cursor `.mdc` rules grows, managing which rules activate for a given task becomes messy. Cursor rules use globs and LLM similarity matching, which can sometimes lead to unexpected behaviour. I built skillctl, a dependency resolver and bundle manager that reads your existing `.cursor/rules/*.mdc` files. Because both use YAML frontmatter, skillctl can sit on top of your existing rules and add deterministic keyword triggers, transitive dependency resolution, and strict token-budget enforcement.

By defining explicit triggers, you remove the guesswork. skillctl uses word-boundary matching against your prompt, meaning you can predict exactly what will load. You can run `skillctl suggest` to see which rules it would pick up for a given request:

    $ skillctl suggest "we need to deploy v2 to staging tonight"
    # Suggested BUNDLES (prefer these over individual rules):
      - deploy (overlap 3/3): skillctl bundle deploy
    
    # Suggested rules to load (in tier order):
      tier 2: safe-deploy  (triggers: deploy)
      tier 2: docker-control  (triggers: deploy)
      tier 2: branch-management  (triggers: staging)

You can also use skillctl to define named bundles. For instance, a `deploy` bundle could transitively resolve to multiple rules, ensuring all necessary context is loaded together. 

    $ skillctl bundle deploy
    [Markdown content of safe-deploy, docker-control, and branch-management combined, within token budgets]

You can try it out by running `pip install skillctl` and pointing it at your rules directory. The project is MIT licensed and available at https://github.com/suthakamal2/skillctl.

This is a v0.1 early access release extracted from a private codebase. Note that for Cursor specifically, the prompt-submit-hook integration is weaker because Cursor does not expose one directly. However, the CLI remains highly useful for pre-task setup, generating context bundles, and running `skillctl why` to debug rule activation directly in your editor terminal. I would love feedback on how it handles your existing `.mdc` files and whether the token budget enforcement is helpful.
