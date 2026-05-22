# Security Policy

## Supported Versions

Security fixes are accepted for the current main branch. Tagged releases should upgrade to the latest patch release when available.

## Reporting A Vulnerability

Please report security issues privately before opening a public issue. If no private channel is listed on the GitHub repository, open a minimal public issue that says a security report is available without sharing exploit details or credential values.

Useful reports include:

- Affected file and line.
- What an attacker or unsafe automation could do.
- Minimal reproduction steps.
- Suggested fix, if known.

## Project Safety Rules

- Do not submit real credentials, private registry config, cookies, keys, or `.env` contents.
- Use placeholders such as `REDACTED_VALUE` in examples.
- Run `./scripts/secret-scan.sh .` before opening pull requests.
- Run `./scripts/test-fixtures.sh` after changing scripts or hooks.
