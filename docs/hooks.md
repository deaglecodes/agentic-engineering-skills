# Hook Usage

Hooks are optional guardrails. They do not replace human review, tests, or least-privilege tool permissions.

## Generic Hooks

Run before publishing, committing, or handing work back:

```sh
./hooks/verify-before-finish.sh
```

It checks git whitespace and runs the repo secret-like string scan.

Run before agent-driven package installs:

```sh
./hooks/block-risky-package-install.sh npm /path/to/project
./hooks/block-risky-package-install.sh pnpm /path/to/project
./hooks/block-risky-package-install.sh yarn /path/to/project
./hooks/block-risky-package-install.sh bun /path/to/project
./hooks/block-risky-package-install.sh uv /path/to/project
./hooks/block-risky-package-install.sh pip /path/to/project
```

The hook allows supported tools when either project-local config or user/runtime config has the 7-day release-age gate. Pip is stricter: the project-local pip file is only a template, so pip is allowed only when `PIP_CONFIG_FILE`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip config makes the setting active. The hook blocks unsupported package managers such as RubyGems, Bundler, Homebrew, Cargo, Go modules, and Composer because this pack cannot enforce a native 7-day release-age delay for them.

## Claude Code Hooks

Claude Code hook examples live under `hooks/claude/`:

- `pretooluse-package-install-safety.sh`: `PreToolUse` gate for Bash package install commands.
- `stop-verify-before-finish.sh`: `Stop` gate that asks Claude to continue when verification fails.
- `posttooluse-light-checks.sh`: optional `PostToolUse` whitespace feedback after edits.
- `sessionstart-reminder.sh`: optional `SessionStart` context reminder.

Settings examples:

- `examples/claude/settings.project.json`: minimal shared project hooks.
- `examples/claude/settings.local.json`: fuller local-only hook set.

## Disable Or Debug

- Disable a hook by removing its event entry from the settings file.
- Run a hook manually with mock JSON on stdin.
- Use `--scope=project` package-safety checks before enabling package gates.
- Keep local-only experiments in `.claude/settings.local.json`.

## Limits

Hooks can block known unsafe patterns, but they cannot prove arbitrary shell commands are safe. Keep package manager permissions narrow and review generated commands.
