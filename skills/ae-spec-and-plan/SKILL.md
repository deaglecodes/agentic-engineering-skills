---
name: ae-spec-and-plan
description: Use before implementation when a coding task is broad, ambiguous, risky, product-facing, or likely to touch multiple files. Convert intent into a decision-complete plan with success criteria, constraints, and tests.
metadata:
  short-description: Turn intent into a decision-complete plan
---

# Spec And Plan

## When To Use

Use this skill before broad features, migrations, refactors, product-facing UI, dependency changes, release work, security-sensitive work, or any request where a hidden assumption could change the result.

## Workflow

1. Inspect discoverable facts in the repo before asking questions.
2. Separate known constraints from preferences and guesses.
3. Ask only questions that change the implementation or acceptance criteria.
4. Define in-scope and out-of-scope behavior.
5. Choose the simplest path that satisfies the goal.
6. Name the files, interfaces, commands, data, and user-visible behavior that may change.
7. Define checks and expected outcomes before editing.
8. Record assumptions when a reasonable default is needed.

## Do

- Keep plans short and actionable.
- Include success criteria that can be tested or inspected.
- Call out tradeoffs when options differ in cost, risk, or user behavior.
- Use project conventions and existing tools.

## Don't

- Do not ask questions that local inspection can answer.
- Do not turn a plan into a long speculative design document.
- Do not plan destructive, publishing, or account-changing actions without explicit approval.
- Do not proceed when two plausible interpretations would produce meaningfully different behavior.

## Expected Output

Provide a concise plan with summary, key changes, files or interfaces, verification steps, assumptions, and any required approvals.

## Verification Checklist

- Success criteria are concrete.
- Scope boundaries are stated.
- Checks are tied to the requested outcome.
- Risky side effects are identified before implementation.

## Failure Modes

- The repo does not contain enough information to choose safely.
- The user request conflicts with repository or safety instructions.
- The plan depends on unavailable tools or external permissions.
- The lowest-risk path still requires approval.
