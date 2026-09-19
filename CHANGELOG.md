# Changelog

## Unreleased

- Added a reproducible paired coding pilot with three authored tasks, frozen external graders, two repetitions per condition, and public results: all six runs passed in each condition, with higher observed time and token usage for the pack.
- Added grader self-checks to repository validation without model calls, and kept evaluation tasks, answers, and transcripts out of project installations.
- Added a project-local installer for Codex, Claude Code, Cursor, and generic agents, with a preview, preserved existing instructions, working local tool paths, repeat-install detection, and removal that refuses modified managed files.
- Added installer fixtures for all four adapters, real installed-tool invocation, preservation of user edits, path conflicts, and symlink refusal.
- Clarified the Karpathy inspiration and separated primary sources, third-party interpretations, and this repository's implementation choices.
- Clarified that eval smoke checks validate prompt structure rather than model behavior.
- Simplified the README so the project purpose, quickstart, package safety, hooks, and checks are easier to understand.
- Added a clearer README USP section explaining the practical jump from loose AI coding to verified agentic engineering.
- Removed the old v0.2 audit note from public docs because it was internal release history, not user-facing guidance.

## 0.2.0 - 2026-05-26

- Hardened the repo for a v0.2 release pass.
- Rewrote the README around adoption, safety model, install modes, evals, hooks, and honest comparison with the Karpathy-inspired reference repo.
- Added first-class Codex, Claude Code, Cursor, and generic agent docs.
- Added Claude plugin-style metadata, packaged hook examples, and settings examples.
- Added standardized skill structure and new verification, debug, repo-audit, and release-readiness skills.
- Changed package-age setup to default to project-local files and require explicit confirmation for user-wide config.
- Added local validation, eval smoke checks, and stronger fixture tests.
- Added release checklist, troubleshooting, architecture docs, and roadmap.
- Added issue templates for bugs, features, and safety reports.
- Added a before/after demo.
- Simplified package-age logic by sharing common shell helpers.
- Clarified README quickstart and security reporting guidance.

## 0.1.0 - 2026-05-22

- Added canonical Agentic Engineering skills.
- Added Codex, Claude, and Cursor adapters.
- Added 7-day package release-age templates for npm, pnpm, Bun, Yarn, uv, pip, and mise.
- Added setup and verification scripts.
- Added optional hooks for final review and package-install gating.
- Added security, contribution, installation, and source documentation.
