# Installation Notes

## Codex

Copy or link `adapters/codex/AGENTS.md` into a project root, then copy any wanted skill folders from `skills/` into your Codex skills directory.

## Claude Code

Copy or link `adapters/claude/CLAUDE.md` into a project root. If your Claude setup supports Agent Skills, install the matching folders from `skills/`.

## Cursor

Copy or link `adapters/cursor/.cursor/rules/agentic-engineering.mdc` into the target project.

## Package Safety

Warning: setup changes user-wide package-manager config in your home directory. Run the dry run first if you are unsure.

Run:

```sh
./scripts/setup-package-age-safety.sh --dry-run
./scripts/setup-package-age-safety.sh
./scripts/check-package-age-safety.sh
```

The scripts write only public-safe settings and do not print secret values. Existing files are backed up under `~/.cache/agentic-engineering/backups` with private permissions before edits; use `--no-backup` if you prefer not to duplicate config files.

## Hooks

Optional hooks live in `hooks/`:

- `verify-before-finish.sh`: checks whitespace and scans changed/public files for credential-like patterns.
- `block-risky-package-install.sh`: blocks package commands unless their 7-day release-age gate is active, or blocks unsupported managers that do not provide one.

Run hooks manually, or wire them into the hook system for your coding agent.
