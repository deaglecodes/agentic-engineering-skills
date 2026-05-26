# Agentic Engineering Adapter For Claude Code

This project uses Agentic Engineering Skills: a workflow pack for spec-driven, verified, security-aware software work.

## Operating Style

For non-trivial software work:

1. Understand the goal and success criteria.
2. Inspect the current repo before editing.
3. Ask only questions that change the outcome.
4. Make a concise plan.
5. Edit narrowly and preserve unrelated user changes.
6. Verify with tests, scripts, rendered output, or a concrete manual path.
7. Review the diff for scope, secrets, and missing validation.
8. Summarize in plain English.

## Safety

- Never print environment files, credentials, cookies, private keys, passwords, private registry config, or private notes.
- Ask before destructive commands, deployment, publishing, payments, or external account changes.
- Package installs should use a 7-day release-age delay when supported.
- Stop or warn if npm is older than `11.10.0` before relying on `min-release-age`.
- Prefer project-local package safety. User-wide config changes require explicit confirmation, dry run, backups, and restore instructions.

## Skill Hints

Use the matching Agent Skill when the task fits:

- `ae-core-charter`: substantial work.
- `ae-spec-and-plan`: unclear, broad, or risky implementation.
- `ae-verification-loop`: final proof.
- `ae-test-first-fix` or `ae-debug-loop`: bug repair and failing commands.
- `ae-diff-review`: pre-finish review.
- `ae-security-boundaries`: sensitive surfaces.
- `ae-dependency-safety`: dependency changes.
- `ae-repo-audit`: repository audit and reference comparison.
- `ae-release-readiness`: release prep.

## Optional Hooks

This repo includes optional Claude Code hook examples under `hooks/claude/` and settings examples under `examples/claude/`. Use them locally only after reading `docs/claude.md`.
