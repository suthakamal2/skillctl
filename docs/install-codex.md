# Using skillctl with Codex CLI

Codex CLI supports passing instructions explicitly.

## Injecting Context

You can pipe `skillctl bundle` or `skillctl load` output directly into the `--instructions` flag:

```bash
skillctl bundle deploy | codex --instructions @-
```

Or for dynamic suggestion based on your prompt:

```bash
skillctl inject "I want to deploy the app" | codex --instructions @-
```
