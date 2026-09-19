# Generic Agent Guide

Use `adapters/generic/AGENTIC_ENGINEERING.md` when an AI coding tool supports a custom instruction file but not this repo's specific adapter formats.

## Install

```sh
./scripts/install.sh --agent generic --target /path/to/project --dry-run
./scripts/install.sh --agent generic --target /path/to/project
```

Then point the agent at that file, paste it into the agent's custom instructions, or merge it into the project instruction file the agent already reads.

## Uninstall

Run `./scripts/install.sh --target /path/to/project --uninstall` from the source checkout. Preview with `--dry-run`. Modified managed files are preserved by refusing removal. See [installation details](install.md).

## Smoke-Test Prompt

```text
Use the Agentic Engineering workflow. Inspect this repo, make one low-risk docs improvement, verify the diff, and summarize checks and remaining risk.
```

## Limitations

Generic agents may not support reusable skills, hooks, stop gates, or structured plans. The installed adapter links to skill files for the agent to read. Run the target application's checks and the optional scripts under `.agentic-engineering/pack/` manually; validating the pack itself does not validate the application.
