# v0.2 Audit Notes

This audit compared the repo against its v0.2 goal and the simpler Karpathy-inspired reference package.

## Release Blockers Found

- README was useful but not adoption-ready: missing direct agent quickstarts, install modes, safety model, evals, roadmap, and honest comparison.
- Codex support existed but was not first-class enough: missing dedicated docs and concrete `/plan`, `/goal`, dependency-safety, repo-audit, and long-running workflow examples.
- Claude support was adapter-only: missing plugin-style metadata, hook settings examples, and Claude-specific hook docs.
- Cursor adapter existed but lacked install, uninstall, smoke-test, and limitation docs.
- Generic agent support was missing.
- Skills were not standardized; several lacked explicit when-to-use, expected output, verification, and failure-mode sections.
- Package-age setup leaned toward user-wide mutation and did not make project-local setup the default.
- Evals directory existed but had no prompt scenarios or smoke check.
- CI delegated only part of local validation and did not run a single repo validation entrypoint.
- Release assets were incomplete: no roadmap, architecture, troubleshooting, release checklist, or audit note.

## Fixes Applied

- Rewrote README for adoption and public-release honesty.
- Added first-class Codex, Claude Code, Cursor, and generic docs.
- Added `.claude-plugin/plugin.json`, Claude hook examples, and settings examples while keeping plugin metadata conservative.
- Added new skills for verification, debugging, repo audit, and release readiness.
- Reworked package-age scripts into read-only audit, project-local default setup, explicit user-wide setup, backups, and restore.
- Added eval prompts and `scripts/run-evals-smoke.sh`.
- Added `scripts/validate-repo.sh` and made CI call it.
- Added roadmap, architecture, troubleshooting, and release checklist docs.

## Remaining Caveats

- Hook examples are local guardrails, not a sandbox.
- Plugin marketplace publication still requires maintainer review and official workflow validation.
- Unsupported package managers remain manual-review paths.
- `shellcheck` is optional locally and installed in CI where feasible.
