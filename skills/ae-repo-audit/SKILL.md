---
name: ae-repo-audit
description: Use to inspect a repository before significant work, release readiness checks, public publishing, migration, adapter quality review, security review, or comparison against a reference repo.
metadata:
  short-description: Brutal repository audit
---

# Repo Audit

## When To Use

Use this skill before public release, before adopting a repo, when comparing to a reference implementation, or when a user asks for a brutal audit of docs, scripts, adapters, tests, hooks, safety, and claims.

## Workflow

1. Inventory tracked files, executable files, CI, scripts, adapters, docs, skills, hooks, tests, and release assets.
2. Run read-only checks first.
3. Compare structure and claims against the reference or stated goals.
4. Identify broken formatting, unsafe scripts, missing install paths, overclaims, weak tests, and secret exposure risk.
5. Prioritize findings by user impact and release risk.
6. Convert findings into a concrete repair plan.
7. Verify after fixes with local validation and a fresh-install smoke test when possible.

## Do

- Be direct about release blockers.
- Distinguish missing docs from broken behavior.
- Check executable bits and syntax.
- Validate examples against actual files and commands.
- Keep private local files out of public output.

## Don't

- Do not rely on README claims without checking files.
- Do not mutate global config during an audit.
- Do not compare unfairly against features outside the project's charter.
- Do not call a repo public-ready while evals, CI, or safety checks are missing.

## Expected Output

Provide findings, fixes made or recommended, checks run, smoke-test result, remaining caveats, and release readiness.

## Verification Checklist

- File inventory was inspected.
- Scripts and hooks passed syntax checks.
- CI exists and runs local validation.
- Docs have install, uninstall, limitations, safety, and troubleshooting paths.
- Public files do not contain secret-like strings.

## Failure Modes

- The reference repo or official docs are unavailable.
- The repo contains private material that cannot be shown.
- The audit finds issues too large for one change set.
- A required validation cannot run in the local environment.
