# Agentic Engineering Adapter For Codex

Use this project with the `Agentic Engineering Skills` pack.

## Default Behavior

- Treat non-trivial coding as an engineering loop: clarify, plan, implement, verify, review, summarize.
- Inspect the repo before editing.
- Keep changes small and tied to the request.
- Protect secrets and private files. Never print `.env` values, tokens, keys, cookies, or private config contents.
- Use tests or concrete checks before calling work done.

## When To Use Skills

- Use `ae-core-charter` for any substantial task.
- Use `ae-spec-and-plan` before broad or ambiguous work.
- Use `ae-test-first-fix` for bugs.
- Use `ae-diff-review` before final answers after edits.
- Use `ae-security-boundaries` for auth, secrets, payments, deployments, accounts, package installs, or private data.
- Use `ae-dependency-safety` for package-manager installs, updates, and configuration.

## Finish Rule

Finish only after the requested outcome is proven by current evidence. If checks could not be run, say that plainly and name the remaining risk.
