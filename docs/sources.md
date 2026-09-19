# Sources

This is an independent implementation inspired by Andrej Karpathy's writing on agentic engineering. It is not authored, maintained, or endorsed by Karpathy, and does not claim to be an official "Karpathy Method."

## Concept Sources

- [Andrej Karpathy, Sequoia Ascent 2026 summary](https://karpathy.bearblog.dev/sequoia-ascent-2026/) (April 30, 2026): primary source for the distinction between vibe coding and agentic engineering, human responsibility for software quality, and verifiable feedback loops. His page identifies its summary and cleaned transcript as AI-assisted content he reviewed.
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills): a third-party interpretation of Karpathy's observations, used as a reference for concise agent instructions. It is separate from Karpathy's own publications.

## What This Repository Adds

The project-local installer, tool-specific adapters, optional hooks, package-age checks, fixtures, and release process are this repository's implementation choices. In particular, the 7-day dependency delay is a local policy, not a rule attributed to Karpathy. These mechanisms need their own verification; inspiration is not evidence that they improve every agent or task.

The source list credits specific, inspectable references. It does not claim coverage of all of Karpathy's posts or attribute unidentified LinkedIn reposts to him.

## Agent Docs

- Claude Code overview: https://docs.anthropic.com/en/docs/claude-code/overview
- Claude Code settings: https://docs.anthropic.com/en/docs/claude-code/settings
- Claude Code hooks reference: https://docs.anthropic.com/en/docs/claude-code/hooks

## Package Age Sources

- npm `min-release-age`: https://docs.npmjs.com/cli/v11/using-npm/config
- npm changelog showing `min-release-age` added in `11.10.0`: https://docs.npmjs.com/cli/v11/using-npm/changelog/
- pnpm `minimumReleaseAge`: https://pnpm.io/settings
- Bun `minimumReleaseAge`: https://bun.com/docs/pm/cli/install
- Yarn `npmMinimalAgeGate`: https://yarnpkg.com/configuration/yarnrc
- uv `exclude-newer`: https://docs.astral.sh/uv/reference/settings/
- pip `uploaded-prior-to`: https://pip.pypa.io/en/stable/cli/pip_install/
- mise `minimum_release_age`: https://mise.jdx.dev/configuration/settings.html
