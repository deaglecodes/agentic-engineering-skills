# Cursor Guide

Cursor can use this pack through a project rule.

## Install

```sh
./scripts/install.sh --agent cursor --target /path/to/project --dry-run
./scripts/install.sh --agent cursor --target /path/to/project
```

## Uninstall

Run `./scripts/install.sh --target /path/to/project --uninstall` from the source checkout. Preview with `--dry-run`. Modified managed files are preserved by refusing removal. See [installation details](install.md).

## Smoke-Test Prompt

```text
Use the Agentic Engineering workflow. Inspect this repo first, make one safe docs improvement, verify the result, review the diff, and summarize checks.
```

## Package Safety

Cursor rules can remind the agent to use package-age safety, but they do not automatically block commands. Run the scripts manually or wire them into your local workflow:

```sh
./.agentic-engineering/pack/scripts/check-package-age-safety.sh --scope=all --target .
./.agentic-engineering/pack/scripts/setup-package-age-safety.sh --mode=project-local --target .
```

## Limitations

- Cursor does not read `.claude-plugin/` or `CLAUDE.md` by default.
- Hook behavior depends on external tooling; the Cursor rule is an instruction, not an enforcement layer.
- Keep existing project rules in mind when merging this rule.
