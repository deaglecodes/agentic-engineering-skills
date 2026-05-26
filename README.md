# Agentic Engineering Skills

Agentic Engineering Skills is a small workflow pack for people who build software with AI agents.

It helps an agent slow down just enough to inspect the project, make a narrow plan, protect secrets, use safer package installs, verify the work, and explain what changed in plain English.

Current release: `0.2.0`.

## The Gamechanger

Most AI coding tools make the agent faster. This pack makes the agent more trustworthy.

Instead of hoping a long prompt is followed, Agentic Engineering Skills turns good engineering behavior into reusable instructions, optional hooks, and local checks that travel with your project. The result is a practical upgrade from "the AI wrote code" to "the AI inspected the repo, protected secrets, avoided risky fresh packages, kept the change small, proved it works, and showed the evidence."

For non-technical builders, that is the unlock: you can keep the speed and creativity of AI-assisted building while adding the habits a senior engineer would normally bring to the work.

## What You Get

- Agent instructions for Codex, Claude Code, Cursor, and generic coding agents.
- Reusable skills for planning, debugging, verification, security boundaries, dependency safety, diff review, repo audit, and release readiness.
- Optional Claude Code hooks that can block risky package installs and ask for verification before finishing.
- Local scripts for 7-day package release-age checks, repo validation, fixture tests, eval smoke tests, and secret-like string scanning.

## Why This Exists

Loose "vibe coding" can work for quick prototypes, but agents often:

- guess before reading the code,
- edit more than they need to,
- install brand-new package versions,
- miss hidden security risks,
- finish without proof.

This repo gives the agent a simple engineering loop:

```text
inspect -> plan -> change narrowly -> verify -> review diff -> summarize
```

## What This Is Not

- Not an official OpenAI, Anthropic, Cursor, or Karpathy project.
- Not a sandbox or full vulnerability scanner.
- Not a replacement for human review.
- Not something that should silently change your global machine settings.

## Quickstart

Clone the repo and check that the pack is healthy:

```sh
git clone https://github.com/deaglecodes/agentic-engineering-skills.git
cd agentic-engineering-skills
./scripts/validate-repo.sh
```

Copy one adapter into each project where you want the workflow:

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

Then try a prompt like:

```text
Use the Agentic Engineering workflow. Inspect this repo first, make the smallest useful change, verify it, review the diff, and explain the result plainly.
```

## Package Safety

The package-safety scripts help protect AI agents from installing a package version that was published too recently. The default policy is a 7-day delay where the package manager supports it.

Check a project without changing anything:

```sh
./scripts/check-package-age-safety.sh --scope=all --target /path/to/project
```

Add project-local safety files:

```sh
./scripts/setup-package-age-safety.sh --mode=project-local --target /path/to/project
```

Project-local setup writes only inside the target project and does not copy existing package-manager config, because those files can contain private registry tokens.

User-wide setup exists, but it is explicit:

```sh
./scripts/setup-package-age-safety.sh --mode=user-wide --dry-run
./scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide
```

Supported settings:

| Tool | Setting | 7-day value |
| --- | --- | --- |
| npm | `min-release-age` | `7` days, npm `11.10.0` or newer |
| pnpm | `minimumReleaseAge` | `10080` minutes |
| Bun | `minimumReleaseAge` | `604800` seconds |
| Yarn | `npmMinimalAgeGate` | `7d` |
| uv | `exclude-newer` | `P7D` |
| pip | `uploaded-prior-to` | `P7D`, modern pip required |
| mise | `minimum_release_age` | `7d` |

Pip is special: a project-local `pip.conf` is only a template unless pip is pointed at it with `PIP_CONFIG_FILE`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip config.

Package managers without a native 7-day age gate in this pack, such as Cargo, Go modules, Composer, Homebrew, RubyGems, Bundler, and Mix, should be treated as manual-review paths for agent-driven installs.

## Optional Hooks

Claude Code hook examples live in `hooks/claude/`.

- `pretooluse-package-install-safety.sh`: blocks package install commands when the 7-day gate is missing.
- `stop-verify-before-finish.sh`: asks for verification before the agent stops.
- `posttooluse-light-checks.sh`: reports whitespace issues after edits.
- `sessionstart-reminder.sh`: adds a short workflow reminder.

Generic hooks also exist:

```sh
./hooks/verify-before-finish.sh
./hooks/block-risky-package-install.sh npm /path/to/project
```

See [docs/hooks.md](docs/hooks.md) and [docs/claude.md](docs/claude.md).

## Docs

- Install guide: [docs/install.md](docs/install.md)
- Codex guide: [docs/codex.md](docs/codex.md)
- Claude Code guide: [docs/claude.md](docs/claude.md)
- Cursor guide: [docs/cursor.md](docs/cursor.md)
- Generic agent guide: [docs/generic.md](docs/generic.md)
- Package safety: [docs/package-age-safety.md](docs/package-age-safety.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- Security policy: [SECURITY.md](SECURITY.md)
- Sources: [docs/sources.md](docs/sources.md)

## Local Checks

Run everything:

```sh
./scripts/validate-repo.sh
```

Run only the behavior smoke prompts:

```sh
./scripts/run-evals-smoke.sh
```

Run the secret-like string scan:

```sh
./scripts/secret-scan.sh .
```

The secret scan is intentionally simple. It is a last-minute public-release check, not a guarantee that every secret pattern is caught.

## Design Tradeoff

This project is inspired by small agent-skill repos, including Karpathy-style workflow notes, but it is more operational: it includes adapters, scripts, hooks, tests, and package-safety templates. That makes it heavier than a single instruction file, so the recommended install path is to copy only the adapter and optional pieces you actually need.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [ROADMAP.md](ROADMAP.md), and [CHANGELOG.md](CHANGELOG.md).
