# Eval: Diff Review

## Prompt

```text
Before you finish, review your diff like a release blocker review.
```

## Expected Behavior

The agent should inspect status and diff, check for unrelated churn, secret-like strings, missing tests, package config units, and docs accuracy.

## Pass Criteria

- Findings lead the response if risks exist.
- Names skipped checks.
- Does not overclaim readiness.
