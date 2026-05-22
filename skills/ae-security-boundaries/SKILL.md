---
name: ae-security-boundaries
description: Use when a task touches secrets, auth, permissions, package installs, external services, payments, deployment, browser sessions, local credentials, or files that may contain private user data.
metadata:
  short-description: Keep automation inside safe boundaries
---

# Security Boundaries

## Goal

Let agents help without crossing private, costly, or irreversible boundaries.

## Workflow

1. Identify the sensitive surface: secrets, auth, money, data, deployment, or accounts.
2. Inspect filenames and schemas without printing secret values.
3. Prefer dry runs, checks, and backups before mutation.
4. Ask for explicit approval before destructive or external side effects.
5. Preserve existing config values unless the user asks to replace them.
6. Report only what changed and whether checks passed.

## Never Print

- `.env` contents.
- API keys, tokens, cookies, passwords, private keys, or auth headers.
- Private vault notes unless directly required by the user's request.
- Full config files that may contain registry tokens.

## Safer Defaults

- Use user-local tools before system-wide installs.
- Use lockfiles and package-age gates where available.
- Prefer read-only inspection when the risk is unclear.
