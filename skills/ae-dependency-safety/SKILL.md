---
name: ae-dependency-safety
description: Use when installing, updating, auditing, or configuring package managers. Enforce a 7-day release-age delay where supported, stop or warn on unsupported versions, and report managers without native age gates.
metadata:
  short-description: Package-manager release-age protection
---

# Dependency Safety

## When To Use

Use this skill before package installs, dependency updates, package-manager setup, scaffold commands that install dependencies, or docs that recommend install commands.

## Workflow

1. Identify the package manager and install action.
2. Run a read-only audit when possible: `scripts/check-package-age-safety.sh --scope=all`.
3. Prefer project-local setup: `scripts/setup-package-age-safety.sh --mode=project-local --target .`.
4. Use user-wide setup only with explicit confirmation, dry run first, backups enabled, and restore instructions.
5. Stop or warn when npm is older than `11.10.0`.
6. For unsupported managers, require lockfiles, hashes, pinned versions, manual review, or a different install path.
7. Verify settings after setup.

## Do

- Use a 7-day release-age delay.
- Keep package-manager config values out of logs when they may contain private registry data.
- Prefer project-local settings for shared repos.
- Explain unsupported managers honestly.

## Don't

- Do not globally install or update package tools just to set safety config.
- Do not silently mutate user-wide package-manager config.
- Do not claim unsupported ecosystems have native age gates.
- Do not set npm `min-release-age` on npm older than `11.10.0`.

## Expected Output

List supported managers checked, whether each has the 7-day gate, unsupported managers found, setup mode used, backup or restore path if relevant, and any install that remains blocked.

## Verification Checklist

- Project-local or user/runtime audit ran.
- npm version was checked before relying on `min-release-age`.
- Package-age units are correct: npm days, pnpm minutes, Bun seconds, Yarn duration, uv ISO duration, pip ISO duration, mise duration.
- Unsupported managers are not treated as safe by default.

## Failure Modes

- The package manager is unsupported by the pack.
- The local package-manager version does not support the needed setting.
- User-wide mutation lacks explicit approval.
- A project requires a tool that conflicts with the 7-day age policy.
