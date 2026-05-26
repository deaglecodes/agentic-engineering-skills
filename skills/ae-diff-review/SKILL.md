---
name: ae-diff-review
description: Use before finishing any code, docs, script, or config change. Review the diff for behavior changes, secret exposure, accidental churn, missing tests, and whether the implementation matches the user's requested outcome.
metadata:
  short-description: Review changes before declaring done
---

# Diff Review

## When To Use

Use this skill before any final response after edits, before committing, before creating a pull request, and after generated or bulk changes.

## Workflow

1. Inspect `git status` and the diff.
2. Map every changed file to the requested outcome.
3. Look for unrelated formatting, generated noise, accidental deletions, and stale docs.
4. Search changed files for credential-like strings.
5. Check package-manager settings and units when dependencies or install docs changed.
6. Confirm tests or validation match the risk of the change.
7. Note skipped checks and residual risk.

## Do

- Prioritize behavioral risks over style nits.
- Keep review notes grounded in files and commands.
- Check executable bits for scripts and hooks.
- Confirm docs match actual commands.

## Don't

- Do not ignore unrelated user changes.
- Do not hide validation failures.
- Do not claim security guarantees the repo cannot prove.
- Do not commit generated churn that does not support the task.

## Expected Output

Report whether the diff is ready, what checks passed, which files changed, and any remaining caveats or follow-up tasks.

## Verification Checklist

- `git diff --check` passes.
- Secret scan passes or findings are intentionally resolved.
- Scripts touched by the change pass syntax checks.
- New docs point to real files and commands.
- Final summary does not overclaim.

## Failure Modes

- The diff contains unrelated changes that cannot be separated safely.
- A validation command fails and the cause is not understood.
- A secret-like value appears in a public file.
- Documentation cannot be reconciled with actual behavior.
