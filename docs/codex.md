# Codex Guide

Codex reads `AGENTS.md` files as local operating instructions. This repo provides both a root `AGENTS.md` for contributors and `adapters/codex/AGENTS.md` for installing Agentic Engineering Skills into another project.

## Install

```sh
cp adapters/codex/AGENTS.md /path/to/project/AGENTS.md
```

Optional: copy selected `skills/*` folders into your Codex skills directory if your runtime supports local skills.

## Uninstall

Remove the copied `AGENTS.md`, or merge out the Agentic Engineering section if the project already had instructions.

## Prompt Examples

Normal prompt:

```text
Use the Agentic Engineering workflow. Add the requested feature, inspect the repo before editing, verify it, review the diff, and summarize checks.
```

Plan prompt:

```text
/plan Inspect the repo and make a short implementation plan with success criteria, files likely to change, and exact checks. Do not edit yet.
```

Goal prompt:

```text
/goal Harden this repo for release. Work autonomously, keep changes scoped, run validation, do a temp-directory smoke test, and report readiness.
```

Dependency safety prompt:

```text
Before adding a dependency, run the package-age audit. Prefer project-local 7-day release-age setup and block unsupported managers unless I approve a manual-review path.
```

Repo audit prompt:

```text
Audit this repo brutally for public release: scripts, docs, adapters, hooks, CI, evals, package safety, and overclaims. Fix what is in scope and verify.
```

Long-running task prompt:

```text
Work until the goal is handled. Give short progress updates, preserve unrelated changes, avoid global config mutation, and finish with files changed, commands run, smoke-test result, caveats, and PR text.
```

## Smoke Test

In a scratch repo, run:

```text
Use the Agentic Engineering workflow. Inspect this repo, make one safe docs improvement, verify the diff, and summarize the evidence.
```

The expected behavior is: inspect first, edit narrowly, run a relevant check, review the diff, and report remaining risk.

## Limitations

Codex behavior depends on the active runtime instructions and available tools. Hooks in this repo are examples; Codex will not automatically use Claude Code hook settings.
