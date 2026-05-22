# Agentic Engineering Skills

Agentic Engineering Skills is an open-source skill pack for people who build software with AI. It turns loose vibe-coding into a steadier loop: clarify the goal, write a plan, make small changes, verify the result, inspect the diff, and protect package installs from fresh malicious releases.

The project is inspired by Andrej Karpathy's "agentic engineering" framing, but it is not branded as a Karpathy project. See [docs/sources.md](docs/sources.md) for the sources and package-manager references used.

## What Is Included

- `skills/`: canonical Agent Skills.
- `adapters/codex/AGENTS.md`: a Codex-ready instruction adapter.
- `adapters/claude/CLAUDE.md`: a Claude Code-ready instruction adapter.
- `adapters/cursor/.cursor/rules/agentic-engineering.mdc`: a Cursor rule adapter.
- `templates/package-age/`: public-safe examples for 7-day package release-age settings.
- `scripts/`: safe setup and check scripts that avoid printing secrets.
- `hooks/`: optional hook examples for review gates.

## Install In An Agent

Use one adapter per project:

```sh
cp adapters/codex/AGENTS.md /path/to/project/AGENTS.md
cp adapters/claude/CLAUDE.md /path/to/project/CLAUDE.md
mkdir -p /path/to/project/.cursor/rules
cp adapters/cursor/.cursor/rules/agentic-engineering.mdc /path/to/project/.cursor/rules/
```

Install only the skill folders your agent supports. The `skills/` folder is the source of truth; adapters are short reminders.

## Package Safety

Run checks without changing anything:

```sh
./scripts/check-package-age-safety.sh
```

Preview what setup would do:

```sh
./scripts/setup-package-age-safety.sh --dry-run
```

Apply user-wide package safety:

```sh
./scripts/setup-package-age-safety.sh
```

Important: setup changes package-manager config files in your home directory. It creates private backups first by default. Use `--dry-run` to preview, or `--no-backup` if you do not want backup copies of existing config files.

## Demo

Loose prompt:

> build my app idea and make it work

Agentic prompt:

> Inspect the repo first. Clarify anything that changes the outcome. Make the smallest useful version, verify it, review the diff for secrets or risky package installs, then summarize what changed in plain English.

See [docs/demo.md](docs/demo.md) for a before/after workflow.

## Hook Usage

The hook scripts are optional guardrails for agent workflows:

```sh
./hooks/verify-before-finish.sh
./hooks/block-risky-package-install.sh npm
./hooks/block-risky-package-install.sh pnpm
```

Use `verify-before-finish.sh` before publishing or handing off changes. Use `block-risky-package-install.sh <tool>` before agent-driven installs. See [docs/hooks.md](docs/hooks.md).

## Safety Promise

- The setup script makes private backups under `~/.cache/agentic-engineering/backups` before editing existing files, keeps only recent backup folders, and supports `--no-backup`.
- The scripts do not print config file contents.
- The repo ignores common secret file patterns.
- npm is only configured when the detected npm is version `11.10.0` or newer.
- Package managers without a native 7-day release-age setting are reported as tools to avoid for AI-agent installs.

## Package Age Defaults

The default policy is 7 days: npm `min-release-age=7`, pnpm `minimumReleaseAge: 10080`, Bun `minimumReleaseAge = 604800`, Yarn `npmMinimalAgeGate: 7d`, uv `exclude-newer = "P7D"`, pip `uploaded-prior-to = P7D`, and mise `minimum_release_age = "7d"`.

## Known Limitations

Some package managers do not currently expose a native 7-day release-age gate. The install hook blocks them for agent-driven installs by default: RubyGems, Bundler, Hex/Mix, Homebrew, Cargo, Go modules, and Composer. Use lockfiles, hashes, pinned versions, and manual review for those ecosystems.
