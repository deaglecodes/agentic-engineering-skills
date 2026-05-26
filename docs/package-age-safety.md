# 7-Day Package Safety

Package managers often install the newest matching package. If a popular package is hijacked, the newest version can be the riskiest one. A 7-day delay gives maintainers and the community time to detect and remove bad releases before an AI agent installs them.

## Modes

Read-only audit:

```sh
./scripts/check-package-age-safety.sh --scope=all
```

Project-local setup:

```sh
./scripts/setup-package-age-safety.sh --mode=project-local --target .
```

Project-local setup writes only files inside the target project. It does not make backup copies of existing package-manager config, because those files can contain private registry tokens. Review the project diff before committing.

User-wide setup:

```sh
./scripts/setup-package-age-safety.sh --mode=user-wide --dry-run
./scripts/setup-package-age-safety.sh --mode=user-wide --confirm-user-wide
```

Restore user-wide backups:

```sh
./scripts/setup-package-age-safety.sh --restore=/path/to/backup
```

## Settings

| Tool | Setting | 7-day value | Unit |
| --- | --- | --- | --- |
| npm | `min-release-age` | `7` | days |
| pnpm | `minimumReleaseAge` | `10080` | minutes |
| Bun | `minimumReleaseAge` | `604800` | seconds |
| Yarn | `npmMinimalAgeGate` | `7d` | duration |
| uv | `exclude-newer` | `P7D` | ISO duration |
| pip | `uploaded-prior-to` | `P7D` | ISO duration |
| mise | `minimum_release_age` | `7d` | duration |

## Important Version Rules

- npm must be `11.10.0` or newer before relying on `min-release-age`.
- pip duration upload filters require modern pip support. The scripts skip or warn when local pip cannot support the setting.
- Project-local pip config is provided as a template because pip does not automatically read a repo-root config file. Pip installs are protected only when `PIP_CONFIG_FILE=.agentic-engineering/package-safety/pip.conf`, `PIP_UPLOADED_PRIOR_TO=P7D`, or user/site pip config is active.

## Unsupported Managers

These package managers do not currently have a native 7-day release-age gate in this pack:

- RubyGems `gem`: Ruby packages.
- Bundler: Ruby application dependencies.
- Hex/Mix: Elixir and Erlang packages.
- Homebrew: macOS command-line apps.
- Cargo: Rust packages.
- Go modules: Go packages.
- Composer: PHP packages.

Use lockfiles, hashes, pinned versions, manual review, or a safer install path for these ecosystems.
