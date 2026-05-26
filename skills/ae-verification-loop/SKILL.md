---
name: ae-verification-loop
description: Use when a task needs proof before handoff. Choose targeted checks, run them, interpret failures, and produce a final validation summary instead of relying on confidence.
metadata:
  short-description: Verify work before handoff
---

# Verification Loop

## When To Use

Use this skill after implementation, before final handoff, before release, after script changes, or whenever the user asks for proof that the work is done.

## Workflow

1. Identify the claim that needs proof.
2. Pick the smallest check that directly tests the claim.
3. Run syntax, unit, integration, lint, render, smoke, or manual checks as appropriate.
4. If a check fails, inspect the cause before changing code.
5. Rerun the failed check after the fix.
6. Add broader validation when the touched area is shared or release-facing.
7. Summarize checks with pass, fail, skipped, and residual risk.

## Do

- Tie each check to a claim.
- Prefer repeatable commands over visual confidence.
- Keep raw logs concise in the final response.
- Document skipped checks and why they matter.

## Don't

- Do not treat "no obvious error" as verification.
- Do not bury failing checks in a success summary.
- Do not run risky commands just to increase confidence.
- Do not over-test unrelated areas when a focused check proves the change.

## Expected Output

Produce a validation summary with commands run, results, failures fixed, skipped checks, and release readiness.

## Verification Checklist

- At least one meaningful check proves the requested behavior.
- Shell scripts pass syntax checks when touched.
- Docs commands were tested or manually reconciled.
- Final summary distinguishes evidence from assumptions.

## Failure Modes

- Required services, secrets, or external systems are unavailable.
- A failure is unrelated but blocks trustworthy handoff.
- The repo has no automated harness and manual checks are insufficient.
- The verification command would mutate external state.
