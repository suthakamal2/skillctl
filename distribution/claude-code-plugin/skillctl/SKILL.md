---
name: skillctl
description: "Resolve rule dependencies and load bundles deterministically into Claude Code's context. Use when the user mentions rules, skills, bundles, or when they want to know why a rule did or didn't trigger."
---
<!-- MIT-licensed -->
# skillctl Claude Code Plugin

This plugin wraps the `skillctl` CLI.

## Usage

- To suggest rules: run `skillctl suggest --json "$prompt"`
- To load a bundle: run `skillctl bundle <name>`
- To debug: `skillctl why <topic>`
