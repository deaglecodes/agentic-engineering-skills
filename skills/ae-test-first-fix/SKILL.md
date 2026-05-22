---
name: ae-test-first-fix
description: Use when fixing a reproducible bug or regression in existing code. First reproduce or define the failure, then add or locate a test, implement the minimum fix, and rerun targeted checks.
metadata:
  short-description: Bug fixing with a verification loop
---

# Test-First Fix

## Goal

Repair bugs with proof, not guesses.

## Workflow

1. State the failing behavior and expected behavior.
2. Reproduce the issue or explain why reproduction is not possible.
3. Add or locate a focused failing test when practical.
4. Confirm the test fails for the expected reason.
5. Make the smallest fix that addresses the root cause.
6. Rerun the focused test.
7. Run nearby regression checks if the touched code is shared.
8. Summarize root cause, fix, tests, and remaining risk.

## Guardrails

- Do not refactor unrelated code while fixing the bug.
- Do not delete failing tests to get green output.
- If no test harness exists, create the smallest repeatable check or document a manual verification path.
