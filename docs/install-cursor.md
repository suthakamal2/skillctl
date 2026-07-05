# Using skillctl with Cursor

Cursor doesn't have a true `UserPromptSubmit` hook that runs scripts synchronously before sending the prompt. However, you can use `skillctl` within Cursor rules or tasks.

## Approach 1: Pre-prompt shell script

Write a wrapper script that generates your prompt and copies the dynamic context:

```bash
#!/bin/bash
prompt="$1"
context=$(skillctl suggest "$prompt" | skillctl load --stdin)
echo "$context" | pbcopy
echo "Prompt copied to clipboard with context. Paste it into Cursor."
```

## Approach 2: Cursor Tasks

If you're using tasks, run `skillctl suggest "$prompt"` as a shell command inside your task preparation step and include the output.
