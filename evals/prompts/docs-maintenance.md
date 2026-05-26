# Eval: Docs Maintenance

## Prompt

```text
Update the install docs after changing the package-safety scripts.
```

## Expected Behavior

The agent should reconcile README, install docs, package-safety docs, hooks docs, and examples with the actual script behavior.

## Pass Criteria

- README commands match real script flags.
- Docs mention install, uninstall, limitations, and safe modes.
- Validation includes a docs or pack structure check.
