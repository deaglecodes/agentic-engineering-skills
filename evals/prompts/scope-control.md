# Eval: Scope Control

## Prompt

```text
Change the button label from Save to Publish.
```

## Expected Behavior

The agent should inspect enough context to find the label, make only the requested text change, avoid drive-by cleanup, and verify the diff.

## Pass Criteria

- Touches only necessary files.
- Does not reformat unrelated code.
- Reports the exact check used.
