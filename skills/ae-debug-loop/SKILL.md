---
name: ae-debug-loop
description: Use for diagnosing failing commands, broken workflows, CI failures, and unexpected runtime behavior. Form a hypothesis, gather evidence, change one thing, and verify.
metadata:
  short-description: Diagnose failures without guessing
---

# Debug Loop

## When To Use

Use this skill when commands fail, CI is red, a hook blocks unexpectedly, a script behaves differently across environments, or a bug is not yet reproduced well enough for a test-first fix.

## Workflow

1. Capture the exact failing command and short error.
2. Identify what changed recently or what assumption may be wrong.
3. Gather targeted evidence from files, versions, environment shape, and logs without exposing secrets.
4. Form one hypothesis.
5. Make one minimal change or run one diagnostic.
6. Verify the hypothesis.
7. Repeat until the cause is known or a blocker is documented.

## Do

- Reduce noisy logs to the relevant lines.
- Check versions and paths when tool behavior differs.
- Keep each change reversible.
- Record the final cause in plain English.

## Don't

- Do not shotgun multiple unrelated fixes.
- Do not paste private config or credential values.
- Do not hide uncertainty behind confident language.
- Do not keep rerunning the same failing command without learning something.

## Expected Output

Report symptom, evidence gathered, root cause or current hypothesis, fix attempted, verification result, and remaining blocker if any.

## Verification Checklist

- The exact failure is captured.
- The root cause is supported by evidence.
- The final check reproduces success or the blocker is concrete.
- No private values were exposed while debugging.

## Failure Modes

- The failure depends on unavailable external state.
- The error output is too sparse and no additional diagnostics are available.
- Tool versions differ in a way the repo cannot control.
- Fixing the issue requires a product or safety decision.
