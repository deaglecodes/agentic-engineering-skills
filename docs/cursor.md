# Cursor Guide

Cursor can use this pack through a project rule.

## Install

```sh
mkdir -p /path/to/project/.cursor/rules
cp adapters/cursor/.cursor/rules/agentic-engineering.mdc /path/to/project/.cursor/rules/
```

## Uninstall

```sh
rm /path/to/project/.cursor/rules/agentic-engineering.mdc
```

## Smoke-Test Prompt

```text
Use the Agentic Engineering workflow. Inspect this repo first, make one safe docs improvement, verify the result, review the diff, and summarize checks.
```

## Package Safety

Cursor rules can remind the agent to use package-age safety, but they do not automatically block commands. Run the scripts manually or wire them into your local workflow:

```sh
./scripts/check-package-age-safety.sh --scope=all
./scripts/setup-package-age-safety.sh --mode=project-local --target .
```

## Limitations

- Cursor does not read `.claude-plugin/` or `CLAUDE.md` by default.
- Hook behavior depends on external tooling; the Cursor rule is an instruction, not an enforcement layer.
- Keep existing project rules in mind when merging this rule.
