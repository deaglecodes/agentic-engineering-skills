# Agentic Engineering Skills Repo

This repo contains reusable AI-agent skills and adapters. Keep all public files safe to publish.

## Working Rules

- Never copy private config values, tokens, `.env` contents, or personal vault notes into this repo.
- Keep `skills/` as the canonical source. Adapters should stay short and point back to the skill behaviors.
- Prefer plain English over jargon. The target user may not be an engineer.
- Before finishing changes, run the safety checks in `scripts/` and scan for secret-like strings.
- Package-manager safety examples must use a 7-day release-age delay.

## Adapter Rules

- Codex: use `adapters/codex/AGENTS.md`.
- Claude Code: use `adapters/claude/CLAUDE.md`.
- Cursor: use `adapters/cursor/.cursor/rules/agentic-engineering.mdc`.

Adapters are intentionally smaller than the skills. Do not turn them into long duplicated manuals.
