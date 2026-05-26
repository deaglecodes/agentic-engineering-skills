# Agentic Engineering Skills Repo

This repo contains reusable AI-agent skills, adapters, hooks, eval prompts, and package-safety examples. Keep every public file safe to publish.

## Working Rules

- Never copy private config values, credentials, `.env` contents, cookies, private keys, personal vault notes, or private registry config into this repo.
- Keep `skills/` as the canonical source. Adapters should stay short and point back to the skill behaviors.
- Prefer plain English over jargon. The target user may not be an engineer.
- Before finishing changes, run `./scripts/validate-repo.sh` or document why it could not run.
- Package-manager safety examples must use a 7-day release-age delay.
- Project-local package safety is the default. User-wide setup must require an explicit confirmation flag, dry-run path, backups, and restore instructions.
- Do not push to `main`, publish a plugin, tag a release, or mutate global user config unless the user explicitly asks.

## Release Gate

Before calling a release public-ready:

1. Run shell syntax checks and fixtures.
2. Run the secret scan.
3. Run eval smoke checks.
4. Check executable permissions.
5. Do a fresh-install smoke test in a temp directory.
6. Confirm README commands match actual files.

## Adapter Rules

- Codex: keep root `AGENTS.md`, `adapters/codex/AGENTS.md`, and `docs/codex.md` in sync.
- Claude Code: keep `adapters/claude/CLAUDE.md`, `.claude-plugin/`, `hooks/claude/`, and `docs/claude.md` in sync.
- Cursor: keep `adapters/cursor/.cursor/rules/agentic-engineering.mdc` and `docs/cursor.md` in sync.
- Generic agents: keep `adapters/generic/AGENTIC_ENGINEERING.md` and `docs/generic.md` in sync.

Adapters are intentionally smaller than the skills. Do not turn them into long duplicated manuals.
