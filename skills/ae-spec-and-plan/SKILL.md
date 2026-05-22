---
name: ae-spec-and-plan
description: Use before implementation when a coding task is broad, ambiguous, risky, product-facing, or likely to touch multiple files. Convert intent into a decision-complete plan with success criteria, constraints, and tests.
metadata:
  short-description: Turn intent into a decision-complete plan
---

# Spec And Plan

## Goal

Turn a rough request into a clear engineering plan.

## Workflow

1. Inspect the repo for discoverable facts before asking questions.
2. Separate facts from preferences.
3. Ask only questions that change the plan.
4. Define what is in scope and out of scope.
5. Choose the simplest implementation path that satisfies the goal.
6. Name the files, interfaces, checks, and acceptance criteria.
7. Record assumptions if the user does not choose a preference.

## Plan Shape

- Summary: one paragraph.
- Key changes: behavior-level bullets.
- Interfaces: public files, commands, schemas, or APIs that change.
- Test plan: exact checks and expected outcomes.
- Assumptions: defaults chosen and why.

## Stop Conditions

- If implementation could expose secrets, change accounts, spend money, or publish externally, require explicit user approval.
- If multiple designs would produce meaningfully different user outcomes, ask before planning.
