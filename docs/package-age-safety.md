# 7-Day Package Safety

Package managers usually install the newest matching package. If a bad actor hijacks a popular package and publishes a malicious version, the freshest version is often the risky one. A 7-day delay gives the community time to find and remove bad releases before an AI agent installs them.

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

## Important npm Rule

Do not set `min-release-age` on npm older than `11.10.0`. Older npm versions may ignore the setting. The setup script stops before touching npm config if it detects an old npm.

## Tools To Avoid For Agent Installs

Some package managers do not currently provide a native release-age delay. They may still be useful, but they should not be the default path for AI-agent dependency installs:

- RubyGems `gem`: Ruby packages.
- Bundler: Ruby application dependencies.
- Hex/Mix: Elixir and Erlang packages.
- Homebrew: macOS command-line apps.
- Cargo: Rust packages.
- Go modules: Go packages.
- Composer: PHP packages.

Use lockfiles, hashes, pinned versions, and manual review for these ecosystems.
