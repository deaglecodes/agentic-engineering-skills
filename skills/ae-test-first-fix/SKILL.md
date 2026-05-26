---
name: ae-test-first-fix
description: Use when fixing a reproducible bug or regression in existing code. First reproduce or define the failure, then add or locate a test, implement the minimum fix, and rerun targeted checks.
metadata:
  short-description: Bug fixing with a verification loop
---

# Test-First Fix

## When To Use

Use this skill for known bugs, regressions, failing tests, broken scripts, incorrect docs commands, and behavior that can be reproduced or turned into a focused check.

## Workflow

1. State the failing behavior and expected behavior.
2. Reproduce the issue or explain why reproduction is not possible.
3. Add or locate a focused failing test when practical.
4. Confirm the failure is for the expected reason.
5. Make the smallest fix that addresses the root cause.
6. Rerun the focused test.
7. Run nearby regression checks if touched code is shared.
8. Summarize root cause, fix, tests, and remaining risk.

## Do

- Keep the first check as small as possible.
- Preserve the failing evidence until the fix is in place.
- Add a regression test when the project has a suitable harness.
- Document a manual verification path when automation is not available.

## Don't

- Do not delete or weaken failing tests to get green output.
- Do not refactor unrelated code while fixing the bug.
- Do not assume the first visible error is the root cause.
- Do not call a bug fixed without rerunning the relevant check.

## Expected Output

Report the failing behavior, root cause, fix, exact checks run, and any test gaps that remain.

## Verification Checklist

- The failure was reproduced or clearly defined.
- The fix is minimal and tied to the failure.
- Focused checks pass after the change.
- Shared code changes received broader regression checks.

## Failure Modes

- The bug cannot be reproduced and no reliable acceptance check exists.
- The available test harness is broken for unrelated reasons.
- The fix requires product or security decisions outside the request.
- A broader refactor is needed and should be planned separately.
