# Agentic Engineering Adapter

Use this file with agents that support a root instruction, memory, rule, or system-prompt file.

## Operating Loop

For non-trivial software work:

1. Clarify the goal and success criteria.
2. Inspect the repo before editing.
3. Plan the smallest useful change.
4. Edit narrowly and preserve unrelated user work.
5. Verify with tests, checks, or a concrete manual path.
6. Review the diff for secrets, scope creep, and missing validation.
7. Summarize changes, evidence, and remaining risk.

## Safety Rules

- Do not print private config values, credentials, cookies, private keys, or environment files.
- Ask before destructive commands, deployment, publishing, payments, account changes, or external side effects.
- Use a 7-day package release-age delay before agent-driven package installs where supported.
- Treat unsupported package managers as manual-review paths.

## Install

Copy this file into the target agent's instruction location, then copy the specific `skills/` folders only if the agent supports reusable skills.

## Smoke-Test Prompt

```text
Use the Agentic Engineering workflow. Inspect this repo, identify one low-risk documentation improvement, make it, verify the diff, and summarize the evidence.
```

## Uninstall

Remove the copied instruction file and any copied `skills/`, hook settings, or package-safety templates.

## Limitations

Generic agents may not support hooks, skills, or structured stop gates. In that case, run the scripts manually and keep the final verification summary in the conversation.
