---
name: ae-dependency-safety
description: Use when installing, updating, auditing, or configuring package managers. Enforce a 7-day release-age delay where supported, stop on npm older than 11.10.0, and report package managers without native age gates.
metadata:
  short-description: Package-manager release-age protection
---

# Dependency Safety

## Goal

Reduce supply-chain risk by avoiding package versions published in the last 7 days.

## Workflow

1. Detect installed package managers without printing private config values.
2. If npm is present, check `npm --version` before setting config.
3. Stop if npm is older than `11.10.0`.
4. Set supported package managers to a 7-day release-age delay.
5. Verify settings through each tool when possible.
6. Report unsupported tools and what they are typically used for.

## Required Settings

- npm: `min-release-age=7`
- pnpm: `minimumReleaseAge: 10080`
- Bun: `minimumReleaseAge = 604800`
- Yarn: `npmMinimalAgeGate: 7d`
- uv: `exclude-newer = "P7D"`
- pip: `uploaded-prior-to = P7D`
- mise: `minimum_release_age = "7d"`

## Unsupported Or Weakly Covered

Report these as tools to avoid for AI-agent dependency installs unless the project has strong lockfile, hash, and review practices:

- RubyGems `gem`: Ruby packages.
- Bundler: Ruby app dependencies.
- Hex/Mix: Elixir and Erlang packages.
- Homebrew: macOS command-line apps.
- Cargo: Rust packages.
- Go modules: Go packages.
- Composer: PHP packages.

## Plain-English Summary Format

- `npm`: found, `min-release-age=7`
- `gem`: found, no native 7-day age gate, Ruby packages
- `brew`: not found
