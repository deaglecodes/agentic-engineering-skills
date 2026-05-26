# Architecture

Agentic Engineering Skills is organized around a small source-of-truth core and thin adapters.

## Source Of Truth

- `skills/`: canonical reusable behaviors.
- `scripts/`: local validation, package-age safety, fixture tests, and secret-like string scans.
- `hooks/`: generic and Claude Code hook examples.
- `templates/package-age/`: public-safe package-age config examples.
- `evals/prompts/`: behavior smoke prompts and pass criteria.

## Adapters

- `AGENTS.md`: instructions for contributors working in this repo.
- `adapters/codex/AGENTS.md`: Codex project adapter.
- `adapters/claude/CLAUDE.md`: Claude Code project adapter.
- `adapters/cursor/.cursor/rules/agentic-engineering.mdc`: Cursor project rule.
- `adapters/generic/AGENTIC_ENGINEERING.md`: fallback instruction file.

Adapters should stay shorter than the skills and avoid duplicating the full manual.

## Safety Boundaries

The repo favors:

- Project-local config before user-wide config.
- Read-only audit before mutation.
- Explicit confirmation for user-wide setup.
- Private backups and restore instructions.
- Secret-like string scans before release.
- Honest caveats for unsupported package managers.

## Validation Flow

`scripts/validate-repo.sh` is the local CI-equivalent. It runs shell syntax checks, optional shellcheck, JSON validation, pack structure checks, secret scan, fixtures, eval smoke checks, and executable-permission checks.
