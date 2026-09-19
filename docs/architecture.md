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

## Project Installer

`scripts/install.sh` uses Python standard-library code to copy the public pack and add a managed instruction section. It records file hashes and executable modes, preserves existing project instructions, and refuses removal if managed content changed. Symlinked managed paths are refused. Installation neither registers native skills nor enables hooks or package settings.

## Safety Boundaries

The repo favors:

- Project-local config before user-wide config.
- Read-only audit before mutation.
- Explicit confirmation for user-wide setup.
- Private backups and restore instructions.
- Secret-like string scans before release.
- Honest caveats for unsupported package managers.

## Validation Flow

`scripts/validate-repo.sh` is the local CI-equivalent. It runs shell syntax checks, optional shellcheck, JSON validation, pack structure checks, secret scan, fixtures, project-installer tests, eval prompt structure checks, and executable-permission checks.
