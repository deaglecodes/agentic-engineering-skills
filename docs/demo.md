# Demo

This project changes the shape of an AI coding request from "make it work" to "prove it works."

## Before

Prompt:

```text
Build the dashboard and make the data save.
```

Typical result:

- The agent starts editing before understanding the repo.
- It may install packages without checking release age.
- It may call the work done without tests or a diff review.

## After

Prompt:

```text
Use the agentic engineering workflow. Inspect the repo, ask only outcome-changing questions, make the smallest useful dashboard, verify save/load behavior, run the safety checks, and summarize the result in plain English.
```

Expected result:

- The agent inspects the current app first.
- It makes a short plan with success criteria.
- It edits only the files needed for the dashboard.
- It verifies the save/load path.
- It runs `./hooks/verify-before-finish.sh`.
- It reports changed files, checks passed, and remaining risk.

## Package Install Example

Before an agent runs a package install:

```sh
./hooks/block-risky-package-install.sh npm .
```

If npm is too old or the 7-day delay is missing, the hook blocks the install and explains what to fix.

## Release Example

Prompt:

```text
Audit this repo for public release. Compare the docs to the actual files, run validation, do a temp-directory smoke test, and tell me whether it is ready to promote.
```

Expected result:

- The agent inventories the repo before editing.
- It identifies release blockers.
- It fixes docs, scripts, hooks, and tests within scope.
- It runs `./scripts/validate-repo.sh`.
- It reports smoke-test results and caveats without overclaiming.
