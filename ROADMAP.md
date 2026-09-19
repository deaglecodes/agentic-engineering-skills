# Roadmap

## v0.2

- First-class Codex, Claude Code, Cursor, and generic adapters.
- Claude plugin-style skill packaging.
- Optional Claude Code hook examples.
- Project-local package-age safety by default.
- Local validation and eval smoke checks.
- Release assets and public-readiness docs.

## v0.3 Candidates

- Implemented: project-local adapter installation and safe removal, with preview and preservation fixtures.
- Completed: [paired pilot and machine-readable results](evals/paired-pilot/results/2026-09-19/report.md) on three authored coding exercises; both conditions passed every run, with higher time and token usage for the pack.
- Next: freeze independent repository issues and compare conditions on harder scope, dependency, and verification decisions. The current pilot does not establish a model-quality advantage.
- Add more ecosystem-specific dependency safety recipes.
- Add adapter sync tests to detect drift between skills and instructions.
- Add optional GitHub release workflow after maintainer review.
- Add examples for real projects without including private code.

## Not Planned Without Strong Evidence

- Automatic mutation of global package-manager config by default.
- Claims that unsupported package managers are safe for agent-driven installs.
- Replacing human review, code owners, or CI policy.
