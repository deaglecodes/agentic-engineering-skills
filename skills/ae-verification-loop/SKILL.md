---
name: ae-verification-loop
description: Choose checks for a coding change and report actual results. Use the optional receipt runner for several checks or preservation of unrelated user files.
metadata:
  short-description: Verify work before handoff
---

# Verification Loop

## When To Use

Use this skill after implementation, before final handoff, before release, after script changes, or whenever the user asks for proof that the work is done.

## Workflow

1. Choose project checks that directly establish the requested behavior. A single direct command may be enough.
2. For several checks or unrelated files that must stay untouched, use `scripts/verify.sh`: define separate argv entries in a JSON plan, snapshot protected files before editing, then run the plan after implementation. Read [the receipt guide](../../docs/verification-receipts.md) for its schema and commands. Installed paths are under `.agentic-engineering/pack/`.
3. Read each result. A successful final command does not erase an earlier failure. A timeout or unavailable executable is not a pass.
4. Fix relevant failures and rerun the affected checks. Keep earlier receipts; use a new output filename.
5. Report what ran, what failed or was skipped, and any behavior the checks did not establish.

## Do

- Tie each check to a claim.
- Prefer repeatable commands over visual confidence.
- Keep raw logs concise in the final response.
- Document skipped checks and why they matter.
- Choose protected paths from the user's scope; the runner detects changes but does not restore them.

## Don't

- Do not treat "no obvious error" as verification.
- Do not bury failing checks in a success summary.
- Do not run risky commands just to increase confidence.
- Do not over-test unrelated areas when a focused check proves the change.
- Do not regenerate a snapshot after accidental edits just to obtain a passing receipt.
- Do not substitute pack validation for the application's own checks.

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
