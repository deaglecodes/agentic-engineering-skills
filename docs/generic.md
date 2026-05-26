# Generic Agent Guide

Use `adapters/generic/AGENTIC_ENGINEERING.md` when an AI coding tool supports a custom instruction file but not this repo's specific adapter formats.

## Install

```sh
cp adapters/generic/AGENTIC_ENGINEERING.md /path/to/project/AGENTIC_ENGINEERING.md
```

Then point the agent at that file, paste it into the agent's custom instructions, or merge it into the project instruction file the agent already reads.

## Uninstall

Remove the copied file or delete the Agentic Engineering section from the target agent's instructions.

## Smoke-Test Prompt

```text
Use the Agentic Engineering workflow. Inspect this repo, make one low-risk docs improvement, verify the diff, and summarize checks and remaining risk.
```

## Limitations

Generic agents may not support reusable skills, hooks, stop gates, or structured plans. In that case, run `scripts/validate-repo.sh`, `hooks/verify-before-finish.sh`, and package-safety checks manually.
