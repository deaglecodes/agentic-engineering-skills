# Claude Code Guide

Claude Code supports project instructions through `CLAUDE.md`, settings-driven hooks, and plugin-style skills. This repo includes all three paths, but keeps hooks optional and local.

## Per-Project Install

```sh
cp adapters/claude/CLAUDE.md /path/to/project/CLAUDE.md
```

Uninstall by deleting the copied file or removing the Agentic Engineering section.

## Plugin-Style Packaging

The package metadata lives in `.claude-plugin/plugin.json` and lists the skills under `skills/`. The manifest is intentionally conservative and follows the simple reference shape: metadata plus skill paths.

Hooks are packaged beside the plugin under `.claude-plugin/hooks.json` and `hooks/claude/`, but hook settings are managed through Claude Code settings files rather than assumed as plugin schema.

## Hook Install

Minimal shared project hooks:

```sh
mkdir -p /path/to/project/.claude
cp examples/claude/settings.project.json /path/to/project/.claude/settings.json
cp -R hooks /path/to/project/hooks
cp -R scripts /path/to/project/scripts
```

Local-only hook experiment:

```sh
mkdir -p /path/to/project/.claude
cp examples/claude/settings.local.json /path/to/project/.claude/settings.local.json
cp -R hooks /path/to/project/hooks
cp -R scripts /path/to/project/scripts
```

Claude Code's hook docs describe `PreToolUse`, `PostToolUse`, `Stop`, and `SessionStart`, show that hooks are configured in settings files such as `.claude/settings.json` and `.claude/settings.local.json`, and recommend `$CLAUDE_PROJECT_DIR` for project hook scripts.

## Hook Behavior

- `PreToolUse`: blocks Bash package install commands unless project-local or user/runtime package-age safety is active.
- `Stop`: runs final verification and asks Claude to continue if it fails.
- `PostToolUse`: optional whitespace feedback after edits.
- `SessionStart`: optional reminder injected at session start.

For pip installs, the project-local pip file is a template only. Claude allows pip only when `PIP_CONFIG_FILE`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip config makes `uploaded-prior-to=P7D` active.

## Disable Or Debug

- Remove the event block from `.claude/settings.json` or `.claude/settings.local.json`.
- Run hooks manually with mock JSON from `scripts/test-fixtures.sh` as a model.
- Keep local experiments in `.claude/settings.local.json`.
- If a hook blocks unexpectedly, run `./scripts/check-package-age-safety.sh --scope=all` and `./hooks/verify-before-finish.sh`.

## Smoke Test

```text
Use the Agentic Engineering workflow. Inspect the repo, make one narrow docs improvement, verify it, and summarize the diff and checks.
```

## Limitations

Hooks inspect known command patterns; they cannot prove arbitrary shell commands are safe. Keep Claude Code permissions narrow and review dependency changes.
