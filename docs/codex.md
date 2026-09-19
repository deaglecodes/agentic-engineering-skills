# Codex Guide

Codex reads `AGENTS.md` files as local operating instructions. This repo provides both a root `AGENTS.md` for contributors and `adapters/codex/AGENTS.md` for installing Agentic Engineering Skills into another project.

## Install

```sh
./scripts/install.sh --agent codex --target /path/to/project --dry-run
./scripts/install.sh --agent codex --target /path/to/project
```

The installer appends a managed section to existing instructions and includes local skill references under `.agentic-engineering/pack/skills/`. It does not register native slash commands. Start a new session after installation.

## Uninstall

Run `./scripts/install.sh --target /path/to/project --uninstall` from the source checkout. Preview with `--dry-run`. Modified managed files are preserved by refusing removal. See [installation details](install.md).

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

## Verification Receipts

The installed `./.agentic-engineering/pack/scripts/verify.sh` records individual check results and compares explicitly protected files against a snapshot taken before edits. It works independently of agent hooks. See [the plan format and commands](verification-receipts.md); a single direct check may be enough for small tasks.
