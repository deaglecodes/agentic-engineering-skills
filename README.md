# Agentic Engineering Skills

Agentic Engineering Skills is a cross-agent workflow pack that helps AI coding agents move from loose vibe coding to spec-driven, verified, security-aware engineering.

## Problem

AI coding agents are useful, but they often make hidden assumptions, overbuild, touch unrelated files, install fresh dependencies without supply-chain guardrails, and finish without proof. This pack gives agents a compact operating loop and local checks so their work is easier to trust.

## What This Is

- Reusable skills for planning, verification, debugging, diff review, dependency safety, repo audit, and release readiness.
- Adapters for Codex, Claude Code, Cursor, and generic instruction-file agents.
- Optional Claude Code hook examples for package-install gating and pre-finish verification.
- Local scripts for package-age setup, validation, secret-like string scanning, and smoke checks.
- Evals and demos that describe expected agent behavior.

## What This Is Not

- Not an official OpenAI, Anthropic, Cursor, or Karpathy project.
- Not a sandbox, vulnerability scanner, or substitute for human code review.
- Not a promise that every package manager can enforce release-age delays.
- Not a tool that should mutate global user config by default.

## Quickstart

Clone and validate:

```sh
git clone https://github.com/deaglecodes/agentic-engineering-skills.git
cd agentic-engineering-skills
./scripts/validate-repo.sh
```

Install one adapter per target project:

```sh
# Codex
cp adapters/codex/AGENTS.md /path/to/project/AGENTS.md

# Claude Code
cp adapters/claude/CLAUDE.md /path/to/project/CLAUDE.md

# Cursor
mkdir -p /path/to/project/.cursor/rules
cp adapters/cursor/.cursor/rules/agentic-engineering.mdc /path/to/project/.cursor/rules/

# Generic agents
cp adapters/generic/AGENTIC_ENGINEERING.md /path/to/project/AGENTIC_ENGINEERING.md
```

Project-local package safety:

```sh
./scripts/check-package-age-safety.sh --scope=project --target /path/to/project
./scripts/setup-package-age-safety.sh --mode=project-local --target /path/to/project
```

Project-local setup writes only files inside the target project and does not make backup copies of existing package-manager config, so it will not duplicate private registry tokens. Review the resulting diff before committing. For pip, project-local setup writes a template only; use `PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip config for actual pip installs.

User-wide package safety is explicit:

```sh
./scripts/setup-package-age-safety.sh --mode=user-wide --dry-run
./scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide
```

## Install Modes

| Mode | Best for | What changes |
| --- | --- | --- |
| Adapter copy | One project | Adds one instruction file to the target repo. |
| Skill copy | Agents with reusable skill support | Copies selected `skills/*` folders into the agent's skill directory. |
| Claude plugin-style package | Claude Code plugin workflows | Uses `.claude-plugin/plugin.json` and the packaged `skills/`. Hooks remain optional examples. |
| Hooks | Claude Code users who want local guardrails | Adds settings entries that call scripts under `hooks/claude/`. |
| Package-safety templates | Repos that allow shared config | Adds project-local package-manager config files. |

## Agent Guides

- Codex: [docs/codex.md](docs/codex.md)
- Claude Code: [docs/claude.md](docs/claude.md)
- Cursor: [docs/cursor.md](docs/cursor.md)
- Generic agents: [docs/generic.md](docs/generic.md)

## Safety Model

The default safety posture is local and reversible:

- Inspect before editing.
- Ask only outcome-changing questions.
- Keep diffs narrow.
- Do not print secrets or private config values.
- Prefer project-local config over user-wide config.
- Use dry runs and backups before user-wide changes.
- Verify before handoff.
- Review the diff before final claims.

Run the full local gate:

```sh
./scripts/validate-repo.sh
```

## Package-Age Safety

The package-safety policy is a 7-day release-age delay where supported:

| Tool | Setting | 7-day value |
| --- | --- | --- |
| npm | `min-release-age` | `7` days, npm `11.10.0` or newer |
| pnpm | `minimumReleaseAge` | `10080` minutes |
| Bun | `minimumReleaseAge` | `604800` seconds |
| Yarn | `npmMinimalAgeGate` | `7d` |
| uv | `exclude-newer` | `P7D` |
| pip | `uploaded-prior-to` | `P7D`, pip version support required |
| mise | `minimum_release_age` | `7d` |

For pip, the project-local file is not auto-read by pip. The gate is active only when pip is pointed at it with `PIP_CONFIG_FILE`, when `PIP_UPLOADED_PRIOR_TO=P7D` is set, or when user/site pip config contains the setting.

Unsupported or weakly covered managers such as Cargo, Go modules, Composer, Homebrew, RubyGems, Bundler, and Mix should be treated as manual-review paths for agent-driven installs.

## Hooks

Claude Code hook examples live under `hooks/claude/`:

- `pretooluse-package-install-safety.sh`: blocks package install commands without a project or user/runtime age gate.
- `stop-verify-before-finish.sh`: blocks final stop when `hooks/verify-before-finish.sh` fails.
- `posttooluse-light-checks.sh`: reports whitespace issues after edits.
- `sessionstart-reminder.sh`: adds a short workflow reminder.

See [docs/hooks.md](docs/hooks.md) and [docs/claude.md](docs/claude.md).

## Skills

The core skills are:

- `ae-core-charter`
- `ae-spec-and-plan`
- `ae-verification-loop`
- `ae-diff-review`
- `ae-security-boundaries`
- `ae-dependency-safety`
- `ae-debug-loop`
- `ae-test-first-fix`
- `ae-repo-audit`
- `ae-release-readiness`

Each skill defines when to use it, workflow, do and don't rules, expected output, verification checklist, and failure modes.

## Evals And Demos

Behavior examples live in `docs/demo.md` and `evals/prompts/`. Run the eval smoke check:

```sh
./scripts/run-evals-smoke.sh
```

The eval prompts cover ambiguity handling, bug fix workflow, dependency add safety, security-sensitive requests, scope control, diff review, final validation summary, and docs maintenance.

## Comparison With Karpathy Skills

This project is directly inspired by the reference repo, but it has a different scope:

| Area | Karpathy-inspired reference | Agentic Engineering Skills |
| --- | --- | --- |
| Main focus | A compact behavioral guide for Claude Code | A cross-agent workflow pack with adapters, hooks, scripts, evals, and release assets |
| Agent support | Claude Code and Cursor | Codex, Claude Code, Cursor, and generic agents |
| Package safety | Not the focus | 7-day package release-age policy, audit/setup scripts, and hook examples |
| Verification | Behavioral principle | Local validation script, fixtures, eval smoke checks, and release checklist |
| Complexity | Very small and easy to read | Broader and more operational, with more moving parts |

Honest tradeoff: the reference repo is simpler and easier to install. This repo is heavier because it tries to cover multiple agents, supply-chain safety, hooks, and public-release readiness.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Release And Troubleshooting

- Architecture: [docs/architecture.md](docs/architecture.md)
- Release checklist: [docs/release-checklist.md](docs/release-checklist.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security: [SECURITY.md](SECURITY.md)
- Sources: [docs/sources.md](docs/sources.md)
