---
name: ae-security-boundaries
description: Use when a task touches secrets, auth, permissions, package installs, external services, payments, deployment, browser sessions, local credentials, or files that may contain private user data.
metadata:
  short-description: Keep automation inside safe boundaries
---

# Security Boundaries

## When To Use

Use this skill for secrets, authentication, package installs, permissions, deployment, publishing, payments, external services, browser profiles, production data, private notes, or local credential files.

## Workflow

1. Identify the sensitive surface: secrets, auth, money, data, deployment, or accounts.
2. Inspect filenames, schemas, and metadata without printing private values.
3. Prefer read-only checks, dry runs, local setup, and backups before mutation.
4. Ask for explicit approval before destructive or external side effects.
5. Preserve existing config values unless replacement is requested.
6. Report only what changed and whether checks passed.

## Do

- Use placeholders such as `REDACTED_VALUE` in examples.
- Keep backups private when touching user-wide config.
- Favor project-local config over user-wide config.
- Use lockfiles, package-age gates, hashes, and manual review for supply-chain work.

## Don't

- Do not print environment files, credentials, cookies, private keys, private registry config, or authorization headers.
- Do not open private notes or personal files unless directly required.
- Do not run destructive commands without approval.
- Do not publish or deploy as a side effect of a local task.

## Expected Output

State the sensitive area, the safer path chosen, the checks run, and any approval still required.

## Verification Checklist

- No private value was printed or copied into public files.
- Config mutation used project-local mode, dry run, or backup where possible.
- Unsupported package managers were handled as manual-review paths.
- External side effects were avoided or explicitly approved.

## Failure Modes

- The task requires a secret value that the agent should not see.
- The action would mutate external state without approval.
- Available tooling cannot verify the safety claim.
- Existing config may contain private values and cannot be safely displayed.
