# Security Policy

## Supported Versions

Security fixes are accepted for the current main branch. Tagged releases should upgrade to the latest patch release when available.

## Reporting A Vulnerability

Please report security issues privately before opening a public issue. Use GitHub private vulnerability reporting when it is enabled for this repository.

If private reporting is unavailable, open a minimal public issue that says a security report is available. Do not include exploit details, credential values, private config, cookies, keys, or `.env` contents in the public issue.

Useful reports include:

- Affected file and line.
- What an attacker or unsafe automation could do.
- Minimal reproduction steps.
- Suggested fix, if known.

## Project Safety Rules

- Do not submit real credentials, private registry config, cookies, keys, or `.env` contents.
- Use placeholders such as `REDACTED_VALUE` in examples.
- Run `./scripts/secret-scan.sh .` before opening pull requests.
- Run `./scripts/validate-repo.sh` after changing scripts, hooks, adapters, or release docs.
- Prefer project-local package-safety setup. User-wide setup must be explicit, use dry-run first, and keep private backups with restore instructions.
