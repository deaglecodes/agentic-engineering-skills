# Agentic Engineering Adapter For Claude Code

This project uses the `Agentic Engineering Skills` pack.

## Operating Style

For non-trivial software work:

1. Understand the goal.
2. Inspect the current repo.
3. Ask only questions that change the outcome.
4. Make a concise plan.
5. Edit narrowly.
6. Verify with tests or concrete checks.
7. Review the diff.
8. Summarize in plain English.

## Safety

- Never print `.env` contents, tokens, keys, cookies, passwords, private registry config, or private notes.
- Ask before destructive commands, deployment, publishing, payments, or external account changes.
- Package installs should use a 7-day release-age delay when supported.
- Stop if npm is older than `11.10.0` before setting `min-release-age`.

## Skill Hints

Use the matching Agent Skill when the task fits:

- `ae-spec-and-plan`: unclear or broad implementation.
- `ae-test-first-fix`: bug repair.
- `ae-diff-review`: pre-finish review.
- `ae-security-boundaries`: sensitive surfaces.
- `ae-dependency-safety`: dependency changes.
