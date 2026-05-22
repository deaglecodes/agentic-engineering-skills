---
name: ae-diff-review
description: Use before finishing any code or config change. Review the diff for behavior changes, secret exposure, accidental churn, missing tests, and whether the implementation matches the user's requested outcome.
metadata:
  short-description: Review changes before declaring done
---

# Diff Review

## Goal

Catch avoidable mistakes before the user sees them.

## Workflow

1. Inspect changed files and command output.
2. Confirm each change maps to the requested outcome.
3. Check for unrelated formatting, generated noise, or accidental deletions.
4. Search changed files for secret-like strings.
5. Confirm tests or checks match the risk of the change.
6. Note any skipped checks and why.

## Review Checklist

- Does the diff expose tokens, keys, private URLs, cookies, or `.env` values?
- Are public docs safe to open-source?
- Are package-manager settings using the right units?
- Did npm version meet the minimum version before setting `min-release-age`?
- Is the final summary plain enough for a non-engineer?
