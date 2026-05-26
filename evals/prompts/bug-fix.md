# Eval: Bug Fix Workflow

## Prompt

```text
Fix the failing save button.
```

## Expected Behavior

The agent should reproduce or define the failure, locate the relevant code, add or use a focused check, make the smallest fix, and rerun the check.

## Pass Criteria

- Captures failing and expected behavior.
- Avoids unrelated refactors.
- Reports root cause, fix, and verification.
